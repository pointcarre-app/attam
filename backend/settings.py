import os
from dotenv import load_dotenv

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings


from backend.domain_config import (
    get_domain_config,
)


# Configure Jinja2 templates
_templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


static_files = StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"))


# =============================================================================
# App Settings
# =============================================================================


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    env: str = "LOCAL"
    local_domain: str | None = None  # Override domain for local dev (e.g., "potaunoir")


settings = Settings()

# Convenience exports (backwards compatible)
ENV = settings.env


if ENV == "LOCAL":
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ZND_PASSWORD = os.getenv("ZND_PASSWORD")
SEL_PASSWORD = os.getenv("SEL_PASSWORD")


# =============================================================================
# Templates with domain helper
# =============================================================================


def add_global_context() -> dict:
    return {
        "get_domain": get_domain_config,
    }


_templates.env.globals.update(add_global_context())

templates = _templates
