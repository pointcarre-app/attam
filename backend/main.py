from fastapi import FastAPI

from backend.settings import static_files
from backend.lifespan import lifespan
from backend.routers.root import router as root_router
from backend.routers.trame import router as trame_router


# Create FastAPI app instance with lifespan
app = FastAPI(title="Attam App", version="0.0.1", lifespan=lifespan)
app.mount("/static", static_files, name="static")

# Include routers
app.include_router(root_router)
app.include_router(trame_router)
