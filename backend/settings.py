from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os


# Configure Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


static_files = StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"))


# =============================================================================
# Domain Configuration
# =============================================================================


class DomainConfig(BaseModel):
    """Configuration for a single domain/brand"""

    name: str
    hosts: list[str]
    logo: str | None = None
    theme: str = "default"


DOMAINS: dict[str, DomainConfig] = {
    "potaunoir": DomainConfig(
        name="Pot au Noir",
        hosts=["pot-au-noir.fr", "pot-au-noir.com"],
        logo="/static/trames/potaunoir/logo-1.png",
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
