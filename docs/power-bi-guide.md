# Optional Power BI recreation

The included, runnable dashboard is HTML/CSS/JavaScript. There is **no .pbix
file** and no claim that one was built as part of this implementation.

To create your own Power BI report, import `outputs/customers.csv`,
`outputs/segments.csv` and `outputs/monthly.csv`. Convert cents to EUR in
Power Query or DAX. Set customer_id as text. Use the customer table for RFM
charts, with segment/country slicers. Keep the monthly summary disconnected
if you want it to remain an unfiltered overall sales trend.

Suggested measures on the customers table:

```dax
Customers = DISTINCTCOUNT(customers[customer_id])
Net Sales EUR = DIVIDE(SUM(customers[monetary_cents]), 100)
Orders = SUM(customers[frequency])
Orders per Customer = DIVIDE([Orders], [Customers])
Median Recency = MEDIAN(customers[recency_days])
```

Reconcile your unfiltered Net Sales measure against analysis.json. Include a
visible fictional-data label and the snapshot date on every report page.
