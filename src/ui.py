import streamlit as st

from .entities import Paper


def abstract_preview(text: str, max_chars: int = 250) -> str:
    """
    Produce a short preview of an abstract.

    Args:
        text (str): Full abstract text.
        max_chars (int): Maximum number of characters to display.

    Returns:
        str: Preview string (with "..." appended if truncated).
    """
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "..."


def render_results(results: list[Paper]) -> None:
    """
    Render a compact list of paper results in Streamlit.

    Args:
        results (list[Paper]): Ranked papers to display.

    Returns:
        None
    """
    st.write(f"{len(results)} result(s)")

    for paper in results:
        _ = st.markdown(f"**{paper.title or 'Untitled'}**")

        authors = ", ".join(paper.authors) if paper.authors else "Unknown authors"
        year = str(paper.year) if paper.year is not None else ""
        meta_parts = [authors, year]
        meta = " · ".join(part for part in meta_parts if part)

        if meta:
            st.write(meta)

        if paper.journal:
            st.write(paper.journal)

        if paper.abstract:
            st.write(abstract_preview(paper.abstract))

        with st.expander("Details"):
            if paper.abstract:
                st.write(paper.abstract)

            if paper.doi:
                st.write("DOI:", paper.doi)

            if paper.keywords:
                st.write("Keywords:", ", ".join(paper.keywords))

        _ = st.divider()
