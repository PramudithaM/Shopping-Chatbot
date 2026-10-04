import argparse  # read options from the command line

from common import (  # helper functions from common.py
    DATASETS,
    PROCESSED_DIR,
    build_documents,
    chunk_documents,
    detect_text_column,
    load_split,
    save_jsonl,
)

# chunk settings for each dataset
SETTINGS = {
    "support": {"chunk_size": 800, "chunk_overlap": 100},  # long conversations -> bigger chunks
    "reviews": {"chunk_size": 500, "chunk_overlap": 50},  # short reviews -> smaller chunks
}


def main():
    parser = argparse.ArgumentParser()  # command line options
    parser.add_argument("--support-col", default=None)  # main text column of support dataset
    parser.add_argument("--reviews-col", default=None)  # main text column of reviews dataset
    parser.add_argument("--max-rows", type=int, default=5000)  # limit rows while developing
    args = parser.parse_args()
    overrides = {"support": args.support_col, "reviews": args.reviews_col}

    for name, repo in DATASETS.items():  # go through both datasets
        print("\n" + "=" * 70)
        print(f"{name.upper()}  ->  {repo}")
        print("=" * 70)

        ds = load_split(repo)  # load the dataset (from cache now)
        text_col = overrides[name] or detect_text_column(ds)  # manual column, or auto-detect
        print(f"Main text column : {text_col}")

        docs = build_documents(ds, source=name, text_col=text_col, max_rows=args.max_rows)  # clean + remove duplicates
        print(f"Clean documents  : {len(docs)}")

        chunks = chunk_documents(docs, **SETTINGS[name])  # cut into chunks
        avg = sum(len(c.page_content) for c in chunks) / max(len(chunks), 1)  # average chunk length
        print(f"Chunks           : {len(chunks)}   (average length: {avg:.0f} characters)")

        if chunks:  # show one example chunk
            print("\nSample chunk:")
            print("-" * 40)
            print(chunks[0].page_content[:500])
            print("-" * 40)
            print("metadata:", chunks[0].metadata)

        out = PROCESSED_DIR / f"{name}_chunks.jsonl"  # data/processed/<name>_chunks.jsonl
        save_jsonl(chunks, out)  # save to disk
        print(f"\nSaved: {out}")


if __name__ == "__main__":  # runs only when we run this file directly
    main()