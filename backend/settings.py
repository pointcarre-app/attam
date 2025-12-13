from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import Response
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os


# Configure Jinja2 templates
_templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


static_files = StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"))


# =============================================================================
# Domain Configuration
# =============================================================================


class DomainConfig(BaseModel):
    """Configuration for a single domain/brand"""

    name: str
    hosts: list[str]
    logo: str | None = None
    theme: str = "anchor"
    slug: str


DOMAINS: dict[str, DomainConfig] = {
    "potaunoir": DomainConfig(
        name="Pot au Noir",
        hosts=["pot-au-noir.fr", "pot-au-noir.com", "localhost", "127.0.0.1", "*"],
        logo="/static/trames/potaunoir/logo-1.png",
        slug="pot-au-noir",
    ),
    # "alidade": DomainConfig(
    #     name="Alidade",
    #     hosts=["alidade.fr"],
    #     logo=None,
    # ),
    "attam": DomainConfig(
        name="All Things to All Men",
        hosts=["allthingstoallmen.org", "attam0.osc-fr1.scalingo.io"],
        logo=None,
        slug="attam",
    ),
}


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

# Production allowed hosts (derived from DOMAINS)
PRODUCTION_HOSTS = [host for domain in DOMAINS.values() for host in domain.hosts]


# =============================================================================
# Templates with auto-injected domain
# =============================================================================


def _get_domain_from_request(request: Request) -> DomainConfig | None:
    """Get domain config from request host"""
    host = request.headers.get("host", "")
    for config in DOMAINS.values():
        if any(h in host for h in config.hosts):
            return config
    return None


class Templates:
    """Wrapper around Jinja2Templates that auto-injects domain into context"""

    def __init__(self, jinja_templates: Jinja2Templates):
        self.jinja = jinja_templates
        self.env = jinja_templates.env

    def TemplateResponse(
        self,
        name: str,
        context: dict,
        status_code: int = 200,
        headers: dict | None = None,
        media_type: str | None = None,
        background=None,
    ) -> Response:
        """Render template with domain auto-injected"""
        request = context.get("request")
        if request and "domain" not in context:
            context["domain"] = _get_domain_from_request(request)

        return self.jinja.TemplateResponse(
            name=name,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


templates = Templates(_templates)
