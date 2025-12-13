from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime

from ..settings import templates
from ..dependencies import get_deps_from

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root():
    """Single view that returns an HTTP response"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attam App</title>
    </head>
    <body>
        <h1>Welcome to Attam App</h1>
        <p>This is a minimal FastAPI application running successfully!</p>
    </body>
    </html>
    """


@router.get("/template")
async def template_view(request: Request, deps: str = "local"):
    """View that renders a template from the templates folder

    Args:
        deps: 'local' to use local static files, 'cdn' to use CDN URLs
    """
    # Get dependencies based on the deps argument
    dependencies = get_deps_from(deps)

    context = {
        "request": request,
        "title": "Attam Template Page",
        "heading": "Welcome to Template Rendering!",
        "message": "This page is rendered using Jinja2 templates",
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deps": dependencies,
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "App is running"}
