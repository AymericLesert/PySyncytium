# -*- coding: utf-8 -*-

"""
API - Functions API Rest to get access data
"""

import json

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from logger.logger import DSLogger
from logger.loggerobject import asyncloggerexecutiontime

from interface.schemas import DSSchemas
from interface.authentication import new_token, decrypt_user

from app.schema.criteria.criteriafactory import factory as criteriafactory

class RequestAPI:
    """Class containing properties of an API Request"""
    def __init__(self, client, application, table, newrecord, oldrecord, query):
        self.client = client
        self.application = application
        self.table = table
        self.newrecord = newrecord
        self.oldrecord = oldrecord
        self.query = query

# Handle the API routes

app = FastAPI(title=DSLogger.Instance.project,
              description="API Interface - Getting service access",
              version=DSLogger.Instance.version)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def decrypt_user_api(token = Security(oauth2_scheme)):
    """
    Retrieve user profile from api interface
    """
    return decrypt_user(token,
                        None,
                        DSSchemas().configuration.items.interface.api)

def query_string_api(application: str = None,
                     table: str = None,
                     newrecord: str = None,
                     oldrecord: str = None,
                     query: str = None,
                     user = Depends(decrypt_user_api)):
    """
    Retrieve parameter of the api interface
    """
    def convert(schema, value):
        dsrecord = None
        if value is not None:
            items = json.loads(value)
            if isinstance(items, (list, tuple)):
                dsrecord = []
                for item in items:
                    dsrecord.append(schema[table].new(item))
            else:
                dsrecord = schema[table].new(items)
        return dsrecord

    if query is not None:
        query = json.loads(query)

    if (user["client"] is None) != (application is None):
        raise HTTPException(status_code=405, detail="Not allowed !")

    with DSSchemas().get_session(user["client"], application) as schema:
        dsoldrecord = convert(schema, oldrecord)
        dsnewrecord = convert(schema, newrecord)

    return RequestAPI(user["client"],
                      application,
                      table,
                      dsnewrecord,
                      dsoldrecord,
                      query)

# --------------------------------------
# API handles the CRUD into the database
# --------------------------------------

@app.post("/token")
@asyncloggerexecutiontime
async def get_token(form: OAuth2PasswordRequestForm = Depends()):
    """
    Generate a new token for a given user
    """
    return new_token(DSSchemas.Interface.API.value,
                     form.username,
                     form.password,
                     DSSchemas().configuration.items.interface.api)

@app.get("/profil")
@asyncloggerexecutiontime
async def get_profil(user = Depends(decrypt_user_api)):
    """
    Retrieve the profil of the current user
    """
    return {"message": "You are authenticated", "user": user}

# ---------------------------------------------------------------
# API handles the CRUD into the database from a given application
# ---------------------------------------------------------------

@app.post("/schema/{table}/")
@app.post("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def insert(request = Depends(query_string_api)):
    """
    Create a new record into an administration table :
    * oldrecord is ignored
    """
    with DSSchemas().get_session(request.client, request.application) as schema:
        with schema:
            newrecord = schema[request.table].insert(request.newrecord)
            schema.commit()
    return newrecord.to_dict()

@app.get("/schema/{table}/")
@app.get("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def select(request = Depends(query_string_api)):
    """
    Select a list of records from an administration table
    * query : describes a filter on the list of records 
    
    Example : ['=', 'Name', 'Tutu'] => List of records having 'Name' = 'Tutu'
    """
    with DSSchemas().get_session(request.client, request.application) as schema:
        records = []
        with schema:
            if request.query is None:
                for record in schema[request.table]:
                    records.append(record.to_dict())
            else:
                for record in schema[request.table].select(lambda t: criteriafactory(request.query, t)):
                    records.append(record.to_dict())
        return { "table": records }

@app.put("/schema/{table}/")
@app.put("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def update(request = Depends(query_string_api)):
    """
    Update an existing record within a new record into an administration table
    * oldrecord has to match the record to update
    * newrecord has to contain the fields to update
    """
    with DSSchemas().get_session(request.client, request.application) as schema:
        with schema:
            newrecordupdated = schema[request.table].update(request.oldrecord, request.newrecord)
            schema.commit()
    if newrecordupdated is None:
        raise HTTPException(status_code=404, detail="Key missing")
    return newrecordupdated.to_dict()

@app.delete("/schema/{table}/")
@app.delete("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def delete(request = Depends(query_string_api)):
    """
    Delete an existing record from an administration table
    """
    with DSSchemas().get_session(request.client, request.application) as schema:
        with schema:
            oldrecord = schema[request.table].delete(request.oldrecord)
            schema.commit()
    return oldrecord.to_dict()
