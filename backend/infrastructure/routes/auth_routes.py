import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from passlib.hash import bcrypt
from typing import Optional
from shared.db.db_connection import get_session_local
from shared.models.internal_user import InternalUser
from backend.infrastructure.core.security.jwt_handler import create_access_token, decode_access_token

load_dotenv()
debug_mode = os.getenv("DEBUG_MODE").lower()

router = APIRouter(prefix="/auth", tags=["Authentication"])
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    last_name: str

@router.post("/login", response_model=LoginResponse)
def login_user(login_req: LoginRequest, db: Session = Depends(get_session_local)):
    user = db.query(InternalUser).options(
        joinedload(InternalUser.data_user),
    ).filter(
        InternalUser.username == login_req.username,
        InternalUser.status == 1
    ).first()
    if not user or not bcrypt.verify(login_req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    token = create_access_token(
        {
            "user_id": str(user.id), 
            "username": user.username,
            "name": user.data_user.name,
        }
    )
    return LoginResponse(
        access_token=token,
        user_id = user.id,
        name = user.data_user.name,
        last_name = user.data_user.last_name
    )

@router.get('/test-jwt')
def user(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
        payload = decode_access_token(token)
        return {"user": payload.get("user_id"), "username": payload.get("username"), 'data': 'jwt test works! from auth_routes.py'}
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    
if debug_mode == "false":
    def get_current_user(authorization: str = Header(...)):
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
            payload = decode_access_token(token)
            return payload  # contiene user_id, username, role
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
else:
    def get_current_user(authorization: str = Header(...)):
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
            payload = decode_access_token(token)
            return payload  # contiene user_id, username, role
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
