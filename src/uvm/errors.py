"""Ошибки обработки программ УВМ."""


class AssemblerError(ValueError):
    """Ошибка в исходном тексте программы."""


class ExecutionError(ValueError):
    """Ошибка декодирования или выполнения программы УВМ."""
