from __future__ import annotations

from dataclasses import dataclass

from src.ak_lab4.isa import Instruction, Opcode, decode
from src.ak_lab4.simulator.cache import SimpleCache
from src.ak_lab4.simulator.io import MMIO_IN_DATA, MMIO_IN_STATUS, MMIO_OUT_DATA


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
        cache_lines: int = 16,
        cache_hit_ticks: int = 1,
        cache_miss_ticks: int = 10,
        detailed_tick: bool = False,
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
        self.cache = SimpleCache(lines_count=cache_lines)
        self.cache_hit_ticks = cache_hit_ticks
        self.cache_miss_ticks = cache_miss_ticks
        self.detailed_tick = detailed_tick
        self.irq_data_latch: int | None = None
        self.phase: str = "FETCH"
        self.current_word: int | None = None
        self.current_instr: Instruction | None = None
        self.current_instr_ip: int = 0
        self.next_ip: int = 0
        self.mem_kind: str | None = None
        self.mem_addr: int = 0
        self.mem_rd: int = 0
        self.mem_value: int = 0
        self.mem_wait_remaining: int = 0
        self.mem_value_latch: int = 0
        self.mem_initialized: bool = False

    @staticmethod
    def _as_signed32(value: int) -> int:
        value &= 0xFFFFFFFF
        if value & 0x80000000:
            return value - 0x100000000
        return value

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
        if self.irq_data_latch is None:
            self.irq_data_latch = self.pending_irq_values.pop(0)
        self.return_ip = self.ip
        self.in_interrupt = True
        self.ip = self.interrupt_vector_addr
        self.phase = "FETCH"
        self.current_word = None
        self.current_instr = None
        self.mem_kind = None
        self.mem_wait_remaining = 0
        self.mem_initialized = False
        return True

    def _read_mmio(self, addr: int) -> int | None:
        if addr == MMIO_IN_DATA:
            if self.irq_data_latch is not None:
                value = self.irq_data_latch
                self.irq_data_latch = None
                return value
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

    def _log_event(self, opcode: str) -> None:
        self.logs.append(
            TickLog(
                tick=self.tick,
                ip=self.ip,
                word=0,
                opcode=opcode,
                regs=tuple(self.regs),
                in_interrupt=self.in_interrupt,
            )
        )

    def _tick_phase(self, phase: str) -> None:
        if self.detailed_tick:
            self.logs.append(
                TickLog(
                    tick=self.tick,
                    ip=self.ip,
                    word=0,
                    opcode=f"PHASE_{phase}",
                    regs=tuple(self.regs),
                    in_interrupt=self.in_interrupt,
                )
            )

    def _log_cache_and_add_penalty(self, is_hit: bool) -> None:
        if is_hit:
            self._log_event("CACHE_HIT")
            self.mem_wait_remaining = self.cache_hit_ticks
        else:
            self._log_event("CACHE_MISS")
            self.mem_wait_remaining = self.cache_miss_ticks

    def _backing_read(self, addr: int) -> int:
        self._ensure_addr(addr)
        return self.memory[addr] & 0xFFFFFFFF

    def _backing_write(self, addr: int, value: int) -> None:
        self._ensure_addr(addr)
        self.memory[addr] = value & 0xFFFFFFFF

    def _fetch_word(self, addr: int) -> int:
        self._ensure_addr(addr)
        return self.memory[addr] & 0xFFFFFFFF

    def _complete_instruction(self) -> None:
        if self.current_instr is None or self.current_word is None:
            raise RuntimeError("instruction completion without decoded instruction")
        self.logs.append(
            TickLog(
                tick=self.tick,
                ip=self.current_instr_ip,
                word=self.current_word,
                opcode=self.current_instr.opcode.name,
                regs=tuple(self.regs),
                in_interrupt=self.in_interrupt,
            )
        )
        self.ip = self.next_ip
        self.phase = "FETCH"
        self.current_word = None
        self.current_instr = None
        self.mem_kind = None
        self.mem_wait_remaining = 0
        self.mem_initialized = False

    def step(self) -> None:
        if self.halted:
            return

        self._tick_phase("IRQ_CHECK")
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

        if self.phase == "FETCH":
            self._tick_phase("FETCH")
            self.current_instr_ip = self.ip
            self.current_word = self._fetch_word(self.ip)
            self._tick_phase("DECODE")
            self.current_instr = decode(self.current_word)
            self.next_ip = self.current_instr_ip + 1
            self.phase = "EXEC"
            self.tick += 1
            return

        if self.phase == "EXEC":
            if self.current_instr is None:
                raise RuntimeError("execute phase without decoded instruction")
            self._tick_phase("EXEC")
            instr = self.current_instr

            if instr.opcode == Opcode.HLT:
                self.halted = True
                self._complete_instruction()
            elif instr.opcode == Opcode.IRET:
                if not self.in_interrupt or self.return_ip is None:
                    raise RuntimeError("IRET executed outside interrupt context")
                self.next_ip = self.return_ip
                self.return_ip = None
                self.in_interrupt = False
                self._complete_instruction()
            elif instr.opcode == Opcode.ADD:
                self.regs[instr.rd] = (self.regs[instr.rs1] + self.regs[instr.rs2]) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.SUB:
                self.regs[instr.rd] = (self.regs[instr.rs1] - self.regs[instr.rs2]) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.MUL:
                self.regs[instr.rd] = (self.regs[instr.rs1] * self.regs[instr.rs2]) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.DIV:
                divisor = self.regs[instr.rs2]
                if divisor == 0:
                    raise RuntimeError("division by zero")
                self.regs[instr.rd] = (self.regs[instr.rs1] // divisor) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.MOD:
                divisor = self.regs[instr.rs2]
                if divisor == 0:
                    raise RuntimeError("modulo by zero")
                self.regs[instr.rd] = (self.regs[instr.rs1] % divisor) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.AND:
                self.regs[instr.rd] = self.regs[instr.rs1] & self.regs[instr.rs2]
                self._complete_instruction()
            elif instr.opcode == Opcode.OR:
                self.regs[instr.rd] = self.regs[instr.rs1] | self.regs[instr.rs2]
                self._complete_instruction()
            elif instr.opcode == Opcode.XOR:
                self.regs[instr.rd] = self.regs[instr.rs1] ^ self.regs[instr.rs2]
                self._complete_instruction()
            elif instr.opcode == Opcode.SHL:
                shift = self.regs[instr.rs2] & 0x1F
                self.regs[instr.rd] = (self.regs[instr.rs1] << shift) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.SHR:
                shift = self.regs[instr.rs2] & 0x1F
                self.regs[instr.rd] = (self.regs[instr.rs1] >> shift) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.ADDI:
                self.regs[instr.rd] = (self.regs[instr.rs1] + instr.imm) & 0xFFFFFFFF
                self._complete_instruction()
            elif instr.opcode == Opcode.LD:
                self.mem_addr = self.regs[instr.rs1]
                mmio_value = self._read_mmio(self.mem_addr)
                if mmio_value is not None:
                    self.regs[instr.rd] = mmio_value & 0xFFFFFFFF
                    self._complete_instruction()
                else:
                    self.mem_kind = "LD"
                    self.mem_rd = instr.rd
                    self.mem_initialized = False
                    self.phase = "MEM"
            elif instr.opcode == Opcode.ST:
                self.mem_addr = self.regs[instr.rd]
                self.mem_value = self.regs[instr.rs1]
                if self._write_mmio(self.mem_addr, self.mem_value):
                    self._complete_instruction()
                else:
                    self.mem_kind = "ST"
                    self.mem_initialized = False
                    self.phase = "MEM"
            elif instr.opcode == Opcode.BEQ:
                if self.regs[instr.rs1] == self.regs[instr.rs2]:
                    self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.BNE:
                if self.regs[instr.rs1] != self.regs[instr.rs2]:
                    self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.BGT:
                if self._as_signed32(self.regs[instr.rs1]) > self._as_signed32(self.regs[instr.rs2]):
                    self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.BLT:
                if self._as_signed32(self.regs[instr.rs1]) < self._as_signed32(self.regs[instr.rs2]):
                    self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.BLE:
                if self._as_signed32(self.regs[instr.rs1]) <= self._as_signed32(self.regs[instr.rs2]):
                    self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.BGE:
                if self._as_signed32(self.regs[instr.rs1]) >= self._as_signed32(self.regs[instr.rs2]):
                    self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.JMP:
                self.next_ip = instr.imm
                self._complete_instruction()
            elif instr.opcode == Opcode.TRAP:
                self.last_trap = instr.imm
                self._complete_instruction()
            else:
                raise ValueError(f"unsupported opcode in CPU: {instr.opcode}")

            self.tick += 1
            return

        if self.phase == "MEM":
            self._tick_phase("MEM")
            if self.mem_kind is None:
                raise RuntimeError("MEM phase without memory operation")

            if not self.mem_initialized:
                if self.mem_kind == "LD":
                    self.mem_value_latch, is_hit = self.cache.read(self.mem_addr, self._backing_read)
                    self._log_cache_and_add_penalty(is_hit)
                else:
                    is_hit = self.cache.write(self.mem_addr, self.mem_value, self._backing_write)
                    self._log_cache_and_add_penalty(is_hit)
                self.mem_initialized = True

            self.mem_wait_remaining -= 1
            if self.mem_wait_remaining <= 0:
                if self.mem_kind == "LD":
                    self.regs[self.mem_rd] = self.mem_value_latch & 0xFFFFFFFF
                self._complete_instruction()

            self.tick += 1
            return

        raise RuntimeError(f"unknown CPU phase: {self.phase}")

    def run(self, max_ticks: int = 100_000) -> None:
        while not self.halted and self.tick < max_ticks:
            self.step()
        if not self.halted:
            raise RuntimeError(f"execution did not halt within {max_ticks} ticks")
