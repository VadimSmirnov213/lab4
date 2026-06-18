from pathlib import Path

from src.ak_lab4.machine import CPU, MMIO_OUT_DATA
from src.ak_lab4.translator import assemble, write_binary, write_listing


def _run_case(
    case_dir: Path,
    tmp_path: Path,
    *,
    input_bytes: bytes = b"",
    interrupt_schedule: list[tuple[int, int]] | None = None,
    interrupt_vector_addr: int = 0,
    preset_regs: dict[int, int] | None = None,
    start_ip: int | None = None,
) -> tuple[str, list[str]]:
    source = (case_dir / "source.asm").read_text(encoding="utf-8")
    expected_output = (case_dir / "expected_output.txt").read_text(encoding="utf-8")

    result = assemble(source)

    out_bin = tmp_path / f"{case_dir.name}.bin"
    out_lst = tmp_path / f"{case_dir.name}.lst"
    write_binary(result.words, str(out_bin))
    write_listing(result.listing_entries, str(out_lst))
    assert out_bin.exists() and out_bin.stat().st_size == len(result.words) * 4
    lst_lines = out_lst.read_text(encoding="utf-8").splitlines()
    assert lst_lines, f"listing is empty for {case_dir.name}"
    assert len(lst_lines) == len(result.listing_entries)

    cpu = CPU(
        memory=result.words,
        input_bytes=input_bytes,
        interrupt_schedule=interrupt_schedule,
        interrupt_vector_addr=interrupt_vector_addr,
    )
    cpu.regs[7] = MMIO_OUT_DATA
    for reg, value in (preset_regs or {}).items():
        cpu.regs[reg] = value
    if start_ip is not None:
        cpu.ip = start_ip
    cpu.run()

    output = "".join(chr(b) for b in cpu.output_buffer)
    assert output == expected_output, f"output mismatch for {case_dir.name}"

    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    actual_lines = [f"{log.opcode}\t{log.ip}" for log in cpu.logs[: len(expected_trace_lines)]]
    return output, actual_lines


def test_golden_hello(tmp_path: Path) -> None:
    case_dir = Path("golden/hello")
    _, actual_lines = _run_case(case_dir, tmp_path)
    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    assert actual_lines == expected_trace_lines


def test_golden_cat(tmp_path: Path) -> None:
    case_dir = Path("golden/cat")
    _, actual_lines = _run_case(case_dir, tmp_path, input_bytes=b"cat\n", preset_regs={6: 0xFF00, 7: 0xFF02})
    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    assert actual_lines == expected_trace_lines


def test_golden_hello_user_name_irq(tmp_path: Path) -> None:
    case_dir = Path("golden/hello_user_name")
    schedule = [
        (28, ord("A")),
        (31, ord("l")),
        (34, ord("i")),
        (37, ord("c")),
        (40, ord("e")),
    ]
    _, actual_lines = _run_case(
        case_dir,
        tmp_path,
        interrupt_schedule=schedule,
        interrupt_vector_addr=0,
        preset_regs={6: 0xFF00, 7: 0xFF02},
        start_ip=20,
    )
    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    assert actual_lines == expected_trace_lines


def test_golden_sort(tmp_path: Path) -> None:
    case_dir = Path("golden/sort")
    _, actual_lines = _run_case(case_dir, tmp_path)
    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    assert actual_lines == expected_trace_lines


def test_golden_double_precision(tmp_path: Path) -> None:
    case_dir = Path("golden/double_precision")
    _, actual_lines = _run_case(case_dir, tmp_path)
    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    assert actual_lines == expected_trace_lines


def test_golden_prob1(tmp_path: Path) -> None:
    case_dir = Path("golden/prob1")
    _, actual_lines = _run_case(case_dir, tmp_path)
    expected_trace_lines = (case_dir / "expected_trace_lines.txt").read_text(encoding="utf-8").splitlines()
    assert actual_lines == expected_trace_lines
