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
@rate_limiter(limit=6, seconds=60)
async def shorten_url(
        request: Request,
        long_url: Annotated[str, Form()],
        custom_url: str = Form(None),
        db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    if not validate_url(long_url):
        raise HTTPException(status_code=400, detail="URL is not valid")

    if custom_url:
        existing_url = db.query(URL).filter(URL.short_url == custom_url).first()
        if existing_url:
            raise HTTPException(status_code=400, detail="Custom link already in use")
        short_url = custom_url
    else:
        short_url = generate_short_url()

    url_link = URL()
    url_link.long_url = long_url
    url_link.short_url = short_url
    url_link.clicks = 0
    url_link.user_id = user.get("id")

    db.add(url_link)
    db.commit()
    db.refresh(url_link)

    return templates.TemplateResponse("short_url.html", {"request": request, "short_url": short_url})


@url_router.get("/history", response_class=HTMLResponse)
@rate_limiter(limit=5, seconds=60)
async def url_history(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    urls = db.query(URL).filter(URL.user_id == user.get("id")).all()

    return templates.TemplateResponse("history.html", {"request": request, "urls": urls})


@url_router.get("/download-qrcode")
@rate_limiter(limit=5, seconds=60)
async def download_qr_code_form(request: Request):
    return templates.TemplateResponse("qrcode_form.html", {"request": request})


@url_router.get("/qrcode")
@rate_limiter(limit=3, seconds=60)
async def download_qr_code(request: Request, url: str):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    qr_code_path = generate_qr_code(url)
    return FileResponse(
        qr_code_path,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=qr_code.png"}
    )


@url_router.get("/url-analytics", response_class=HTMLResponse)
@rate_limiter(limit=5, seconds=60)
async def show_analytics_form(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("analytics_form.html", {"request": request})


@url_router.post("/analytics", response_class=HTMLResponse)
@rate_limiter(limit=5, seconds=60)
async def get_analytics(request: Request, short_url: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    url_in_db = db.query(URL).filter(URL.short_url == short_url).first()
    if not url_in_db:
        raise HTTPException(status_code=404, detail="URL not found")

    click_records = db.query(Click).filter(Click.url_id == url_in_db.id).all()

    analytics_data = []

    for click in click_records:
        analytics_data.append({
            "ip_address": click.ip_address,
            "country": click.country,
            "state": click.state,
            "city": click.city
        })
        
   

    return templates.TemplateResponse("analytics.html",
                                      {"request": request, "url": url_in_db, "analytics_data": analytics_data})


@url_router.get("/{short_url}")
async def redirect_to_long_url(request: Request, short_url: str, db: Session = Depends(get_db)):
    user_ip_address = get_ip_address()
    original_url = db.query(URL).filter(URL.short_url == short_url).first()
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
