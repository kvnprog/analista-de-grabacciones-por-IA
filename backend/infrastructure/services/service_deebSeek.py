from fastapi import UploadFile
from openai import OpenAI
import whisper
import os, re

model_whisper = whisper.load_model("base")
client = OpenAI(
    base_url="http://host.docker.internal:11434/v1",
    api_key="ollama"  # Requerido por la librería, pero Ollama no lo valida
)

def audio_to_text(file: UploadFile):
    print("Entro")
    # asegurar puntero
    file.file.seek(0)

    temp_file = "temp_audio.wav"
    print(f"Escribiendo en: {temp_file}")
    
    with open(temp_file, "wb") as buffer:
        buffer.write(file.file.read())

    # 2. Transcribir LOCALMENTE
    result = model_whisper.transcribe(temp_file)

    # 3. Limpiar
    os.remove(temp_file)
    
    print(result["text"])
    return result["text"]

def analyze_text_with_deepseek(text: str, words: list[str]):
    print(text)
    
    response = client.chat.completions.create(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system", 
                "content": (
                    "Eres un corrector ortográfico automático. Tu única tarea es corregir palabras mal escritas. "
                    "No cambies el orden, no resumas, no añadas comentarios. Solo devuelve el texto corregido.\n\n"
                    "EJEMPLO:\n"
                    "Entrada: El busón de la vos está yeno.\n"
                    "Salida: El buzón de la voz está lleno."
                )
            },
            {
                "role": "user", 
                "content": f"Corrige la ortografía de este texto:\n{text}"
            }
        ],
        temperature=0.0
    )

    raw_response = response.choices[0].message.content
    
    print(f"Holaaaaa {raw_response}")

    clean_text = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
    count_words = count_words_exactly(clean_text, words)
    
    return count_words

def count_words_exactly(text: str, words: list[str]):
    results = {}
    text_lower = text.lower()
    
    for word in words:
        word_lower = word.lower()
        count = len(re.findall(rf'\b{word_lower}\b', text_lower))
        results[word] = count
        
    print(f"Pruebaaaaaaaaaa {results}")
    return results