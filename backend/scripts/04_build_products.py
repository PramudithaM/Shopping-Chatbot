import json  # save the products file
import random  # make the sample prices
from pathlib import Path  # file paths

from common import BACKEND_DIR, DATASETS, load_split  # helpers from common.py

OUT = BACKEND_DIR / "data" / "products.json"  # output file

# sample price range (USD) for each clothing class. The dataset has NO prices, so these are made up.
PRICE_RANGES = {
    "Dresses": (35, 160),
    "Knits": (25, 90),
    "Blouses": (25, 95),
    "Sweaters": (35, 110),
    "Pants": (30, 120),
    "Jeans": (40, 130),
    "Skirts": (25, 100),
    "Intimates": (12, 55),
    "Lounge": (20, 80),
    "Outerwear": (60, 220),
}
DEFAULT_RANGE = (20, 120)  # for any other class


def mode(series):  # most common value in a column
    series = series.dropna()
    return series.mode().iat[0] if len(series) else None


def main():
    df = load_split(DATASETS["reviews"]).to_pandas()  # reviews dataset as a table
    df = df.dropna(subset=["Clothing ID", "Rating"])  # we need an id and a rating

    products = []
    for clothing_id, g in df.groupby("Clothing ID"):  # one product = one Clothing ID
        cls = mode(g["Class Name"]) or "Other"  # Dresses, Knits, Blouses ...
        lo, hi = PRICE_RANGES.get(cls, DEFAULT_RANGE)
        price = round(random.Random(int(clothing_id)).uniform(lo, hi))  # same id -> same price every time
        products.append(
            {
                "id": int(clothing_id),
                "name": f"{cls} #{int(clothing_id)}",  # the dataset has no product names
                "department": mode(g["Department Name"]),
                "class": cls,
                "price_usd": price,  # SAMPLE price (not real)
                "avg_rating": round(float(g["Rating"].mean()), 2),
                "review_count": int(len(g)),
                "recommend_rate": round(float(g["Recommended IND"].mean()), 2) if "Recommended IND" in g else None,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)  # make sure data/ exists
    OUT.write_text(json.dumps(products, indent=1), encoding="utf-8")  # save
    print(f"Products: {len(products)}   Saved: {OUT}")

    # quick look: cheapest well-reviewed dresses
    good = [p for p in products if p["class"] == "Dresses" and p["review_count"] >= 5 and p["avg_rating"] >= 4.5]
    print("\nCheapest well-reviewed dresses (sample prices):")
    for p in sorted(good, key=lambda p: p["price_usd"])[:5]:
        print(f'  {p["name"]}  ${p["price_usd"]}  rating {p["avg_rating"]}  reviews {p["review_count"]}')


if __name__ == "__main__":  # runs only when we run this file directly
    main()