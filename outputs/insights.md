# P10 — Findings & recommendations (from the SAMPLE data)

## 3 key findings

1. **Karahi is the profit engine, Biryani is the volume engine.**
   Chicken Karahi (half) is the top seller by money — PKR 195,500 from
   only 169 orders — while Chicken Biryani leads on reach (281 orders,
   PKR 134,050). *So what:* Karahi earns the menu's top slot and the
   Biryani earns the "most ordered" badge; both sell the restaurant,
   for different reasons.
2. **Two peaks carry two-thirds of the business.** Lunch 13:00–15:00
   is 550 orders (30.6%) and dinner 19:00–22:00 is 595 orders (33.1%)
   — 63.7% of all orders land in 7 hours of the day. August is the
   best month (PKR 569,970 food sales, 651 orders) against July's
   PKR 505,470. *So what:* rider and kitchen staffing is a peak-hours
   problem, not an all-day problem; a shortfall at 20:00 costs roughly
   three times a shortfall at 10:00.
3. **Delivery is the weak link, and it is geographic.** Average
   delivery is 32.6 minutes, but 151 orders (8.4%) took over 45
   minutes, and the gap is area, not food: Johar Town averages 39.3
   minutes against Gulberg's 26.8. *So what:* fix rider allocation in
   Johar Town before spending on ads there — a slow delivery in the
   area you are promoting is the fastest way to lose a repeat order.
   (Average rating 4.31 / 5 from 1,268 rated orders says the food
   itself is not the problem.)

## The numbers behind them

- Food sales PKR 1,591,120 · delivery fees PKR 121,760 ·
  total revenue PKR 1,712,880 · 1,800 orders · 3,296 lines ·
  average order value PKR 884 (food only) / PKR 952 (with fee).
- Top category: BBQ & Grill PKR 389,280 (24.5%); Desi Curries
  PKR 350,620; Fast Food PKR 346,930; Biryani PKR 309,610;
  Beverages PKR 110,150; Desserts PKR 84,530 (5.3%).
- Channels: App 1,041 orders (57.8%), Website 488, Phone 271.
  App food sales PKR 910,340 — the App is already the business.
- Payment: COD 1,006 orders (55.9%), Card 529, Wallet 265.
- Free delivery (food ≥ PKR 1,500): 278 orders (15.4%).

## 3 recommendations

1. **Menu order = sales order.** Karahi, Chicken Biryani and Zinger
   Burger lead the App menu; desserts ride as a PKR 150 add-on to
   Karahi/Biryani combos instead of a discount on the main dish.
2. **Staff the peaks, not the day.** Kitchen + riders peak at
   13:00–15:00 and 19:00–22:00; mid-morning is the prep window.
3. **Fix Johar Town first.** Reallocate one rider there (or a
   pickup point) and watch the >45-minute share — it is the one
   number that moves repeat orders.

All numbers are recomputed from `data/raw/orders_SAMPLE.csv` by
`src/build_report.py` and proven by `src/checks.py` (25 checks).
