"""Запись результата с заменой файла после успешного завершения."""

from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile


def write_chunks(path: Path, chunks: Iterable[bytes]) -> None:
    """Записать блоки во временный файл и перенести его по заданному пути."""
    stream = NamedTemporaryFile(dir=path.parent, delete=False)
    temporary = Path(stream.name)
    try:
        with stream:
            stream.writelines(chunks)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
