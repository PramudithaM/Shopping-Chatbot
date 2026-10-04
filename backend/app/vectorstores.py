from functools import lru_cache  # cache a function result so it runs only once

from langchain_chroma import Chroma  # ChromaDB wrapper (vector database)
from langchain_huggingface import HuggingFaceEmbeddings  # Hugging Face text-to-numbers model

from app.config import CHROMA_DIR, EMBEDDING_MODEL  # settings from config.py


@lru_cache(maxsize=1)  # load the model only once, reuse it every time after
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)  # downloads the model on first run


def get_store(collection: str) -> Chroma:  # collection = "support" or "reviews"
    return Chroma(
        collection_name=collection,  # name of the collection inside ChromaDB
        embedding_function=get_embeddings(),  # model that converts text to numbers
        persist_directory=CHROMA_DIR,  # folder where the data is saved on disk
    )