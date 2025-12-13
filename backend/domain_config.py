"""
Get domain config from request host.
"""

from fastapi import Request

from .settings import DOMAINS, DomainConfig


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
