"""Декодирование машинного кода по таблице команд."""

from collections.abc import Iterator

from .errors import ExecutionError
from .isa import BY_OPCODE, OPCODE_BITS, OPERAND_SHIFT, Instruction

OPCODE_MASK = (1 << OPCODE_BITS) - 1


def decode(program: bytes) -> Iterator[Instruction]:
    """Последовательно прочитать инструкции, учитывая размер каждой."""
    position = 0
    while position < len(program):
        opcode = program[position] & OPCODE_MASK
        spec = BY_OPCODE.get(opcode)
        if spec is None:
            raise ExecutionError(f"Байт {position}: неизвестный код A={opcode}")
        end = position + spec.size
        if end > len(program):
            raise ExecutionError(f"Байт {position}: обрыв команды A={opcode}")
        word = int.from_bytes(program[position:end], byteorder="little")
        yield Instruction(opcode, (word >> OPERAND_SHIFT) & spec.max_operand)
        position = end
