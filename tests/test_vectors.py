"""Сквозная проверка поэлементного отрицания трёх векторов."""

import json
from pathlib import Path

import pytest

from uvm.assembler import main as assemble
from uvm.interpreter import main as interpret

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
FIRST_ADDRESS = 400


@pytest.mark.parametrize(
    ("name", "values"),
    [
        ("vector_neg_1", [7, 2, 19, 0, 5, 1, 13, 4]),
        ("vector_neg_2", [0, 1, 1, 0, 1, 0, 0, 1]),
        ("vector_neg_3", [511, 510, 509, 508, 507, 506, 505, 504]),
    ],
)
def test_vector_dump(tmp_path: Path, name: str, values: list[int]) -> None:
    """Сверить адрес и значение каждого элемента итогового JSON-массива."""
    source = EXAMPLES / f"{name}.csv"
    binary = tmp_path / f"{name}.bin"
    dump = tmp_path / f"{name}.json"
    assert assemble([str(source), str(binary)]) == 0
    assert interpret([str(binary), str(dump), "--range", "400:407"]) == 0
    assert json.loads(dump.read_bytes()) == [
        {"address": address, "value": -value}
        for address, value in enumerate(values, start=FIRST_ADDRESS)
    ]
