from src.ak_lab4.translator.types import ParsedLine


def strip_comment(line: str) -> str:
    return line.split(";", 1)[0].strip()


def split_label(line: str) -> tuple[str | None, str]:
    if ":" not in line:
        return None, line
    label, rest = line.split(":", 1)
    label = label.strip()
    if not label:
        raise ValueError("empty label definition")
    return label, rest.strip()


def split_op_args(text: str) -> tuple[str, tuple[str, ...]]:
    parts = text.split(maxsplit=1)
    op = parts[0]
    if len(parts) == 1:
        return op, ()
    args = tuple(arg.strip() for arg in parts[1].split(",") if arg.strip())
    return op, args


def parse_line(clean: str, raw: str, line_no: int) -> ParsedLine:
    label, rest = split_label(clean)
    if not rest:
        return ParsedLine(line_no=line_no, label=label, kind="label", op="", args=(), source=raw)

    op, args = split_op_args(rest)
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
        clean = strip_comment(raw)
        if not clean:
            continue
        parsed.append(parse_line(clean=clean, raw=raw, line_no=line_no))
    return parsed
