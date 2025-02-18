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

# Handle the API routes

app = FastAPI(title=DSLogger.Instance.application,
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

@app.post("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def insert(application,
                 table,
                 record,
                 user = Depends(decrypt_user_api)):
    """
    Create a new record into a table
    """
    with DSSchemas().get_session(user["client"], application) as schema:
        schema_table = schema[table]
        record = schema_table.new(record)
        with schema:
            newrecord = schema_table.insert(record)
            schema.commit()
    return newrecord.to_dict()

@app.get("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def select(application,
                 table,
                 query = None,
                 user = Depends(decrypt_user_api)):
    """
    Select a list of records from a table
    * query : describes a filter on the list of records 
    
    Example : ['=', 'Name', 'Tutu'] => List of records having 'Name' = 'Tutu'
    """
    with DSSchemas().get_session(user["client"], application) as schema:
        schema_table = schema[table]
        with schema:
            if query is None:
                return { table: [record.to_dict() for record in schema_table] }
            return { table: [record.to_dict()
                             for record
                             in schema_table.select(lambda record: criteriafactory(json.loads(query), record))] }

@app.put("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def update(application,
                 table,
                 oldrecord,
                 newrecord,
                 user = Depends(decrypt_user_api)):
    """
    Update an existing record within a new record into a table
    * oldrecord has to match the record to update
    * newrecord has to contain the fields to update
    """
    with DSSchemas().get_session(user["client"], application) as schema:
        schema_table = schema[table]
        oldrecord = schema_table.new(oldrecord)
        newrecord = schema_table.new(newrecord)
        with schema:
            newrecordupdated = schema_table.update(oldrecord, newrecord)
            schema.commit()
    if newrecordupdated is None:
        raise HTTPException(status_code=404, detail="Key missing")
    return newrecordupdated.to_dict()

@app.delete("/{application}/schema/{table}/")
@asyncloggerexecutiontime
async def delete(application,
                 table,
                 record,
                 user = Depends(decrypt_user_api)):
    """
    Delete an existing record from a table
    """
    with DSSchemas().get_session(user["client"], application) as schema:
        schema_table = schema[table]
        record = schema_table.new(record)
        with schema:
            oldrecord = schema_table.delete(record)
            schema.commit()
    return oldrecord.to_dict()
