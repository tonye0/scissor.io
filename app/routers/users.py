from fastapi import APIRouter, status, Depends, HTTPException, Request, Response, Form
from pydantic import BaseModel
from ..database.models import User
from ..database.db import get_db
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta, datetime
from fastapi.responses import HTMLResponse
from typing import Optional
from fastapi.responses import RedirectResponse
from ..utils import Hasher, templates
from ..config import settings


user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="user/token")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_auth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False

    if not Hasher.verify_password(password, user.password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise None
        return {"username": username, "id": user_id}
    except JWTError:
        msg = "Your last session has ended. Log in again."
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")


@user_router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        return False

    token = create_access_token(user.username, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True


@user_router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@user_router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_auth_form()
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Invalid username or password. Try again!"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown error. Try logging in again."
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@user_router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "You have successfully logged out"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


@user_router.get("/signup", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@user_router.post("/signup", response_class=HTMLResponse)
async def register_user(request: Request, db: db_dependency, email: str = Form(...), username: str = Form(...),
                        password: str = Form(...),
                        password2: str = Form(...),
                        ):
    validation1 = db.query(User).filter(User.username == username).first()

    validation2 = db.query(User).filter(User.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid input. Try again!"
        return templates.TemplateResponse("signup.html", {"request": request, "msg": msg})

    user_model = User()

    user_model.email = email
    user_model. username = username
    user_model.password = Hasher.hash_password(password)
    db.add(user_model)
    db.commit()

    msg = "You have sucessfuly signed up for scissor"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

    
    
    
