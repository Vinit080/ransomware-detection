import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    # 32-byte key for AES-256
    TELEMETRY_AES_KEY = bytes.fromhex(os.getenv("TELEMETRY_AES_KEY", "0" * 64))

settings = Settings()
