from dataclasses import dataclass
from typing import Callable


@dataclass
class CacheLine:
    valid: bool = False
    tag: int = 0
    data: int = 0


class SimpleCache:
    def __init__(self, lines_count: int = 16) -> None:
        if lines_count <= 0:
            raise ValueError("lines_count must be positive")
        self.lines_count = lines_count
        self.lines: list[CacheLine] = [CacheLine() for _ in range(lines_count)]

    def _locate(self, addr: int) -> tuple[int, int]:
        index = addr % self.lines_count
        tag = addr // self.lines_count
        return index, tag

    def read(self, addr: int, backing_read: Callable[[int], int]) -> tuple[int, bool]:
        index, tag = self._locate(addr)
        line = self.lines[index]
        if line.valid and line.tag == tag:
            return line.data, True
        value = backing_read(addr) & 0xFFFFFFFF
        self.lines[index] = CacheLine(valid=True, tag=tag, data=value)
        return value, False

    def write(self, addr: int, value: int, backing_write: Callable[[int, int], None]) -> bool:
        index, tag = self._locate(addr)
        line = self.lines[index]
        hit = line.valid and line.tag == tag
        if hit:
            line.data = value & 0xFFFFFFFF
        else:
            self.lines[index] = CacheLine(valid=True, tag=tag, data=value & 0xFFFFFFFF)
        backing_write(addr, value & 0xFFFFFFFF)
        return hit
