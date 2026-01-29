import re
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/whatsapp_submissions_raw.csv")
INTERIM = Path("data/interim/daily_sales_parsed.csv")
PROCESSED = Path("data/processed/daily_sales_fact.csv")
DQ = Path("data/processed/data_quality_report.csv")

def ensure_dirs():
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)

def parse_units(text: str):
    """
    Handles:
    - units=7
    - u 7
    - u=7
    - 7 u
    - 7 (u)
    - 7 (unit)
    - 7 unit / 7 units
    """
    if not isinstance(text, str):
        return None
    t = text.lower()

    patterns = [
        r"\bunits?\s*=\s*(\d+)\b",
        r"\bu\s*=\s*(\d+)\b",
        r"\bu\s+(\d+)\b",                 # u 7
        r"\bunits?\s*[:\-]?\s*(\d+)\b",   # units 7 / units:7
        r"\bunit\s*[:\-]?\s*(\d+)\b",     # unit 7
        r"\b(\d+)\s*(?:units?|unit|u)\b", # 7 units / 7 unit / 7 u
        r"\b(\d+)\s*\((?:u|unit|units)\)\b", # 7 (u) / 7 (unit)
    ]

    for p in patterns:
        m = re.search(p, t)
        if m:
            return int(m.group(1))
    return None


def parse_revenue(text: str):
    """
    Handles:
    - R27,401 / R 23,596 / 11848
    - 9.1k / 14.8k
    - R0 / 0
    - "George: 14.8k and 7 u" (no label)
    """
    if not isinstance(text, str):
        return None

    # Normalize
    t = text.lower().replace(" ", "")

    # k format like 9.1k, r9.1k
    mk = re.search(r"r?(\d+(?:\.\d+)?)k\b", t)
    if mk:
        return float(mk.group(1)) * 1000

    # Explicit revenue labels (rev/revenue/sales)
    mlabel = re.search(r"(rev|revenue|sales)\D{0,5}r?\D*(\d{1,3}(?:[,\s]\d{3})+|\d+)", text.lower())
    if mlabel:
        s = mlabel.group(2).replace(",", "").replace(" ", "")
        try:
            return float(s)
        except:
            return None

    # Currency forms like R0, R 12,450, R12450
    mcur = re.search(r"\br\s*([0-9][0-9,\s]*)\b", text.lower())
    if mcur:
        s = mcur.group(1).replace(",", "").replace(" ", "")
        try:
            return float(s)
        except:
            return None

    # Fallback: if nothing else, pick the largest number in the string
    # (helps with "George: 14.8k and 7 u" already handled above; now handles plain numbers)
    nums = re.findall(r"\b\d+(?:\.\d+)?\b", t)
    if nums:
        # choose the largest numeric value
        vals = []
        for n in nums:
            try:
                vals.append(float(n))
            except:
                pass
        if vals:
            return max(vals)

    return None


def resolve_sale_date(claimed_date, msg_ts):
    if pd.isna(msg_ts) or pd.isna(claimed_date):
        return None, "missing"
    msg_date = msg_ts.date()
    claimed = claimed_date.date()

    if claimed == msg_date:
        return claimed, "claimed_eq_msgdate"

    if (msg_date - claimed).days == 1 and (6 <= msg_ts.hour <= 11):
        return claimed, "next_day_morning_keep_claimed"

    if abs((msg_date - claimed).days) > 1:
        return msg_date, "claim_far_off_use_msgdate"

    return claimed, "small_mismatch_keep_claimed"

def classify_submission_status(sale_date, msg_ts):
    if sale_date is None or pd.isna(msg_ts):
        return "unknown"
    msg_date = msg_ts.date()
    if msg_date == sale_date:
        return "late" if msg_ts.hour >= 20 else "on_time"
    if (msg_date - sale_date).days == 1:
        return "next_day"
    return "other"

def main():
    ensure_dirs()

    if not RAW.exists():
        raise FileNotFoundError(
            f"Missing raw file: {RAW}\n"
            "Place the FULL dataset at data/raw/whatsapp_submissions_raw.csv"
        )

    df = pd.read_csv(RAW, parse_dates=["message_timestamp"])
    df["sales_date_claimed"] = pd.to_datetime(df["sales_date_claimed"], errors="coerce")

    df["units_sold"] = df["raw_text"].apply(parse_units)
    df["revenue"] = df["raw_text"].apply(parse_revenue)

    resolved = df.apply(lambda r: resolve_sale_date(r["sales_date_claimed"], r["message_timestamp"]), axis=1)
    df["sale_date"] = [x[0] for x in resolved]
    df["date_resolution_rule"] = [x[1] for x in resolved]

    df["submission_status"] = df.apply(lambda r: classify_submission_status(r["sale_date"], r["message_timestamp"]), axis=1)

    df["rep_key"] = df["rep_id"].fillna(df["rep_name"])
    df["dup_key"] = (
        df["rep_key"].astype(str) + "|" +
        df["store"].astype(str) + "|" +
        df["sale_date"].astype(str) + "|" +
        df["units_sold"].astype(str) + "|" +
        df["revenue"].astype(str)
    )
    df["is_duplicate"] = df.duplicated(subset=["dup_key"], keep="first")

    df["parse_status"] = "parsed_ok"
    df.loc[df["units_sold"].isna(), "parse_status"] = "missing_units"
    df.loc[df["revenue"].isna(), "parse_status"] = "missing_revenue"
    df.loc[df["units_sold"].isna() & df["revenue"].isna(), "parse_status"] = "missing_both"

    df.to_csv(INTERIM, index=False)

    clean = df[~df["is_duplicate"]].copy()

    fact = (clean
        .groupby(["sale_date", "region", "store", "rep_key"], as_index=False)
        .agg(
            units_sold=("units_sold", "sum"),
            revenue=("revenue", "sum"),
            submissions=("message_id", "count"),
            submission_status=("submission_status", lambda x: x.value_counts().index[0]),
            parse_status=("parse_status", lambda x: x.value_counts().index[0]),
        )
    )
    fact.to_csv(PROCESSED, index=False)

    dq = pd.DataFrame({
        "metric": [
            "raw_rows",
            "duplicates_flagged",
            "missing_units_rows",
            "missing_revenue_rows",
            "missing_both_rows",
            "on_time_rows",
            "late_rows",
            "next_day_rows",
        ],
        "value": [
            len(df),
            int(df["is_duplicate"].sum()),
            int(df["units_sold"].isna().sum()),
            int(df["revenue"].isna().sum()),
            int((df["units_sold"].isna() & df["revenue"].isna()).sum()),
            int((df["submission_status"] == "on_time").sum()),
            int((df["submission_status"] == "late").sum()),
            int((df["submission_status"] == "next_day").sum()),
        ]
    })
    dq.to_csv(DQ, index=False)

    print("Saved:")
    print(" -", INTERIM)
    print(" -", PROCESSED)
    print(" -", DQ)

if __name__ == "__main__":
    main()
