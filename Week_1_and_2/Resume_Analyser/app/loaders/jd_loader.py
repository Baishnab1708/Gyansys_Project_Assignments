from pathlib import Path
from typing import Union


def load_jd_from_file(file_path: Union[str, Path]) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_jd_from_text(text: str) -> str:
        return text.strip()
