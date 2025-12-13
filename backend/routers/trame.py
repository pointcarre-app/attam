from pathlib import Path
from fastapi import APIRouter, Request


from trame import Trame, Piece

from backend.dependencies import get_deps_from
from backend.trame_reader import read_trame
from backend.settings import templates


router = APIRouter(tags=["trame"], prefix="/trame")


trame_attr = [attr for attr in dir(Trame) if not attr.startswith("_")]
piece_attr = [attr for attr in dir(Piece) if not attr.startswith("_")]


# Get only the field names defined in the Pydantic model
trame_model_fields = list(Trame.model_fields.keys())
piece_model_fields = list(Piece.model_fields.keys())


@router.get("/path/{trame_path:path}")
async def get_trame(request: Request, trame_path: Path):
    dependencies = get_deps_from("local")
    trame = read_trame(trame_path)
    # from pprint import pprint

    # pprint(trame)

    context = {
        "request": request,
        "trame": trame,
        "deps": dependencies,
    }
    return templates.TemplateResponse("trame.html", context)


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
