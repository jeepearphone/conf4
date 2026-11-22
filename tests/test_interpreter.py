"""Проверки декодера, команд памяти и записи дампа."""

import argparse
import json
from pathlib import Path

import pytest

from uvm.assembler import main as assemble
from uvm.decoder import decode
from uvm.dump import parse_range
from uvm.errors import ExecutionError
from uvm.interpreter import execute, main
from uvm.isa import Instruction
from uvm.memory import MAX_ADDRESS, Memory

COPY = Path(__file__).resolve().parents[1] / "examples" / "copy_array.csv"
VALUES = [7, 0, 511]
SOURCE = 100
DESTINATION = 200


def test_decoder() -> None:
    """Сверить длины команд и поля по эталонному двоичному коду."""
    program = b"\xde\x03\x64\x01\xfd\x09\x00\x21\x0d\x00"
    assert list(decode(program)) == [
        Instruction(6, 123), Instruction(4, 44),
        Instruction(5, 319), Instruction(1, 420),
    ]


def test_load() -> None:
    """Загрузить константу из поля B."""
    expected = 123
    assert execute(Memory(b"\xde\x03")) == expected


def test_read() -> None:
    """Прочитать ячейку по сумме аккумулятора и смещения."""
    value = -715
    memory = Memory(b"\xde\x03\x64\x01")
    memory.write(123 + 44, value)
    assert execute(memory) == value


def test_write() -> None:
    """Записать аккумулятор по максимальному адресу."""
    value = 123
    memory = Memory(b"\xde\x03\xfd\xff\x3f")
    assert execute(memory) == value
    assert memory.read(MAX_ADDRESS) == value


@pytest.mark.parametrize("base", [-1, MAX_ADDRESS + 1])
def test_bad_read_address(base: int) -> None:
    """Отклонить адрес за любой из двух границ памяти."""
    memory = Memory(b"\x04\x00\x04\x00")
    memory.write(0, base)
    with pytest.raises(ExecutionError, match=f"Адрес {base} вне диапазона"):
        execute(memory)


@pytest.mark.parametrize(
    ("program", "error"),
    [
        (b"\x06\x00\x07", "Байт 2: неизвестный код A=7"),
        (b"\x06", "Байт 0: обрыв команды"),
        (b"\x05\x00", "Байт 0: обрыв команды"),
    ],
)
def test_invalid_program(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    program: bytes, error: str,
) -> None:
    """Сообщить о повреждении программы и сохранить предыдущий дамп."""
    binary = tmp_path / "bad.bin"
    binary.write_bytes(program)
    dump = tmp_path / "dump.json"
    dump.write_text("[]", encoding="utf-8")
    assert main([str(binary), str(dump), "--range", "0:0"]) != 0
    assert error in capsys.readouterr().err
    assert dump.read_text(encoding="utf-8") == "[]"


@pytest.mark.parametrize("text", ["0", "a:1", "-1:2", "3:2", "0:524288"])
def test_invalid_range(text: str) -> None:
    """Проверить формат, порядок и границы адресов дампа."""
    with pytest.raises(argparse.ArgumentTypeError):
        parse_range(text)


def test_single_cell(tmp_path: Path) -> None:
    """Сохранить последнюю нулевую ячейку при пустой программе."""
    binary = tmp_path / "empty.bin"
    binary.write_bytes(b"")
    dump = tmp_path / "dump.json"
    limits = f"{MAX_ADDRESS}:{MAX_ADDRESS}"
    assert main([str(binary), str(dump), "--range", limits]) == 0
    assert json.loads(dump.read_bytes()) == [
        {"address": MAX_ADDRESS, "value": 0},
    ]


def test_copy_array(tmp_path: Path) -> None:
    """Сверить исходный массив, его копию и запрошенный диапазон дампа."""
    binary = tmp_path / "copy.bin"
    dump = tmp_path / "dump.json"
    assert assemble([str(COPY), str(binary)]) == 0
    memory = Memory(binary.read_bytes())
    execute(memory)
    for index, value in enumerate(VALUES):
        assert memory.read(SOURCE + index) == value
        assert memory.read(DESTINATION + index) == value
    assert main([str(binary), str(dump), "--range", "200:202"]) == 0
    assert json.loads(dump.read_bytes()) == [
        {"address": DESTINATION + i, "value": value}
        for i, value in enumerate(VALUES)
    ]
