from src.isa import Instruction, Opcode, decode, encode, word_from_bytes, word_to_bytes


def test_encode_decode_roundtrip_add() -> None:
    instr = Instruction(opcode=Opcode.ADD, rd=1, rs1=2, rs2=3, imm=0)
    word = encode(instr)
    decoded = decode(word)
    assert decoded == instr


def test_encode_decode_roundtrip_beq_negative_imm() -> None:
    instr = Instruction(opcode=Opcode.BEQ, rd=0, rs1=4, rs2=5, imm=-12)
    word = encode(instr)
    decoded = decode(word)
    assert decoded == instr


def test_word_bytes_roundtrip() -> None:
    instr = Instruction(opcode=Opcode.JMP, rd=0, rs1=0, rs2=0, imm=256)
    word = encode(instr)
    raw = word_to_bytes(word)
    restored = word_from_bytes(raw)
    assert restored == word
    assert decode(restored) == instr


def test_encode_decode_roundtrip_mul_and_branch() -> None:
    mul_instr = Instruction(opcode=Opcode.MUL, rd=5, rs1=1, rs2=2, imm=0)
    bgt_instr = Instruction(opcode=Opcode.BGT, rd=0, rs1=5, rs2=3, imm=127)
    assert decode(encode(mul_instr)) == mul_instr
    assert decode(encode(bgt_instr)) == bgt_instr
