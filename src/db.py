import json
from pathlib import Path
from typing import cast

from entities import JSONDict, Paper


def load_papers(path: Path) -> list[Paper]:
    """
    Load research papers from a JSON file.

    Args:
        path (Path): Path to a JSON file containing a top-level "references" list.

    Returns:
        list[Paper]: Parsed Paper instances.

    Raises:
        ValueError: If the JSON structure is unexpected.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = cast(object, json.load(f))

    if not isinstance(raw, dict):
        raise ValueError("Expected top-level JSON object to be a dictionary.")

    root = cast(JSONDict, raw)

    if "references" not in root:
        raise ValueError('Missing required key: "references".')

    references_obj = root["references"]

    if not isinstance(references_obj, list):
        raise ValueError('Expected "references" to be a list.')

    references_list = cast(list[object], references_obj)

    references: list[JSONDict] = []
    for item in references_list:
        if not isinstance(item, dict):
            raise ValueError('Expected each item in "references" to be a dictionary.')
        references.append(cast(JSONDict, item))

    return [Paper.from_dict(item) for item in references]
