#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from src.isa import Instruction, Opcode, encode, word_to_bytes


@dataclass(frozen=True)
class ParsedLine:
    line_no: int
    label: str | None
    kind: str
    op: str
    args: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class ListingEntry:
    addr: int
    word: int
    text: str


@dataclass(frozen=True)
class AssembleResult:
    words: list[int]
    listing_entries: list[ListingEntry]


@dataclass(frozen=True)
class MacroDef:
    name: str
    params: tuple[str, ...]
    body: tuple[str, ...]


def _strip_comment(line: str) -> str:
    return line.split(";", 1)[0].strip()


def _split_label(line: str) -> tuple[str | None, str]:
    if ":" not in line:
        return None, line
    label, rest = line.split(":", 1)
    label = label.strip()
    if not label:
        raise ValueError("empty label definition")
    return label, rest.strip()


def _split_op_args(text: str) -> tuple[str, tuple[str, ...]]:
    parts = text.split(maxsplit=1)
    op = parts[0]
    if len(parts) == 1:
        return op, ()
    args = tuple(arg.strip() for arg in parts[1].split(",") if arg.strip())
    return op, args


def _parse_line(clean: str, raw: str, line_no: int) -> ParsedLine:
    label, rest = _split_label(clean)
    if not rest:
        return ParsedLine(line_no=line_no, label=label, kind="label", op="", args=(), source=raw)

    op, args = _split_op_args(rest)
    if op.startswith("."):
        return ParsedLine(
            line_no=line_no,
            label=label,
            kind="directive",
            op=op.lower(),
            args=args,
            source=raw,
        )
    return ParsedLine(
        line_no=line_no,
        label=label,
        kind="instruction",
        op=op.upper(),
        args=args,
        source=raw,
    )


def parse_source(source: str) -> list[ParsedLine]:
    parsed: list[ParsedLine] = []
    for line_no, raw in enumerate(source.splitlines(), start=1):
        clean = _strip_comment(raw)
        if not clean:
            continue
        parsed.append(_parse_line(clean=clean, raw=raw, line_no=line_no))
    return parsed


def _current_cond_active(stack: list[dict[str, bool]]) -> bool:
    if not stack:
        return True
    top = stack[-1]
    branch_active = top["cond_true"] if not top["in_else"] else (not top["cond_true"])
    return top["parent_active"] and branch_active


def _resolve_preproc_value(token: str, defines: dict[str, int]) -> int:
    if token in defines:
        return defines[token]
    return int(token, 0)


def _apply_macro_params(line: str, mapping: dict[str, str]) -> str:
    result = line
    for name, value in mapping.items():
        pattern = rf"\b{re.escape(name)}\b"
        result = re.sub(pattern, value, result)
    return result


def _parse_macro_signature(rest: str) -> tuple[str, tuple[str, ...]]:
    signature = rest[len(".macro") :].strip()
    if not signature:
        raise ValueError(".macro expects macro name")
    if "," in signature:
        parts = [part.strip() for part in signature.split(",") if part.strip()]
        name_and_maybe_param0 = parts[0].split()
        name = name_and_maybe_param0[0]
        params = tuple(name_and_maybe_param0[1:] + parts[1:])
        return name, params
    tokens = signature.split()
    return tokens[0], tuple(tokens[1:])


def preprocess_source(source: str) -> str:
    input_lines = deque(_strip_comment(line) for line in source.splitlines())
    output_lines: list[str] = []
    macros: dict[str, MacroDef] = {}
    defines: dict[str, int] = {}
    cond_stack: list[dict[str, bool]] = []
    current_macro_name: str | None = None
    current_macro_params: tuple[str, ...] = ()
    current_macro_body: list[str] = []
    macro_expand_limit = 512
    macro_expansions = 0

    while input_lines:
        clean = input_lines.popleft().strip()
        if not clean:
            continue

        active = _current_cond_active(cond_stack)
        label, rest = _split_label(clean)
        op = ""
        args: tuple[str, ...] = ()
        if rest:
            op, args = _split_op_args(rest)
        op_lower = op.lower()

        if current_macro_name is not None:
            if op_lower == ".endm":
                macros[current_macro_name] = MacroDef(
                    name=current_macro_name,
                    params=current_macro_params,
                    body=tuple(current_macro_body),
                )
                current_macro_name = None
                current_macro_params = ()
                current_macro_body = []
            else:
                current_macro_body.append(clean)
            continue

        if op_lower == ".if":
            if len(args) != 1:
                raise ValueError(".if expects one argument")
            parent_active = _current_cond_active(cond_stack)
            cond_true = bool(_resolve_preproc_value(args[0], defines)) if parent_active else False
            cond_stack.append({"parent_active": parent_active, "cond_true": cond_true, "in_else": False})
            continue

        if op_lower == ".else":
            if not cond_stack:
                raise ValueError(".else without matching .if")
            if cond_stack[-1]["in_else"]:
                raise ValueError("duplicate .else in the same .if block")
            cond_stack[-1]["in_else"] = True
            continue

        if op_lower == ".endif":
            if not cond_stack:
                raise ValueError(".endif without matching .if")
            cond_stack.pop()
            continue

        if not active:
            continue

        if op_lower == ".macro":
            if not rest:
                raise ValueError(".macro expects macro name")
            macro_name, macro_params = _parse_macro_signature(rest)
            if macro_name in macros:
                raise ValueError(f"duplicate macro: {macro_name}")
            current_macro_name = macro_name
            current_macro_params = macro_params
            current_macro_body = []
            continue

        if op_lower == ".equ" and len(args) == 2:
            name, value_token = args
            defines[name] = _resolve_preproc_value(value_token, defines)

        if op in macros:
            macro_expansions += 1
            if macro_expansions > macro_expand_limit:
                raise ValueError("macro expansion limit exceeded")
            macro = macros[op]
            if len(args) != len(macro.params):
                raise ValueError(
                    f"macro {macro.name} expects {len(macro.params)} args, got {len(args)}"
                )
            mapping = dict(zip(macro.params, args, strict=True))
            expanded = [_apply_macro_params(line, mapping) for line in macro.body]
            if label is not None and expanded:
                expanded[0] = f"{label}: {expanded[0]}"
            for line in reversed(expanded):
                input_lines.appendleft(line)
            continue

        output_lines.append(clean)

    if current_macro_name is not None:
        raise ValueError(f"unterminated macro definition: {current_macro_name}")
    if cond_stack:
        raise ValueError("unterminated .if block")

    return "\n".join(output_lines)


def _parse_int(token: str) -> int:
    return int(token, 0)


def _parse_cstr(token: str) -> str:
    if not (token.startswith('"') and token.endswith('"')):
        raise ValueError(f".asciiz expects quoted string, got: {token}")
    parsed = ast.literal_eval(token)
    if not isinstance(parsed, str):
        raise ValueError(f"invalid string literal: {token}")
    return parsed


def _resolve_value(token: str, labels: dict[str, int], constants: dict[str, int]) -> int:
    if token in labels:
        return labels[token]
    if token in constants:
        return constants[token]
    return _parse_int(token)


def _directive_size(line: ParsedLine) -> int:
    if line.op == ".word":
        if len(line.args) != 1:
            raise ValueError(".word expects one argument")
        return 1
    if line.op == ".asciiz":
        if len(line.args) != 1:
            raise ValueError(".asciiz expects one quoted string argument")
        return len(_parse_cstr(line.args[0])) + 1
    return 0


def pass1_collect_labels(lines: list[ParsedLine]) -> tuple[dict[str, int], dict[str, int]]:
    labels: dict[str, int] = {}
    constants: dict[str, int] = {}
    pc = 0
    for line in lines:
        if line.label is not None:
            if line.label in labels:
                raise ValueError(f"duplicate label: {line.label}")
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
            pc = _resolve_value(line.args[0], labels=labels, constants=constants)
            continue
        if line.op == ".equ":
            if len(line.args) != 2:
                raise ValueError(".equ expects two arguments: NAME, VALUE")
            name = line.args[0]
            if name in constants:
                raise ValueError(f"duplicate constant: {name}")
            constants[name] = _resolve_value(line.args[1], labels=labels, constants=constants)
            continue
        pc += _directive_size(line)
    return labels, constants


def _parse_reg(token: str) -> int:
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


def _to_instruction(
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
            rd=_parse_reg(args[0]),
            rs1=_parse_reg(args[1]),
            rs2=_parse_reg(args[2]),
            imm=0,
        )

    if op == "ADDI":
        if len(args) != 3:
            raise ValueError("ADDI expects 2 registers and immediate/label")
        return Instruction(
            opcode=Opcode.ADDI,
            rd=_parse_reg(args[0]),
            rs1=_parse_reg(args[1]),
            rs2=0,
            imm=_resolve_value(args[2], labels=labels, constants=constants),
        )

    if op in {"LD", "ST"}:
        if len(args) != 2:
            raise ValueError(f"{op} expects 2 register arguments")
        return Instruction(
            opcode=Opcode[op],
            rd=_parse_reg(args[0]),
            rs1=_parse_reg(args[1]),
            rs2=0,
            imm=0,
        )

    if op in {"BEQ", "BNE", "BGT", "BLT", "BLE", "BGE"}:
        if len(args) != 3:
            raise ValueError(f"{op} expects 2 registers and immediate/label")
        return Instruction(
            opcode=Opcode[op],
            rd=0,
            rs1=_parse_reg(args[0]),
            rs2=_parse_reg(args[1]),
            imm=_resolve_value(args[2], labels=labels, constants=constants),
        )

    if op == "JMP":
        if len(args) != 1:
            raise ValueError("JMP expects immediate/label")
        return Instruction(opcode=Opcode.JMP, imm=_resolve_value(args[0], labels=labels, constants=constants))

    if op == "TRAP":
        if len(args) != 1:
            raise ValueError("TRAP expects trap id immediate")
        return Instruction(opcode=Opcode.TRAP, imm=_resolve_value(args[0], labels=labels, constants=constants))

    raise ValueError(f"unsupported opcode: {op}")


def assemble(source: str) -> AssembleResult:
    preprocessed = preprocess_source(source)
    parsed = parse_source(preprocessed)
    labels, constants = pass1_collect_labels(parsed)
    memory: dict[int, int] = {}
    listing_entries: list[ListingEntry] = []
    pc = 0

    def emit(word: int, text: str) -> None:
        nonlocal pc
        if pc in memory:
            raise ValueError(f"address already initialized: {pc}")
        memory[pc] = word & 0xFFFFFFFF
        listing_entries.append(ListingEntry(addr=pc, word=word & 0xFFFFFFFF, text=text))
        pc += 1

    for line in parsed:
        if line.kind == "label":
            continue
        if line.kind == "directive":
            if line.op in {".text", ".data"}:
                continue
            if line.op == ".org":
                pc = _resolve_value(line.args[0], labels=labels, constants=constants)
                continue
            if line.op == ".equ":
                continue
            if line.op == ".word":
                value = _resolve_value(line.args[0], labels=labels, constants=constants)
                emit(value, f".word {line.args[0]}")
                continue
            if line.op == ".asciiz":
                s = _parse_cstr(line.args[0])
                for ch in s:
                    emit(ord(ch), f".asciiz {line.args[0]}")
                emit(0, f".asciiz {line.args[0]}")
                continue
            raise ValueError(f"unsupported directive: {line.op} at line {line.line_no}")

        instr = _to_instruction(line.op, line.args, labels, constants)
        emit(encode(instr), f"{line.op} {', '.join(line.args)}".rstrip())

    if not memory:
        return AssembleResult(words=[], listing_entries=[])
    max_addr = max(memory)
    words = [0] * (max_addr + 1)
    for addr, word in memory.items():
        words[addr] = word
    return AssembleResult(words=words, listing_entries=listing_entries)


def assemble_to_words(source: str) -> list[int]:
    return assemble(source).words


def write_binary(words: list[int], output_path: str) -> None:
    payload = b"".join(word_to_bytes(word) for word in words)
    Path(output_path).write_bytes(payload)


def write_listing(listing_entries: list[ListingEntry], output_path: str) -> None:
    lines = [f"{entry.addr:04d} - {entry.word:08X} - {entry.text}" for entry in listing_entries]
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def assemble_file(input_path: str, output_bin: str, listing_path: str | None = None) -> AssembleResult:
    source = Path(input_path).read_text(encoding="utf-8")
    result = assemble(source)
    write_binary(result.words, output_bin)
    if listing_path is not None:
        write_listing(result.listing_entries, listing_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="ASM -> binary translator")
    parser.add_argument("input_file", help="input .asm file")
    parser.add_argument("output_file", help="output .bin file")
    parser.add_argument("--listing", help="optional output listing file")
    args = parser.parse_args()
    assemble_file(args.input_file, args.output_file, args.listing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
