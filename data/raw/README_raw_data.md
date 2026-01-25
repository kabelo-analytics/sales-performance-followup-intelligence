# Raw WhatsApp Submissions (Synthetic)

This folder contains a **synthetic** dataset designed to mimic a realistic "WhatsApp → Excel" daily sales submission workflow
for an independent distributor operating inside large retail environments.

## Files
- `whatsapp_submissions_raw.csv` : full synthetic raw dataset (messy on purpose)
- `whatsapp_submissions_raw_sample_500.csv` : small sample you can commit to GitHub

## Quick sanity check (generation settings)
- Days: 120
- Reps: 120
- Potential rep-days: 14,400
- Actual messages created: 13,478

Messiness counters:
- Late submissions: 1,776
- Next-day submissions: 763
- Duplicate messages created: 646
- Missing rep_id rows: 1,028
- Claimed date errors: 398

> Disclaimer: All data is synthetic; no confidential or proprietary data was used.