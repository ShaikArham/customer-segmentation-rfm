# Data contract

`data/transactions.csv` is **fictional data**, generated with `random.Random(42)`.
No real customer records, external dataset or client material is used.

| Column | Meaning | Validation |
|---|---|---|
| order_id | One unique order per row | Nonempty, globally unique |
| customer_id | Fictional customer key | Nonempty |
| order_date | Purchase date | ISO YYYY-MM-DD |
| country | Stable customer country | Nonempty, consistent per customer |
| amount_eur | Gross order value in EUR | Nonnegative, maximum 2 decimals |
| refund_eur | Refund allocated to that order | Between zero and gross value |
| status | Order state | completed or cancelled |

The analysis window is `[as_of - window_days, as_of)`. No future transactions
enter the scores. RFM uses positive-net, completed orders only. Fully refunded
and cancelled orders are tracked in quality checks but excluded from RFM.
This choice also excludes customers with only fully refunded/cancelled orders.

Output monetary values use **integer cents**, including dashboard CSV exports.
Frequency is distinct eligible order count, not transaction-line count.
Recency is integer days from the snapshot date to the last eligible purchase.

## Score and segment rules

Four nearest-rank quintile cutoffs are computed for each metric. A value earns
one additional point for each cutoff it **strictly exceeds**. Recency scores
are reversed. Ties are not split. For all-equal values F/M = 1 and R = 5;
interpret such labels cautiously, especially for small datasets.

Rules apply in this order (R/F/M are scores, not raw values):

1. R >= 4, F >= 4, M >= 4: Champions.
2. R <= 2, F >= 4: At risk.
3. R <= 2, F <= 2: Hibernating.
4. R >= 4, F <= 2: New customers.
5. R >= 3, F >= 4: Loyal customers.
6. R >= 3, F >= 2: Potential loyalists.
7. Otherwise: Needs attention.

New customers means recent with low *relative* frequency, not a verified first
purchase in the customer's entire lifetime. At risk is a heuristic label, not
a churn probability. Segment actions are proposed experiments, not outcomes.

## Adapting real data

Aggregate line-item data to one order before loading. Convert currency to EUR
using a documented exchange-rate policy. Remove personal identifiers. Obtain
permission before analysis or publication. Do not commit real customer data.
Use `data/private/` and `outputs/private/` for local inputs/outputs and pass a
private site directory to `--site`. Never publish a generated data.js containing
private customer rows. The tool processes locally and does not upload data.
