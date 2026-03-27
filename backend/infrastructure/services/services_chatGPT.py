# services/services_chatGPT.py
from infrastructure.core.config import client
from fastapi import UploadFile

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

def analyze_text_with_chatgpt(text: str, words: list[str]):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Devuelve únicamente JSON válido. No texto adicional."
            },
            {
                "role": "user",
                "content": f"""
Cuenta cuántas veces aparece cada palabra en el texto.

Palabras: {words}

Texto:
{text}
"""
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    return response.choices[0].message.content




