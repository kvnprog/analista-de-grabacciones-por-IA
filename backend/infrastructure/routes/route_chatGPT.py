# routes/route_chatGPT.py
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from infrastructure.services.services_chatGPT import audio_to_text,analyze_text_with_chatgpt,conteo_exacto_dinamico
from infrastructure.services.services_excel import create_analysis_excel
import json
from typing import List

router = APIRouter()

@router.post("/analyze-text")
async def analyze_multiple_audios(
    files: List[UploadFile] = File(...),
    words: str | None = Form(None),
    textSearch: str | None = Form(None)
):
    if not files or len(files) == 0:
        return {"error": "Debes enviar al menos un archivo"}

    if not words:
        words_to_find = []
    else:
        words_to_find = [w.strip() for w in words.split(",") if w.strip()]

    if not words_to_find and not textSearch:
        return {"error": "Debes enviar al menos una forma de búsqueda"}

    transcriptions = []
    conteo_palabras = []

    for file in files:
        try:
            # 🔹 Validaciones antes de procesar
            if not file.filename:
                raise Exception("Archivo sin nombre")

            file.file.seek(0)
            content = file.file.read()

            if not content or len(content) == 0:
                raise Exception("Archivo vacío")

            # 🔹 Regresar puntero para que audio_to_text lo lea bien
            file.file.seek(0)

            # 🔹 Transcripción segura
            text = audio_to_text(file)

            transcriptions.append(f"{file.filename}: {text}")

            if words_to_find:
                conteo_palabras.append(
                    conteo_exacto_dinamico(text, words_to_find, file.filename)
                )
            else:
                conteo_palabras.append({
                    "audio": file.filename,
                    "palabras": {}
                })

        except Exception as e:
            # 🔥 Aquí evitas que truene todo el proceso
            conteo_palabras.append({
                "audio": file.filename if file.filename else "desconocido",
                "palabras": {},
                "error": str(e),
                "busqueda": {}
            })

            transcriptions.append(f"{file.filename}: ERROR - {str(e)}")

    # 🔹 Análisis con IA si aplica
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
            item['busqueda'] = {}

    # 🔹 Crear Excel
    excel_path = create_analysis_excel(conteo_palabras)

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="analisis_texto.xlsx"
    )