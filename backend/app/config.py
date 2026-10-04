import os  # load built in os
from pathlib import Path  # load files path

from dotenv import load_dotenv  # read the .env file

load_dotenv()  # load env file

BACKEND_DIR = Path(__file__).resolve().parent.parent  # path of backend folder
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"  # chunks saving folder
CHROMA_DIR = str(BACKEND_DIR / "data" / "chroma")  # vector DB (ChromaDB) saving folder

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Hugging Face model: text -> numerical values

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # default LLM: "gemini" or "openai"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI key
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")  # OpenAI model name

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")  # Google AI Studio key (either name works)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")  # Gemini model name

AVAILABLE_PROVIDERS = [  # LLMs that have a key in .env (shown as buttons in the UI)
    name for name, key in (("gemini", GEMINI_API_KEY), ("openai", OPENAI_API_KEY)) if key
]

FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]  # React CORS