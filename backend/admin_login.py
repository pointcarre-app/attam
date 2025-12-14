"""
Admin login system using JWT tokens with HTTP-only cookies.
Simple, stateless authentication without database or session storage.
"""

from datetime import timedelta
from typing import Optional
from fastapi import Request, Form, Cookie, HTTPException
from fastapi.responses import RedirectResponse

from backend.dependencies import get_deps_from
from backend.settings import templates, ZND_PASSWORD, SEL_PASSWORD
from backend.jwt_handler import (
    create_access_token,
    verify_access_token,
    ACCESS_TOKEN_EXPIRE_HOURS,
)


# Access names mapping
ACCESS_NAMES = {"znd": "Znd", "sel": "Sel"}

# Access credentials (access_name: password)
# TODO: Move to environment variables or secure config
ACCESS_CREDENTIALS = {
    "znd": ZND_PASSWORD,  # Change these!
    "sel": SEL_PASSWORD,  # Change these!
}


async def admin_access(request: Request, access_name: str):
    """
    Login page - shows password form for valid access names.
    """
    dependencies = get_deps_from("local")

    context = {
        "request": request,
        "deps": dependencies,
        "access_name_slug": access_name,  # Pass the slug for form action
    }

    if access_name not in ACCESS_NAMES:
        context["access_name"] = "Unknown"
        context["access_makes_sense"] = False
    else:
        context["access_name"] = ACCESS_NAMES[access_name]
        context["access_makes_sense"] = True

    return templates.TemplateResponse("trame/admin.html", context)


async def login_submit(request: Request, password: str = Form(...)):
    """
    Handle login form submission.
    Verifies password and sets JWT token in HTTP-only cookie if valid.
    """
    # Get the referer to extract access_name
    referer = request.headers.get("referer", "")

    # Extract access_name from referer URL
    # Expected format: /trame/admin/{access_name}
    access_name = None
    if "/trame/admin/" in referer:
        parts = referer.split("/trame/admin/")
        if len(parts) > 1:
            access_name = parts[1].split("/")[0].split("?")[0]

    # Validate access_name exists
    if not access_name or access_name not in ACCESS_CREDENTIALS:
        raise HTTPException(status_code=400, detail="Invalid access")

    # Verify password
    if ACCESS_CREDENTIALS[access_name] != password:
        # Return to login page with error
        dependencies = get_deps_from("local")
        context = {
            "request": request,
            "deps": dependencies,
            "access_name": ACCESS_NAMES.get(access_name, "Unknown"),
            "access_makes_sense": True,
            "access_name_slug": access_name,
            "error": "Invalid password",
        }
        return templates.TemplateResponse("trame/admin.html", context)

    # Create JWT token
    expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    token = create_access_token(access_name, expires)

    # Set HTTP-only cookie
    redirect_response = RedirectResponse(
        url=f"/trame/admin/{access_name}/dashboard", status_code=303
    )
    redirect_response.set_cookie(
        key="trame_access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
    )

    return redirect_response


async def admin_dashboard(
    request: Request,
    access_name: str,
    trame_access_token: Optional[str] = Cookie(None),
):
    """
    Protected dashboard - requires valid JWT token.
    """
    # Verify token
    if not trame_access_token:
        return RedirectResponse(url=f"/trame/admin/{access_name}", status_code=303)

    token_access_name = verify_access_token(trame_access_token)

    # Check if token is valid and matches the requested access
    if not token_access_name or token_access_name != access_name:
        return RedirectResponse(url=f"/trame/admin/{access_name}", status_code=303)

    # Token is valid - show dashboard
    dependencies = get_deps_from("local")
    context = {
        "request": request,
        "deps": dependencies,
        "access_name": ACCESS_NAMES.get(access_name, "Unknown"),
        "access_name_slug": access_name,
    }

    return templates.TemplateResponse("trame/admin_dashboard.html", context)


async def admin_logout(access_name: str):
    """
    Logout - clears the JWT cookie and redirects to login page.
    """
    redirect_response = RedirectResponse(url=f"/trame/admin/{access_name}", status_code=303)
    redirect_response.delete_cookie(key="trame_access_token")
    return redirect_response
