import json
from pathlib import Path
from typing import Any

from .entities import Paper


def load_papers(path: Path) -> list[Paper]:
    """
    Load research papers from a JSON file.

    Args:
        path (Path): Path to a JSON file containing a top-level "references" list.

    Returns:
        list[Paper]: Parsed Paper instances.

    Raises:
        KeyError: If the JSON file does not contain a "references" field.
        ValueError: If "references" is not a list.
    """
    with open(path, "r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    references = data["references"]

    if not isinstance(references, list):
        raise ValueError('Expected "references" to be a list.')

    return [Paper.from_dict(item) for item in references]
