-- P10 — Food-Delivery Sales Analysis: star-schema DDL.
-- Loads into SQLite as-is (data/model.db). PostgreSQL-ready: only the
-- type names differ (INTEGER/TEXT/REAL are valid in both).
-- Grain: one row per order line. Delivery fee repeats per line of an
-- order by design (it is an order-level charge); order-level totals
-- must use DISTINCT order_id, never SUM over lines. See checks.py.

CREATE TABLE dim_item (
    item_id        INTEGER PRIMARY KEY,
    item           TEXT NOT NULL,
    category       TEXT NOT NULL,
    unit_price_pkr INTEGER NOT NULL
);

CREATE TABLE dim_date (
    date_id  TEXT PRIMARY KEY,  -- YYYY-MM-DD
    month    TEXT NOT NULL,     -- YYYY-MM
    weekday  TEXT NOT NULL
);

CREATE TABLE fact_order_lines (
    order_id           TEXT NOT NULL,
    date_id            TEXT NOT NULL REFERENCES dim_date(date_id),
    order_hour         INTEGER NOT NULL,
    area               TEXT NOT NULL,
    channel            TEXT NOT NULL,
    payment_method     TEXT NOT NULL,
    item_id            INTEGER NOT NULL REFERENCES dim_item(item_id),
    quantity           INTEGER NOT NULL,
    unit_price_pkr     INTEGER NOT NULL,
    line_total_pkr     INTEGER NOT NULL,
    delivery_fee_pkr   INTEGER NOT NULL,
    delivery_minutes   INTEGER NOT NULL,
    rating             TEXT
);
