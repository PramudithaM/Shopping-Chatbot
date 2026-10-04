import json  # read the chunk files
import sys  # to edit the python search path
from pathlib import Path  # file paths

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # let this script import the "app" package

from app.config import PROCESSED_DIR  # folder with the Day 2 chunk files
from app.vectorstores import get_store  # gives us a ChromaDB collection

BATCH = 256  # how many chunks to embed at once


def build(name: str) -> None:  # name = "support" or "reviews"
    path = PROCESSED_DIR / f"{name}_chunks.jsonl"  # the chunk file for this collection
    if not path.exists():  # stop if Day 2 was not run
        print(f"!! {path} not found. Run 02_prepare_chunks.py first.")
        return

    # read the file: one JSON record per line
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"\n{name}: embedding {len(records)} chunks...")

    store = get_store(name)  # open the collection
    store.delete_collection()  # remove old data so we can rebuild cleanly
    store = get_store(name)  # create the collection again (empty)

    for i in range(0, len(records), BATCH):  # go through the chunks in batches
        batch = records[i : i + BATCH]  # current batch
        store.add_texts(
            texts=[r["text"] for r in batch],  # the text to embed
            metadatas=[r["metadata"] for r in batch],  # extra info (rating, category...)
            ids=[r["id"] for r in batch],  # unique id for each chunk
        )
        print(f"  {min(i + BATCH, len(records))}/{len(records)}")  # progress


if __name__ == "__main__":  # runs only when we run this file directly
    for collection in ("support", "reviews"):  # build both collections
        build(collection)
    print("\nDone. Saved in data/chroma/")