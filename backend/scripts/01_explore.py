import json  # to print and save rows as JSON

from common import DATASETS, SAMPLES_DIR, load_split  # helpers from common.py


def short(value, limit=300):  # cut very long text so the output stays readable
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + " ...[truncated]"
    return value


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)  # make sure data/samples exists

    for name, repo in DATASETS.items():  # go through both datasets
        print("\n" + "=" * 70)
        print(f"{name.upper()}  ->  {repo}")
        print("=" * 70)

        try:
            ds = load_split(repo)  # download the dataset (cached after first time)
        except Exception as e:  # network error, wrong name, etc.
            print(f"!! Download failed: {e}")
            continue

        print(f"Rows    : {len(ds)}")  # how many rows
        print(f"Columns : {ds.column_names}")  # column names
        print(f"Types   : {ds.features}")  # type of each column

        print("\nFirst 2 rows:")
        for i in range(min(2, len(ds))):
            row = {k: short(v) for k, v in ds[i].items()}  # shorten long text values
            print(json.dumps(row, indent=2, ensure_ascii=False, default=str))

        sample = [ds[i] for i in range(min(5, len(ds)))]  # first 5 rows
        out = SAMPLES_DIR / f"{name}_sample.json"  # data/samples/<name>_sample.json
        out.write_text(json.dumps(sample, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(f"\nSample saved: {out}")


if __name__ == "__main__":  # runs only when we run this file directly
    main()