# routes/route_chatGPT.py
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from infrastructure.services.services_chatGPT import audio_to_text, analyze_text_with_chatgpt
from infrastructure.services.services_excel import create_analysis_excel
import json
from typing import List


router = APIRouter(
    prefix="/chaGPTServices",
    tags=["chaGPTServices"]
)

@router.post("/audio-to-text")
async def convert_audio(file: UploadFile = File(...)):
    text = audio_to_text(file)  # 👈 PASAMOS file.file
    return {
        "success": True,
        "text": text
    }


router = APIRouter()

@router.post("/analyze-text")
async def analyze_multiple_audios(
    files: List[UploadFile] = File(...),
    words: str = Form(...)
):
    """
    files: múltiples audios
    words: "hola,api,chatgpt"
    """

    # 1️⃣ Convertir palabras a lista
    words_to_find = [w.strip() for w in words.split(",") if w.strip()]

    if not words_to_find:
        return {"error": "Debes enviar al menos una palabra"}

    # 2️⃣ Transcribir todos los audios
    transcriptions = []

    for file in files:
        text = audio_to_text(file)
        transcriptions.append(text)

    # 3️⃣ Unir transcripciones
    full_text = "\n".join(transcriptions)

    # 4️⃣ Analizar texto completo
    analysis_raw = analyze_text_with_chatgpt(full_text, words_to_find)
    analysis = json.loads(analysis_raw)

    # 5️⃣ Crear Excel
    excel_path = create_analysis_excel(analysis)

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="analisis_texto.xlsx"
    )
