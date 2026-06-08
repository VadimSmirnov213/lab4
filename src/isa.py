

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


WORD_MASK = 0xFFFFFFFF
IMM12_MASK = 0xFFF


class Opcode(IntEnum):
    HLT = 0x00
    ADD = 0x01
    SUB = 0x02
    LD = 0x03
    ST = 0x04
    BEQ = 0x05
    JMP = 0x06
    TRAP = 0x07
    IRET = 0x08
    ADDI = 0x09
    MUL = 0x0A
    DIV = 0x0B
    BNE = 0x0C
    BGT = 0x0D


@dataclass(frozen=True)
class Instruction:
    opcode: Opcode
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    imm: int = 0


def _check_reg(name: str, value: int) -> None:
    if not 0 <= value <= 0xF:
        raise ValueError(f"{name} must fit 4 bits: {value}")


def _check_imm12(value: int) -> None:
    if not -(1 << 11) <= value <= (1 << 11) - 1:
        raise ValueError(f"imm must fit signed 12 bits: {value}")


def _encode_imm12(value: int) -> int:
    _check_imm12(value)
    return value & IMM12_MASK


def _decode_imm12(value: int) -> int:
    value &= IMM12_MASK
    if value & 0x800:
        return value - 0x1000
    return value


def encode(instr: Instruction) -> int:
    _check_reg("rd", instr.rd)
    _check_reg("rs1", instr.rs1)
    _check_reg("rs2", instr.rs2)
    imm = _encode_imm12(instr.imm)

    word = 0
    word |= (int(instr.opcode) & 0xFF) << 24
    word |= (instr.rd & 0xF) << 20
    word |= (instr.rs1 & 0xF) << 16
    word |= (instr.rs2 & 0xF) << 12
    word |= imm
    return word & WORD_MASK


def decode(word: int) -> Instruction:
    word &= WORD_MASK
    opcode_raw = (word >> 24) & 0xFF
    try:
        opcode = Opcode(opcode_raw)
    except ValueError as exc:
        raise ValueError(f"unknown opcode: 0x{opcode_raw:02X}") from exc

    rd = (word >> 20) & 0xF
    rs1 = (word >> 16) & 0xF
    rs2 = (word >> 12) & 0xF
    imm = _decode_imm12(word & IMM12_MASK)
    return Instruction(opcode=opcode, rd=rd, rs1=rs1, rs2=rs2, imm=imm)


def word_to_bytes(word: int) -> bytes:
    return (word & WORD_MASK).to_bytes(4, byteorder="big", signed=False)


def word_from_bytes(data: bytes) -> int:
    if len(data) != 4:
        raise ValueError(f"word must be exactly 4 bytes, got {len(data)}")
    return int.from_bytes(data, byteorder="big", signed=False)
