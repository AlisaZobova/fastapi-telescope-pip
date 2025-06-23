import os

from fastapi import APIRouter

from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi_telescope.config import get_api_config

router = APIRouter()

templates = Jinja2Templates(directory= os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "templates"))

api_configs = get_api_config()

# any path processing
@router.get("/{path:path}", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "site_url": api_configs.site_url, "api_prefix": api_configs.api_prefix})
