"""Раздельная память команд и данных УВМ."""

from array import array

from .errors import ExecutionError
from .isa import COMMANDS

MAX_ADDRESS = COMMANDS["write"].max_operand
DATA_SIZE = MAX_ADDRESS + 1


class Memory:
    """Хранить байты программы и ячейки данных с нулевой инициализацией."""

    def __init__(self, program: bytes) -> None:
        """Загрузить программу и подготовить память данных."""
        self.program = program
        self._data = array("i", [0]) * DATA_SIZE

    def read(self, address: int) -> int:
        """Прочитать значение по адресу данных."""
        _check_address(address)
        return self._data[address]

    def write(self, address: int, value: int) -> None:
        """Записать значение по адресу данных."""
        _check_address(address)
        self._data[address] = value


def _check_address(address: int) -> None:
    if not 0 <= address <= MAX_ADDRESS:
        raise ExecutionError(f"Адрес {address} вне диапазона 0..{MAX_ADDRESS}")
