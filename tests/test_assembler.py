from pathlib import Path

from src.assembler import assemble, assemble_file, assemble_to_words
from src.isa import Instruction, Opcode, encode


def test_assemble_basic_program_with_label() -> None:
    source = """
    ; tiny program
    _start:
        ADD %R1, %R2, %R3
        BEQ %R1, %R0, done
        TRAP 1
    done:
        HLT
    """

    words = assemble_to_words(source)
    expected = [
        encode(Instruction(opcode=Opcode.ADD, rd=1, rs1=2, rs2=3)),
        encode(Instruction(opcode=Opcode.BEQ, rd=0, rs1=1, rs2=0, imm=3)),
        encode(Instruction(opcode=Opcode.TRAP, imm=1)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    assert words == expected


def test_assemble_with_org_data_and_equ() -> None:
    source = """
    .equ TRAP_PRINT, 1
    .text
    _start:
        JMP message
    .org 4
    message:
        .asciiz "OK"
    .data
    .org 16
    value:
        .word 42
    """

    words = assemble_to_words(source)
    assert words[0] == encode(Instruction(opcode=Opcode.JMP, imm=4))
    assert words[4] == ord("O")
    assert words[5] == ord("K")
    assert words[6] == 0
    assert words[16] == 42


def test_assemble_file_writes_binary_and_listing(tmp_path: Path) -> None:
    asm = tmp_path / "prog.asm"
    out_bin = tmp_path / "prog.bin"
    out_lst = tmp_path / "prog.lst"
    asm.write_text(
        """
        _start:
            TRAP 1
            HLT
        """,
        encoding="utf-8",
    )
    result = assemble_file(str(asm), str(out_bin), str(out_lst))

    assert len(result.words) == 2
    assert out_bin.exists()
    assert out_bin.stat().st_size == 8

    lst = out_lst.read_text(encoding="utf-8")
    assert "0000 - " in lst
    assert "TRAP 1" in lst
    assert "0001 - " in lst
    assert "HLT" in lst


def test_assemble_returns_listing_entries() -> None:
    source = """
    _start:
        ADD %R1, %R2, %R3
        HLT
    """
    result = assemble(source)
    assert len(result.listing_entries) == 2
    assert result.listing_entries[0].addr == 0
    assert result.listing_entries[1].addr == 1


def test_assemble_iret_instruction() -> None:
    words = assemble_to_words(
        """
        _start:
            IRET
        """
    )
    assert words == [encode(Instruction(opcode=Opcode.IRET))]


def test_assemble_with_user_macro() -> None:
    source = """
    .macro INC reg, one
        ADD reg, reg, one
    .endm

    _start:
        INC %R1, %R2
        HLT
    """
    words = assemble_to_words(source)
    assert words == [
        encode(Instruction(opcode=Opcode.ADD, rd=1, rs1=1, rs2=2)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]


def test_assemble_with_conditional_compilation() -> None:
    source = """
    .equ ENABLE_FAST, 1

    _start:
    .if ENABLE_FAST
        TRAP 1
    .else
        TRAP 2
    .endif
        HLT
    """
    words = assemble_to_words(source)
    assert words == [
        encode(Instruction(opcode=Opcode.TRAP, imm=1)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
