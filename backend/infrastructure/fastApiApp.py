from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse

from infrastructure.routes.route_chatGPT import router as chatGPT

app = FastAPI()

origins = [
    "http://172.18.232.195:3000"
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
app.include_router(chatGPT)
