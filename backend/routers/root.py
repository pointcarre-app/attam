from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime, UTC

from ..settings import templates, ENV
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
        <h2>znd</h2>
        <ul>
            <li style="padding-bottom:8px;"><a href="/trame/path/trames/alidade/batiment_guepard.jpg"> 🐆 Trame Guépard </a></li>
            <li style="padding-bottom:8px;"><a href="trame/path/trames/alidade/nav_et_trigo.md"> 📝 Trame Editor </a></li>
            <li style="padding-bottom:8px;"><a href="/fonts"> 🎨 Fonts </a></li>
        </ul>

        <h2>sel</h2>
        <ul>
            <li style="padding-bottom:8px;"><a href="/template">🎨 Template</a></li>
            <li style="padding-bottom:8px;"><a href="/health"> 🛡️ Health </a></li>
            <li style="padding-bottom:8px;"><a href="/trame/debug"> ⚙️ Trame Debug </a></li>
        </ul>


    </body>
    </html>
    """


@router.get("/template")
async def template_view(request: Request, deps: str = "local"):
    """View that renders the DaisyUI showcase template

    Args:
        deps: 'local' to use local static files, 'cdn' to use CDN URLs
    """
    dependencies = get_deps_from(deps)
    host = request.headers.get("host", "")

    # Show pot-au-noir logo if LOCAL env or pot-au-noir domain
    show_potaunoir_logo = ENV == "LOCAL" or "pot-au-noir.fr" in host or "pot-au-noir.com" in host

    context = {
        "request": request,
        "deps": dependencies,
        "show_potaunoir_logo": show_potaunoir_logo,
    }
    return templates.TemplateResponse("template_showcase.html", context)


@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "App is running",
        "host": request.headers.get("host"),
        "time_utc": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
    }


@router.get("/fonts")
async def fonts(request: Request):
    """Fonts endpoint"""

    dependencies = get_deps_from("local")

    host = request.headers.get("host", "")

    # Show pot-au-noir logo if LOCAL env or pot-au-noir domain
    show_potaunoir_logo = ENV == "LOCAL" or "pot-au-noir.fr" in host or "pot-au-noir.com" in host
    context = {
        "request": request,
        "status": "ok",
        "message": "Fonts are running",
        "host": request.headers.get("host"),
        "time_utc": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "deps": dependencies,
        "show_potaunoir_logo": show_potaunoir_logo,
    }

    return templates.TemplateResponse("fonts.html", context)
