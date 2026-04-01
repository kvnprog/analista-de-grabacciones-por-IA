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
    """
    files: múltiples audios
    words: "hola,api,chatgpt"
    textSearch: "Busca un monto en la llamada"
    """
    
    if not words:
        words_to_find = []
    else:
        words_to_find = [w.strip() for w in words.split(",") if w.strip()]

    if not words_to_find and not textSearch:
        return {"error": "Debes enviar almenos una forma de busqueda"}

    # 2️⃣ Transcribir todos los audios
    transcriptions = []
    conteo_palabras = []

    for file in files:
        text = audio_to_text(file)
        transcriptions.append(f"{file.filename}: {text}")
        if words_to_find:
            conteo_palabras.append(conteo_exacto_dinamico(text, words_to_find,file.filename))
        else :
            conteo_palabras.append({
                "audio": file.filename,
                "palabras": {}
            })

    if textSearch:
        # 3️⃣ Unir transcripciones
        full_text = "\n".join(transcriptions)

        # 4️⃣ Analizar texto completo
        analysis_raw = analyze_text_with_chatgpt(full_text, textSearch)
        try:
            if isinstance(analysis_raw, str):
                analysis_data = json.loads(analysis_raw)
            else:
                analysis_data = analysis_raw
        except json.JSONDecodeError:
            analysis_data = {"Error": "La IA no devolvió un formato válido"}

        mapa_busqueda = {item['nombre']: item['busqueda'] for item in analysis_data['audios']}
        for item in conteo_palabras:
            nombre = item['audio']
            item['busqueda'] = mapa_busqueda.get(nombre, {})
    else :
        for item in conteo_palabras:
            item['busqueda'] = {}
    
    # 5️⃣ Crear Excelx
    excel_path = create_analysis_excel(conteo_palabras)

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="analisis_texto.xlsx"
    )
