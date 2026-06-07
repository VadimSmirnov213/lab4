from pathlib import Path

from src.assembler import assemble, write_binary, write_listing
from src.cpu import CPU, MMIO_OUT_DATA


def test_golden_hello(tmp_path: Path) -> None:
    case_dir = Path("golden/hello")
    source = (case_dir / "source.asm").read_text(encoding="utf-8")
    expected_output = (case_dir / "expected_output.txt").read_text(encoding="utf-8")

    result = assemble(source)

    out_bin = tmp_path / "hello.bin"
    out_lst = tmp_path / "hello.lst"
    write_binary(result.words, str(out_bin))
    write_listing(result.listing_entries, str(out_lst))

    cpu = CPU(memory=result.words)
    cpu.regs[7] = MMIO_OUT_DATA
    cpu.run()

    output = "".join(chr(b) for b in cpu.output_buffer)
    assert output == expected_output

    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    actual_lines = [f"{log.opcode}\t{log.ip}" for log in cpu.logs[: len(expected_trace_lines)]]
    assert actual_lines == expected_trace_lines
