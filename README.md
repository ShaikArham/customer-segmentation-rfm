<div align="center">

# CUSTOMER LENS

### KNOW THE PATTERN. TEST THE NEXT MOVE.

**A transparent RFM segmentation pipeline with an interactive retail analytics dashboard.**

[**Explore the demo**](https://shaikarham.github.io/customer-segmentation-rfm/site/) · [**Source repository**](https://github.com/ShaikArham/customer-segmentation-rfm) · [**Arham's portfolio**](https://arham-bi.vercel.app/)

![Project](https://img.shields.io/badge/Portfolio-Independent%20project-075d60?style=flat-square) ![Evidence](https://img.shields.io/badge/Approach-Evidence%20first-334155?style=flat-square)

*Shaik Arham Saquib · Dublin, Ireland*

</div>

---

## 01 / THE QUESTION

**What can a retailer learn from transaction history without confusing descriptive segments with predicted behaviour?**

The pipeline validates orders, handles refunds in integer cents, applies explicit RFM scoring rules and makes segments inspectable in a browser dashboard.

> **The goal:** Show the reasoning behind the result, not just the interface that displays it.

## 02 / AT A GLANCE

**3,658 fictional orders | 569 eligible customers | 12 calculation and reconciliation tests**

| Reviewer's lens | What to look for |
| :--- | :--- |
| **Product thinking** | The operational question and intended user journey |
| **Engineering** | Python 3.12+, standard library, CSV/JSON, static browser dashboard. |
| **Evidence** | Reproducible examples, explicit rules and documented boundaries |
| **Trust** | No predictive customer lifetime value, causal marketing effect or real customer data. |

## 03 / FIVE-MINUTE REVIEW

Start with the dashboard, inspect the segment rules, then run the deterministic generator and test suite. Campaign ideas are hypotheses, not measured uplift.

## 04 / WHAT IT DEMONSTRATES

- **Problem framing:** Make the operational decision and its context explicit.
- **Traceability:** Explain the inputs, transformations and outputs a reviewer can inspect.
- **Responsible claims:** Separate fictional scenarios, demonstrated results and future work.
- **Communication:** Make technical decisions understandable to both analysts and hiring managers.

## 05 / IMPLEMENTATION AND REPRODUCTION

The original project documentation follows below, including exact commands, metric definitions, architecture, test evidence and limitations where available. The project README remains the authoritative source for its own implementation details.

---

## Detailed project documentation

Reproducible Python customer segmentation and an interactive sales dashboard.

**All supplied data is fictional.** Built as a new portfolio demonstration in October 2026; this is not evidence of historical client work or commercial improvements.

[Open the live dashboard](https://shaikarham.github.io/customer-segmentation-rfm/site/)

## Run

Python 3.12+, no third-party packages required:

```bash
python scripts/generate_data.py
python scripts/build.py --synthetic
python -m unittest discover -s tests -v
python -m http.server 8000 --directory site
```

Open http://localhost:8000 or open `site/index.html` directly. Prebuilt sample outputs are included.

## Features

- Strict CSV validation and exact integer-cent calculations.
- RFM scoring, seven customer segments and campaign test hypotheses.
- Country/segment filters, customer search, sorting, pagination and CSV export.
- Monthly sales, accessible chart tables and data quality diagnostics.
- Deterministic data generation, reconciliation tests and GitHub Actions verification.

## Sample results

| Measure | Synthetic result |
|---|---:|
| Input orders | 3,658 |
| Eligible orders | 2,950 |
| Eligible customers | 569 |
| Net sales | €605,967.39 |

Seed 42. Analysis date 1 November 2026; window 1 November 2025 inclusive to 1 November 2026 exclusive. These figures describe fictional transactions, not business impact.

## Method

One row represents one unique order. Cancelled and zero-net orders are excluded; partial refunds reduce net sales. Recency is days since the latest eligible order, frequency counts eligible orders, monetary value sums net cents.

Scores use nearest-rank 20th/40th/60th/80th percentile thresholds. Each strictly exceeded threshold adds one point; recency is reversed. Ties stay together, so groups may be unequal. If all values tie, F/M score 1 and R scores 5.

Rules apply in the following order:

| Segment | Condition |
|---|---|
| Champions | R ≥ 4, F ≥ 4, M ≥ 4 |
| At risk | R ≤ 2, F ≥ 4 |
| Hibernating | R ≤ 2, F ≤ 2 |
| New customers | R ≥ 4, F ≤ 2 |
| Loyal | R ≥ 3, F ≥ 4 |
| Potential loyalists | R ≥ 3, F ≥ 2 |
| Needs attention | Remaining customers |

Dashboard filters do not recalculate scores. Monthly sales display the full population and are labelled unfiltered.

## Your own data

See [data dictionary](docs/data-dictionary.md), then:

```bash
python scripts/build.py --input /path/to/transactions.csv --as-of 2026-11-01 --window-days 365
```

Omit `--synthetic` for non-fictional data. Generated dashboard files contain customer-level records; publish only fictional or suitably anonymised data. The browser dashboard uploads nothing.

## Files

- `src/customer_segmentation/analysis.py`: validation, scoring and aggregation.
- `scripts/`: sample generation and build commands.
- `data/`: fictional input CSV.
- `outputs/`: customer/segment/monthly CSVs and complete JSON analysis.
- `site/`: standalone dashboard and generated payload.
- `tests/`: calculation, boundary, validation and reconciliation tests.
- `docs/`: field definitions and [optional Power BI guide](docs/power-bi-guide.md).

## Limitations

Descriptive segmentation only: no predictive model, estimated lifetime value, causal uplift claims or Power BI `.pbix` file. Campaign suggestions are hypotheses for experiments. Synthetic patterns and customer country assumptions simplify real retail operations.

