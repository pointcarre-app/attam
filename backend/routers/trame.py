from pathlib import Path
from fastapi import APIRouter, Request
from pydantic import BaseModel
import tempfile
import logging


from trame import Trame, Piece, TrameBuilder

from backend.dependencies import get_deps_from
from backend.trame_reader import read_trame, prepare_trame_for_rendering
from backend.settings import templates
from backend import admin_login


logger = logging.getLogger(__name__)


class MarkdownContent(BaseModel):
    content: str


router = APIRouter(tags=["trame"], prefix="/trame")


trame_attr = [attr for attr in dir(Trame) if not attr.startswith("_")]
piece_attr = [attr for attr in dir(Piece) if not attr.startswith("_")]


# Get only the field names defined in the Pydantic model
trame_model_fields = list(Trame.model_fields.keys())
piece_model_fields = list(Piece.model_fields.keys())


@router.get("/path/{trame_path:path}")
async def get_trame(request: Request, trame_path: Path):
    dependencies = get_deps_from("local")

    # Detect file extension and route accordingly
    file_extension = trame_path.suffix.lower()

    if file_extension == ".md":
        # Markdown processing
        trame = read_trame(trame_path)
        prepared_pieces = prepare_trame_for_rendering(trame)
        trame_html_content = trame_path.read_text(encoding="utf-8")

        context = {
            "request": request,
            "trame": trame,
            "prepared_pieces": prepared_pieces,
            "trame_html_content": trame_html_content,
            "deps": dependencies,
        }
        return templates.TemplateResponse("trame.html", context)

    elif file_extension in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        # Image viewer
        # Serve from static folder (trames are copied there on startup)
        image_url = f"/static/{trame_path}"

        context = {
            "request": request,
            "image_path": str(trame_path),
            "image_name": trame_path.name,
            "image_url": image_url,
            "file_extension": file_extension,
            "deps": dependencies,
        }
        return templates.TemplateResponse("image_viewer.html", context)

    else:
        # Unsupported file type
        return {"error": f"Unsupported file type: {file_extension}", "path": str(trame_path)}


# TODO : ensure logic
@router.post("/process")
async def process_markdown(request: Request, markdown_data: MarkdownContent):
    logger.info("Processing markdown content")

    # Create temporary file with markdown content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(markdown_data.content)
        tmp_path = Path(tmp_file.name)

    try:
        # Process the markdown file
        trame = TrameBuilder.from_file(path=tmp_path)
        prepared_pieces = prepare_trame_for_rendering(trame)

        logger.info(f"Processed {len(prepared_pieces)} pieces from markdown")
        logger.info(f"Prepared pieces: {prepared_pieces}")

        # Render the HTML partial
        rendered_html = templates.get_template("pieces/_rendered_content.html").render(
            prepared_pieces=prepared_pieces
        )

        return {
            "success": True,
            "prepared_pieces": prepared_pieces,
            "piece_count": len(prepared_pieces),
            "rendered_html": rendered_html,
        }
    finally:
        # Clean up temporary file
        tmp_path.unlink(missing_ok=True)


@router.get("/debug")
async def debug(request: Request):
    dependencies = get_deps_from("local")

    context = {
        "request": request,
        # "trame": trame,
        "deps": dependencies,
        "trame_attr": trame_attr,
        "piece_attr": piece_attr,
        "trame_model_fields": trame_model_fields,
        "piece_model_fields": piece_model_fields,
    }
    return templates.TemplateResponse("trame_debug.html", context)


# Admin login routes
router.get("/admin/{access_name:str}")(admin_login.admin_access)
router.post("/admin/login")(admin_login.login_submit)
router.get("/admin/{access_name:str}/dashboard")(admin_login.admin_dashboard)
router.get("/admin/{access_name:str}/logout")(admin_login.admin_logout)
