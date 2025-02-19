# -*- coding: utf-8 -*-

"""
This module handles the authentication mode
"""

import datetime
import hashlib

import jwt
from fastapi import HTTPException

from interface.schemas import DSSchemas

# Handle the authentification user
# ---------------------------------

def create_access_token(data, configuration):
    """Create a JWT Token containing current information of a new valid session"""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=configuration.jwt.expires)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, configuration.jwt.secret_key, algorithm=configuration.jwt.algorithm)

def new_token(interface, username, password, configuration):
    """Generate a token to a given user"""
    with DSSchemas().get_session() as schema:
        with schema:
            users = list(schema.User.select(lambda record : (record.Interface == interface) &
                                                            (record.Login == username)))
            if len(users) == 0:
                raise HTTPException(status_code=400, detail="Invalid username or password")

            h = hashlib.new(configuration.password.algorithm)
            h.update(password.encode(configuration.password.encoding))
            password = h.hexdigest()

            if users[0].Password != password:
                raise HTTPException(status_code=400, detail="Invalid username or password")

            client = None
            clients = list(schema.Client.select(lambda record : record.Id == users[0].ClientId))
            if len(clients) > 0:
                client = clients[0].Name

            return {
                "access_token": create_access_token({
                    "sub": username, 
                    "client": client
                    }, configuration),
                "token_type": "bearer"
                }

def decrypt_user(token, access_token, configuration):
    """Retrieve user profile authenticated"""
    token = token or access_token  # Utilise l'en-tête si dispo, sinon le cookie
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        return jwt.decode(token.replace("Bearer ", ""),
                          configuration.jwt.secret_key,
                          algorithms=[configuration.jwt.algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
