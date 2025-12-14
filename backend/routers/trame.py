from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Request, Cookie, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import logging


from trame import Trame, Piece

from backend.dependencies import get_deps_from
from backend.trame_reader import read_trame, prepare_trame_for_rendering, process_markdown_content
from backend.settings import templates, DATABASE_URL
from backend import admin_login
from backend.jwt_handler import verify_access_token
from backend.postgres_manager import PostgresManager


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

    prepared_pieces = process_markdown_content(markdown_data.content)

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


# TODO : after dashboard
@router.get("/admin/{access_name:str}/raw_trame_list")
async def raw_trame_list(
    request: Request,
    access_name: str,
    trame_access_token: Optional[str] = Cookie(None),
):
    """
    Example protected view that requires login.
    """
    # Verify token
    token_user = verify_access_token(trame_access_token) if trame_access_token else None

    # Check if logged in and user matches
    if not token_user or token_user != access_name:
        # Redirect to login page if not authenticated
        return RedirectResponse(url=f"/trame/admin/{access_name}", status_code=303)

    raw_trame_records = []
    if DATABASE_URL:
        try:
            db_manager = PostgresManager(DATABASE_URL)
            raw_trame_records = db_manager.get_all_raw_trames()
        except Exception as e:
            logger.error(f"Failed to fetch raw trames: {e}")

    dependencies = get_deps_from("local")
    context = {
        "request": request,
        "deps": dependencies,
        "access_name": token_user,
        "access_name_slug": access_name,
        "raw_trame_records": raw_trame_records,
    }
    return templates.TemplateResponse("trame/raw_trame_list.html", context)


@router.get("/admin/{access_name:str}/raw_trame/{raw_trame_id:int}")
async def view_raw_trame(
    request: Request,
    access_name: str,
    raw_trame_id: int,
    trame_access_token: Optional[str] = Cookie(None),
):
    """
    Protected view to render a specific raw trame from the database.
    """
    # Verify token
    token_user = verify_access_token(trame_access_token) if trame_access_token else None

    # Check if logged in and user matches
    if not token_user or token_user != access_name:
        return RedirectResponse(url=f"/trame/admin/{access_name}", status_code=303)

    raw_trame = None
    prepared_pieces = []
    trame_html_content = ""

    if DATABASE_URL:
        try:
            db_manager = PostgresManager(DATABASE_URL)
            raw_trame = db_manager.get_raw_trame_by_id(raw_trame_id)
        except Exception as e:
            logger.error(f"Failed to fetch raw trame {raw_trame_id}: {e}")

    if not raw_trame:
        raise HTTPException(status_code=404, detail="Raw trame not found")

    # Process content
    trame_html_content = raw_trame.get("md_content", "")
    prepared_pieces = process_markdown_content(trame_html_content)

    dependencies = get_deps_from("local")
    context = {
        "request": request,
        "trame": None,  # Not needed for raw rendering
        "raw_trame": raw_trame,
        "prepared_pieces": prepared_pieces,
        "trame_html_content": trame_html_content,
        "deps": dependencies,
        "access_name": token_user,
    }
    return templates.TemplateResponse("trame/raw_trame_view.html", context)


@router.get("/admin/{access_name:str}/raw_trame_editor/{raw_trame_id:int}")
async def editor_raw_trame(
    request: Request,
    access_name: str,
    raw_trame_id: int,
    trame_access_token: Optional[str] = Cookie(None),
):
    """
    Protected view to edit a specific raw trame.
    """
    # Verify token
    token_user = verify_access_token(trame_access_token) if trame_access_token else None

    # Check if logged in and user matches
    if not token_user or token_user != access_name:
        return RedirectResponse(url=f"/trame/admin/{access_name}", status_code=303)

    raw_trame = None
    prepared_pieces = []
    trame_html_content = ""

    if DATABASE_URL:
        try:
            db_manager = PostgresManager(DATABASE_URL)
            raw_trame = db_manager.get_raw_trame_by_id(raw_trame_id)
        except Exception as e:
            logger.error(f"Failed to fetch raw trame {raw_trame_id}: {e}")

    if not raw_trame:
        raise HTTPException(status_code=404, detail="Raw trame not found")

    # Process content
    trame_html_content = raw_trame.get("md_content", "")
    prepared_pieces = process_markdown_content(trame_html_content)

    dependencies = get_deps_from("local")
    context = {
        "request": request,
        "trame": None,
        "raw_trame": raw_trame,
        "prepared_pieces": prepared_pieces,
        "trame_html_content": trame_html_content,
        "deps": dependencies,
        "access_name": token_user,
    }
    return templates.TemplateResponse("trame/raw_trame_editor.html", context)


# Admin login routes
# Specific routes must come before parameterized routes
router.post("/admin/login")(admin_login.login_submit)
router.get("/admin/logout")(admin_login.admin_logout)
router.get("/admin/logout/confirmed")(admin_login.admin_logout_confirmed)
router.get("/admin/{access_name:str}/dashboard")(admin_login.admin_dashboard)
# router.get("/admin/{access_name:str}/protected-example")(raw_trame_list)
router.get("/admin/{access_name:str}")(admin_login.admin_access)
