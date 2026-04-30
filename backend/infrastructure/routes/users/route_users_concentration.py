from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from backend.infrastructure.routes.auth_routes import get_current_user
from backend.infrastructure.services.services_logs import newLogRequests
from shared.db.db_connection import get_session_local
from sqlalchemy.orm import Session
from shared.models.concentration_user import ConcentrationUser
from shared.models.internal_user import InternalUser


router = APIRouter(prefix="/users-ctn", tags=["Users"])

class UserCreateRequest(BaseModel):
    id_employed: int | None = None
    username: str
    password: str
    name: str
    client: str
    plataform: str
    role: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_employed: int | None = None
    username: str
    password: str
    name: str
    client: str
    plataform: str
    role: str
    status: int
    id_user_create: int
    created_at: datetime

@router.post("/")
def create_user (
    user: UserCreateRequest, 
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)
):
    try:
        new_user = ConcentrationUser(
            id_employed = user.id_employed,
            username = user.username,
            password = user.password,
            name = user.name,
            client = user.client,
            plataform = user.plataform,
            role = user.role,
            status = 1,
            id_user_create = current_user['user_id']
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        newLogRequests(db, current_user['user_id'], "/users-ctn/", "POST")
        
        return {
            "status": "success",
            "user": {
                "id": new_user.id,
                "username": new_user.username
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_session_local), current_user: InternalUser = Depends(get_current_user)):
    data_users = db.query(ConcentrationUser).order_by(ConcentrationUser.id.asc()).all()
    return data_users

@router.put("/{user_id}")
def update_user(
    user_id: int, 
    user_update: UserCreateRequest,
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)
):
    db_user = db.query(ConcentrationUser).filter(ConcentrationUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.username != db_user.username:
        existing = db.query(ConcentrationUser).filter(ConcentrationUser.username == user_update.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    try:
        db_user.id_employed = user_update.id_employed
        db_user.username = user_update.username
        db_user.password = user_update.password
        db_user.name = user_update.name
        db_user.client = user_update.client
        db_user.plataform = user_update.plataform
        db_user.role = user_update.role

        db.commit()
        db.refresh(db_user)

        newLogRequests(db, current_user['user_id'], "/users-ctn/" + str(user_id), "PUT")
        
        return {
            "status": "success",
            "user": {
                "id": db_user.id,
                "username": db_user.username
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.delete("/delete-user/{user_id}")
def delete_user(user_id: int,
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)
):
    user = db.query(ConcentrationUser).filter(ConcentrationUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    try:
        user.status = 0
        db.commit()
        
        newLogRequests(db, current_user['user_id'], "/users-ctn/delete-user/" + str(user_id), "DELETE")
        
        return {
            "status": "success",
            "message": "Usuario eliminado"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))