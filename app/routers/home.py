from fastapi import APIRouter, Request
from ..utils import templates


home_router = APIRouter(
    tags=["HomePage"]
)

@home_router.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@home_router.get("/features")
async def features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})


@home_router.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})