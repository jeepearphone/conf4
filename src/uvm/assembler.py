"""Разбор исходной программы и командная строка ассемблера."""

import argparse
import csv
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from .errors import AssemblerError
from .isa import COMMANDS, Instruction

HEADER = ["command", "operand"]
MIN_OPERAND = 0
DECIMAL = 10
HEXADECIMAL = 16
NUMBER = re.compile(r"-?(?:[0-9]+|0[xX][0-9a-fA-F]+)\Z")


def _parse_row(row: list[str], line: int) -> Instruction:
    if len(row) != len(HEADER):
        raise AssemblerError(f"Строка {line}: ожидаются два столбца")
    name, token = row
    if name not in COMMANDS:
        raise AssemblerError(f"Строка {line}: неизвестная команда '{name}'")
    if not NUMBER.match(token):
        raise AssemblerError(f"Строка {line}: неверное целое число '{token}'")
    spec = COMMANDS[name]
    base = HEXADECIMAL if "x" in token.lower() else DECIMAL
    try:
        operand = int(token, base)
    except ValueError as exc:
        raise AssemblerError(f"Строка {line}: слишком длинное число") from exc
    if not MIN_OPERAND <= operand <= spec.max_operand:
        raise AssemblerError(
            f"Строка {line}: операнд вне диапазона 0..{spec.max_operand}"
        )
    return Instruction(spec.opcode, operand)


def parse_program(lines: Iterable[str]) -> list[Instruction]:
    """Преобразовать строки CSV в последовательность инструкций."""
    program: list[Instruction] = []
    has_header = False
    for line, source in enumerate(lines, start=1):
        if not source.strip():
            continue
        try:
            record = next(csv.reader([source], strict=True))
        except csv.Error as exc:
            raise AssemblerError(f"Строка {line}: ошибка CSV ({exc})") from exc
        row = [field.strip() for field in record]
        if has_header:
            program.append(_parse_row(row, line))
        elif row == HEADER:
            has_header = True
        else:
            raise AssemblerError(f"Строка {line}: ожидается command,operand")
    if not has_header:
        raise AssemblerError("Строка 1: отсутствует заголовок command,operand")
    return program


def main(argv: Sequence[str] | None = None) -> int:
    """Разобрать файл и вывести поля команд в режиме проверки."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path, help="исходный CSV-файл")
    parser.add_argument("out", type=Path, help="путь для машинного кода")
    parser.add_argument("--test", action="store_true", help="вывести поля A, B")
    args = parser.parse_args(argv)
    try:
        with args.src.open(encoding="utf-8-sig", newline="") as source:
            program = parse_program(source)
    except (AssemblerError, OSError, UnicodeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    if args.test:
        for instruction in program:
            print(f"A={instruction.opcode}, B={instruction.operand}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
