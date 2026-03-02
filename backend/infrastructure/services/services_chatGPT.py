# services/services_chatGPT.py
from infrastructure.core.config import client
from fastapi import UploadFile

def audio_to_text(file: UploadFile):
    # asegurar puntero
    file.file.seek(0)

    transcription = client.audio.transcriptions.create(
        file=(file.filename, file.file, file.content_type),
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




