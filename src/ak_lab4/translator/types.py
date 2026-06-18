from dataclasses import dataclass


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
