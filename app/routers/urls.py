from typing import Annotated

from fastapi import Request, HTTPException, Depends, APIRouter, status, Form
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from validators import url as validate_url

from fastapi_simple_rate_limiter import rate_limiter


from .users import get_current_user
from ..database.db import get_db
from ..database.models import URL, Click
from ..utils import generate_short_url, generate_qr_code, templates, get_ip_address, get_ip_info
from ..services.urls import url_handler, URLService

url_router = APIRouter(
    tags=["URLs"]
)



@url_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("profile.html", {"request": request, "username": user.get("username")})


@url_router.post("/shortened-url")
@rate_limiter(limit=25, seconds=60)
def shorten_url(
        request: Request,
        long_url: Annotated[str, Form()],
        custom_url: str = Form(None),
        db: Session = Depends(get_db)
):
    return url_handler.shorten_url(request, long_url, custom_url, db)


@url_router.get("/history", response_class=HTMLResponse)
@rate_limiter(limit=25, seconds=60)
def url_history(request: Request, db: Session = Depends(get_db)):
    return url_handler.history(request, db)


@url_router.get("/download-qrcode")
@rate_limiter(limit=5, seconds=60)
async def download_qr_code_form(request: Request):
    return templates.TemplateResponse("qrcode_form.html", {"request": request})


@url_router.get("/qrcode")
@rate_limiter(limit=3, seconds=3)
def download_qr_code(request: Request, url: str):
    return url_handler.download_qr_code(request, url)

@url_router.get("/url-analytics", response_class=HTMLResponse)
@rate_limiter(limit=5, seconds=60)
async def show_analytics_form(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("analytics_form.html", {"request": request})


@url_router.post("/analytics", response_class=HTMLResponse)
@rate_limiter(limit=5, seconds=60)
def get_analytics(request: Request, short_url: str = Form(...), db: Session =Depends(get_db)):
    return url_handler.get_analytics(request, short_url, db)


@url_router.post("/delete/{url_id}")
async def delete_url(request: Request, url_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    urls = db.query(URL).filter(URL.user_id == user.get("id")).all()

    url_to_delete = db.query(URL).filter(URL.id == url_id).first()

    if not url_to_delete:
        raise HTTPException(status_code=404, detail="URL not found")

    db.delete(url_to_delete)
    db.commit()
    return RedirectResponse("/history/", status_code=status.HTTP_303_SEE_OTHER)



@url_router.get("/{complete_short_url}")
def redirect_to_long_url(request: Request, complete_short_url: str, db: Session = Depends(get_db)):
    user_ip_address = get_ip_address()
    original_url = db.query(URL).filter(URL.short_url == complete_short_url).first()
    if original_url:
        original_url.clicks += 1
        ip_info = get_ip_info(user_ip_address)
        country = ip_info.get('country', 'Unknown')
        state = ip_info.get('region', 'Unknown')
        city = ip_info.get('city', 'Unknown')
        clicks = Click(
            url_id=original_url.id,
            ip_address=user_ip_address,
            country=country,
            state=state,
            city=city
        )
        db.add(clicks)
        db.commit()
        db.refresh(clicks)
        return RedirectResponse(original_url.long_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        raise HTTPException(status_code=404, detail="URL not found")
