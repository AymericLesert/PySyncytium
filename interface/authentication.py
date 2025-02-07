"""
This module handles the authentication mode
"""

import datetime
import os

import jwt
from fastapi import HTTPException, Security, Cookie
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecret")
ALGORITHM = "HS256"

# Handle the authentification user
# ---------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

fake_users_db = {
    "test": {
        "username": "test",
        "password": "password",  # ⚠️ Remplace cela par un hash sécurisé en production
        "schema": "Syncytium"
    }
}

def create_access_token(data: dict, expires_delta: int = 30):
    """Create a JWT Token containing current information of a new valid session"""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def new_token(username, password):
    """Génère un token pour un utilisateur"""
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {
        "access_token": create_access_token({"sub": username, "schema": user["schema"]}), 
        "token_type": "bearer"
        }

def decrypt_user(token = None, access_token = None):
    """Retrieve user profile authenticated"""
    # pylint: disable=raise-missing-from
    token = token or access_token  # Utilise l'en-tête si dispo, sinon le cookie
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token.replace("Bearer ", ""), SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def decrypt_user_api(token = Security(oauth2_scheme)):
    """Retrieve user profile"""
    return decrypt_user(token = token)

def decrypt_user_web(access_token = Cookie(None)):
    """Retrieve user profile"""
    if access_token is None:
        return None
    return decrypt_user(access_token = access_token)
