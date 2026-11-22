"""Проверки унарного минуса и программы с записью результата в память."""

import json
from pathlib import Path

import pytest

from uvm.alu import negate
from uvm.assembler import main as assemble
from uvm.interpreter import main as interpret

DEMO = Path(__file__).resolve().parents[1] / "examples" / "neg_demo.csv"
MIN_INT32 = -2_147_483_648
MAX_INT32 = 2_147_483_647


@pytest.mark.parametrize(
    ("operand", "expected"),
    [
        (MIN_INT32, MIN_INT32),
        (MIN_INT32 + 1, MAX_INT32),
        (MAX_INT32, -MAX_INT32),
        (0, 0),
    ],
)
def test_negate(operand: int, expected: int) -> None:
    """Проверить знаковый результат, включая переполнение на нижней границе."""
    assert negate(operand) == expected


def test_neg_demo(tmp_path: Path) -> None:
    """Сверить дамп после двойного отрицания и обработки нуля."""
    binary = tmp_path / "neg.bin"
    dump = tmp_path / "neg.json"
    assert assemble([str(DEMO), str(binary)]) == 0
    assert interpret([str(binary), str(dump), "--range", "300:304"]) == 0
    assert json.loads(dump.read_bytes()) == [
        {"address": 300, "value": 37},
        {"address": 301, "value": -37},
        {"address": 302, "value": 37},
        {"address": 303, "value": 0},
        {"address": 304, "value": 0},
    ]
