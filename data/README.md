# P10 — Data dictionary

**Source:** generated SAMPLE data (`src/build_model.py`, seed 10) for
the fictional "Lahore Food Co" restaurant. 1,800 orders, 1 Jul – 30 Sep
2026, 24 menu items in 6 categories, 6 Lahore areas, 3 channels.
No real restaurant, no real customers, no payment details.

## `data/raw/orders_SAMPLE.csv` — one row per order line (3,296 rows)

| Column | Type | Meaning |
|---|---|---|
| order_id | text | `LFC-00001` … `LFC-01800`, one per order |
| order_date | date | YYYY-MM-DD, 2026-07-01 → 2026-09-30 |
| order_hour | int | Hour of day (0–23); lunch/dinner peaks built in |
| order_minute | int | Minute of the hour |
| area | text | Gulberg, DHA, Model Town, Johar Town, Cantt, Township |
| channel | text | App, Website, Phone |
| payment_method | text | COD, Card, Wallet |
| item | text | Menu item name |
| category | text | Biryani, BBQ & Grill, Fast Food, Desi Curries, Beverages, Desserts |
| quantity | int | Units of this item on the order (1–3) |
| unit_price_pkr | int | Menu price in PKR |
| line_total_pkr | int | quantity × unit_price_pkr |
| delivery_fee_pkr | int | PKR 80 per order, PKR 0 when the order's food ≥ PKR 1,500 (repeated on every line of the order — order-level totals must use DISTINCT order_id) |
| delivery_minutes | int | Order-level delivery time; area-based base + variation, occasional slow outlier |
| rating | int/blank | 1–5 when the order was rated (70% of orders), blank otherwise |

## `data/model.db` — SQLite star schema (`sql/schema.sql`)

- `fact_order_lines` — the CSV above, plus `item_id` (FK to dim_item).
- `dim_item` — 24 rows: item_id, item, category, unit_price_pkr.
- `dim_date` — 92 rows: date_id, month (YYYY-MM), weekday name.

## `data/processed/*.csv` — Power BI-ready exports of the three tables.

## Rules baked into the data

- Delivery fee and delivery minutes are **order-level** facts stored
  per line: never `SUM(delivery_fee_pkr)` over lines (see the DAX
  comment in `dax/measures.dax`).
- Weekend days (Fri–Sun) carry slightly more orders than weekdays.
- Prices are realistic PKR menu ranges, not real prices.
