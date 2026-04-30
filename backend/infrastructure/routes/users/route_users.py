import secrets
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, joinedload

from backend.infrastructure.routes.auth_routes import get_current_user
from backend.infrastructure.services.services_logs import newLogRequests
from shared.db.db_connection import get_session_local
from shared.models.data_user import DataUser
from shared.models.enums import InternalUserRole
from shared.models.internal_campaign import InternalCampaign
from shared.models.internal_user import InternalUser

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DataUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    last_name: str
    id_employed: int | None = None

class UserCreateRequest(BaseModel):
    username: str
    role: str
    email: str
    campaign_id: int
    data_user: DataUserSchema

class DataCampaignSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str
    email: str
    campaign_id: int
    data_user: Optional[DataUserSchema] = None
    campaign: Optional[DataCampaignSchema] = None

class CampaignOption(BaseModel):
    id: int
    name: str

class UtilsResponse(BaseModel):
    roles: List[str]
    campaigns: List[CampaignOption]

class UserCreated(BaseModel):
    id: int
    username: str

class SaveResponse(BaseModel):
    status: str
    temp_password: str
    user: UserCreated 

class UpdateResponse(BaseModel):
    status: str
    user: UserCreated 

def generate_temp_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

@router.post("/")
def create_user(
    user: UserCreateRequest, 
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)
):
    existing = db.query(InternalUser).filter(InternalUser.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    try:
        print("-----------------------------------------")
        print(user)
        
        temp_password = generate_temp_password()
        
        new_user = InternalUser (
            username = user.username,
            role = user.role,
            email = user.email,
            campaign_id = user.campaign_id,
            password_hash = pwd_context.hash(temp_password),
            id_user_create = current_user['user_id']
        )
        db.add(new_user)
        db.flush()
        
        new_data_user = DataUser (
            id = new_user.id,
            name = user.data_user.name,
            last_name = user.data_user.last_name,
            id_employed = user.data_user.id_employed
        )
        db.add(new_data_user)
        
        db.commit()
        db.refresh(new_user)
        
        newLogRequests(db, current_user['user_id'], "/users/", "POST")
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

@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_session_local), current_user: InternalUser = Depends(get_current_user)):
    query = db.query(InternalUser).options(
        joinedload(InternalUser.data_user),
        joinedload(InternalUser.campaign)
    ).filter(InternalUser.status == 1)

    if current_user['role'] != InternalUserRole.admin_develop.value:
        newLogRequests(db, current_user['user_id'], "/users/", "GET")
        return query.filter(
            InternalUser.campaign_id == current_user['campaign_id']
        ).order_by(InternalUser.id.asc()).all()
    
    newLogRequests(db, current_user['user_id'], "/users/", "GET")
    
    return query.order_by(InternalUser.id.asc()).all()

@router.get("/get-data", response_model=UtilsResponse)
def list_data(
    db: Session = Depends(get_session_local), 
    current_user: InternalUser = Depends(get_current_user)):
    
    roles_list = [role.value for role in InternalUserRole]
    campaigns_db = db.query(InternalCampaign)
    
    if current_user['role'] != InternalUserRole.admin_develop.value:
        campaigns_db = db.query(InternalCampaign).filter(
            InternalCampaign.id == current_user['campaign_id']
        ).all()
        
        roles_list = [r for r in roles_list if r != InternalUserRole.admin_develop.value]
    else :
        campaigns_db = db.query(InternalCampaign).all()
    
    newLogRequests(db, current_user['user_id'], "/users/get-data", "GET")
    
    return {
        "roles": roles_list,
        "campaigns": [{"id": c.id, "name": c.name} for c in campaigns_db]
    }

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
        
        newLogRequests(db, current_user['user_id'], "/users/reset-password/" + str(user_id), "PUT")
        
        return {
            "status": "success",
            "message": "Contraseña restablecida",
            "temp_password": new_temp_password
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}", response_model=UpdateResponse)
def update_user(
    user_id: int, 
    user_update: UserCreateRequest,
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)
):
    db_user = db.query(InternalUser).filter(InternalUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.username != db_user.username:
        existing = db.query(InternalUser).filter(InternalUser.username == user_update.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    try:
        db_user.username = user_update.username
        db_user.role = user_update.role
        db_user.email = user_update.email
        db_user.campaign_id = user_update.campaign_id

        if db_user.data_user:
            db_user.data_user.name = user_update.data_user.name
            db_user.data_user.last_name = user_update.data_user.last_name
            db_user.data_user.id_employed = user_update.data_user.id_employed
        else:
            new_data = DataUser(
                id=db_user.id,
                name=user_update.data_user.name,
                last_name=user_update.data_user.last_name,
                id_employed=user_update.data_user.id_employed
            )
            db.add(new_data)

        db.commit()
        db.refresh(db_user)

        newLogRequests(db, current_user['user_id'], "/users/" + str(user_id), "PUT")
        
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
def DeleteUser(
    user_id: int,
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)):
    
    user = db.query(InternalUser).filter(InternalUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    try:
        user.status = 0
        db.commit()
        
        newLogRequests(db, current_user['user_id'], "/users/delete-user/" + str(user_id), "DELETE")
        
        return {
            "status": "success",
            "message": "Usuario eliminado"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))