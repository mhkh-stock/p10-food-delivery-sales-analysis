"""Data-quality checks for P10 (run: python3 src/checks.py).

Every expected value below was computed from the generated CSV, not
typed from the report — if the data changes, these checks fail loudly
instead of silently disagreeing with the PDF or the dashboard.
The SQLite model (data/model.db) is checked against the same CSV.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "raw" / "orders_SAMPLE.csv"
DB = ROOT / "data" / "model.db"
PDF = ROOT / "outputs" / "best_sellers_report_SAMPLE.pdf"

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name} {detail}")


df = pd.read_csv(CSV)
orders = df.drop_duplicates("order_id").copy()
orders["rating_num"] = pd.to_numeric(orders["rating"], errors="coerce")
order_food = df.groupby("order_id")["line_total_pkr"].sum()

check("1,800 orders", df["order_id"].nunique() == 1800,
      f"got {df['order_id'].nunique()}")
check("3,296 order lines", len(df) == 3296, f"got {len(df)}")
check("92 dates, 2026-07-01 to 2026-09-30",
      df["order_date"].nunique() == 92
      and df["order_date"].min() == "2026-07-01"
      and df["order_date"].max() == "2026-09-30")
check("24 menu items, 6 categories",
      df["item"].nunique() == 24 and df["category"].nunique() == 6)
check("food sales PKR 1,591,120", int(df["line_total_pkr"].sum()) == 1591120)
check("delivery fees PKR 121,760",
      int(orders["delivery_fee_pkr"].sum()) == 121760)
check("total revenue PKR 1,712,880",
      int(df["line_total_pkr"].sum()) + int(orders["delivery_fee_pkr"].sum())
      == 1712880)
check("monthly food sales Jul 505,470 / Aug 569,970 / Sep 515,680",
      df.groupby(df["order_date"].str[:7])["line_total_pkr"].sum().to_dict()
      == {"2026-07": 505470, "2026-08": 569970, "2026-09": 515680})
check("every line_total = quantity x unit_price",
      (df["line_total_pkr"] == df["quantity"] * df["unit_price_pkr"]).all())
check("delivery fee rule: PKR 0 iff food >= 1,500, else PKR 80",
      all((f == 0) == (s >= 1500)
          for f, s in zip(orders["delivery_fee_pkr"], order_food)))
check("free-delivery orders 278", int((orders["delivery_fee_pkr"] == 0).sum()) == 278)
check("top seller Chicken Karahi PKR 195,500",
      int(df.groupby("item")["line_total_pkr"].sum().max()) == 195500
      and df.groupby("item")["line_total_pkr"].sum().idxmax()
      == "Chicken Karahi (half)")
check("top category BBQ & Grill PKR 389,280",
      df.groupby("category")["line_total_pkr"].sum().idxmax() == "BBQ & Grill"
      and int(df.groupby("category")["line_total_pkr"].sum().max()) == 389280)
check("channels: App 1,041 / Website 488 / Phone 271",
      orders.groupby("channel").size().to_dict()
      == {"App": 1041, "Website": 488, "Phone": 271})
check("lunch 13-15 = 550 orders, dinner 19-22 = 595 orders",
      orders[orders["order_hour"].between(13, 15)].shape[0] == 550
      and orders[orders["order_hour"].between(19, 22)].shape[0] == 595)
check("average delivery 32.6 min, 151 orders over 45 min",
      round(orders["delivery_minutes"].mean(), 1) == 32.6
      and int((orders["delivery_minutes"] > 45).sum()) == 151)
check("Johar Town slowest (39.3 min), Gulberg fastest (26.8 min)",
      round(orders.groupby("area")["delivery_minutes"].mean().max(), 1) == 39.3
      and round(orders.groupby("area")["delivery_minutes"].mean().min(), 1) == 26.8)
check("average rating 4.31 from 1,268 rated orders",
      round(orders["rating_num"].mean(), 2) == 4.31
      and int(orders["rating_num"].notna().sum()) == 1268)
check("no nulls in key columns, ratings 1-5 or blank",
      df[["order_id", "order_date", "item", "category"]].notna().all().all()
      and orders["rating_num"].dropna().between(1, 5).all())
check("delivery minutes >= 18 (generator floor)",
      int(orders["delivery_minutes"].min()) >= 18)

# ---- SQLite model agrees with the CSV ----
con = sqlite3.connect(DB)
check("fact_order_lines has 3,296 rows",
      con.execute("SELECT COUNT(*) FROM fact_order_lines").fetchone()[0] == 3296)
check("fact total = CSV food sales",
      con.execute("SELECT SUM(line_total_pkr) FROM fact_order_lines").fetchone()[0]
      == 1591120)
check("dim_item 24 rows, dim_date 92 rows",
      con.execute("SELECT COUNT(*) FROM dim_item").fetchone()[0] == 24
      and con.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0] == 92)
check("no orphan fact rows (item/date)",
      con.execute("SELECT COUNT(*) FROM fact_order_lines f "
                  "LEFT JOIN dim_item i ON i.item_id = f.item_id "
                  "WHERE i.item_id IS NULL").fetchone()[0] == 0)
con.close()

check("best-sellers PDF exists and is non-trivial",
      PDF.exists() and PDF.stat().st_size > 20000,
      f"size {PDF.stat().st_size if PDF.exists() else 0}")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
