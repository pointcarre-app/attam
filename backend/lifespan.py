from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import shutil

from backend.settings import DATABASE_URL
from backend.postgres_manager import PostgresManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to copy dependencies and trames folders to static folder"""
    # Startup: Copy folders to backend/static
    backend_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(backend_dir)
    static_dir = os.path.join(backend_dir, "static")

    # Create static directory if it doesn't exist
    os.makedirs(static_dir, exist_ok=True)

    # Initialize Database
    if DATABASE_URL:
        try:
            db_manager = PostgresManager(DATABASE_URL)
            db_manager.create_raw_trame_table_if_not_exists()
            print("✓ Database initialized and table 'raw_trame' checked.")

            # Example insertion preparation
            example_username = "sel"
            example_md_content = "# Example Title\n\nThis is a test content."
            example_piece_count = 1
            example_title = "Example Title"
            example_slug = "example-title"
            example_saving_origin = "lifespan_test"
            example_metadata = {"key": "value", "description": "Test insertion"}

            # Use upsert to prevent ID increment on restart
            db_manager.upsert_raw_trame(
                username=example_username,
                md_content=example_md_content,
                piece_count=example_piece_count,
                title=example_title,
                slug=example_slug,
                saving_origin=example_saving_origin,
                metadata=example_metadata,
            )

        except Exception as e:
            print(f"⚠ Database initialization failed: {e}")
    else:
        print("⚠ DATABASE_URL not found in environment variables. Database initialization skipped.")

    # Copy dependencies folder
    dependencies_src = os.path.join(project_root, "dependencies")
    dependencies_dst = os.path.join(static_dir, "dependencies")
    if os.path.exists(dependencies_src):
        if os.path.exists(dependencies_dst):
            shutil.rmtree(dependencies_dst)
        shutil.copytree(dependencies_src, dependencies_dst)
        print(f"✓ Copied dependencies from {dependencies_src} to {dependencies_dst}")
    else:
        print(f"⚠ Dependencies folder not found at {dependencies_src}")

    # Copy trames folder
    trames_src = os.path.join(project_root, "trames")
    trames_dst = os.path.join(static_dir, "trames")
    if os.path.exists(trames_src):
        if os.path.exists(trames_dst):
            shutil.rmtree(trames_dst)
        shutil.copytree(trames_src, trames_dst)
        print(f"✓ Copied trames from {trames_src} to {trames_dst}")
    else:
        print(f"⚠ Trames folder not found at {trames_src}")

    yield

    # Shutdown: cleanup if needed
    print("✓ App shutdown")
