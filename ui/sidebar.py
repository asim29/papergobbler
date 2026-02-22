"""Sidebar with navigation and collection management."""

from __future__ import annotations

import uuid
from typing import cast

import streamlit as st

from entities import Collection
from src.storage import delete_collection, load_all_collections, save_collection
from ui.detail_view import DetailView


def render_sidebar() -> None:
    """Render sidebar: navigation, collection CRUD, and quick view."""
    # ---- Nav ----
    if st.sidebar.button("Search", key="nav_search"):
        st.session_state["page"] = "search"
        st.rerun()

    if st.sidebar.button("Collection", key="nav_collection"):
        st.session_state["page"] = "collection"
        st.rerun()

    _ = st.sidebar.divider()

    # ---- Collections ----
    _ = st.sidebar.header("Collections")

    collections = load_all_collections()
    st.session_state["collections"] = collections

    # Create
    with st.sidebar.form("create_collection_form", clear_on_submit=True):
        new_name: str = st.text_input("New collection name", key="new_collection_name")
        create = st.form_submit_button("Create")

    if create:
        name = new_name.strip()
        if not name:
            _ = st.sidebar.error("Enter a name.")
        else:
            c = Collection(id=str(uuid.uuid4()), name=name)
            save_collection(c)
            st.session_state["active_collection_id"] = c.id
            st.rerun()

    if not collections:
        _ = st.sidebar.caption("No collections yet.")
        return

    # Select
    active_id = cast("str | None", st.session_state.get("active_collection_id"))
    names = [c.name for c in collections]
    ids = [c.id for c in collections]

    if active_id in ids:
        default_idx = ids.index(active_id)
    else:
        default_idx = 0

    picked_name = st.sidebar.selectbox("Select collection", names, index=default_idx)
    picked = next(c for c in collections if c.name == picked_name)
    st.session_state["active_collection_id"] = picked.id

    # Delete
    if st.sidebar.button("Delete collection", key="delete_collection"):
        delete_collection(picked.id)
        if st.session_state.get("active_collection_id") == picked.id:
            st.session_state["active_collection_id"] = None
        st.rerun()

    _ = st.sidebar.divider()

    # ---- Quick view ----
    active = next(
        (
            c
            for c in collections
            if c.id == st.session_state.get("active_collection_id")
        ),
        None,
    )
    if active is None:
        return

    _ = st.sidebar.subheader(f"{active.name} ({len(active.paper_ids)})")

    if not active.paper_ids:
        _ = st.sidebar.caption("Empty.")
        return

    for pid in active.paper_ids:
        if st.sidebar.button(f"• {pid[:12]}…", key=f"qv_{pid}"):
            stack = cast("list[object]", st.session_state["view_stack"])
            stack.append(DetailView(paper_id=pid))
            st.session_state["page"] = "search"
            st.rerun()
