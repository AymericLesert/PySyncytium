# -*- coding: utf-8 -*-
# pylint: disable=eval-used
# pylint: disable=unused-argument

"""
Test program (FastAPI - FrontEnd)
"""

import os

from fastapi import FastAPI, Depends, Form, Query, HTTPException, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from logger.logger import DSLogger
from logger.loggerobject import asyncloggerexecutiontime

from interface.schemas import DSSchemas
from interface.authentication import new_token, decrypt_user

# Handle the API routes

app = FastAPI(title=DSLogger.Instance.application,
              description="Web Interface - Getting HTML pages",
              version=DSLogger.Instance.version)

def decrypt_user_web(access_token = Cookie(None)):
    """
    Retrieve user profile from web cookie
    """
    if access_token is None:
        return None
    return decrypt_user(None,
                        access_token,
                        DSSchemas().configuration.items.interface.web)

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
    """
    Extract a file within an authenticated user
    """
    file_path = os.path.join("interface/web/script", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

# --------------
# Authentication
# --------------

@app.get("/login", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_login(request, redirect_to = Query("/protected")):
    """Access to the login page"""
    return templates.TemplateResponse("login.html", {"request": request, "redirect_to": redirect_to})

@app.post("/login")
@asyncloggerexecutiontime
async def post_login(username = Form(...), password = Form(...), redirect_to = Form("/protected")):
    """Commit the authentication of the user"""
    access_token = new_token(DSSchemas.Interface.WEB.value,
                             username,
                             password,
                             DSSchemas().configuration.items.interface.web)
    response = RedirectResponse(url=redirect_to, status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token['access_token']}", httponly=True)
    return response

# ---------
# Home page
# ---------

@app.get("/", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_home(request, user = Depends(decrypt_user_web)):
    """Access to the home page of the current user"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    with DSSchemas().get_session(user["client"]) as schema:
        return templates.TemplateResponse("index.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "schema": schema.to_dict()
                                          })

@app.get("/{application}/", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_application(application, request, user = Depends(decrypt_user_web)):
    """Access to the home page of an application"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    with DSSchemas().get_session(user["client"], application) as schema:
        return templates.TemplateResponse("application.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "application": application,
                                              "schema": schema.to_dict()
                                          })

@app.get("/{application}/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_insert(application, table, request, user = Depends(decrypt_user_web)):
    """Access to the page creating a new record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    with DSSchemas().get_session(user["client"], application) as schema:
        return templates.TemplateResponse("insert.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "table": schema[table].to_dict()
                                          })

@app.post("/{application}/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_insert(application, table, request, user = Depends(decrypt_user_web)):
    """Insert a new record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            schema[table].insert(dict(record))
            schema.commit()
    return RedirectResponse(url=f"/{application}/select/{table}", status_code=303)

@app.get("/{application}/select/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_select(application, table, request, user = Depends(decrypt_user_web)):
    """Access to the page showing the list of records"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    records = []
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            for record in schema[table]:
                records.append(record.to_dict())
        return templates.TemplateResponse("select.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "table": schema[table].to_dict(),
                                              "records": records
                                          })

@app.get("/{application}/update/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_update(application, table, key, request, user = Depends(decrypt_user_web)):
    """Access to the page updating an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    records = []
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
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

@app.post("/{application}/update/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_update(application, table, key, request, user = Depends(decrypt_user_web)):
    """Update an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    newrecord = await request.form()
    records = []
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            for oldrecord in schema[table].select(lambda t : eval(f"t.{schema[table].key}") == key):
                records.append(oldrecord.to_dict())
            schema[table].update(records[0], dict(newrecord))
            schema.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/{application}/delete/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_delete(application, table, key, request, user = Depends(decrypt_user_web)):
    """Access to the page deleting an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    records = []
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
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

@app.post("/{application}/delete/{table}/{key}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_delete(application, table, key, request, user = Depends(decrypt_user_web)):
    """Delete an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            schema[table].delete(dict(record))
            schema.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/chat", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_chat(request, user = Depends(decrypt_user_web)):
    """Access to the chat page"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("chat.html",
                                      {
                                          "request": request,
                                          "user": user
                                      })
