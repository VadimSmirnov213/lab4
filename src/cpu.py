

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.isa import Opcode, decode, word_from_bytes

MMIO_IN_DATA = 0xFF00
MMIO_IN_STATUS = 0xFF01
MMIO_OUT_DATA = 0xFF02


@dataclass(frozen=True)
class TickLog:
    tick: int
    ip: int
    word: int
    opcode: str
    regs: tuple[int, ...]
    in_interrupt: bool


class CPU:
    def __init__(
        self,
        memory: list[int] | None = None,
        input_bytes: bytes | None = None,
        interrupt_schedule: list[tuple[int, int]] | None = None,
        interrupt_vector_addr: int = 0,
    ) -> None:
        self.memory: list[int] = list(memory or [])
        self.regs: list[int] = [0] * 8
        self.ip: int = 0
        self.tick: int = 0
        self.halted: bool = False
        self.last_trap: int | None = None
        self.logs: list[TickLog] = []
        self.input_buffer: list[int] = list(input_bytes or b"")
        self.output_buffer: list[int] = []
        self.interrupt_schedule: list[tuple[int, int]] = sorted(list(interrupt_schedule or []), key=lambda x: x[0])
        self.interrupt_vector_addr: int = interrupt_vector_addr
        self.in_interrupt: bool = False
        self.return_ip: int | None = None
        self.pending_irq_values: list[int] = []

    def _ensure_addr(self, addr: int) -> None:
        if addr < 0:
            raise ValueError(f"negative memory address: {addr}")
        if addr >= len(self.memory):
            self.memory.extend([0] * (addr - len(self.memory) + 1))

    def _poll_interrupt_event(self) -> None:
        while self.interrupt_schedule and self.interrupt_schedule[0][0] <= self.tick:
            _, value = self.interrupt_schedule.pop(0)
            self.pending_irq_values.append(value & 0xFF)

    def _try_enter_interrupt(self) -> bool:
        if self.in_interrupt:
            return False
        if not self.pending_irq_values:
            return False
        self.return_ip = self.ip
        self.in_interrupt = True
        self.ip = self.interrupt_vector_addr
        return True

    def _read_mmio(self, addr: int) -> int | None:
        if addr == MMIO_IN_DATA:
            if self.pending_irq_values:
                value = self.pending_irq_values.pop(0)
                return value
            if self.input_buffer:
                return self.input_buffer.pop(0) & 0xFF
            return 0
        if addr == MMIO_IN_STATUS:
            return 1 if (self.pending_irq_values or self.input_buffer) else 0
        if addr == MMIO_OUT_DATA:
            return 0
        return None

    def _write_mmio(self, addr: int, value: int) -> bool:
        if addr == MMIO_OUT_DATA:
            self.output_buffer.append(value & 0xFF)
            return True
        if addr in {MMIO_IN_DATA, MMIO_IN_STATUS}:
            return True
        return False

    def _read_mem(self, addr: int) -> int:
        mmio_value = self._read_mmio(addr)
        if mmio_value is not None:
            return mmio_value
        self._ensure_addr(addr)
        return self.memory[addr] & 0xFFFFFFFF

    def _write_mem(self, addr: int, value: int) -> None:
        if self._write_mmio(addr, value):
            return
        self._ensure_addr(addr)
        self.memory[addr] = value & 0xFFFFFFFF

    def step(self) -> None:
        if self.halted:
            return
        self._poll_interrupt_event()
        if self._try_enter_interrupt():
            self.logs.append(
                TickLog(
                    tick=self.tick,
                    ip=self.ip,
                    word=0,
                    opcode="IRQ_ENTER",
                    regs=tuple(self.regs),
                    in_interrupt=self.in_interrupt,
                )
            )
            self.tick += 1
            return
        word = self._read_mem(self.ip)
        instr = decode(word)
        next_ip = self.ip + 1

        if instr.opcode == Opcode.HLT:
            self.halted = True
        elif instr.opcode == Opcode.IRET:
            if not self.in_interrupt or self.return_ip is None:
                raise RuntimeError("IRET executed outside interrupt context")
            next_ip = self.return_ip
            self.return_ip = None
            self.in_interrupt = False
        elif instr.opcode == Opcode.ADD:
            self.regs[instr.rd] = (self.regs[instr.rs1] + self.regs[instr.rs2]) & 0xFFFFFFFF
        elif instr.opcode == Opcode.SUB:
            self.regs[instr.rd] = (self.regs[instr.rs1] - self.regs[instr.rs2]) & 0xFFFFFFFF
        elif instr.opcode == Opcode.LD:
            addr = self.regs[instr.rs1]
            self.regs[instr.rd] = self._read_mem(addr)
        elif instr.opcode == Opcode.ST:
            addr = self.regs[instr.rd]
            self._write_mem(addr, self.regs[instr.rs1])
        elif instr.opcode == Opcode.BEQ:
            if self.regs[instr.rs1] == self.regs[instr.rs2]:
                next_ip = instr.imm
        elif instr.opcode == Opcode.JMP:
            next_ip = instr.imm
        elif instr.opcode == Opcode.TRAP:
            self.last_trap = instr.imm
        else:
            raise ValueError(f"unsupported opcode in CPU: {instr.opcode}")

        self.logs.append(
            TickLog(
                tick=self.tick,
                ip=self.ip,
                word=word,
                opcode=instr.opcode.name,
                regs=tuple(self.regs),
                in_interrupt=self.in_interrupt,
            )
        )
        self.tick += 1
        self.ip = next_ip

    def run(self, max_ticks: int = 100_000) -> None:
        while not self.halted and self.tick < max_ticks:
            self.step()
        if not self.halted:
            raise RuntimeError(f"execution did not halt within {max_ticks} ticks")


def load_words_from_binary(path: str) -> list[int]:
    data = Path(path).read_bytes()
    if len(data) % 4 != 0:
        raise ValueError("binary size must be a multiple of 4 bytes")
    return [word_from_bytes(data[i : i + 4]) for i in range(0, len(data), 4)]
