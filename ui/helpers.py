"""Shared UI helpers used by list_view and detail_view."""

from __future__ import annotations

from typing import cast

import streamlit as st

from entities import Collection, Paper
from src.storage import save_collection


def truncate(text: str, max_chars: int = 250) -> str:
    """Truncate text to max_chars, appending '...' if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def push_view(view: object) -> None:
    """Push a view onto the session state view stack."""
    stack = cast("list[object]", st.session_state["view_stack"])
    stack.append(view)


def add_to_collection(paper: Paper) -> None:
    """Add a paper to the active collection and save to disk."""
    active_id: str | None = st.session_state.get("active_collection_id")
    if active_id is None:
        _ = st.warning("Select a collection first.")
        return

    collections = cast("list[Collection]", st.session_state.get("collections", []))

    for c in collections:
        if c.id != active_id:
            continue
        if paper.paper_id in c.paper_ids:
            _ = st.info("Already in collection.")
            return
        c.paper_ids.append(paper.paper_id)
        c.paper_titles[paper.paper_id] = paper.title
        c.paper_metadata[paper.paper_id] = {
            "year": paper.year,
            "citation_count": paper.citation_count,
            "venue": paper.venue,
        }
        save_collection(c)
        st.rerun()

    _ = st.warning("Active collection not found.")
