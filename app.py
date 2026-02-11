from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.db import Paper, load_papers
from src.search import search_papers
from src.ui import render_results


DATA_PATH = Path(__file__).parent / "data" / "papers.json"


@st.cache_data
def cached_load_papers(path: Path) -> list[Paper]:
    """
    Load papers with Streamlit caching enabled.

    Args:
        path (Path): JSON path.

    Returns:
        list[Paper]: Loaded papers.
    """
    return load_papers(path)


def main() -> None:
    """
    Streamlit app entrypoint.

    Returns:
        None
    """
    st.title("Literature Search")

    papers = cached_load_papers(DATA_PATH)

    query = st.text_input("Search")

    if st.button("Search"):
        results = search_papers(papers, query)
        render_results(results)


if __name__ == "__main__":
    main()
