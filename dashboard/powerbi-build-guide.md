# P10 — Power BI build guide (~15 minutes)

Build the Lahore Food Co delivery dashboard in Power BI Desktop from
the files in this repo. No `.pbix` is bundled (see the honest note in
the README) — this guide plus the model and DAX below produce it.

## 1. Import (2 min)

**Get Data → Text/CSV**, import these three files from
`data/processed/`:

| File | Table name in Power BI |
|---|---|
| `fact_order_lines.csv` | fact_order_lines |
| `dim_item.csv` | dim_item |
| `dim_date.csv` | dim_date |

## 2. Relationships (3 min, Model view)

| From | To | Cardinality | Cross-filter |
|---|---|---|---|
| fact_order_lines[item_id] | dim_item[item_id] | Many to one | Single |
| fact_order_lines[date_id] | dim_date[date_id] | Many to one | Single |

No relationship is needed for area / channel / payment — they live on
the fact table as low-cardinality text columns and work as slicers
directly.

## 3. Measures (3 min)

**Modeling → New measure**, paste each measure from `dax/measures.dax`:
Total Food Sales · Total Delivery Fees · Total Revenue · Orders ·
Average Order Value · Average Delivery Minutes · Slow Orders % ·
Food Sales Share % · Top Item Sales · MoM Food Sales Growth %.

⚠️ **Read the comment on Total Delivery Fees before changing it:**
the fee repeats on every line of an order, so a plain `SUM` would
count it 1.83× too high. The measure takes the fee once per order.
The same applies to Average Delivery Minutes and Slow Orders % —
delivery time is an order-level fact.

## 4. Visuals (7 min, one page, "Delivery Sales — Q3 2026")

| Visual | Fields |
|---|---|
| 4 KPI cards | Total Revenue · Total Food Sales · Orders · Average Order Value |
| Line chart | Axis: dim_date[month] (or date_id for daily) · Values: Total Food Sales |
| Bar chart | Axis: dim_item[category] · Values: Total Food Sales |
| Bar chart | Axis: dim_item[item] (Top N filter: Top 10 by Total Food Sales) · Values: Total Food Sales |
| Column chart | Axis: fact_order_lines[order_hour] · Values: Orders |
| Table | dim_item[item] · Total Food Sales · Orders · Food Sales Share % |
| Slicers | fact_order_lines[channel] · fact_order_lines[area] · dim_date[month] |

## 5. Check the numbers before sharing

With no slicers active the cards must read exactly:

| Card | Must read |
|---|---|
| Total Revenue | PKR 1,712,880 |
| Total Food Sales | PKR 1,591,120 |
| Orders | 1,800 |
| Average Order Value | PKR 884 |

If any card disagrees, the relationships in step 2 are wrong — check
them before trusting any visual. (`src/checks.py` proves the same
totals from the raw CSV.)

## Preview renders

`dashboard/previews/*.png` are matplotlib renders of the same data so
a buyer can see the dashboard's shape without Power BI — they are
labelled as renders, **not** Power BI screenshots.
