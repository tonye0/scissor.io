import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
from jose import jwt, JWTError

from .utils import templates
from .database import models
from .database.db import engine
from .routers.urls import url_router
from .routers.home import home_router
from .routers.users import user_router
from .config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="scissor.io"
)

# @app.exception_handler(FastAPIHTTPException)
# async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
#     if exc.status_code == 404:
#         return templates.TemplateResponse("404.html", {"request": request, "error": "page not found"}, status_code=404)
#     return templates.TemplateResponse("505.html", {"request": request, "error": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException)
async def generic_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("505.html", {"request": request})


# @app.exception_handler(HTTPException)
# async def jwt_error_exception_handler(request: Request, exc: HTTPException):
#     return templates.TemplateResponse("exception.html", {"request": request})


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(home_router)
app.include_router(url_router)
app.include_router(user_router)



@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("exception.html",
                                      {"request": request, "status_code": exc.status_code, "exc": exc})


@app.exception_handler(404)
async def http_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("exception.html", {"request": request, "status_code": 404, "exc": exc})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run(app, host="0.0.0.0", port=port)

