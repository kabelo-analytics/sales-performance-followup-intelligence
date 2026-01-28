📊 Sales Performance Follow-Up Intelligence
Overview

This project demonstrates how unstructured daily sales submissions (e.g. WhatsApp messages from in-store sales reps) can be transformed into actionable commercial intelligence.

The focus is on operational realism, not perfect data:

late submissions

missing fields

duplicates

next-day reporting

These conditions reflect how sales data is actually reported in distributed retail environments.

Business Context

In many retail distribution and concession models:

Sales reps report daily performance manually

Managers lack real-time visibility

Follow-ups are reactive and inconsistent

This project simulates that environment and shows how analytics can support:

daily revenue monitoring

performance management

reporting discipline

follow-up prioritisation

Data Pipeline (High Level)

1. Raw submissions
Synthetic WhatsApp-style sales messages (generated to reflect real reporting behaviour).

2. Parsing & cleaning (Python)

Extracted revenue and units from free-text

Resolved sale date vs submission date

Flagged late / next-day submissions

Removed duplicates

Preserved data quality signals (not over-cleaned)

3. Analytics-ready fact table
daily_sales_fact_v2.csv
Each row represents a rep × store × day.

Notebook: Commercial Manager Insight Pack

📘 Notebook:
notebooks/04_commercial_manager_insights.ipynb

This notebook is designed as a manager-facing insight pack, not a technical experiment.

Questions it answers

How are we trading daily, monthly, and yearly?

Who are the top performing reps?

How disciplined is reporting (on-time vs late vs next-day)?

Who needs follow-up today?

Key Outputs
Revenue Trends

Daily revenue trend (volatility & anomalies)

Monthly revenue trend (momentum & run-rate)

Yearly revenue summary (executive view)

Performance Management

Top 15 reps by total revenue

Long-tail performance distribution

Operational Discipline

Submission status breakdown:

on-time

late

next-day

Follow-Up Priority List

A ranked list of reps/stores requiring attention, based on:

late or next-day submission

missing data fields

revenue impact

📄 Output file:

reports/follow_up_priority_top25.csv

Outputs Saved for Review

Running the notebook generates:

reports/figures/
├── 01_daily_revenue_trend.png
├── 02_monthly_revenue_trend.png
├── 03_yearly_revenue_summary.png
├── 04_rep_leaderboard_top15.png
└── 05_submission_status_counts.png


These are intentionally saved as static images for easy sharing and review.

Tools Used

Python (pandas, matplotlib)

Jupyter Notebook

Git & GitHub

Power BI can optionally be used to replicate these views in an interactive dashboard. The notebook is the primary, source-of-truth analytical artefact.

Disclaimer

All data in this repository is synthetic and generated solely for demonstration purposes.
No real company, individual, or proprietary dataset is represented.

Why This Project Matters

This project demonstrates:

Commercial thinking over cosmetic dashboards

Comfort with messy, real-world data

Ability to translate operations into decision support

Clear separation of data engineering and insight delivery