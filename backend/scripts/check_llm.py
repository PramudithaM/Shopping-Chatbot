import sys  # to edit the python search path
from pathlib import Path  # file paths

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # let this script import the "app" package

from app.config import GEMINI_API_KEY, GEMINI_MODEL, LLM_PROVIDER, OPENAI_MODEL  # settings from .env
from app.rag import make_llm  # the same LLM the chatbot uses

print("Provider :", LLM_PROVIDER)  # openai or gemini
print("Model    :", GEMINI_MODEL if LLM_PROVIDER == "gemini" else OPENAI_MODEL)  # model name in use

if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:  # key missing in .env
    print("FAILED: no GOOGLE_API_KEY / GEMINI_API_KEY found in .env")
    sys.exit(1)

try:
    reply = make_llm().invoke("Reply with exactly one word: OK")  # send one tiny test message
    print("Key works! Model replied:", reply.text)  # success
except Exception as e:  # wrong key, wrong model, no credits, rate limit...
    print("FAILED:", type(e).__name__)
    print(str(e)[:500])  # first part of the error message
    