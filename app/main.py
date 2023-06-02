from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from typing import List
from pydantic import BaseModel
import models
from database import engine, sessionlocal, get_db, create_tables, drop_tables
from sqlalchemy.orm import Session
import bcrypt
import jwt
from datetime import datetime, timedelta
import config

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
        
@app.on_event("startup")
async def startup_event():
    drop_tables()
    create_tables()

@app.get("/", response_class=HTMLResponse)
async def render_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/list", response_class=HTMLResponse)
async def render_list(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id.desc())
    return templates.TemplateResponse("list-users.html", {"request": request, "users": users})

@app.get("/register", response_class=HTMLResponse)
async def render_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def render_profile(request: Request):
    # cookie_authorization: str = request.cookies.get("Authorization")
    
    # cookie_scheme, cookie_param = get_authorization_scheme_param(
    # cookie_authorization
    # )
    
    # if cookie_scheme.lower() == "bearer":
    #     authorization = True
    #     scheme = cookie_scheme
    # else:
    #     authorization = False
        
    # if not authorization or scheme.lower() != "bearer":
    #     return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("profile.html", {"request": request})

@app.post("/create-user", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    try:        
        form = await request.form()
        name = form["name"]
        city = form["city"]
        district = form["district"]
        oil_quantity = form["oil_quantity"]
        email = form["email"]
        password = form["hashed_password"]
        hashed_password = hash_password(password)
        
        user = models.User(
            name=name,
            city=city,
            district=district,
            oil_quantity=oil_quantity,
            email=email,
            hashed_password=hashed_password)
        
        db.add(user)
        db.commit()
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        
        
@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(form_data.username, db)
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    if not check_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    token = jwt.encode({"user_id": user.id,
                                    "email": user.email,
                                    "exp": datetime.utcnow() + timedelta(days=30)},
                                    key=config.settings.SIGN_IN_KEY,
                                    algorithm="HS256")
    
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        domain="localtest.me",
        httponly=True,
        max_age=1800,
        expires=1800,
        )
    
    return response
    
    

def check_password(password: str, hashed_password: str) -> bool:
    print(type(password), type(hashed_password))
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def get_user_by_email(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first()