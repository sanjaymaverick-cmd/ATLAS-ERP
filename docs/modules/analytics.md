# Sales Analytics — funnel and model monitor

**Primary question:** Who is in the funnel?

Counts native Lead `atlas_stage`. Conversion is won / (won + lost). Band mix from `atlas_band`. Model monitor counts hybrid vs external CatBoost **scores already stored** — it does not call CatBoost and does not implement Ordered Target Statistics.

Desk page `sales-analytics`. Channel seats cannot open it. Does not book, pay, or lock a unit.

Customer 360: `erpatlas.pipeline.intake.customer_360` assembles Lead + Booking + Commission for a phone. Read-only.
