from pathlib import Path

from src.ak_lab4.isa import word_from_bytes


def load_words_from_binary(path: str) -> list[int]:
    data = Path(path).read_bytes()
    if len(data) % 4 != 0:
        raise ValueError("binary size must be a multiple of 4 bytes")
    return [word_from_bytes(data[i : i + 4]) for i in range(0, len(data), 4)]
