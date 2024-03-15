from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, FileResponse

from sqlalchemy.orm import Session
from validators import url as validate_url

from ..routers.users import get_current_user
from ..utils import generate_short_url, generate_qr_code, templates, get_ip_address, get_ip_info
from ..database.models import URL, Click


class URLService:

    @staticmethod
    async def shorten_url(request: Request, long_url, custom_url, db: Session):
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

        domain = request.url.scheme + "://" + request.url.hostname
        complete_short_url = domain + "/" + short_url

        url_link = URL()
        url_link.long_url = long_url
        url_link.short_url = complete_short_url
        url_link.clicks = 0
        url_link.user_id = user.get("id")

        db.add(url_link)
        db.commit()
        db.refresh(url_link)

        return templates.TemplateResponse("short_url.html", {"request": request, "short_url": complete_short_url})

    @staticmethod
    async def history(request: Request, db: Session):
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

        urls = db.query(URL).filter(URL.user_id == user.get("id")).all()

        return templates.TemplateResponse("history.html", {"request": request, "urls": urls})

    @staticmethod
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

    @staticmethod
    async def get_analytics(request: Request, short_url: str, db: Session):
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

    @staticmethod
    async def delete_url(request: Request, url_id: int, db: Session):
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

        urls = db.query(URL).filter(URL.user_id == user.get("id")).all()

        url_to_delete = db.query(URL).filter(URL.id == url_id).first()

        if not url_to_delete:
            raise HTTPException(status_code=404, detail="URL not found")

        db.delete(url_to_delete)
        db.commit()
        return templates.TemplateResponse("history.html", {"request": request, "urls": urls})


url_handler = URLService()
