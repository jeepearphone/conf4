"""Исполнение программы УВМ и сохранение диапазона памяти данных."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .alu import negate
from .decoder import decode
from .dump import dump_rows, parse_range
from .errors import ExecutionError
from .isa import COMMANDS
from .memory import Memory
from .output import write_chunks


def execute(memory: Memory) -> int:
    """Выполнить программу и вернуть итоговое значение аккумулятора."""
    accumulator = 0
    for instruction in decode(memory.program):
        operand = instruction.operand
        if instruction.opcode == COMMANDS["load_const"].opcode:
            accumulator = operand
        elif instruction.opcode == COMMANDS["read"].opcode:
            accumulator = memory.read(accumulator + operand)
        elif instruction.opcode == COMMANDS["write"].opcode:
            memory.write(operand, accumulator)
        elif instruction.opcode == COMMANDS["neg"].opcode:
            accumulator = negate(memory.read(operand))
    return accumulator


def main(argv: Sequence[str] | None = None) -> int:
    """Выполнить двоичный файл и записать выбранные ячейки в JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path, help="двоичный файл программы")
    parser.add_argument("dump", type=Path, help="выходной JSON-файл")
    parser.add_argument(
        "--range", required=True, metavar="START:END", type=parse_range,
        dest="addresses", help="адреса данных, обе границы включительно",
    )
    args = parser.parse_args(argv)
    try:
        memory = Memory(args.program.read_bytes())
        execute(memory)
        write_chunks(args.dump, dump_rows(memory, args.addresses))
    except (ExecutionError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
