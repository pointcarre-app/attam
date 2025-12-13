from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os


# Configure Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


static_files = StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"))


# Environment
ENV = os.getenv("ENV", "LOCAL")

# Production allowed hosts
PRODUCTION_HOSTS = [
    "attam0.osc-fr1.scalingo.io",
    "allthingstoallmen.org",
    "pot-au-noir.com",
    "pot-au-noir.fr",
]
