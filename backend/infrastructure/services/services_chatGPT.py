# services/services_chatGPT.py
from infrastructure.core.config import client
from fastapi import UploadFile
import re

import subprocess
import uuid
import os

def audio_to_text(file: UploadFile):
    file.file.seek(0)
    audio_bytes = file.file.read()

    print("Nombre:", file.filename)
    print("Tipo:", file.content_type)
    print("Size:", len(audio_bytes))

    if len(audio_bytes) == 0:
        raise Exception("Archivo vacío")

    # nombres únicos
    input_path = f"/tmp/{uuid.uuid4()}"
    output_path = f"{input_path}.wav"

    # guardar archivo original
    with open(input_path, "wb") as f:
        f.write(audio_bytes)

    # convertir a WAV
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",      # sample rate recomendado
        "-ac", "1",          # mono
        output_path
    ], check=True)

    # leer WAV convertido
    with open(output_path, "rb") as f:
        converted_audio = f.read()

    # limpiar archivos temporales
    os.remove(input_path)
    os.remove(output_path)

    # enviar a OpenAI
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", converted_audio, "audio/wav"),
        model="gpt-4o-transcribe"
    )

    return transcription.text


def text_from_txt(file: UploadFile):
    """
    Lee un archivo .txt y regresa su contenido como texto plano.
    No pasa por transcripción, solo decodifica el contenido.
    """
    file.file.seek(0)
    raw_bytes = file.file.read()

    if not raw_bytes or len(raw_bytes) == 0:
        raise Exception("Archivo vacío")

    # Intenta utf-8 primero, si falla usa latin-1 como respaldo
    # (algunos .txt exportados desde Windows vienen en otra codificación)
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1")

    text = text.strip()

    if not text:
        raise Exception("El archivo de texto está vacío")

    return text


def get_text_from_file(file: UploadFile, tipo_entrada: str):
    """
    Punto único de entrada: decide si transcribe audio o lee texto plano,
    según el tipo de entrada que mandó el frontend.
    """
    if tipo_entrada == "texto":
        return text_from_txt(file)
    else:
        return audio_to_text(file)


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

def analyze_emotions_with_chatgpt(text: str):
    """
    Analiza emociones de una llamada, intentando separar bot/agente vs cliente.
    Al no haber diarización real (separación de audio por voz), el modelo infiere
    los turnos de habla por contexto conversacional. Incluye un nivel de confianza
    para que se pueda distinguir qué resultados son más confiables.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                    Eres un analista de emociones especializado en llamadas de servicio al cliente.
                    Recibirás la transcripción de una llamada SIN etiquetas de quién habla.
                    Debes inferir, basándote en el contexto (saludos formales, resolución de problemas,
                    quejas, preguntas, tono de las frases), qué partes corresponden al agente/bot
                    y cuáles al cliente.

                    Tu única salida debe ser un objeto JSON válido con esta estructura exacta:
                    {
                        "bot": {
                            "emocion": "una palabra: neutral, amable, frustrado, molesto, empatico, etc.",
                            "detalle": "breve justificación de por qué se detectó esa emoción"
                        },
                        "cliente": {
                            "emocion": "una palabra: satisfecho, molesto, frustrado, neutral, enojado, confundido, etc.",
                            "detalle": "breve justificación de por qué se detectó esa emoción"
                        },
                        "confianza": "alta, media o baja - qué tan clara fue la separación entre hablantes"
                    }
                    No incluyas texto adicional, solo el JSON.
                """
            },
            {
                "role": "user",
                "content": f"Transcripción de la llamada:\n{text}"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    return response.choices[0].message.content

def analyze_multiple_questions_with_chatgpt(text: str, questions: list[str]):
    """
    Responde varias preguntas sobre una sola transcripción en una sola llamada a la IA,
    en lugar de una llamada por pregunta (más rápido y más barato).
    """
    preguntas_texto = "\n".join(f"- {q}" for q in questions)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                    Eres un analista de datos. Recibirás una transcripción y una lista de preguntas.
                    Responde cada pregunta basándote únicamente en la información de la transcripción.
                    Si la transcripción no tiene información suficiente para responder alguna pregunta,
                    responde exactamente "No se encontró información suficiente" para esa pregunta.

                    Tu única salida debe ser un objeto JSON válido con esta estructura exacta:
                    {
                        "respuestas": [
                            {"pregunta": "texto exacto de la pregunta", "respuesta": "respuesta breve y concreta"}
                        ]
                    }
                    Debes incluir TODAS las preguntas recibidas, en el mismo orden, una entrada por cada una.
                    No incluyas texto adicional, solo el JSON.
                """
            },
            {
                "role": "user",
                "content": f"Preguntas:\n{preguntas_texto}\n\nTranscripción:\n{text}"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    return response.choices[0].message.content