from typing import cast

import streamlit as st

from entities import Collection, Paper


def render_active_collection(papers: list[Paper]) -> None:
    """
    Render the currently active collection in the sidebar.

    Args:
        papers (list[Paper]): All papers (used to map paper_id -> Paper).

    Returns:
        None
    """
    collections = cast(list[Collection], st.session_state["collections"])
    active_id = cast(str | None, st.session_state["active_collection_id"])

    if active_id is None:
        _ = st.sidebar.caption("No active collection.")
        return

    active = next((c for c in collections if c.id == active_id), None)
    if active is None:
        _ = st.sidebar.caption("Active collection not found.")
        return

    by_id = {p.paper_id: p for p in papers}

    _ = st.sidebar.subheader(f"Items ({len(active.paper_ids)})")

    if not active.paper_ids:
        _ = st.sidebar.caption("Empty.")
        return

    for pid in active.paper_ids:
        p = by_id.get(pid)
        title = p.title if p is not None and p.title else "(missing)"
        _ = st.sidebar.write(f"• {title}")
