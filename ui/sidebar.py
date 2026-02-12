import hashlib
from typing import cast

import streamlit as st

from entities import Collection, Paper


def render_sidebar(papers: list[Paper]) -> None:
    """
    Render sidebar navigation + collections + items list.

    Args:
        papers (list[Paper]): All papers (for mapping paper_id -> Paper).

    Returns:
        None
    """
    collections = cast(list[Collection], st.session_state["collections"])
    active_id = cast(str | None, st.session_state["active_collection_id"])
    selected_id = cast(str | None, st.session_state["selected_paper_id"])

    by_id = {p.paper_id: p for p in papers}

    # ---- Nav ----
    if st.sidebar.button("Search", key="nav_search"):
        st.session_state["page"] = "search"
        st.rerun()

    _ = st.sidebar.divider()

    # ---- Collections ----
    _ = st.sidebar.header("Collections")

    with st.sidebar.form("create_collection_form", clear_on_submit=True):
        new_name: str = st.text_input("New collection name", key="new_collection_name")
        create = st.form_submit_button("Create collection")

    if create:
        name = new_name.strip()
        if not name:
            _ = st.sidebar.error("Enter a name.")
        else:
            cid = hashlib.sha1(name.encode("utf-8")).hexdigest()
            if any(c.id == cid for c in collections):
                _ = st.sidebar.warning("Collection already exists.")
            else:
                collections.append(Collection(id=cid, name=name))
                st.session_state["active_collection_id"] = cid
                st.rerun()

    if not collections:
        _ = st.sidebar.caption("No collections yet.")
        return

    # Clickable collections list
    names = [c.name for c in collections]
    active = next((c for c in collections if c.id == active_id), None)
    default_idx = 0 if active is None else names.index(active.name)

    picked = st.sidebar.selectbox("Collections", names, index=default_idx)
    picked_col = next(c for c in collections if c.name == picked)

    st.session_state["active_collection_id"] = picked_col.id

    _ = st.sidebar.divider()

    # ---- Items (active collection) ----
    active = next((c for c in collections if c.id == active_id), None)
    if active is None:
        _ = st.sidebar.caption("Select a collection to see items.")
        return

    if st.sidebar.button(
        f"{active.name} ({len(active.paper_ids)})", key="open_active_collection"
    ):
        st.session_state["page"] = "collection"
        st.rerun()

    if not active.paper_ids:
        _ = st.sidebar.caption("Empty.")
        return

    for pid in active.paper_ids:
        p = by_id.get(pid)
        title = p.title if p is not None and p.title else "(missing)"
        prefix = "• "
        if pid == selected_id:
            prefix = "→ "
        if st.sidebar.button(f"{prefix}{title}", key=f"item_{pid}"):
            st.session_state["selected_paper_id"] = pid
            st.session_state["page"] = "collection"
            st.rerun()
