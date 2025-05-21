# -*- coding: utf-8 -*-
# pylint: disable=eval-used
# pylint: disable=unused-argument

"""
Test program (FastAPI - FrontEnd)
"""

import os

from fastapi import FastAPI, Depends, Form, Query, HTTPException, Cookie, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from logger.logger import DSLogger
from logger.loggerobject import asyncloggerexecutiontime

from interface.schemas import DSSchemas
from interface.authentication import new_token, decrypt_user

from app.schema.criteria.criteriacomparableequal import DSCriteriaComparableEqual
from app.schema.criteria.criterialogicaland import DSCriteriaLogicalAnd
from app.schema.criteria.criteriafactory import factory as criteriafactory

# Handle the API routes

app = FastAPI(title=DSLogger.Instance.project,
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

templates = Jinja2Templates(directory="interface/web/html/primevue")

# ------------
# Static files
# ------------

app.mount("/style", StaticFiles(directory="interface/web/style"), name="style")
app.mount("/image", StaticFiles(directory="interface/web/image"), name="image")

@app.get("/script/{filename:path}")
def get_protected_file(filename,
                       user = Depends(decrypt_user_web)):
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
async def get_login(request : Request,
                    redirect_to = Query("/")):
    """Access to the login page"""
    return templates.TemplateResponse("login.html", {"request": request, "redirect_to": redirect_to})

@app.post("/login")
@asyncloggerexecutiontime
async def post_login(username = Form(...),
                     password = Form(...),
                     redirect_to = Form("/")):
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
async def get_home(request : Request,
                   user = Depends(decrypt_user_web)):
    """Access to the home page of the current user"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    if user["client"] is None:
        return templates.TemplateResponse("main/index.html",
                                            {
                                                "request": request,
                                                "user": user,
                                                "projet": DSSchemas().configuration.project,
                                                "version": DSSchemas().configuration.version,
                                                "schema": DSSchemas().configuration.items.main.schema.to_dict()
                                            })

    client = DSSchemas().configuration.items.clients.get(user["client"],
                                                         DSSchemas().configuration.empty.items)
    return templates.TemplateResponse("client/index.html",
                                        {
                                            "request": request,
                                            "user": user,
                                            "projet": DSSchemas().configuration.project,
                                            "version": DSSchemas().configuration.version,
                                            "client": client.to_dict()
                                        })

# ---------------------
# Home page of a client
# ---------------------

@app.get("/{application}/index.html", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_application(application : str,
                          request : Request,
                          user = Depends(decrypt_user_web)):
    """Access to the home page of an application"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    client = DSSchemas().configuration.items.clients.get(user["client"],
                                                         DSSchemas().configuration.empty.items)
    application_context = client.get(f"applications.{application}", DSSchemas().configuration.empty.items)

    with DSSchemas().get_session(user["client"], application) as schema:
        return templates.TemplateResponse("client/application/index.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "client": client.to_dict(),
                                              "application": application_context.to_dict(),
                                              "schema": schema.to_dict()
                                          })

@app.get("/{application}/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_insert(application : str,
                           table : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page creating a new record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    client = DSSchemas().configuration.items.clients.get(user["client"],
                                                         DSSchemas().configuration.empty.items)
    application_context = client.get(f"applications.{application}", DSSchemas().configuration.empty.items)

    with DSSchemas().get_session(user["client"], application) as schema:
        return templates.TemplateResponse("client/application/insert.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "client": client.to_dict(),
                                              "application": application_context.to_dict(),
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict()
                                          })

@app.post("/{application}/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_insert(application : str,
                            table : str,
                            request : Request,
                            user = Depends(decrypt_user_web)):
    """Insert a new record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    print(record)
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            schema[table].insert(schema[table].new(dict(record)))
            schema.commit()
    return RedirectResponse(url=f"/{application}/select/{table}", status_code=303)

@app.get("/{application}/select/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_select(application : str,
                           table : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page showing the list of records"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    client = DSSchemas().configuration.items.clients.get(user["client"],
                                                         DSSchemas().configuration.empty.items)
    application_context = client.get(f"applications.{application}", DSSchemas().configuration.empty.items)

    with DSSchemas().get_session(user["client"], application) as schema:
        records = []
        with schema:
            for record in schema[table]:
                newRecord = record.to_dict()
                newRecord['_tableName'] = table
                newRecord['_key'] = ','.join([newRecord[key] for key in schema[table].key])
                records.append(newRecord)
        return templates.TemplateResponse("client/application/select.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "client": client.to_dict(),
                                              "application": application_context.to_dict(),
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict(),
                                              "records": records
                                          })

@app.get("/{application}/update/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_update(application : str,
                           table : str,
                           keys : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page updating an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    client = DSSchemas().configuration.items.clients.get(user["client"],
                                                         DSSchemas().configuration.empty.items)
    application_context = client.get(f"applications.{application}", DSSchemas().configuration.empty.items)

    with DSSchemas().get_session(user["client"], application) as schema:
        records = []
        with schema:
            clause = [DSCriteriaLogicalAnd.SIGN,
                      [
                          [DSCriteriaComparableEqual.SIGN, key, value]
                          for key, value in zip(schema[table].key, keys.split(","))
                          ]
                      ]
            for record in schema[table].select(lambda t : criteriafactory(clause, t)):
                records.append(record.to_dict())
        return templates.TemplateResponse("client/application/update.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "client": client.to_dict(),
                                              "application": application_context.to_dict(),
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict(),
                                              "record": records[0],
                                              "keys": keys
                                          })

@app.post("/{application}/update/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_update(application : str,
                            table : str,
                            keys : str,
                            request : Request,
                            user = Depends(decrypt_user_web)):
    """Update an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    newrecord = await request.form()
    records = []
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            clause = [DSCriteriaLogicalAnd.SIGN,
                      [
                          [DSCriteriaComparableEqual.SIGN, key, value]
                          for key, value in zip(schema[table].key, keys.split(","))
                          ]
                      ]
            for oldrecord in schema[table].select(lambda t : criteriafactory(clause, t)):
                records.append(oldrecord.clone())
            schema[table].update(records[0], schema[table].new(dict(newrecord)))
            schema.commit()
    return RedirectResponse(url=f"/{application}/select/{table}", status_code=303)

@app.get("/{application}/delete/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_table_delete(application : str,
                           table : str,
                           keys : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page deleting an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    client = DSSchemas().configuration.items.clients.get(user["client"],
                                                         DSSchemas().configuration.empty.items)
    application_context = client.get(f"applications.{application}", DSSchemas().configuration.empty.items)

    with DSSchemas().get_session(user["client"], application) as schema:
        records = []
        with schema:
            clause = [DSCriteriaLogicalAnd.SIGN,
                      [
                          [DSCriteriaComparableEqual.SIGN, key, value]
                          for key, value in zip(schema[table].key, keys.split(","))
                          ]
                      ]
            for record in schema[table].select(lambda t : criteriafactory(clause, t)):
                records.append(record.to_dict())
        return templates.TemplateResponse("client/application/delete.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "client": client.to_dict(),
                                              "application": application_context.to_dict(),
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict(),
                                              "record": records[0],
                                              "keys": keys
                                          })

@app.post("/{application}/delete/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_table_delete(application : str,
                            table : str,
                            keys : str,
                            request : Request,
                            user = Depends(decrypt_user_web)):
    """Delete an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with DSSchemas().get_session(user["client"], application) as schema:
        with schema:
            schema[table].delete(schema[table].new(dict(record)))
            schema.commit()
    return RedirectResponse(url=f"/{application}/select/{table}", status_code=303)

@app.get("/chat", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_chat(request : Request,
                   user = Depends(decrypt_user_web)):
    """Access to the chat page"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("chat.html",
                                      {
                                          "request": request,
                                          "user": user
                                      })

@app.get("/test", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_chat(request : Request,
                   user = Depends(decrypt_user_web)):
    """Access to the chat page"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)
    return templates.TemplateResponse("test.html",
                                      {
                                          "request": request,
                                          "user": user
                                      })

# -------------------------------
# Home page of the administration
# -------------------------------

@app.get("/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_admin_table_insert(table : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page creating a new record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    with DSSchemas().get_session() as schema:
        return templates.TemplateResponse("main/insert.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict()
                                          })

@app.post("/insert/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_admin_table_insert(table : str,
                            request : Request,
                            user = Depends(decrypt_user_web)):
    """Insert a new record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with DSSchemas().get_session() as schema:
        with schema:
            schema[table].insert(schema[table].new(dict(record)))
            schema.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/select/{table}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_admin_table_select(table : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page showing the list of records"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    with DSSchemas().get_session() as schema:
        records = []
        with schema:
            for record in schema[table]:
                records.append(record.to_dict())
        return templates.TemplateResponse("main/select.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict(),
                                              "records": records
                                          })

@app.get("/update/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_admin_table_update(table : str,
                           keys : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page updating an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    with DSSchemas().get_session() as schema:
        records = []
        with schema:
            clause = [DSCriteriaLogicalAnd.SIGN,
                      [
                          [DSCriteriaComparableEqual.SIGN, key, value]
                          for key, value in zip(schema[table].key, keys.split(","))
                          ]
                      ]
            for record in schema[table].select(lambda t : criteriafactory(clause, t)):
                records.append(record.to_dict())
        return templates.TemplateResponse("main/update.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict(),
                                              "record": records[0],
                                              "keys": keys
                                          })

@app.post("/update/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_admin_table_update(table : str,
                            keys : str,
                            request : Request,
                            user = Depends(decrypt_user_web)):
    """Update an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    newrecord = await request.form()
    records = []
    with DSSchemas().get_session() as schema:
        with schema:
            clause = [DSCriteriaLogicalAnd.SIGN,
                      [
                          [DSCriteriaComparableEqual.SIGN, key, value]
                          for key, value in zip(schema[table].key, keys.split(","))
                          ]
                      ]
            for oldrecord in schema[table].select(lambda t : criteriafactory(clause, t)):
                records.append(oldrecord.clone())
            schema[table].update(records[0], schema[table].new(dict(newrecord)))
            schema.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)

@app.get("/delete/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def get_admin_table_delete(table : str,
                           keys : str,
                           request : Request,
                           user = Depends(decrypt_user_web)):
    """Access to the page deleting an existing record"""
    if user is None:
        return RedirectResponse(url=f"/login?redirect_to={request.url}", status_code=303)

    with DSSchemas().get_session() as schema:
        records = []
        with schema:
            clause = [DSCriteriaLogicalAnd.SIGN,
                      [
                          [DSCriteriaComparableEqual.SIGN, key, value]
                          for key, value in zip(schema[table].key, keys.split(","))
                          ]
                      ]
            for record in schema[table].select(lambda t : criteriafactory(clause, t)):
                records.append(record.to_dict())
        return templates.TemplateResponse("main/delete.html",
                                          {
                                              "request": request,
                                              "user": user,
                                              "projet": DSSchemas().configuration.project,
                                              "version": DSSchemas().configuration.version,
                                              "schema": schema.to_dict(),
                                              "table": schema[table].to_dict(),
                                              "record": records[0],
                                              "keys": keys
                                          })

@app.post("/delete/{table}/{keys}", response_class=HTMLResponse)
@asyncloggerexecutiontime
async def post_admin_table_delete(table : str,
                            keys : str,
                            request : Request,
                            user = Depends(decrypt_user_web)):
    """Delete an existing record to the database"""
    if user is None:
        raise HTTPException(status_code=400, detail="Not authenticated")
    record = await request.form()
    with DSSchemas().get_session() as schema:
        with schema:
            schema[table].delete(schema[table].new(dict(record)))
            schema.commit()
    return RedirectResponse(url=f"/select/{table}", status_code=303)
