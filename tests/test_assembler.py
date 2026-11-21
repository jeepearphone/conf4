"""Проверки промежуточного представления и CLI ассемблера."""

from io import StringIO
from pathlib import Path

import pytest

from uvm.assembler import main, parse_program
from uvm.errors import AssemblerError
from uvm.isa import Instruction

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "spec_tests.csv"
EXPECTED = [
    Instruction(6, 123),
    Instruction(4, 44),
    Instruction(5, 319),
    Instruction(1, 420),
]
OUTPUT = "A=6, B=123\nA=4, B=44\nA=5, B=319\nA=1, B=420\n"


def test_specification() -> None:
    """Сверить поля четырёх команд с примерами варианта."""
    with EXAMPLE.open(encoding="utf-8", newline="") as source:
        assert parse_program(source) == EXPECTED


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("skip,1", "неизвестная команда"),
        ("load_const,512", "0..511"),
        ("read,128", "0..127"),
        ("write,524288", "0..524287"),
        ("neg,-1", "0..524287"),
        ("neg,0x80000", "0..524287"),
        ("write", "два столбца"),
        ("write,1,2", "два столбца"),
        ("read,", "целое число"),
        ("read,1.5", "целое число"),
        ('read,"7', "ошибка CSV"),
    ],
)
def test_bad_row(row: str, message: str) -> None:
    """Сообщать причину ошибки и физический номер строки."""
    with pytest.raises(AssemblerError) as error:
        parse_program(StringIO(f"command,operand\n\n{row}\n"))
    assert str(error.value).startswith("Строка 3:")
    assert message in str(error.value)


@pytest.mark.parametrize("source", ["", "load_const,1", "operand,command"])
def test_missing_header(source: str) -> None:
    """Требовать заголовок в начале программы."""
    with pytest.raises(AssemblerError, match="Строка 1:"):
        parse_program(StringIO(source))


def test_operand_limits() -> None:
    """Разбирать границы полей, десятичные числа и шестнадцатеричный ввод."""
    rows = [
        "command,operand", "load_const,000", "load_const,511", 'read,"0x7F"',
        "write,0X7FFFF", "neg, 524287",
    ]
    assert parse_program(rows) == [
        Instruction(6, 0), Instruction(6, 511), Instruction(4, 127),
        Instruction(5, 524287), Instruction(1, 524287),
    ]


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Проверить вывод и обращение с выходным файлом в обоих режимах."""
    output = tmp_path / "program.bin"
    args = [str(EXAMPLE), str(output)]
    assert main([*args, "--test"]) == 0
    assert capsys.readouterr().out == OUTPUT
    assert not output.exists()
    output.write_bytes(b"original")
    assert main(args) == 0
    assert capsys.readouterr().out == ""
    assert output.read_bytes() == b"original"


def test_cli_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Направлять диагностику в stderr даже после верной команды."""
    source = tmp_path / "bad.csv"
    source.write_text("command,operand\nread,5\nneg,-1", encoding="utf-8")
    assert main([str(source), str(tmp_path / "out.bin"), "--test"]) != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("Строка 3:")
