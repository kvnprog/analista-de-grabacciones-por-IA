# routes/route_chatGPT.py
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.infrastructure.routes.auth_routes import get_current_user
from backend.infrastructure.services.services_logs import newLogRequests
from infrastructure.services.services_chatGPT import (
    get_text_from_file,
    analyze_text_with_chatgpt,
    analyze_emotions_with_chatgpt,
    analyze_multiple_questions_with_chatgpt,
    conteo_exacto_dinamico
)
from infrastructure.services.services_excel import create_analysis_excel, read_questions_from_excel
import json
from typing import List
from shared.db.db_connection import get_session_local
from shared.models.internal_user import InternalUser

router = APIRouter()

@router.post("/analyze-text")
async def analyze_multiple_audios(
    files: List[UploadFile] = File(...),
    words: str | None = Form(None),
    textSearch: str | None = Form(None),
    tipoEntrada: str = Form("audio"),
    detectarEmociones: bool = Form(False),
    questionsFile: UploadFile | None = File(None),
    db: Session = Depends(get_session_local),
    current_user: InternalUser = Depends(get_current_user)
):
    if not files or len(files) == 0:
        return {"error": "Debes enviar al menos un archivo"}

    if not words:
        words_to_find = []
    else:
        words_to_find = [w.strip() for w in words.split(",") if w.strip()]

    detectar_emociones_activo = detectarEmociones and tipoEntrada == "audio"

    # 🔹 Leer preguntas del Excel, si viene
    preguntas_excel = []
    if questionsFile is not None:
        try:
            preguntas_excel = read_questions_from_excel(questionsFile)
        except Exception as e:
            return {"error": f"Error al leer el Excel de preguntas: {str(e)}"}

    if not words_to_find and not textSearch and not detectar_emociones_activo and not preguntas_excel:
        return {"error": "Debes enviar al menos una forma de búsqueda"}

    transcriptions = []
    conteo_palabras = []

    for file in files:
        try:
            if not file.filename:
                raise Exception("Archivo sin nombre")

            file.file.seek(0)
            content = file.file.read()

            if not content or len(content) == 0:
                raise Exception("Archivo vacío")

            file.file.seek(0)

            text = get_text_from_file(file, tipoEntrada)

            transcriptions.append(f"{file.filename}: {text}")

            item = {"audio": file.filename, "palabras": {}}

            if words_to_find:
                conteo = conteo_exacto_dinamico(text, words_to_find, file.filename)
                item["palabras"] = conteo["palabras"]

            # 🔹 Responder preguntas del Excel para este archivo
            if preguntas_excel:
                try:
                    respuestas_raw = analyze_multiple_questions_with_chatgpt(text, preguntas_excel)
                    respuestas_data = json.loads(respuestas_raw) if isinstance(respuestas_raw, str) else respuestas_raw

                    mapa_respuestas = {
                        r.get("pregunta"): r.get("respuesta", "N/A")
                        for r in respuestas_data.get("respuestas", [])
                    }

                    # Aseguramos que todas las preguntas originales queden presentes,
                    # aunque la IA no haya regresado exactamente el mismo texto de pregunta
                    item["preguntas_excel"] = {
                        pregunta: mapa_respuestas.get(pregunta, "N/A")
                        for pregunta in preguntas_excel
                    }
                except Exception as preg_err:
                    item["preguntas_excel"] = {
                        pregunta: f"Error: {str(preg_err)}" for pregunta in preguntas_excel
                    }

            # 🔹 Detección de emociones por archivo
            if detectar_emociones_activo:
                try:
                    emociones_raw = analyze_emotions_with_chatgpt(text)
                    emociones_data = json.loads(emociones_raw) if isinstance(emociones_raw, str) else emociones_raw
                    item["emociones"] = {
                        "bot": emociones_data.get("bot", {}).get("emocion", ""),
                        "bot_detalle": emociones_data.get("bot", {}).get("detalle", ""),
                        "cliente": emociones_data.get("cliente", {}).get("emocion", ""),
                        "cliente_detalle": emociones_data.get("cliente", {}).get("detalle", ""),
                        "confianza": emociones_data.get("confianza", "")
                    }
                except Exception as emo_err:
                    item["emociones"] = {
                        "bot": "", "bot_detalle": "",
                        "cliente": "", "cliente_detalle": "",
                        "confianza": "",
                        "error": f"No se pudo analizar emociones: {str(emo_err)}"
                    }

            conteo_palabras.append(item)

        except Exception as e:
            conteo_palabras.append({
                "audio": file.filename if file.filename else "desconocido",
                "palabras": {},
                "error": str(e),
                "busqueda": {}
            })

            transcriptions.append(f"{file.filename}: ERROR - {str(e)}")

    # 🔹 Análisis con IA si aplica (búsqueda de texto libre)
    if textSearch:
        full_text = "\n".join(transcriptions)

        analysis_raw = analyze_text_with_chatgpt(full_text, textSearch)

        try:
            if isinstance(analysis_raw, str):
                analysis_data = json.loads(analysis_raw)
            else:
                analysis_data = analysis_raw
        except json.JSONDecodeError:
            analysis_data = {"audios": []}

        mapa_busqueda = {
            item.get('nombre'): item.get('busqueda', {})
            for item in analysis_data.get('audios', [])
        }

        for item in conteo_palabras:
            nombre = item['audio']
            item['busqueda'] = mapa_busqueda.get(nombre, {})

    else:
        for item in conteo_palabras:
            item.setdefault('busqueda', {})

    excel_path = create_analysis_excel(conteo_palabras)

    newLogRequests(db, current_user['user_id'], "/analyze-text", "POST")

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="analisis_texto.xlsx"
    )