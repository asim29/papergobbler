"""PaperGobbler — Literature search interface."""

from __future__ import annotations

from typing import cast

import streamlit as st

from src.api import search_papers
from ui import (
    DetailView,
    ListView,
    render_collection_page,
    render_detail_view,
    render_list_view,
    render_sidebar,
)


def init_state() -> None:
    """Initialize session state with defaults."""
    if "view_stack" not in st.session_state:
        st.session_state["view_stack"] = []  # list[ListView | DetailView]

    if "active_collection_id" not in st.session_state:
        st.session_state["active_collection_id"] = None  # str | None

    if "page" not in st.session_state:
        st.session_state["page"] = "search"


def main() -> None:
    """Streamlit application entrypoint."""
    _ = st.title("PaperGobbler")
    init_state()
    render_sidebar()

    page = cast("str", st.session_state["page"])

    if page == "collection":
        render_collection_page()
        return

    # ---- Search page ----
    with st.form("search_form"):
        query = st.text_input("Search papers")
        submitted = st.form_submit_button("Search")

    if submitted and query.strip():
        papers, next_offset = search_papers(query.strip())
        view = ListView(
            source="search",
            label=f'Search: "{query.strip()}"',
            query=query.strip(),
            results=papers,
            next_offset=next_offset,
        )
        stack = cast("list[ListView | DetailView]", st.session_state["view_stack"])
        stack.clear()
        stack.append(view)
        st.rerun()

    stack = cast("list[ListView | DetailView]", st.session_state["view_stack"])

    if not stack:
        _ = st.caption("Enter a query above to search for papers.")
        return

    # Back button
    if len(stack) > 1:
        if st.button("Back"):
            _ = stack.pop()
            st.rerun()

    # Render top of stack
    top = stack[-1]
    if isinstance(top, ListView):
        render_list_view(top)
    else:
        render_detail_view(top)


if __name__ == "__main__":
    main()
