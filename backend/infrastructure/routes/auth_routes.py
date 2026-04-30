import os
from dotenv import load_dotenv

from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Response
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from passlib.hash import bcrypt
from typing import Optional
from backend.infrastructure.services.services_logs import newLogRequests, newLogSession, updateLogSession
from shared.db.db_connection import get_session_local
from shared.models.internal_user import InternalUser
from backend.infrastructure.core.security.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token

load_dotenv()
debug_mode = os.getenv("DEBUG_MODE").lower()

router = APIRouter(prefix="/auth", tags=["Authentication"])
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: int
    user_role: Optional[str] = None
    name: str
    last_name: str

@router.post("/login", response_model=LoginResponse)
def login_user(login_req: LoginRequest, response: Response,  db: Session = Depends(get_session_local)):
    user = db.query(InternalUser).options(
        joinedload(InternalUser.data_user),
    ).filter(
        InternalUser.username == login_req.username,
        InternalUser.status == 1
    ).first()
    if not user or not bcrypt.verify(login_req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    data_log = newLogSession(db, user.id)
    
    token = create_access_token(
        {
            "id": str(data_log),
            "user_id": str(user.id), 
            "username": user.username,
            "role": user.role.value, 
            "name": user.data_user.name,
            "campaign_id": user.campaign_id
        }
    )
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Siempre True en producción con HTTPS
        samesite="lax", 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return LoginResponse(
        user_id = user.id,
        user_role=user.role.value,
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
    def get_current_user(access_token: Optional[str] = Cookie(None)):
        if not access_token:
            raise HTTPException(status_code=401, detail="No autorizado: Falta el token")
        
        try:
            payload = decode_access_token(access_token)
            return payload
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
else:
    def get_current_user(access_token: Optional[str] = Cookie(None)):
        if not access_token:
            raise HTTPException(status_code=401, detail="No autorizado: Falta el token")
        
        try:
            payload = decode_access_token(access_token)
            return payload
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.put('/logout')
def logout_user( db: Session = Depends(get_session_local), current_user: any = Depends(get_current_user)):
    try:
        id_del_log = current_user.get('id') 
    
        if not id_del_log:
            print("Error: No se encontró 'id' en current_user")
            raise HTTPException(status_code=400, detail="Token no contiene ID de sesión")
        
        updateLogSession(db, int(id_del_log))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")