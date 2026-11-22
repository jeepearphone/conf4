"""Диапазон адресов и дамп памяти в формате JSON."""

import argparse
import json
from collections.abc import Iterator

from .memory import MAX_ADDRESS, Memory


def parse_range(text: str) -> range:
    """Разобрать две включительные границы диапазона."""
    try:
        first, last = map(int, text.split(":"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ожидается START:END") from exc
    if not 0 <= first <= last <= MAX_ADDRESS:
        message = f"ожидается 0 <= START <= END <= {MAX_ADDRESS}"
        raise argparse.ArgumentTypeError(message)
    return range(first, last + 1)


def dump_rows(memory: Memory, addresses: range) -> Iterator[bytes]:
    """Вывести JSON-массив по одной ячейке на строку."""
    yield b"["
    for index, address in enumerate(addresses):
        prefix = ",\n  " if index else "\n  "
        row = {"address": address, "value": memory.read(address)}
        yield (prefix + json.dumps(row)).encode("utf-8")
    yield b"\n]\n"
