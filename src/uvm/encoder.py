"""Упаковка полей инструкций в машинный код УВМ."""

from .errors import AssemblerError
from .isa import BY_OPCODE, MIN_OPERAND, OPERAND_SHIFT, Instruction


def encode(instruction: Instruction) -> bytes:
    """Вернуть байты инструкции в порядке от младшего к старшему."""
    spec = BY_OPCODE.get(instruction.opcode)
    if spec is None:
        raise AssemblerError(f"Неизвестный код операции: {instruction.opcode}")
    if not MIN_OPERAND <= instruction.operand <= spec.max_operand:
        raise AssemblerError(f"Операнд вне диапазона 0..{spec.max_operand}")
    word = (instruction.operand << OPERAND_SHIFT) | spec.opcode
    return word.to_bytes(spec.size, byteorder="little")
