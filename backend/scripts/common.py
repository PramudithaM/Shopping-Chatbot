import json  # save chunks as json lines
import re  # regex, used for cleaning text
from pathlib import Path  # file paths

from datasets import Dataset, DatasetDict, load_dataset  # Hugging Face datasets
from langchain_core.documents import Document  # LangChain text + metadata container
from langchain_text_splitters import RecursiveCharacterTextSplitter  # cuts long text into chunks

# the two Hugging Face datasets we use
DATASETS = {
    "support": "NebulaByte/E-Commerce_Customer_Support_Conversations",
    "reviews": "Censius-AI/ECommerce-Women-Clothing-Reviews",
}

BACKEND_DIR = Path(__file__).resolve().parent.parent  # path of backend folder
SAMPLES_DIR = BACKEND_DIR / "data" / "samples"  # Day 1 output folder
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"  # Day 2 output folder


def load_split(repo_id: str) -> Dataset:  # download a dataset and return its main split
    ds = load_dataset(repo_id)  # downloads on first run, then uses cache
    if isinstance(ds, DatasetDict):  # dataset has splits (train / test ...)
        key = "train" if "train" in ds else list(ds.keys())[0]  # prefer "train"
        return ds[key]
    return ds


def clean_text(value) -> str:  # tidy one piece of text
    if value is None:  # missing value
        return ""
    text = str(value).replace("\r", "")  # remove windows line endings
    text = re.sub(r"[ \t]+", " ", text)  # many spaces/tabs -> one space
    text = re.sub(r"\n{3,}", "\n\n", text)  # many blank lines -> one blank line
    return text.strip()  # remove spaces at start and end


def detect_text_column(ds: Dataset, sample_size: int = 200) -> str:  # find the main text column
    best_col, best_len = None, -1.0  # best column so far and its average length
    n = min(sample_size, len(ds))  # check only the first rows
    for col in ds.column_names:  # go through every column
        lengths = []
        for i in range(n):
            v = ds[i][col]
            if isinstance(v, str):  # only text values count
                lengths.append(len(v))
        if lengths and len(lengths) >= n * 0.3:  # column must be text in most rows
            avg = sum(lengths) / len(lengths)  # average text length
            if avg > best_len:  # longest text wins
                best_col, best_len = col, avg
    if best_col is None:
        raise ValueError("Could not find a text column. Pass the column name manually.")
    return best_col


def build_documents(
    ds: Dataset,
    source: str,  # "support" or "reviews"
    text_col: str,  # the main text column
    max_rows: int | None = None,  # limit rows while developing
    min_chars: int = 20,  # skip very short texts
) -> list[Document]:
    docs: list[Document] = []
    seen: set[str] = set()  # to detect duplicates

    for i, row in enumerate(ds):  # go through every row
        if max_rows is not None and i >= max_rows:  # stop at the limit
            break

        text = clean_text(row.get(text_col))  # clean the main text
        if len(text) < min_chars:  # too short, skip
            continue
        if text in seen:  # duplicate, skip
            continue
        seen.add(text)

        meta = {"source": source, "row_id": i}  # extra info stored with the text
        for col, val in row.items():  # other columns become metadata
            if col == text_col or val is None:
                continue
            if isinstance(val, (int, float, bool)):  # numbers and booleans are fine
                meta[col] = val
            elif isinstance(val, str) and 0 < len(val) <= 100:  # only short strings
                meta[col] = val.strip()

        docs.append(Document(page_content=text, metadata=meta))  # text + metadata
    return docs


def chunk_documents(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # max characters per chunk
        chunk_overlap=chunk_overlap,  # characters shared between neighbour chunks
    )
    chunks = splitter.split_documents(docs)  # cut every document into chunks

    counters: dict[int, int] = {}  # chunk counter for each row
    for c in chunks:
        rid = c.metadata["row_id"]
        counters[rid] = counters.get(rid, 0) + 1
        c.metadata["chunk_id"] = counters[rid] - 1  # 0, 1, 2 ... inside the row
    return chunks


def save_jsonl(chunks: list[Document], path: Path) -> None:  # save chunks, one JSON per line
    path.parent.mkdir(parents=True, exist_ok=True)  # create the folder if missing
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            m = c.metadata
            rec = {
                "id": f'{m["source"]}-{m["row_id"]}-{m["chunk_id"]}',  # unique id
                "text": c.page_content,
                "metadata": m,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")  # one line per chunk