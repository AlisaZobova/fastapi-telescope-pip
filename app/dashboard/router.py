import os

from fastapi import APIRouter

from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

router = APIRouter()

templates = Jinja2Templates(directory= os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "templates"))

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
