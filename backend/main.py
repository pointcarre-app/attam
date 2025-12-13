from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.settings import static_files, ENV, PRODUCTION_HOSTS
from backend.lifespan import lifespan
from backend.routers.root import router as root_router
from backend.routers.trame import router as trame_router


# Create FastAPI app instance with lifespan
app = FastAPI(title="Attam App", version="0.0.1", lifespan=lifespan)

# Security: Only restrict hosts in production
if ENV == "PRODUCTION":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=PRODUCTION_HOSTS)

elif ENV == "LOCAL":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"])

app.mount("/static", static_files, name="static")

# Include routers
app.include_router(root_router)
app.include_router(trame_router)
