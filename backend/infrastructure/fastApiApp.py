import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse

from infrastructure.routes.route_chatGPT import router as chatGPT
from infrastructure.routes.auth_routes import router as auth
from backend.infrastructure.routes.users.route_users import router as users
from backend.infrastructure.routes.users.route_users_concentration import router as users_ctn


load_dotenv()
app = FastAPI()

IP_WEB = os.getenv("IP_WEB")
origins = [
    IP_WEB
]

# 🔥 CORS (VA AQUÍ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # en producción pon tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 Rutas
app.include_router(auth)
app.include_router(chatGPT)
app.include_router(users)
app.include_router(users_ctn)
