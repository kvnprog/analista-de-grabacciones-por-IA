from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException

from infrastructure.routes.route_chatGPT import router as chatGPT

app = FastAPI()

# 🔥 CORS (VA AQUÍ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción pon tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 Rutas
app.include_router(chatGPT)

