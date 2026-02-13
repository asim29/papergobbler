"""Collection persistence to disk."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from entities import Collection

COLLECTIONS_DIR = Path(__file__).parent.parent / "collections"


def _ensure_dir() -> None:
    """Create the collections directory if it doesn't exist."""
    COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)


def load_all_collections() -> list[Collection]:
    """
    Load all collections from disk.

    Returns collections sorted by created_at ascending.
    """
    _ensure_dir()
    collections: list[Collection] = []
    for path in COLLECTIONS_DIR.glob("*.json"):
        with open(path, "r", encoding="utf-8") as f:
            data: dict[str, object] = json.load(f)  # pyright: ignore[reportAny]
        collections.append(Collection.from_dict(data))
    return sorted(collections, key=lambda c: c.created_at)


def save_collection(collection: Collection) -> None:
    """
    Save a collection to disk. Updates the updated_at timestamp.
    """
    _ensure_dir()
    collection.updated_at = datetime.now(timezone.utc).isoformat()
    path = COLLECTIONS_DIR / f"{collection.id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(collection.to_dict(), f, indent=2)


def delete_collection(collection_id: str) -> None:
    """
    Delete a collection from disk. No-op if it doesn't exist.
    """
    path = COLLECTIONS_DIR / f"{collection_id}.json"
    if path.exists():
        path.unlink()
