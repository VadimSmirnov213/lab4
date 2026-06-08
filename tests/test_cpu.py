from src.assembler import assemble_to_words
from src.cpu import CPU, MMIO_IN_DATA, MMIO_IN_STATUS, MMIO_OUT_DATA
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


def test_cpu_mmio_input_status_and_data() -> None:
    words = [
        encode(Instruction(opcode=Opcode.LD, rd=1, rs1=0)),
        encode(Instruction(opcode=Opcode.LD, rd=2, rs1=3)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words, input_bytes=b"A")
    cpu.regs[0] = MMIO_IN_STATUS
    cpu.regs[3] = MMIO_IN_DATA

    cpu.run()

    assert cpu.regs[1] == 1
    assert cpu.regs[2] == ord("A")
    assert len(cpu.input_buffer) == 0


def test_cpu_mmio_output_data() -> None:
    words = [
        encode(Instruction(opcode=Opcode.ST, rd=0, rs1=1)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words)
    cpu.regs[0] = MMIO_OUT_DATA
    cpu.regs[1] = ord("Z")

    cpu.run()

    assert cpu.output_buffer == [ord("Z")]


def test_cpu_interrupt_schedule_enters_handler_and_returns() -> None:
    source = """
    .org 0
    irq_handler:
        LD %R7, %R6
        IRET

    .org 4
    _start:
        ADD %R1, %R1, %R1
        HLT
    """
    words = assemble_to_words(source)
    cpu = CPU(
        memory=words,
        interrupt_schedule=[(0, ord("Q"))],
        interrupt_vector_addr=0,
    )
    cpu.ip = 4
    cpu.regs[6] = MMIO_IN_DATA

    cpu.run()

    assert cpu.regs[7] == ord("Q")
    assert cpu.halted
    assert any(log.opcode == "IRQ_ENTER" for log in cpu.logs)
    assert any(log.opcode == "IRET" for log in cpu.logs)


def test_cpu_interrupt_not_nested_and_delivered_later() -> None:
    source = """
    .org 0
    irq_handler:
        LD %R7, %R6
        IRET

    .org 4
    _start:
        HLT
    """
    words = assemble_to_words(source)
    cpu = CPU(
        memory=words,
        interrupt_schedule=[(0, ord("A")), (1, ord("B"))],
        interrupt_vector_addr=0,
    )
    cpu.ip = 4
    cpu.regs[6] = MMIO_IN_DATA

    cpu.step()
    cpu.step()
    cpu.step()
    assert cpu.regs[7] == ord("A")
    assert cpu.pending_irq_values == [ord("B")]


def test_cache_miss_then_hit_affects_ticks() -> None:
    words = [
        encode(Instruction(opcode=Opcode.LD, rd=1, rs1=0)),
        encode(Instruction(opcode=Opcode.LD, rd=2, rs1=0)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words)
    cpu.regs[0] = 20
    cpu.memory.extend([0] * 32)
    cpu.memory[20] = 123

    cpu.run()

    assert cpu.tick == 14
    assert cpu.regs[1] == 123
    assert cpu.regs[2] == 123
    assert any(log.opcode == "CACHE_MISS" for log in cpu.logs)
    assert any(log.opcode == "CACHE_HIT" for log in cpu.logs)


def test_mmio_access_bypasses_cache() -> None:
    words = [
        encode(Instruction(opcode=Opcode.LD, rd=1, rs1=0)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words, input_bytes=b"X")
    cpu.regs[0] = MMIO_IN_DATA

    cpu.run()

    assert cpu.regs[1] == ord("X")
    assert cpu.tick == 2
    assert not any(log.opcode.startswith("CACHE_") for log in cpu.logs)


def test_cpu_mul_div_bne_bgt() -> None:
    words = [
        encode(Instruction(opcode=Opcode.MUL, rd=3, rs1=0, rs2=1)),
        encode(Instruction(opcode=Opcode.DIV, rd=4, rs1=3, rs2=2)),
        encode(Instruction(opcode=Opcode.BNE, rs1=4, rs2=1, imm=5)),
        encode(Instruction(opcode=Opcode.TRAP, imm=7)),
        encode(Instruction(opcode=Opcode.BGT, rs1=4, rs2=2, imm=6)),
        encode(Instruction(opcode=Opcode.HLT)),
        encode(Instruction(opcode=Opcode.TRAP, imm=9)),
        encode(Instruction(opcode=Opcode.HLT)),
    ]
    cpu = CPU(memory=words)
    cpu.regs[0] = 6
    cpu.regs[1] = 7
    cpu.regs[2] = 6

    cpu.run()

    assert cpu.regs[3] == 42
    assert cpu.regs[4] == 7
    assert cpu.last_trap == 9
