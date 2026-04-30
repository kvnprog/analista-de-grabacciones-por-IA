from fastapi import HTTPException
from sqlalchemy.orm import Session
from shared.models.log_requests import LogRequests
from shared.models.log_sessions import LogSessions
from shared.utils.utils import get_mexico_time

def newLogSession(db: Session, id_user: int):
    try:
        new_data_log = LogSessions (
            id_user = id_user,
            login_at = get_mexico_time(),
            logout_at = None
        )
        
        db.add(new_data_log)
        db.commit()
        db.refresh(new_data_log)
        
        return new_data_log.id
    except Exception as e:
        db.rollback() # Revierte los cambios si hay un error
        print(f"Error al registrar la sesión: {e}")
        raise e

def updateLogSession(db: Session, id_log: int):
    try:
        db_log = db.query(LogSessions).filter(LogSessions.id == id_log).first()
        
        if not db_log:
            raise HTTPException(status_code=404, detail="Log de sesión no encontrado")
        
        db_log.logout_at = get_mexico_time()
        db.commit()
        db.refresh(db_log)
    except Exception as e:
        db.rollback() # Revierte los cambios si hay un error
        print(f"Error al registrar la sesión: {e}")
        raise e

def newLogRequests(db: Session, id_user: int, path_requests: str, type_requests: str):
    try:
        new_data_log = LogRequests (
            id_user = id_user,
            path_requests = path_requests,
            type_requests = type_requests
        )
        
        db.add(new_data_log)
        db.commit()
        db.refresh(new_data_log)
        
        return new_data_log.id
    except Exception as e:
        db.rollback() # Revierte los cambios si hay un error
        print(f"Error al registrar la petición: {e}")
        raise e