from src.assembler import assemble_to_words
from src.cpu import CPU
from src.isa import Instruction, Opcode, encode


def test_cpu_executes_arithmetic_and_halt() -> None:
    words = [
        encode(Instruction(opcode=Opcode.ADD, rd=2, rs1=0, rs2=1)),
        encode(Instruction(opcode=Opcode.SUB, rd=3, rs1=2, rs2=1)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words)
    cpu.regs[0] = 7
    cpu.regs[1] = 5

    cpu.run()

    assert cpu.regs[2] == 12
    assert cpu.regs[3] == 7
    assert cpu.halted
    assert cpu.tick == 3


def test_cpu_branch_and_jump() -> None:
    words = [
        encode(Instruction(opcode=Opcode.BEQ, rs1=0, rs2=1, imm=3)),
        encode(Instruction(opcode=Opcode.TRAP, imm=99)),
        encode(Instruction(opcode=Opcode.JMP, imm=4)),
        encode(Instruction(opcode=Opcode.TRAP, imm=1)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words)
    cpu.regs[0] = 10
    cpu.regs[1] = 10

    cpu.run()

    assert cpu.last_trap == 1
    assert cpu.halted


def test_cpu_with_assembler_integration() -> None:
    source = """
    _start:
        JMP begin
    .org 8
    begin:
        ADD %R2, %R0, %R1
        HLT
    """
    words = assemble_to_words(source)
    cpu = CPU(memory=words)
    cpu.regs[0] = 20
    cpu.regs[1] = 22

    cpu.run()

    assert cpu.regs[2] == 42
    assert cpu.halted
    assert cpu.tick == 3
