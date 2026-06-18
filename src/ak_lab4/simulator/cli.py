from __future__ import annotations

import argparse
from pathlib import Path

from src.ak_lab4.simulator import CPU, load_words_from_binary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ak_lab4 CPU simulator")
    parser.add_argument("binary_file", help="input .bin file")
    parser.add_argument("--input", dest="input_file", help="optional input bytes file")
    parser.add_argument("--max-ticks", type=int, default=100_000, help="execution tick limit")
    parser.add_argument("--detailed-tick", action="store_true", help="enable phase-level tick logs")
    args = parser.parse_args()

    words = load_words_from_binary(args.binary_file)
    input_bytes = b""
    if args.input_file:
        input_bytes = Path(args.input_file).read_bytes()

    cpu = CPU(memory=words, input_bytes=input_bytes, detailed_tick=args.detailed_tick)
    cpu.run(max_ticks=args.max_ticks)

    output = bytes(cpu.output_buffer)
    print(output.decode("utf-8", errors="replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
