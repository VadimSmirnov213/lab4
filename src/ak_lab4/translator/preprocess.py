import re
from collections import deque
from dataclasses import dataclass

from src.ak_lab4.translator.parser import split_label, split_op_args, strip_comment


@dataclass(frozen=True)
class MacroDef:
    name: str
    params: tuple[str, ...]
    body: tuple[str, ...]


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
    input_lines = deque(strip_comment(line) for line in source.splitlines())
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
        label, rest = split_label(clean)
        op = ""
        args: tuple[str, ...] = ()
        if rest:
            op, args = split_op_args(rest)
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
