import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.infrastructure.routes.auth_routes import get_current_user
from shared.db.db_connection import get_session_local
from shared.models.data_user import DataUser
from shared.models.internal_user import InternalUser

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DataUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    last_name: str

class UserCreateRequest(BaseModel):
    username: str
    email: str
    data_user: DataUserSchema

def generate_temp_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

@router.post("/")
def create_user(
    user: UserCreateRequest, 
    db: Session = Depends(get_session_local)
):
    existing = db.query(InternalUser).filter(InternalUser.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    try:
        temp_password = generate_temp_password()
        
        new_user = InternalUser (
            username = user.username,
            email = user.email,
            password_hash = pwd_context.hash(temp_password)
        )
        db.add(new_user)
        db.flush()
        
        new_data_user = DataUser (
            id = new_user.id,
            name = user.data_user.name,
            last_name = user.data_user.last_name
        )
        db.add(new_data_user)
        
        db.commit()
        db.refresh(new_user)
        return {
            "status": "success",
            "temp_password": temp_password,
            "user": {
                "id": new_user.id,
                "username": new_user.username
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.put("/reset-password/{user_id}")
def update_password(
    user_id: int,
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)):
    
    user = db.query(InternalUser).filter(InternalUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    try:
        new_temp_password = generate_temp_password()
        
        user.password_hash = pwd_context.hash(new_temp_password)
        db.commit()
        
        return {
            "status": "success",
            "message": "Contraseña restablecida",
            "temp_password": new_temp_password
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))