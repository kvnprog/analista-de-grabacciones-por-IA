# core/config.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("🔑 OPENAI_API_KEY cargada:", "SÍ" if api_key else "NO")

client = OpenAI(
    api_key=api_key
)
