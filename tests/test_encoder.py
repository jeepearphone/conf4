"""Проверки упаковки старших битов операнда и ошибок кодирования."""

import pytest

from uvm.encoder import encode
from uvm.errors import AssemblerError
from uvm.isa import Instruction


@pytest.mark.parametrize(
    ("instruction", "expected"),
    [
        (Instruction(6, 511), b"\xfe\x0f"),
        (Instruction(4, 127), b"\xfc\x03"),
        (Instruction(5, 524287), b"\xfd\xff\x3f"),
        (Instruction(1, 524287), b"\xf9\xff\x3f"),
    ],
)
def test_max_operand(instruction: Instruction, expected: bytes) -> None:
    """Сохранить все биты операнда и заполнить свободные биты нулями."""
    assert encode(instruction) == expected


@pytest.mark.parametrize(
    "instruction", [Instruction(7, 0), Instruction(4, -1), Instruction(6, 512)],
)
def test_invalid_instruction(instruction: Instruction) -> None:
    """Отклонить значения, которые нельзя представить в формате команды."""
    with pytest.raises(AssemblerError):
        encode(instruction)
