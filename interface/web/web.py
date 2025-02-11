# -*- coding: utf-8 -*-

"""
Test program (FastAPI - FrontEnd)
"""

# pylint: disable=eval-used
# pylint: disable=unused-argument

import os

from fastapi import FastAPI, Depends, Request, Form, Query, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from logger.logger import DSLogger
from logger.loggerobject import asyncloggerexecutiontime

from interface.authentication import new_token, decrypt_user_web
from interface.db import get_db, schema

# Handle the API routes

app = FastAPI(title=DSLogger.Instance.application,
              description="Web Interface - Getting HTML pages",
              version=DSLogger.Instance.version)

# ---------------
# Templates files
# ---------------

templates = Jinja2Templates(directory="interface/web/template")

# ---------------------------------------
# Static files and static protected files
# ---------------------------------------

app.mount("/static", StaticFiles(directory="interface/web/public"), name="static")

@app.get("/script/{filename}")
def get_protected_file(filename, user = Depends(decrypt_user_web)):
    """Extract a file within an authenticated user"""
    file_path = os.path.join("interface/web/script", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

# --------------
# Authentication
# --------------

@app.get("/login", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_login(request: Request, redirect_to: str = Query("/protected")):
    """Access to the login page"""
    return templates.TemplateResponse("login.html", {"request": request, "redirect_to": redirect_to})

@app.post("/login")
@asyncloggerexecutiontime
async def post_login(username: str = Form(...), password: str = Form(...), redirect_to: str = Form("/protected")):
    """Commit the authentication of the user"""
    access_token = new_token(username, password)
    response = RedirectResponse(url=redirect_to, status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token['access_token']}", httponly=True)
    return response

# ---------
# Home page
# ---------

@app.get("/", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_home(request: Request, user = Depends(decrypt_user_web)):
    """Access to the home page"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("index.html",
                                      {
                                          "request": request,
                                          "user": user,
                                          "schema": schema.to_dict()
                                      })

@app.get("/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_insert(table, request: Request, user = Depends(decrypt_user_web)):
    """Access to the page creating a new record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("insert.html",
                                      {
                                          "request": request,
                                          "user": user,
                                          "table": schema[table].to_dict()
                                      })

@app.post("/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_insert(table, request: Request, user = Depends(decrypt_user_web)):
    """Insert a new record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with get_db() as db:
        db.begin_transaction()
        schema[table].insert(dict(record))
        db.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/select/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_select(table, request: Request, user = Depends(decrypt_user_web)):
    """Access to the page showing the list of records"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    records = []
    with get_db():
        for record in schema[table]:
            records.append(record.to_dict())
    return templates.TemplateResponse("select.html",
                                      {
                                          "request": request,
                                          "user": user,
                                          "table": schema[table].to_dict(),
                                          "records": records
                                      })

@app.get("/update/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_update(table, key, request: Request, user = Depends(decrypt_user_web)):
    """Access to the page updating an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    records = []
    with get_db():
        for record in schema[table].select(lambda t : eval(f"t.{schema[table].key}") == key):
            records.append(record.to_dict())
    return templates.TemplateResponse("update.html",
                                      {
                                          "request": request,
                                          "user": user,
                                          "table": schema[table].to_dict(),
                                          "record": records[0],
                                          "key": key
                                      })

@app.post("/update/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_update(table, key, request: Request, user = Depends(decrypt_user_web)):
    """Update an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    newrecord = await request.form()
    records = []
    with get_db() as db:
        for oldrecord in schema[table].select(lambda t : eval(f"t.{schema[table].key}") == key):
            records.append(oldrecord.to_dict())
        db.rollback()
        db.begin_transaction()
        schema[table].update(records[0], dict(newrecord))
        db.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/delete/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_delete(table, key, request: Request, user = Depends(decrypt_user_web)):
    """Access to the page deleting an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    records = []
    with get_db():
        for record in schema[table].select(lambda t : eval(f"t.{schema[table].key}") == key):
            records.append(record.to_dict())
    return templates.TemplateResponse("delete.html",
                                      {
                                          "request": request,
                                          "user": user,
                                          "table": schema[table].to_dict(),
                                          "record": records[0],
                                          "key": key
                                      })

@app.post("/delete/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_delete(table, key, request: Request, user = Depends(decrypt_user_web)):
    """Delete an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with get_db() as db:
        db.begin_transaction()
        schema[table].delete(dict(record))
        db.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/chat", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_chat(request: Request, user = Depends(decrypt_user_web)):
    """Access to the chat page"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("chat.html",
                                      {
                                          "request": request,
                                          "user": user
                                      })
