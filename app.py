from pathlib import Path

import streamlit as st

from src.db import load_papers
from src.entities import Paper
from src.search import search_papers
from src.ui import render_results


DATA_PATH = Path(__file__).parent / "data" / "papers.json"


@st.cache_data
def cached_load_papers(path: Path) -> list[Paper]:
    """
    Load papers with Streamlit caching enabled.

    Args:
        path (Path): Path to the JSON dataset.

    Returns:
        list[Paper]: Loaded paper entities.
    """
    return load_papers(path)


def main() -> None:
    """
    Streamlit application entrypoint.
    """
    _ = st.title("Literature Search")

    papers: list[Paper] = cached_load_papers(DATA_PATH)

    query: str = st.text_input("Search")

    if st.button("Search"):
        results: list[Paper] = search_papers(papers, query)
        render_results(results)


if __name__ == "__main__":
    main()
