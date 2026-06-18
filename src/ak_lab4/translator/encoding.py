import ast

from src.ak_lab4.isa import Instruction, Opcode
from src.ak_lab4.translator.types import ParsedLine


def parse_int(token: str) -> int:
    return int(token, 0)


def parse_cstr(token: str) -> str:
    if not (token.startswith('"') and token.endswith('"')):
        raise ValueError(f".asciiz expects quoted string, got: {token}")
    parsed = ast.literal_eval(token)
    if not isinstance(parsed, str):
        raise ValueError(f"invalid string literal: {token}")
    return parsed


def resolve_value(token: str, labels: dict[str, int], constants: dict[str, int]) -> int:
    if token in labels:
        return labels[token]
    if token in constants:
        return constants[token]
    return parse_int(token)


def directive_size(line: ParsedLine) -> int:
    if line.op == ".word":
        if len(line.args) != 1:
            raise ValueError(".word expects one argument")
        return 1
    if line.op == ".asciiz":
        if len(line.args) != 1:
            raise ValueError(".asciiz expects one quoted string argument")
        return len(parse_cstr(line.args[0])) + 1
    return 0


def pass1_collect_labels(lines: list[ParsedLine]) -> tuple[dict[str, int], dict[str, int]]:
    labels: dict[str, int] = {}
    constants: dict[str, int] = {}
    pc = 0
    for line in lines:
        if line.label is not None:
            if line.label in labels:
                raise ValueError(f"duplicate label: {line.label}")
            if line.label in constants:
                raise ValueError(f"name already used by constant: {line.label}")
            labels[line.label] = pc
        if line.kind == "instruction":
            pc += 1
            continue
        if line.kind != "directive":
            continue
        if line.op in {".text", ".data"}:
            continue
        if line.op == ".org":
            if len(line.args) != 1:
                raise ValueError(".org expects one argument")
            org_value = resolve_value(line.args[0], labels=labels, constants=constants)
            if org_value < 0:
                raise ValueError(f".org must be non-negative, got: {org_value}")
            pc = org_value
            continue
        if line.op == ".equ":
            if len(line.args) != 2:
                raise ValueError(".equ expects two arguments: NAME, VALUE")
            name = line.args[0]
            if name in constants:
                raise ValueError(f"duplicate constant: {name}")
            if name in labels:
                raise ValueError(f"name already used by label: {name}")
            constants[name] = resolve_value(line.args[1], labels=labels, constants=constants)
            continue
        pc += directive_size(line)
    return labels, constants


def parse_reg(token: str) -> int:
    token = token.strip().upper()
    if not token.startswith("%R"):
        raise ValueError(f"register expected, got: {token}")
    idx_text = token[2:]
    if not idx_text.isdigit():
        raise ValueError(f"invalid register: {token}")
    idx = int(idx_text)
    if not 0 <= idx <= 7:
        raise ValueError(f"register out of range: {token}")
    return idx


def to_instruction(
    op: str,
    args: tuple[str, ...],
    labels: dict[str, int],
    constants: dict[str, int],
) -> Instruction:
    if op in {"HLT", "IRET"}:
        if args:
            raise ValueError(f"{op} takes no arguments")
        return Instruction(opcode=Opcode[op])

    if op in {"ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "SHL", "SHR"}:
        if len(args) != 3:
            raise ValueError(f"{op} expects 3 register arguments")
        return Instruction(
            opcode=Opcode[op],
            rd=parse_reg(args[0]),
            rs1=parse_reg(args[1]),
            rs2=parse_reg(args[2]),
            imm=0,
        )

    if op == "ADDI":
        if len(args) != 3:
            raise ValueError("ADDI expects 2 registers and immediate/label")
        return Instruction(
            opcode=Opcode.ADDI,
            rd=parse_reg(args[0]),
            rs1=parse_reg(args[1]),
            rs2=0,
            imm=resolve_value(args[2], labels=labels, constants=constants),
        )

    if op in {"LD", "ST"}:
        if len(args) != 2:
            raise ValueError(f"{op} expects 2 register arguments")
        return Instruction(
            opcode=Opcode[op],
            rd=parse_reg(args[0]),
            rs1=parse_reg(args[1]),
            rs2=0,
            imm=0,
        )

    if op in {"BEQ", "BNE", "BGT", "BLT", "BLE", "BGE"}:
        if len(args) != 3:
            raise ValueError(f"{op} expects 2 registers and immediate/label")
        return Instruction(
            opcode=Opcode[op],
            rd=0,
            rs1=parse_reg(args[0]),
            rs2=parse_reg(args[1]),
            imm=resolve_value(args[2], labels=labels, constants=constants),
        )

    if op == "JMP":
        if len(args) != 1:
            raise ValueError("JMP expects immediate/label")
        return Instruction(opcode=Opcode.JMP, imm=resolve_value(args[0], labels=labels, constants=constants))

    if op == "TRAP":
        if len(args) != 1:
            raise ValueError("TRAP expects trap id immediate")
        return Instruction(opcode=Opcode.TRAP, imm=resolve_value(args[0], labels=labels, constants=constants))

    raise ValueError(f"unsupported opcode: {op}")
