#!/usr/bin/env python3
import csv, io, zipfile, pathlib, requests, pandas as pd
from datetime import datetime

# -----------------------------
# Config
# -----------------------------
BASE = pathlib.Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
OUT = BASE / "data"
DOCS = BASE / "docs"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

# Jacksonville MSA-ish counties we'll start with
COUNTIES = [
    ("12031", "Florida", "Duval"),
    ("12019", "Florida", "Clay"),
    ("12109", "Florida", "St. Johns"),
    ("12089", "Florida", "Nassau"),
    ("12003", "Florida", "Baker"),
]
STATE_ABBR = "FL"

# -----------------------------
# Data fetch helpers
# -----------------------------

def fetch_epa_aqi_annual(year=2023):
    """
    EPA AirData: Annual AQI by county (counts of days by AQI category). No API key.
    https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_county_YYYY.zip
    Note: Using 2023 as most recent complete year with full data.
    """
    url = f"https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_county_{year}.zip"
    zpath = RAW / f"annual_aqi_by_county_{year}.zip"
    csv_path = RAW / f"annual_aqi_by_county_{year}.csv"

    r = requests.get(url, timeout=60)
    r.raise_for_status()
    zpath.write_bytes(r.content)
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        # The CSV inside is named annual_aqi_by_county_YYYY.csv
        inner = [n for n in zf.namelist() if n.endswith(".csv")][0]
        csv_bytes = zf.read(inner)
        csv_path.write_bytes(csv_bytes)

    df = pd.read_csv(csv_path)
    # Keep Florida only
    df_fl = df[df["State"] == "Florida"].copy()

    # Derive "unhealthy_or_worse_days"
    # Columns: Good Days, Moderate Days, Unhealthy for Sensitive Groups Days, Unhealthy Days, Very Unhealthy Days, Hazardous Days
    u = "Unhealthy Days"
    vu = "Very Unhealthy Days"
    hz = "Hazardous Days"
    df_fl["unhealthy_or_worse_days"] = df_fl[u].fillna(0) + df_fl[vu].fillna(0) + df_fl[hz].fillna(0)

    # Map county names to FIPS codes
    fips_map = {cname.lower(): fips for (fips, st, cname) in COUNTIES}
    df_fl["fips"] = df_fl["County"].str.lower().map(fips_map)
    
    # Only keep our target counties
    df_fl = df_fl[df_fl["fips"].notna()].copy()

    keep = df_fl[["fips", "State", "County", "unhealthy_or_worse_days", "Year"]].rename(
        columns={"State":"state","County":"county","Year":"year"}
    )
    return keep

def fetch_hrsa_hpsa_dashboard():
    """
    HRSA HPSA Dashboard CSV (public, no key).
    https://data.hrsa.gov/DataDownload/DD_Files/HPSA_DASHBOARD.csv
    We'll compute a simple county-level signal: max Primary Care HPSA score in county.
    """
    url = "https://data.hrsa.gov/DataDownload/DD_Files/HPSA_DASHBOARD.csv"
    path = RAW / "HPSA_DASHBOARD.csv"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    df = pd.read_csv(path, dtype=str, quoting=csv.QUOTE_MINIMAL)
    # Normalize columns
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Keep Florida + primary care
    df = df[(df["state"] == "Florida") & (df["discipline"].str.contains("Primary Care", na=False, case=False))]
    # HPSA_Score is numeric; higher = greater shortage
    df["hpsa_score"] = pd.to_numeric(df["hpsa_score"], errors="coerce")
    # Some rows are facility/population-based; aggregate to county max
    g = df.groupby("county", as_index=False)["hpsa_score"].max().rename(columns={"hpsa_score":"hpsa_primary_care_max"})
    # We also add a binary flag
    g["hpsa_primary_care_flag"] = (g["hpsa_primary_care_max"].fillna(0) > 0).astype(int)
    # Attach FIPS from our target list (simple map)
    fips_map = {cname.lower(): fips for (fips, st, cname) in COUNTIES}
    g["fips"] = g["county"].str.lower().map(fips_map)
    return g

def build_scorecard():
    # Fetch sources
    aqi = fetch_epa_aqi_annual(2023)     # last full year available
    hpsa = fetch_hrsa_hpsa_dashboard()

    # Seed frame from our county list
    seed = pd.DataFrame(COUNTIES, columns=["fips","state","county"])

    # Join
    df = seed.merge(aqi[["fips","unhealthy_or_worse_days"]], on="fips", how="left")
    df = df.merge(hpsa[["fips","hpsa_primary_care_max","hpsa_primary_care_flag"]], on="fips", how="left")

    # Scoring (simple, transparent; adjust weights later)
    # - AQI stress (max 40 pts): map unhealthy_or_worse_days into 0–40 (cap at 30 days)
    df["aqi_days"] = df["unhealthy_or_worse_days"].fillna(0).clip(0, 30)
    df["score_air_q"] = (df["aqi_days"] / 30.0) * 40.0

    # - HPSA (max 60 pts): scale max primary-care HPSA score (0–25) to 0–60
    df["score_hpsa"] = (df["hpsa_primary_care_max"].fillna(0).clip(0, 25) / 25.0) * 60.0

    df["readiness_score"] = (df["score_air_q"] + df["score_hpsa"]).round(1)

    # Friendly columns
    df["updated_utc"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    out = df[[
        "fips","state","county",
        "unhealthy_or_worse_days","hpsa_primary_care_max","hpsa_primary_care_flag",
        "score_air_q","score_hpsa","readiness_score","updated_utc"
    ]].sort_values("readiness_score", ascending=False)

    OUT.joinpath("scorecard.csv").write_text(out.to_csv(index=False))
    return out

def write_html_table(df: pd.DataFrame):
    # simple CSS/JS-free sortable table (Cursor-friendly)
    title = "Jacksonville-Area County Health Readiness Scorecard (MVP)"
    subtitle = "Higher score = higher risk/need (AQI + Primary Care HPSA) – updated weekly"
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:24px;max-width:980px}}
h1{{margin:0}} h2{{margin:0;color:#555;font-weight:500;font-size:1rem}}
table{{border-collapse:collapse;width:100%;margin-top:16px}}
th,td{{border:1px solid #ddd;padding:8px}} th{{background:#f7f7f7;text-align:left}}
small{{color:#666}}
</style></head><body>
<h1>{title}</h1>
<h2>{subtitle}</h2>
<small>Sources: EPA AirData Annual AQI (2023), HRSA HPSA Dashboard. See repo README for details.</small>
<table>
<thead><tr>
<th>County</th><th>FIPS</th>
<th>Unhealthy AQI Days (2023)</th>
<th>HPSA Primary Care Max Score</th>
<th>Readiness Score</th>
</tr></thead>
<tbody>
"""
    for _, r in df.iterrows():
        html += f"<tr><td>{r['county']}, {r['state']}</td><td>{r['fips']}</td><td>{int(r['unhealthy_or_worse_days']) if pd.notna(r['unhealthy_or_worse_days']) else ''}</td><td>{'' if pd.isna(r['hpsa_primary_care_max']) else int(r['hpsa_primary_care_max'])}</td><td><b>{r['readiness_score']}</b></td></tr>"
    html += f"""</tbody></table>
<small>Generated {datetime.utcnow().isoformat(timespec="seconds")}Z</small>
</body></html>"""
    DOCS.joinpath("index.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    df = build_scorecard()
    write_html_table(df)
    print("✅ Wrote data/scorecard.csv and docs/index.html")

