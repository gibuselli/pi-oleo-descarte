from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
import models
from database import engine, sessionlocal, get_db, create_tables, drop_tables
from sqlalchemy.orm import Session
import bcrypt
import jwt
from datetime import datetime, timedelta
import config
import os

app = FastAPI()

load_dotenv()

app.mount("/static", StaticFiles(directory="static"), name="static")

session_secret_key = os.getenv("SESSION_SECRET_KEY")
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key=session_secret_key)


        
@app.on_event("startup")
async def startup_event():
    drop_tables()
    create_tables()

@app.get("/", response_class=HTMLResponse)
async def render_login(request: Request, registered: Optional[bool] = False, loginFailed: Optional[bool] = False):
    is_authenticated = check_authenticated(request)
    
    if is_authenticated:
        return templates.TemplateResponse("profile.html", {"request": request})
    
    return templates.TemplateResponse("login.html",
                                      {"request": request,
                                       "is_authenticated": is_authenticated,
                                       "registered": registered, "loginFailed": loginFailed})

@app.get("/list", response_class=HTMLResponse)
async def render_list(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.oil_quantity > 0).all()
    is_authenticated = check_authenticated(request)
    return templates.TemplateResponse("list-users.html", {"request": request, "users": users, "is_authenticated": is_authenticated})

@app.get("/register", response_class=HTMLResponse)
async def render_register(request: Request):
    is_authenticated = check_authenticated(request)
    
    if is_authenticated:
        return templates.TemplateResponse("profile.html", {"request": request, "is_authenticated": is_authenticated})
    
    return templates.TemplateResponse("register.html", {"request": request, "is_authenticated": is_authenticated})

@app.get("/profile", response_class=HTMLResponse)
async def render_profile(request: Request, db: Session = Depends(get_db)):
    is_authenticated = check_authenticated(request)
    
    if is_authenticated:
        user_email = request.session.get("email")
        user = get_user_by_email(user_email, db)
        return templates.TemplateResponse("profile.html", {"request": request, "is_authenticated": is_authenticated, "user": user})
    
    return templates.TemplateResponse("login.html", {"request": request, "is_authenticated": is_authenticated})
    
    

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
        return RedirectResponse(url="/?registered=True", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        
@app.post("/update-user")
async def update_user(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    action = form.get("action")
    user_id = request.session.get("id")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user:
        if action == "update":
            user.name = form.get("name")
            user.email = form.get("email")
            user.district = form.get("district")
            user.city = form.get("city")
            user.oil_quantity = form.get("oil_quantity")
            
            db.commit()
                
            request.session["email"] = user.email
            
            return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
        elif action == "delete":
            db.delete(user)
            db.commit()
            response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
            response.delete_cookie("Authorization", domain="localhost")
            return response
        
        
@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(form_data.username, db)
    
    if not user:
        return RedirectResponse(url="/?loginFailed=True", status_code=status.HTTP_302_FOUND)
    
    if not check_password(form_data.password, user.hashed_password):
        return RedirectResponse(url="/?loginFailed=True", status_code=status.HTTP_302_FOUND)
    
    token = jwt.encode({"user_id": user.id,
                                    "email": user.email,
                                    "exp": datetime.utcnow() + timedelta(days=30)},
                                    key=config.settings.SIGN_IN_KEY,
                                    algorithm="HS256")
    
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    
    request.session["email"] = user.email
    request.session["id"] = user.id
    
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization", domain="localhost")
    return response

def check_password(password: str, hashed_password: str) -> bool:
    print(type(password), type(hashed_password))
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def get_user_by_email(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first()

def check_authenticated(request: Request) -> bool:
    authorization_cookie = request.cookies.get("Authorization")
    if authorization_cookie:
        scheme, param = get_authorization_scheme_param(authorization_cookie)
        if scheme.lower() == "bearer":
            return True
    return False    