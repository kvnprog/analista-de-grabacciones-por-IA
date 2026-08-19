import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.routes.route_chatGPT import router as chatGPT
from infrastructure.routes.auth_routes import router as auth
from backend.infrastructure.routes.users.route_users import router as users
from backend.infrastructure.routes.users.route_users_concentration import router as users_ctn


load_dotenv()

app = FastAPI()

IP_WEB = os.getenv("IP_WEB")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

if IP_WEB:
    origins.append(IP_WEB)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)
app.include_router(chatGPT)
app.include_router(users)
app.include_router(users_ctn)