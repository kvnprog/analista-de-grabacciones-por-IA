# services/services_chatGPT.py
from infrastructure.core.config import client
from fastapi import UploadFile
import re

def audio_to_text(file: UploadFile):
    # asegurar puntero
    file.file.seek(0)

    transcription = client.audio.transcriptions.create(
        file=(file.filename, file.file, file.content_type),
        model="gpt-4o-transcribe"
    )

    return transcription.text

def analyze_text_with_chatgpt(text: str, textSearch: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                    Eres un analista de datos. Tu única salida debe ser un objeto JSON válido.
                    Estructura requerida:
                    {
                    "audios": [
                        {
                            "nombre": "nombre_del_archivo",
                            "busqueda": {
                                "texto": "instruccion_de_busqueda", 
                                "detalle": "Resultado (Si/No y por qué)"
                            }
                        }
                    ]
                    }
                    No incluyas texto adicional, solo el JSON.
                """
            },
            {
                "role": "user",
                "content": f"""
                    Analiza la siguiente transcripción basándote en esta instrucción específica: "{textSearch}"
                    Transcripción: {text}
                    
                    Importante: En 'detalle', explica brevemente si se cumplió la búsqueda específica.
                """
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    return response.choices[0].message.content

def conteo_exacto_dinamico(texto_transcrito, lista_palabras, file_name):
    """
    Busca cualquier palabra que el usuario haya mandado, 
    sin importar si cambian en cada petición.
    """
    resultados = {
        "audio": file_name,
        "palabras": {}
    }
    # Limpiamos el texto de puntos y comas para que no estorben
    texto_limpio = re.sub(r'[^\w\s]', '', texto_transcrito.lower())
    
    for palabra in lista_palabras:
        p_search = palabra.strip().lower()
        # Buscamos la palabra exacta
        matches = re.findall(rf'\b{p_search}\b', texto_limpio)
        resultados["palabras"][palabra] = len(matches)
        
    return resultados



