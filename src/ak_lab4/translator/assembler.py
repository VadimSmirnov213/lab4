from __future__ import annotations

import argparse
from pathlib import Path

from src.ak_lab4.isa import encode, word_to_bytes
from src.ak_lab4.translator.encoding import (
    parse_cstr,
    pass1_collect_labels,
    resolve_value,
    to_instruction,
)
from src.ak_lab4.translator.parser import parse_source
from src.ak_lab4.translator.preprocess import preprocess_source
from src.ak_lab4.translator.types import AssembleResult, ListingEntry, ParsedLine

__all__ = [
    "AssembleResult",
    "ListingEntry",
    "ParsedLine",
    "assemble",
    "assemble_file",
    "assemble_to_words",
    "main",
    "parse_source",
    "pass1_collect_labels",
    "preprocess_source",
    "write_binary",
    "write_listing",
]


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
                org_value = resolve_value(line.args[0], labels=labels, constants=constants)
                if org_value < 0:
                    raise ValueError(f".org must be non-negative, got: {org_value}")
                pc = org_value
                continue
            if line.op == ".equ":
                continue
            if line.op == ".word":
                value = resolve_value(line.args[0], labels=labels, constants=constants)
                emit(value, f".word {line.args[0]}")
                continue
            if line.op == ".asciiz":
                s = parse_cstr(line.args[0])
                for ch in s:
                    emit(ord(ch), f".asciiz {line.args[0]}")
                emit(0, f".asciiz {line.args[0]}")
                continue
            raise ValueError(f"unsupported directive: {line.op} at line {line.line_no}")

        instr = to_instruction(line.op, line.args, labels, constants)
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
