"""
Admin login system using JWT tokens with HTTP-only cookies.
Simple, stateless authentication without database or session storage.
"""

from datetime import timedelta
from typing import Optional
import logging
from fastapi import Request, Form, Cookie, HTTPException
from fastapi.responses import RedirectResponse

from backend.dependencies import get_deps_from
from backend.settings import templates, SEL_PASSWORD, WASABI_PASSWORD
from backend.jwt_handler import (
    create_access_token,
    verify_access_token,
    ACCESS_TOKEN_EXPIRE_HOURS,
)

logger = logging.getLogger(__name__)


# Access names mapping
ACCESS_NAMES = {"wasabi": "Wasabi", "sel": "Sel"}

# Access credentials (access_name: password)
# TODO: Move to environment variables or secure config
ACCESS_CREDENTIALS = {
    "wasabi": WASABI_PASSWORD,  # Change these!
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


async def login_submit(request: Request, password: str = Form(...), access_name: str = Form(...)):
    """
    Handle login form submission.
    Verifies password and sets JWT token in HTTP-only cookie if valid.
    """
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
        path="/",  # Explicitly set path to root
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
    logger.info(
        f"Dashboard access attempt for {access_name}, token present: {trame_access_token is not None}"
    )

    # Verify token
    if not trame_access_token:
        logger.warning("No token found, redirecting to login")
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

    response = templates.TemplateResponse("trame/admin_dashboard.html", context)

    # Add cache control headers to prevent caching of authenticated pages
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


async def admin_logout_confirmed(
    request: Request, trame_access_token: Optional[str] = Cookie(None)
):
    """
    Logout confirmation page - shown after cookie is cleared.
    """
    logger.info(f"Logout confirmed page, token still present: {trame_access_token is not None}")

    # Check if we successfully logged out (token should be None)
    access_name = None
    display_name = "Unknown"

    if trame_access_token:
        # Token still exists! Try to get info from it
        access_name = verify_access_token(trame_access_token)
        if access_name:
            display_name = ACCESS_NAMES.get(access_name, access_name)
            logger.warning(f"Token still present after logout for {display_name}!")

    dependencies = get_deps_from("local")
    context = {
        "request": request,
        "deps": dependencies,
        "logged_out": True,
        "access_name": display_name,
        "access_name_slug": access_name,
    }

    response = templates.TemplateResponse("trame/admin_logout.html", context)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # Ensure cookie is deleted if it still exists
    if trame_access_token:
        response.delete_cookie(
            key="trame_access_token",
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )

    return response


async def admin_logout(request: Request, trame_access_token: Optional[str] = Cookie(None)):
    """
    Logout - clears the JWT cookie and shows confirmation.
    Reads the token to determine which user is logging out.
    """
    logger.info(f"Logout attempt, token present: {trame_access_token is not None}")

    # Try to get the access_name from the token
    access_name = None
    display_name = "Unknown"

    if trame_access_token:
        access_name = verify_access_token(trame_access_token)
        if access_name:
            display_name = ACCESS_NAMES.get(access_name, access_name)
            logger.info(f"Logging out user: {display_name}")

    # Prepare response

    # Instead of rendering a template, redirect immediately after clearing cookie
    redirect_response = RedirectResponse(url="/trame/admin/logout/confirmed", status_code=303)

    # Add cache control headers
    redirect_response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    redirect_response.headers["Pragma"] = "no-cache"
    redirect_response.headers["Expires"] = "0"

    # Delete the cookie
    redirect_response.delete_cookie(
        key="trame_access_token",
        path="/",
        secure=False,
        httponly=True,
        samesite="lax",
    )

    logger.info("Cookie deletion command sent in response")

    return redirect_response
