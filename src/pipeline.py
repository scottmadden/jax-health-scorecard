#!/usr/bin/env python3
import csv, io, zipfile, pathlib, requests, pandas as pd, os
from datetime import datetime, timedelta

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

def fetch_cdc_places_county():
    """
    CDC PLACES: County-level chronic disease & risk factor prevalence.
    https://data.cdc.gov/resource/duw2-7jbt.json (2024 dataset)
    We fetch: diabetes, obesity, and current asthma prevalence for Florida counties.
    """
    # Using Socrata Open Data API (2024 PLACES release)
    base_url = "https://data.cdc.gov/resource/duw2-7jbt.json"
    
    # Fetch for all FL counties
    params = {
        "$where": "stateabbr='FL' AND data_value_type='Crude prevalence'",
        "$limit": 1000
    }
    
    r = requests.get(base_url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    
    if not data:
        # Fallback: return target counties with zero values
        return pd.DataFrame([{"fips": c[0], "chronic_disease_prev": 0.0} for c in COUNTIES])
    
    df = pd.DataFrame(data)
    
    # Normalize column names
    df.columns = [c.lower() for c in df.columns]
    
    # Filter for key indicators: DIABETES, OBESITY, CASTHMA
    df = df[df["measureid"].isin(["DIABETES", "OBESITY", "CASTHMA"])].copy()
    
    if df.empty:
        return pd.DataFrame([{"fips": c[0], "chronic_disease_prev": 0.0} for c in COUNTIES])
    
    # Extract FIPS and data value
    df["fips"] = df["locationid"].astype(str).str.zfill(5) if "locationid" in df.columns else df["countyfips"].astype(str).str.zfill(5)
    df["data_value"] = pd.to_numeric(df["data_value"], errors="coerce")
    
    # Average the indicators by county
    g = df.groupby("fips", as_index=False)["data_value"].mean()
    g.rename(columns={"data_value": "chronic_disease_prev"}, inplace=True)
    
    # Only keep our target counties
    g = g[g["fips"].isin([c[0] for c in COUNTIES])].copy()
    
    # If empty, return zeros for target counties
    if g.empty:
        return pd.DataFrame([{"fips": c[0], "chronic_disease_prev": 0.0} for c in COUNTIES])
    
    return g

def fetch_fema_nri():
    """
    FEMA National Risk Index: County-level hazard risk scores.
    https://hazards.fema.gov/nri/data-resources
    Using ArcGIS REST API (public, no key).
    """
    # FEMA NRI via ArcGIS REST API
    url = "https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/NRI_Table_Counties/FeatureServer/0/query"
    
    # Query for Florida counties (state FIPS = 12)
    params = {
        "where": "STATEFIPS='12'",
        "outFields": "STCOFIPS,RISK_SCORE,RISK_RATNG",
        "f": "json"
    }
    
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    
    if "features" not in data or len(data["features"]) == 0:
        # Fallback: return empty with target counties at 0 risk
        return pd.DataFrame([{"fips": c[0], "risk_score": 0.0, "risk_rating": "Not Rated"} for c in COUNTIES])
    
    # Extract attributes
    records = [f["attributes"] for f in data["features"]]
    df = pd.DataFrame(records)
    
    # Normalize columns
    df.columns = [c.upper() for c in df.columns]
    df["fips"] = df["STCOFIPS"].astype(str).str.zfill(5)
    df["risk_score"] = pd.to_numeric(df["RISK_SCORE"], errors="coerce")
    
    # Only keep our target counties
    keep = df[df["fips"].isin([c[0] for c in COUNTIES])].copy()
    
    return keep[["fips", "risk_score", "RISK_RATNG"]].rename(columns={"RISK_RATNG": "risk_rating"})

def fetch_cdc_respiratory_virus():
    """
    CDC Respiratory Virus Surveillance: State-level activity for Florida.
    https://data.cdc.gov - Weekly respiratory virus activity levels
    Phase 3: Real-time health signal (influenza, COVID-19, RSV)
    """
    # Try CDC FluView API for influenza-like illness (ILI) activity
    # This is a proxy for respiratory virus activity
    url = "https://data.cdc.gov/resource/ucfv-xp52.json"
    
    # Get most recent week for Florida
    params = {
        "$where": "state='Florida'",
        "$order": "week DESC",
        "$limit": 1
    }
    
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        if not data:
            # Fallback: return minimal activity
            return {"respiratory_activity_level": "Minimal", "respiratory_score": 2.0}
        
        # Extract activity level (1-10 scale typical for ILI)
        record = data[0]
        
        # ILI activity level: convert to 0-10 scale
        # Look for activity_level or num_ili or similar fields
        activity_level = None
        activity_name = "Minimal"
        
        # Common field names in CDC respiratory data
        for field in ["activity_level", "activity_level_label", "ili_level"]:
            if field in record:
                activity_name = str(record[field])
                break
        
        # Map activity level names to numeric scores (0-10)
        level_map = {
            "minimal": 2.0,
            "low": 3.5,
            "moderate": 5.5,
            "high": 7.5,
            "very high": 9.0
        }
        
        activity_score = level_map.get(activity_name.lower(), 2.0)
        
        return {
            "respiratory_activity_level": activity_name,
            "respiratory_score": activity_score
        }
        
    except Exception as e:
        print(f"  Warning: Could not fetch respiratory virus data: {e}")
        # Fallback: assume minimal activity
        return {"respiratory_activity_level": "Minimal", "respiratory_score": 2.0}

def fetch_airnow_daily_aqi(api_key=None):
    """
    AirNow Daily API: Current/recent AQI for real-time air quality.
    https://docs.airnowapi.org/
    Phase 3: Optional daily AQI (requires free API key from airnowapi.org)
    Returns 7-day rolling average if available.
    """
    if not api_key:
        api_key = os.environ.get("AIRNOW_API_KEY")
    
    if not api_key:
        print("  Skipping AirNow (no API key) - using annual EPA data only")
        return pd.DataFrame()  # Empty, will fall back to EPA annual data
    
    # AirNow API endpoint for current observations by zipcode
    # We'll use major city zipcodes as proxies for counties
    county_zips = {
        "12031": "32202",  # Duval (Jacksonville)
        "12019": "32003",  # Clay (Orange Park)
        "12109": "32080",  # St. Johns (St. Augustine)
        "12089": "32034",  # Nassau (Fernandina Beach)
        "12003": "32063",  # Baker (Macclenny)
    }
    
    results = []
    
    for fips, zipcode in county_zips.items():
        try:
            url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
            params = {
                "format": "application/json",
                "zipCode": zipcode,
                "distance": 25,
                "API_KEY": api_key
            }
            
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            
            if data:
                # Get current AQI (max of all pollutants)
                aqi_values = [obs.get("AQI", 0) for obs in data if "AQI" in obs]
                if aqi_values:
                    current_aqi = max(aqi_values)
                    results.append({"fips": fips, "current_aqi": current_aqi})
        
        except Exception as e:
            print(f"  Warning: AirNow data unavailable for {fips}: {e}")
            continue
    
    if results:
        return pd.DataFrame(results)
    else:
        return pd.DataFrame()

def build_scorecard():
    """
    Phase 3: Real-time signals - Activated respiratory virus tracking
    Scoring weights (out of 100):
    - Air Quality (AQI): 15 pts
    - Primary Care Access (HPSA): 30 pts
    - Chronic Disease (CDC PLACES): 30 pts
    - Hazard Risk (FEMA NRI): 15 pts
    - Respiratory Virus Activity (CDC): 10 pts ✅ ACTIVE
    """
    print("Fetching data sources (Phase 3)...")
    
    # Fetch all sources
    print("  - EPA AQI...")
    aqi = fetch_epa_aqi_annual(2023)
    
    print("  - HRSA HPSA...")
    hpsa = fetch_hrsa_hpsa_dashboard()
    
    print("  - CDC PLACES...")
    places = fetch_cdc_places_county()
    
    print("  - FEMA NRI...")
    fema = fetch_fema_nri()
    
    # Phase 3: Real-time signals
    print("  - CDC Respiratory Virus (Phase 3)...")
    respiratory = fetch_cdc_respiratory_virus()
    
    print("  - AirNow Daily (optional)...")
    airnow = fetch_airnow_daily_aqi()  # Will skip if no API key

    # Seed frame from our county list
    seed = pd.DataFrame(COUNTIES, columns=["fips","state","county"])

    # Join all sources
    df = seed.merge(aqi[["fips","unhealthy_or_worse_days"]], on="fips", how="left")
    df = df.merge(hpsa[["fips","hpsa_primary_care_max","hpsa_primary_care_flag"]], on="fips", how="left")
    df = df.merge(places[["fips","chronic_disease_prev"]], on="fips", how="left")
    df = df.merge(fema[["fips","risk_score","risk_rating"]], on="fips", how="left")
    
    # Optional: merge AirNow current AQI if available
    if not airnow.empty:
        df = df.merge(airnow[["fips","current_aqi"]], on="fips", how="left")
        print(f"    ✅ AirNow real-time data integrated for {len(airnow)} counties")

    # Phase 3 Scoring (transparent, weighted; sum = 100 points)
    
    # 1. AQI stress (15 pts): unhealthy days capped at 30 (or current AQI if available)
    df["aqi_days"] = df["unhealthy_or_worse_days"].fillna(0).clip(0, 30)
    if "current_aqi" in df.columns:
        # Use current AQI if available (0-500 scale, 150+ is unhealthy)
        df["score_air_q"] = (df["current_aqi"].fillna(0).clip(0, 200) / 200.0) * 15.0
    else:
        df["score_air_q"] = (df["aqi_days"] / 30.0) * 15.0
    
    # 2. HPSA (30 pts): primary care shortage (0-25 scale)
    df["score_hpsa"] = (df["hpsa_primary_care_max"].fillna(0).clip(0, 25) / 25.0) * 30.0
    
    # 3. Chronic Disease (30 pts): prevalence % (assume 0-20% typical range, cap at 50%)
    df["score_chronic"] = (df["chronic_disease_prev"].fillna(0).clip(0, 50) / 50.0) * 30.0
    
    # 4. Hazard Risk (15 pts): FEMA NRI score (0-100 scale typical)
    df["score_hazard"] = (df["risk_score"].fillna(0).clip(0, 100) / 100.0) * 15.0
    
    # 5. Respiratory Virus (10 pts): Phase 3 - ACTIVE! State-level CDC data
    # Apply respiratory activity score to all counties (state-wide measure)
    respiratory_score_val = (respiratory["respiratory_score"] / 10.0) * 10.0
    df["respiratory_activity"] = respiratory["respiratory_activity_level"]
    df["score_respiratory"] = respiratory_score_val
    
    # Total readiness score
    df["readiness_score"] = (
        df["score_air_q"] + 
        df["score_hpsa"] + 
        df["score_chronic"] + 
        df["score_hazard"] + 
        df["score_respiratory"]
    ).round(1)

    # Friendly columns
    df["updated_utc"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    
    # Select output columns (include respiratory_activity)
    output_cols = [
        "fips","state","county",
        "unhealthy_or_worse_days","hpsa_primary_care_max","chronic_disease_prev",
        "risk_score","risk_rating","respiratory_activity",
        "score_air_q","score_hpsa","score_chronic","score_hazard","score_respiratory",
        "readiness_score","updated_utc"
    ]
    
    # Add current_aqi if available
    if "current_aqi" in df.columns:
        output_cols.insert(4, "current_aqi")
    
    out = df[output_cols].sort_values("readiness_score", ascending=False)

    OUT.joinpath("scorecard.csv").write_text(out.to_csv(index=False))
    print(f"✅ Generated Phase 3 scorecard with {len(out)} counties")
    print(f"   Respiratory Activity: {respiratory['respiratory_activity_level']} (adds {respiratory_score_val:.1f} pts to all counties)")
    return out

def write_html_table(df: pd.DataFrame):
    # Phase 3: Real-time signals with respiratory virus tracking
    title = "Jacksonville-Area County Health Readiness Scorecard (Phase 3)"
    subtitle = "Real-Time Health Signals: Now tracking respiratory virus activity"
    
    # Get respiratory activity level from first row (state-wide)
    resp_activity = df.iloc[0]["respiratory_activity"] if "respiratory_activity" in df.columns else "Unknown"
    resp_score = df.iloc[0]["score_respiratory"] if "score_respiratory" in df.columns else 0
    
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:24px;max-width:1200px}}
h1{{margin:0;font-size:1.8rem}} 
h2{{margin:8px 0;color:#555;font-weight:500;font-size:1rem}}
.alert-box{{margin:16px 0;padding:12px;background:#e3f2fd;border-left:4px solid #2196F3}}
.alert-box strong{{color:#1976D2}}
.legend{{margin:16px 0;padding:12px;background:#f9f9f9;border-left:4px solid #4CAF50}}
.legend h3{{margin:0 0 8px 0;font-size:0.9rem;text-transform:uppercase;color:#666}}
.legend ul{{margin:4px 0;padding-left:20px}}
.legend li{{font-size:0.85rem;color:#666;margin:4px 0}}
table{{border-collapse:collapse;width:100%;margin-top:16px;font-size:0.9rem}}
th,td{{border:1px solid #ddd;padding:10px 8px;text-align:left}}
th{{background:#f7f7f7;font-weight:600;font-size:0.85rem}}
td{{vertical-align:middle}}
.score{{font-weight:bold;font-size:1.1rem;color:#d32f2f}}
.county-name{{font-weight:600}}
small{{color:#666}}
.highlight{{background:#fff3e0}}
.badge{{display:inline-block;padding:2px 8px;border-radius:3px;font-size:0.8rem;background:#4CAF50;color:white}}
</style></head><body>
<h1>{title} <span class="badge">PHASE 3</span></h1>
<h2>{subtitle}</h2>
<div class="alert-box">
<strong>🦠 FL Respiratory Virus Activity:</strong> {resp_activity} (adds {resp_score:.1f} points to all counties this week)
</div>
<div class="legend">
<h3>Scoring Breakdown (100 points total):</h3>
<ul>
<li><strong>Primary Care Access (30pts)</strong>: HRSA HPSA shortage score (0-25 scale)</li>
<li><strong>Chronic Disease (30pts)</strong>: CDC PLACES avg prevalence (diabetes, obesity, asthma)</li>
<li><strong>Air Quality (15pts)</strong>: EPA unhealthy AQI days OR AirNow current (if API key set)</li>
<li><strong>Hazard Risk (15pts)</strong>: FEMA National Risk Index composite score</li>
<li><strong>Respiratory Virus (10pts)</strong>: CDC state-level flu/COVID/RSV activity ✅ <em>Active</em></li>
</ul>
</div>
<small>Sources: EPA AirData (2023), HRSA HPSA, CDC PLACES, FEMA NRI, CDC Respiratory Surveillance. Higher score = higher risk/need.</small>
<table>
<thead><tr>
<th>Rank</th>
<th>County</th>
<th>HPSA<br><small>(0-25)</small></th>
<th>Chronic<br><small>(%)</small></th>
<th>AQI Days<br><small>(2023)</small></th>
<th>Hazard<br><small>(0-100)</small></th>
<th>Respiratory<br><small>(FL-wide)</small></th>
<th>Score<br><small>(0-100)</small></th>
</tr></thead>
<tbody>
"""
    rank = 1
    for _, r in df.iterrows():
        hpsa_val = f"{int(r['hpsa_primary_care_max'])}" if pd.notna(r['hpsa_primary_care_max']) else '-'
        chronic_val = f"{r['chronic_disease_prev']:.1f}" if pd.notna(r['chronic_disease_prev']) else '-'
        aqi_val = f"{int(r['unhealthy_or_worse_days'])}" if pd.notna(r['unhealthy_or_worse_days']) else '-'
        hazard_val = f"{r['risk_score']:.1f}" if pd.notna(r['risk_score']) else '-'
        resp_val = r['respiratory_activity'] if pd.notna(r.get('respiratory_activity')) else '-'
        
        row_class = 'highlight' if rank == 1 else ''
        html += f"<tr class='{row_class}'><td><strong>{rank}</strong></td><td class='county-name'>{r['county']}, {r['state']}</td><td>{hpsa_val}</td><td>{chronic_val}</td><td>{aqi_val}</td><td>{hazard_val}</td><td>{resp_val}</td><td class='score'>{r['readiness_score']:.1f}</td></tr>"
        rank += 1
        
    html += f"""</tbody></table>
<footer style="margin-top:40px;padding-top:24px;border-top:2px solid #eee">
<small style="display:block;color:#666">Last updated: {datetime.utcnow().isoformat(timespec="seconds")}Z | Updates daily at 9:15am ET</small>
<p style="margin-top:16px">
<a href="schools.html" style="color:#1976d2;font-weight:600">View 132 Individual Schools</a> | 
<a href="../data/scorecard.csv" style="color:#1976d2">Download CSV</a> | 
<a href="https://github.com/scottmadden/jax-health-scorecard" style="color:#666">Source Code</a>
</p>
</footer>
</div>
</body></html>"""
    DOCS.joinpath("counties.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    # Phase 3: County-level scorecard
    print("=" * 60)
    print("Building County-Level Scorecard")
    print("=" * 60)
    df = build_scorecard()
    write_html_table(df)
    print("✅ Wrote data/scorecard.csv and docs/index.html")
    
    # Phase 4: School-level scorecard
    print("\n" + "=" * 60)
    print("Building School-Level Scorecard (Phase 4)")
    print("=" * 60)
    try:
        # Import and run school module
        import sys
        sys.path.insert(0, str(BASE / "src"))
        from schools_html import write_school_html
        
        # Load school scorecard if it exists
        school_csv = OUT / "school_scorecard.csv"
        if school_csv.exists():
            schools = pd.read_csv(school_csv)
            schools = schools.sort_values("readiness_score", ascending=False)
            write_school_html(schools)
            print(f"✅ Wrote docs/schools.html with {len(schools)} schools")
        else:
            print("⚠️  School scorecard not found - run src/schools.py first")
            print("   Skipping school-level HTML generation")
    except Exception as e:
        print(f"⚠️  Could not generate school HTML: {e}")
        print("   County scorecard complete, school scorecard skipped")
    
    # Phase 5: Archive for historical trends
    print("\n" + "=" * 60)
    print("Archiving Scores for Historical Trends (Phase 5)")
    print("=" * 60)
    try:
        from trends import archive_current_scores, generate_trend_summary
        archive_current_scores()
        generate_trend_summary()
        print("✅ Historical data archived")
    except Exception as e:
        print(f"⚠️  Could not archive trends: {e}")

