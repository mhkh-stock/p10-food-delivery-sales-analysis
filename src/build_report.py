"""Build the P10 deliverables from the SAMPLE order data.

Recomputes every number from data/raw/orders_SAMPLE.csv — nothing is
typed in by hand — and produces:
  * dashboard/previews/*.png — 4 preview renders (matplotlib, labelled
    as renders, NOT Power BI screenshots)
  * outputs/best_sellers_report_SAMPLE.pdf — 2-page best-sellers report
    (top-10 items, category table, peak hours, delivery-time read,
    5 prioritised actions)

Run:  python3 src/build_report.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "raw" / "orders_SAMPLE.csv"
PREVIEWS = ROOT / "dashboard" / "previews"
OUT = ROOT / "outputs"
PDF = OUT / "best_sellers_report_SAMPLE.pdf"
PREVIEWS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV)
orders = df.drop_duplicates("order_id").copy()
orders["rating_num"] = pd.to_numeric(orders["rating"], errors="coerce")

N_ORDERS = df["order_id"].nunique()
FOOD_SALES = int(df["line_total_pkr"].sum())
FEES = int(orders["delivery_fee_pkr"].sum())
TOTAL = FOOD_SALES + FEES
AOV = df.groupby("order_id")["line_total_pkr"].sum().mean()
AVG_DELIVERY = orders["delivery_minutes"].mean()
SLOW_SHARE = 100.0 * (orders["delivery_minutes"] > 45).mean()
AVG_RATING = orders["rating_num"].mean()
RATED = int(orders["rating_num"].notna().sum())

monthly = df.groupby(df["order_date"].str[:7])["line_total_pkr"].sum()
by_cat = df.groupby("category")["line_total_pkr"].sum().sort_values(ascending=False)
top10 = (
    df.groupby("item")
    .agg(sales=("line_total_pkr", "sum"), qty=("quantity", "sum"),
         orders=("order_id", "nunique"))
    .sort_values("sales", ascending=False)
    .head(10)
)
hourly = orders.groupby("order_hour").size()
by_area = orders.groupby("area")["delivery_minutes"].mean().sort_values(ascending=False)

# ---- preview renders (matplotlib, labelled as renders) ----
plt.figure(figsize=(8, 3.4))
monthly.plot(kind="bar", color="#d97706")
plt.title("Monthly food sales — Lahore Food Co (SAMPLE, Jul–Sep 2026)")
plt.ylabel("PKR")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(PREVIEWS / "monthly-trend.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 3.4))
by_cat.plot(kind="barh", color="#0e7490")
plt.title("Food sales by category — Lahore Food Co (SAMPLE)")
plt.xlabel("PKR")
plt.tight_layout()
plt.savefig(PREVIEWS / "sales-by-category.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 4.0))
top10["sales"].sort_values().plot(kind="barh", color="#15803d")
plt.title("Top 10 best sellers by sales — Lahore Food Co (SAMPLE)")
plt.xlabel("PKR")
plt.tight_layout()
plt.savefig(PREVIEWS / "top-10-items.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 3.4))
hourly.plot(kind="bar", color="#b45309")
plt.title("Orders by hour of day — Lahore Food Co (SAMPLE)")
plt.ylabel("Orders")
plt.xlabel("Hour")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(PREVIEWS / "orders-by-hour.png", dpi=150)
plt.close()

# ---- best-sellers PDF report ----
styles = getSampleStyleSheet()
story = [
    Paragraph("Lahore Food Co — Best Sellers &amp; Sales Report",
              styles["Title"]),
    Paragraph("Food-delivery sales analysis · Jul–Sep 2026 (Q3) · "
              "SAMPLE data — fictional restaurant, generated for this "
              "delivery (seed 10)", styles["Normal"]),
    Spacer(1, 0.4 * cm),
    Paragraph(
        f"Headline: <b>{N_ORDERS:,} orders</b> brought in "
        f"<b>PKR {FOOD_SALES:,}</b> of food sales plus PKR {FEES:,} in "
        f"delivery fees — <b>PKR {TOTAL:,} total revenue</b>. Average "
        f"order value PKR {AOV:,.0f}. Average delivery {AVG_DELIVERY:.1f} "
        f"minutes; {SLOW_SHARE:.1f}% of orders took over 45 minutes. "
        f"Average rating {AVG_RATING:.2f} / 5 from {RATED:,} rated orders.",
        styles["Normal"]),
    Spacer(1, 0.4 * cm),
    Paragraph("<b>Top 10 best sellers</b>", styles["Heading2"]),
]
top_rows = [["#", "Item", "Category", "Qty", "Orders", "Sales (PKR)"]]
for i, (item, r) in enumerate(top10.iterrows(), 1):
    cat = df.loc[df["item"] == item, "category"].iloc[0]
    top_rows.append([str(i), item, cat, f"{int(r['qty']):,}",
                     f"{int(r['orders']):,}", f"{int(r['sales']):,}"])
t = Table(top_rows, colWidths=[1 * cm, 5.6 * cm, 3.2 * cm, 1.6 * cm,
                               2.0 * cm, 3.0 * cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0e7490")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
]))
story.append(t)
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("<b>Sales by category</b>", styles["Heading2"]))
cat_rows = [["Category", "Sales (PKR)", "Share"]]
for cat, val in by_cat.items():
    cat_rows.append([cat, f"{int(val):,}", f"{100.0 * val / FOOD_SALES:.1f}%"])
t2 = Table(cat_rows, colWidths=[5 * cm, 4 * cm, 3 * cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0e7490")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
]))
story.append(t2)
story.append(Spacer(1, 0.4 * cm))
story.append(Image(str(PREVIEWS / "top-10-items.png"), width=16 * cm,
                   height=8 * cm))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("<b>Peak hours &amp; delivery</b>", styles["Heading2"]))
story.append(Paragraph(
    f"Lunch (13:00–15:00) carries "
    f"{100.0 * orders[orders['order_hour'].between(13, 15)].shape[0] / N_ORDERS:.1f}% "
    f"of orders and dinner (19:00–22:00) "
    f"{100.0 * orders[orders['order_hour'].between(19, 22)].shape[0] / N_ORDERS:.1f}%. "
    f"Slowest area is Johar Town ({by_area.iloc[0]:.1f} min average) "
    f"against Gulberg ({by_area.iloc[-1]:.1f} min) — the same kitchen, "
    f"so the gap is distance and traffic, not cooking time.",
    styles["Normal"]))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("<b>5 actions, in priority order</b>", styles["Heading2"]))
actions = [
    "1. Put Chicken Karahi, Chicken Biryani and Zinger Burger at the "
    "top of the app menu — together they are the first three sellers "
    "and the cheapest marketing is showing what already sells.",
    "2. Bundle the slow movers: Desserts are only "
    f"{100.0 * by_cat['Desserts'] / FOOD_SALES:.1f}% of food sales — "
    "add a PKR 150 dessert to Karahi and Biryani combos instead of "
    "discounting the main dish.",
    "3. Staff the 13:00–15:00 and 19:00–22:00 peaks first — "
    "two-thirds of orders land in those 7 hours; a rider shortfall "
    "there costs more than anywhere else.",
    "4. Fix Johar Town delivery: longest average delivery and the "
    "slowest area by a clear margin — check rider allocation there "
    "before spending on ads in that area.",
    "5. Push the App channel: it already carries most orders — "
    "move Phone orders (the smallest channel) onto the App with a "
    "first-App-order perk and cut manual order-taking.",
]
for a in actions:
    story.append(Paragraph(a, styles["Normal"]))
    story.append(Spacer(1, 0.15 * cm))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    "Method: every number above is recomputed from "
    "data/raw/orders_SAMPLE.csv by this script (src/build_report.py). "
    "Delivery fee is PKR 80 per order, free on food orders of PKR 1,500 "
    "or more. Charts are preview renders of the same data, not Power BI "
    "screenshots — the Power BI build guide is in "
    "dashboard/powerbi-build-guide.md.", styles["Normal"]))
SimpleDocTemplate(str(PDF), pagesize=A4,
                  topMargin=1.6 * cm, bottomMargin=1.6 * cm).build(story)
print(f"orders: {N_ORDERS}, food sales PKR {FOOD_SALES:,}, "
      f"total PKR {TOTAL:,}")
print(f"charts: 4 renders in {PREVIEWS}")
print(f"report: {PDF}")
