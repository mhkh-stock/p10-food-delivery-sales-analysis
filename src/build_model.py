"""P10 — Food-Delivery Sales Analysis: seeded SAMPLE data generator + star-schema loader.

Generates 1,800 food-delivery orders (Jul-Sep 2026) for the fictional
"Lahore Food Co" restaurant, then loads them into a star-schema SQLite
model (fact_order_lines + dimensions) and writes Power BI-ready CSVs.

Deterministic: seed 10 — re-running reproduces the identical files.
SAMPLE data only: fictional restaurant, realistic PKR prices, no real
orders, no real customers, no payment details.

Run:  python3 src/build_model.py
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "orders_SAMPLE.csv"
DB = ROOT / "data" / "model.db"
PROCESSED = ROOT / "data" / "processed"
SEED = 10

# (item, category, price PKR, popularity weight)
MENU = [
    ("Chicken Biryani", "Biryani", 350, 14),
    ("Beef Biryani", "Biryani", 450, 9),
    ("Sindhi Biryani", "Biryani", 400, 7),
    ("Veg Biryani", "Biryani", 280, 3),
    ("Chicken Tikka", "BBQ & Grill", 420, 10),
    ("Seekh Kabab (4 pc)", "BBQ & Grill", 480, 8),
    ("Malai Boti", "BBQ & Grill", 550, 6),
    ("Beef Kabab", "BBQ & Grill", 520, 5),
    ("Zinger Burger", "Fast Food", 450, 11),
    ("Beef Burger", "Fast Food", 520, 7),
    ("Chicken Shawarma", "Fast Food", 300, 9),
    ("Fries (Large)", "Fast Food", 250, 6),
    ("Chicken Karahi (half)", "Desi Curries", 850, 8),
    ("Daal Fry", "Desi Curries", 280, 4),
    ("Palak Paneer", "Desi Curries", 420, 3),
    ("Nihari", "Desi Curries", 650, 6),
    ("Mint Margarita", "Beverages", 200, 8),
    ("Sweet Lassi", "Beverages", 180, 7),
    ("Soft Drink", "Beverages", 120, 9),
    ("Green Tea", "Beverages", 150, 3),
    ("Gulab Jamun (2 pc)", "Desserts", 150, 6),
    ("Kheer", "Desserts", 180, 5),
    ("Rasmalai", "Desserts", 220, 4),
    ("Brownie", "Desserts", 250, 3),
]

AREAS = ["Gulberg", "DHA", "Model Town", "Johar Town", "Cantt", "Township"]
AREA_W = [22, 24, 16, 14, 12, 12]
# Typical delivery minutes by area (base), before random variation.
AREA_MINUTES = {"Gulberg": 26, "DHA": 34, "Model Town": 30,
                "Johar Town": 38, "Cantt": 29, "Township": 36}
CHANNELS = ["App", "Website", "Phone"]
CHANNEL_W = [58, 27, 15]
PAYMENTS = ["COD", "Card", "Wallet"]
PAYMENT_W = [55, 30, 15]

START = date(2026, 7, 1)
DAYS = 92  # 1 Jul – 30 Sep 2026
N_ORDERS = 1800


def peak_hour(rng):
    """Order hour: lunch peak 13-15, dinner peak 19-22, thin otherwise."""
    r = rng.random()
    if r < 0.30:
        return rng.choice([13, 14, 15])
    if r < 0.62:
        return rng.choice([19, 20, 21, 22])
    if r < 0.75:
        return rng.choice([12, 16, 17, 18])
    if r < 0.85:
        return rng.choice([11, 23])
    return rng.choice([9, 10, 0, 1])


def main():
    rng = random.Random(SEED)
    items = [m[0] for m in MENU]
    weights = [m[3] for m in MENU]
    price_of = {m[0]: m[2] for m in MENU}
    cat_of = {m[0]: m[1] for m in MENU}

    lines = []
    # Exactly N_ORDERS order dates: Fri–Sun weighted heavier (weekend uplift),
    # then sorted so order numbers run in date order.
    all_days = [START + timedelta(days=i) for i in range(DAYS)]
    day_w = [1.25 if d.weekday() in (4, 5, 6) else 1.0 for d in all_days]
    order_dates = sorted(rng.choices(all_days, day_w, k=N_ORDERS))
    for order_no, d in enumerate(order_dates, start=1):
        area = rng.choices(AREAS, AREA_W)[0]
        channel = rng.choices(CHANNELS, CHANNEL_W)[0]
        payment = rng.choices(PAYMENTS, PAYMENT_W)[0]
        hour = peak_hour(rng)
        minute = rng.randint(0, 59)
        n_lines = rng.choices([1, 2, 3, 4], [45, 32, 16, 7])[0]
        chosen = rng.choices(items, weights, k=n_lines)
        delivery = max(18, int(rng.gauss(AREA_MINUTES[area], 7)))
        if rng.random() < 0.05:  # occasional slow outlier
            delivery += rng.randint(15, 35)
        rated = rng.random() < 0.70
        rating = rng.choices([5, 4, 3, 2, 1], [55, 28, 10, 4, 3])[0] if rated else None
        subtotal = 0
        for item in chosen:
            qty = rng.choices([1, 2, 3], [78, 17, 5])[0]
            unit = price_of[item]
            subtotal += qty * unit
            lines.append({
                "order_id": f"LFC-{order_no:05d}",
                "order_date": d.isoformat(),
                "order_hour": hour,
                "order_minute": minute,
                "area": area,
                "channel": channel,
                "payment_method": payment,
                "item": item,
                "category": cat_of[item],
                "quantity": qty,
                "unit_price_pkr": unit,
                "line_total_pkr": qty * unit,
                "delivery_fee_pkr": 0,  # filled below, once per order
                "delivery_minutes": delivery,
                "rating": rating if rating is not None else "",
            })
        fee = 0 if subtotal >= 1500 else 80
        for ln in lines:
            if ln["order_id"] == f"LFC-{order_no:05d}":
                ln["delivery_fee_pkr"] = fee

    df = pd.DataFrame(lines)
    df = df.sort_values(["order_date", "order_id"]).reset_index(drop=True)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW, index=False)

    # ---- star schema ----
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript(Path(ROOT / "sql" / "schema.sql").read_text())
    items_df = pd.DataFrame(
        [{"item_id": i + 1, "item": m[0], "category": m[1], "unit_price_pkr": m[2]}
         for i, m in enumerate(MENU)])
    items_df.to_sql("dim_item", con, if_exists="append", index=False)
    fact = df.rename(columns={
        "order_id": "order_id", "order_date": "date_id",
        "order_hour": "order_hour", "area": "area", "channel": "channel",
        "payment_method": "payment_method", "item": "item",
        "category": "category", "quantity": "quantity",
        "unit_price_pkr": "unit_price_pkr",
        "line_total_pkr": "line_total_pkr",
        "delivery_fee_pkr": "delivery_fee_pkr",
        "delivery_minutes": "delivery_minutes",
        "rating": "rating",
    })
    fact["item_id"] = fact["item"].map(
        {m[0]: i + 1 for i, m in enumerate(MENU)})
    fact = fact[["order_id", "date_id", "order_hour", "area", "channel",
                 "payment_method", "item_id", "quantity", "unit_price_pkr",
                 "line_total_pkr", "delivery_fee_pkr", "delivery_minutes",
                 "rating"]]
    fact.to_sql("fact_order_lines", con, if_exists="append", index=False)

    dates = pd.DataFrame({"date_id": sorted(df["order_date"].unique())})
    dates["month"] = dates["date_id"].str[:7]
    dates["weekday"] = pd.to_datetime(dates["date_id"]).dt.day_name()
    dates.to_sql("dim_date", con, if_exists="append", index=False)
    con.commit()

    # ---- Power BI-ready CSVs ----
    PROCESSED.mkdir(parents=True, exist_ok=True)
    for name, query in {
        "fact_order_lines": "SELECT * FROM fact_order_lines",
        "dim_item": "SELECT * FROM dim_item",
        "dim_date": "SELECT * FROM dim_date",
    }.items():
        pd.read_sql(query, con).to_csv(PROCESSED / f"{name}.csv", index=False)
    con.close()

    n_orders = df["order_id"].nunique()
    gross = int(df["line_total_pkr"].sum())
    fees = int(df.drop_duplicates("order_id")["delivery_fee_pkr"].sum())
    print(f"orders: {n_orders}")
    print(f"order lines: {len(df)}")
    print(f"food sales (lines): PKR {gross:,}")
    print(f"delivery fees: PKR {fees:,}")
    print(f"total revenue: PKR {gross + fees:,}")
    print(f"date range: {df['order_date'].min()} to {df['order_date'].max()}")
    print(f"avg delivery: {df.drop_duplicates('order_id')['delivery_minutes'].mean():.1f} min")


if __name__ == "__main__":
    main()
