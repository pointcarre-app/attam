from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime

from ..settings import templates
from ..dependencies import get_deps_from

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Single view that returns an HTTP response"""

    host = request.headers.get("host")  # e.g., "example.com" or "other.com"
    print(host)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attam App</title>
    </head>
    <body style="max-width: 800px; margin: 0 auto;font-family: monospace; font-size: 1.2rem;">
        <h1>Root</h1>
        <p>Host: {host}</p>
        <ul>
            <li style="padding-bottom:8px;"><a href="/template">Template</a></li>
            <li style="padding-bottom:8px;"><a href="/health">Health</a></li>
            <li style="padding-bottom:8px;"><a href="/trame/debug">Trame Debug</a></li>
            <li style="padding-bottom:8px;"><a href="/trame/path/trames/alidade/batiment_guepard.jpg">Trame Guépard 🐆</a></li>
            <li style="padding-bottom:8px;"><a href="trame/path/trames/alidade/nav_et_trigo.md">Trame Editor</a></li>
        </ul>
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
