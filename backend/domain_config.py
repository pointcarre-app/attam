"""
Domain configuration for multi-tenant support.
"""

from pydantic import BaseModel
from starlette.requests import Request


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
        theme="pan-light",
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

# Production allowed hosts (derived from DOMAINS)
PRODUCTION_HOSTS = [host for domain in DOMAINS.values() for host in domain.hosts]


def get_domain_config(request: Request) -> DomainConfig | None:
    """
    Resolve domain config from request host.

    For local dev, override via:
    - Env var: LOCAL_DOMAIN=potaunoir
    - Query param: ?domain=potaunoir
    """
    host = request.headers.get("host", "")

    # Local override
    # if settings.env == "LOCAL":
    #     override = settings.local_domain or request.query_params.get("domain")
    #     if override and override in DOMAINS:
    #         return DOMAINS[override]

    # Match by host
    for config in DOMAINS.values():
        if any(h in host for h in config.hosts):
            return config

    return None
