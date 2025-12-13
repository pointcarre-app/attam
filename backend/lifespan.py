from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import shutil


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to copy dependencies folder to static folder"""
    # Startup: Copy dependencies folder to backend/static
    backend_dir = os.path.dirname(__file__)
    dependencies_src = os.path.join(os.path.dirname(backend_dir), "dependencies")
    static_dir = os.path.join(backend_dir, "static")
    dependencies_dst = os.path.join(static_dir, "dependencies")

    # Create static directory if it doesn't exist
    os.makedirs(static_dir, exist_ok=True)

    # Copy dependencies folder if it exists
    if os.path.exists(dependencies_src):
        if os.path.exists(dependencies_dst):
            shutil.rmtree(dependencies_dst)
        shutil.copytree(dependencies_src, dependencies_dst)
        print(f"✓ Copied dependencies from {dependencies_src} to {dependencies_dst}")
    else:
        print(f"⚠ Dependencies folder not found at {dependencies_src}")

    yield

    # Shutdown: cleanup if needed
    print("✓ App shutdown")
