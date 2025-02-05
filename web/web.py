"""
Test program (FastAPI - FrontEnd)
"""

from fastapi import FastAPI, Depends, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

from api.authentication import new_token, decrypt_user_web

app = FastAPI()

# Définir le dossier des templates
templates = Jinja2Templates(directory="web/template")

@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request, redirect_to: str = Query("/protected")):
    """Access to the login page"""
    return templates.TemplateResponse("login.html", {"request": request, "redirect_to": redirect_to})

@app.post("/login")
def post_login(username: str = Form(...), password: str = Form(...), redirect_to: str = Form("/protected")):
    """Commit the authentication of the user"""
    access_token = new_token(username, password)
    response = RedirectResponse(url=redirect_to, status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token['access_token']}", httponly=True)
    return response

@app.get("/protected", response_class=HTMLResponse)
def get_protected(request: Request, user = Depends(decrypt_user_web)):
    """Access to the protected page"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("protected.html", {"request": request, "user": user})

@app.get("/")
def get_home(request: Request):
    """Access to the home page"""
    return templates.TemplateResponse("index.html", {"request": request, "username": "John Doe"})
