# -*- coding: utf-8 -*-

"""
Test program (API)
"""

import json

from fastapi import FastAPI, Header, Path, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from interface.authentication import new_token, decrypt_user_api
from interface.db import get_db, schema

from schema.criteria.criteriafactory import factory as criteriafactory

# Handle the API routes

router = FastAPI(title="Syncytium",
                 description="Description how to get access to the API Syncytium",
                 version="0.0.1")

# Handle the API Route
# --------------------

def get_record(table = Path(..., title="TABLE"),
               record = Header(None)):
    """Extract a record from the Header"""
    if not record:
        raise HTTPException(status_code=400, detail="Missing record header")
    return schema[table].new(json.loads(record))

def get_oldrecord(table = Path(..., title="TABLE"),
                  oldrecord = Header(None)):
    """Extract a record from the Header"""
    if not oldrecord:
        raise HTTPException(status_code=400, detail="Missing record header")
    return schema[table].new(json.loads(oldrecord))

def get_newrecord(table = Path(..., title="TABLE"),
                  newrecord = Header(None)):
    """Extract a record from the Header"""
    if not newrecord:
        raise HTTPException(status_code=400, detail="Missing record header")
    return schema[table].new(json.loads(newrecord))

# --------------------------------------
# API handles the CRUD into the database
# --------------------------------------

@router.post("/token")
async def get_token(form: OAuth2PasswordRequestForm = Depends()):
    """Génère un token pour un utilisateur"""
    return new_token(form.username, form.password)

@router.get("/profil")
def get_profil(user = Depends(decrypt_user_api)):
    """
    Retrieve the profil of the current user
    """
    return {"message": "You are authenticated", "user": user}

@router.post("/schema/{table}/")
async def insert(table,
                 record = Depends(get_record),
                 user = Depends(decrypt_user_api)):
    """
    Create a new record into a table
    """
    print(user)
    with get_db() as db:
        db.begin_transaction()
        newrecord = schema[table].insert(record)
        db.commit()
    return newrecord.to_dict()

@router.get("/schema/{table}/")
async def select(table,
                 query = None,
                 user = Depends(decrypt_user_api)):
    """
    Select a list of records from a table
    * query : describes a filter on the list of records 
    
    Example : ['=', 'Name', 'Tutu'] => List of records having 'Name' = 'Tutu'
    """
    with get_db():
        print(user)
        if query is None:
            return { table: [record.to_dict() for record in schema[table]] }
        return { table: [record.to_dict()
                         for record
                         in schema[table].select(lambda record: criteriafactory(json.loads(query), record))] }

@router.put("/schema/{table}/")
async def update(table,
                 oldrecord = Depends(get_oldrecord),
                 newrecord = Depends(get_newrecord),
                 user = Depends(decrypt_user_api)):
    """
    Update an existing record within a new record into a table
    * oldrecord has to match the record to update
    * newrecord has to contain the fields to update
    """
    print(user)
    with get_db() as db:
        db.begin_transaction()
        newrecordupdated = schema[table].update(oldrecord, newrecord)
        db.commit()
    if newrecordupdated is None:
        raise HTTPException(status_code=404, detail="Key missing")
    return newrecordupdated.to_dict()

@router.delete("/schema/{table}/")
async def delete(table,
                 record = Depends(get_record),
                 user = Depends(decrypt_user_api)):
    """
    Delete an existing record from a table
    """
    print(user)
    with get_db() as db:
        db.begin_transaction()
        oldrecord = schema[table].delete(record)
        db.commit()
    return oldrecord.to_dict()
