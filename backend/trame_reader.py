from pathlib import Path
from trame import Trame, TrameBuilder, Piece
from typing import Dict, Any, List
import tempfile
import logging

logger = logging.getLogger(__name__)


# trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)


def read_trame(path: Path) -> Trame:
    return TrameBuilder.from_file(path=path)


def prepare_piece_for_rendering(piece: Piece) -> Dict[str, Any]:
    """
    Prepare a piece for rendering by extracting its data and determining
    which template to use.

    Returns a dictionary with:
    - template: the template name to use (e.g., 'pieces/title.html')
    - data: the data to pass to the template
    """
    piece_type = piece.__class__.__name__

    if piece_type == "Title":
        return {
            "template": "pieces/title.html",
            "data": {"level": piece.level, "text": piece.page_element_bs4.string},
        }

    elif piece_type == "Paragraph":
        print(piece.page_element_bs4)
        return {
            "template": "pieces/paragraph.html",
            "data": {"text": str(piece.page_element_bs4)},
        }

    elif piece_type == "UnorderedList":
        items = [li.string for li in piece.page_element_bs4.find_all("li")]
        return {"template": "pieces/unordered_list.html", "data": {"items": items}}

    elif piece_type in ["Code", "YamlCode"]:
        return {
            "template": "pieces/code.html",
            "data": {
                "language": piece.language if hasattr(piece, "language") else None,
                "code": piece.code_str,
            },
        }

    elif piece_type == "Table":
        table = piece.page_element_bs4
        thead_rows = []
        tbody_rows = []

        if table.thead:
            for row in table.thead.find_all("tr"):
                thead_rows.append([th.string for th in row.find_all("th")])

        if table.tbody:
            for row in table.tbody.find_all("tr"):
                tbody_rows.append([td.string for td in row.find_all("td")])

        return {
            "template": "pieces/table.html",
            "data": {"thead_rows": thead_rows, "tbody_rows": tbody_rows},
        }

    # Default fallback
    return {"template": "pieces/unknown.html", "data": {"piece_type": piece_type}}


def prepare_trame_for_rendering(trame: Trame) -> List[Dict[str, Any]]:
    """
    Process all pieces in a trame and prepare them for rendering.
    Returns a list of prepared pieces ready for the template.
    """
    return [prepare_piece_for_rendering(piece) for piece in trame.pieces]


def process_markdown_content(content: str) -> List[Dict[str, Any]]:
    """
    Process markdown content string into prepared pieces for rendering.
    Creates a temporary file, processes it, and cleans up.
    """
    # Create temporary file with markdown content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        # Process the markdown file
        trame = TrameBuilder.from_file(path=tmp_path)
        prepared_pieces = prepare_trame_for_rendering(trame)

        logger.info(f"Processed {len(prepared_pieces)} pieces from markdown")
        logger.info(f"Prepared pieces: {prepared_pieces}")

        return prepared_pieces
    finally:
        # Clean up temporary file
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    trame = read_trame(path=Path("trames/alidade/nav_et_trigo.md"))
    print(trame)
