"""Поля команд варианта 11 и их промежуточное представление."""

from dataclasses import dataclass

OPCODE_BITS = 3
OPERAND_SHIFT = OPCODE_BITS


@dataclass(frozen=True)
class Command:
    """Описание команды с длиной в байтах и шириной операнда в битах."""

    opcode: int
    size: int
    operand_bits: int

    @property
    def max_operand(self) -> int:
        """Вернуть наибольшее значение поля B."""
        return (1 << self.operand_bits) - 1


COMMANDS = {
    "load_const": Command(6, 2, 9),
    "read": Command(4, 2, 7),
    "write": Command(5, 3, 19),
    "neg": Command(1, 3, 19),
}


@dataclass(frozen=True)
class Instruction:
    """Значения полей A и B одной инструкции."""

    opcode: int
    operand: int
