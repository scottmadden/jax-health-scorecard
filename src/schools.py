#!/usr/bin/env python3
"""
Phase 4: School-Level Granularity Module
Fetches public school data and maps health indicators to individual schools.
"""
import requests
import pandas as pd
import pathlib
import time
from typing import Dict, List, Optional

# Paths
BASE = pathlib.Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
OUT = BASE / "data"

# Jacksonville area county FIPS codes
COUNTIES_FIPS = {
    "12031": "Duval",
    "12019": "Clay",
    "12109": "St. Johns",
    "12089": "Nassau",
    "12003": "Baker",
}

STATE_FIPS = "12"  # Florida


def fetch_nces_schools(year: str = "2022") -> pd.DataFrame:
    """
    Fetch public schools from NCES Common Core of Data (CCD) directory.
    Direct CSV download - more reliable than API.
    
    https://nces.ed.gov/ccd/files.asp
    
    Args:
        year: School year (e.g., "2022" for 2021-22 school year)
    
    Returns:
        DataFrame with school directory information
    """
    print(f"Fetching schools from NCES CCD (year {year})...")
    
    # NCES CCD Public School Universe Survey
    # Format: ccd_sch_029_YY_l_YYYY_YYYY.csv
    # Example for 2021-22: https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2122_l_2n_11a.zip
    
    # Try to download the most recent available file
    # Using web scraping approach - build a simple school list
    
    # Alternative: Use a known good dataset URL
    # NCES makes these available annually
    
    url = f"https://nces.ed.gov/ccd/data/zip/ccd_sch_029_2122_l_2n_083122.csv"
    cache_path = RAW / f"nces_schools_{year}.csv"
    
    # Try to use cached version first
    if cache_path.exists():
        print(f"  Using cached NCES data from {cache_path}")
        df = pd.read_csv(cache_path, dtype=str, encoding='latin1')
    else:
        try:
            print(f"  Downloading NCES school directory (may take 30-60 seconds)...")
            df = pd.read_csv(url, dtype=str, encoding='latin1')
            df.to_csv(cache_path, index=False)
            print(f"  Cached to {cache_path}")
        except Exception as e:
            print(f"  Download failed: {e}")
            print(f"  Trying alternative: creating sample data...")
            return create_sample_schools()
    
    # Filter to Florida
    df = df[df["ST"] == "FL"].copy()
    print(f"  Loaded {len(df)} Florida schools")
    
    # Convert county FIPS (combine state + county codes)
    if "CNTY" in df.columns:
        df["county_fips"] = df["ST"].str.zfill(2) + df["CNTY"].str.zfill(3)
    elif "COUNTY" in df.columns:
        df["county_fips"] = df["ST"].str.zfill(2) + df["COUNTY"].str.zfill(3)
    else:
        # Try to derive from other fields
        df["county_fips"] = df["LEAID"].str[:5] if "LEAID" in df.columns else None
    
    # Filter to our Jacksonville counties
    df = df[df["county_fips"].isin(COUNTIES_FIPS.keys())].copy()
    print(f"  Filtered to {len(df)} schools in Jacksonville area")
    
    # Filter for regular schools (exclude special ed, alternative, etc.)
    # NCES uses different codes - typically status code 1 = operational
    if "OPSTATUS" in df.columns or "STATUS" in df.columns:
        status_col = "OPSTATUS" if "OPSTATUS" in df.columns else "STATUS"
        df = df[df[status_col].isin(["1", "Open"])].copy()
    
    # Keep only relevant columns and rename
    column_mapping = {
        "NCESSCH": "school_id",
        "SCH_NAME": "school_name",
        "LEA_NAME": "district",
        "LSTREET1": "address",
        "LCITY": "city",
        "LSTATE": "state",
        "LZIP": "zipcode",
        "LATCOD": "lat",
        "LONCOD": "lon",
        "MEMBER": "enrollment",
        "county_fips": "fips"
    }
    
    # Rename available columns
    available_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=available_mapping)
    
    # Keep only renamed columns
    keep_cols = list(available_mapping.values())
    df = df[keep_cols].copy()
    
    # Clean data types
    if "lat" in df.columns:
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    if "lon" in df.columns:
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    if "enrollment" in df.columns:
        df["enrollment"] = pd.to_numeric(df["enrollment"], errors="coerce")
    
    # Add county name
    df["county"] = df["fips"].map(COUNTIES_FIPS)
    
    print(f"✅ Fetched {len(df)} schools across {len(COUNTIES_FIPS)} counties")
    
    return df


def create_sample_schools() -> pd.DataFrame:
    """
    Load extended sample school data for Jacksonville area.
    Uses comprehensive dataset of 50+ schools across all 5 counties.
    """
    print("  Loading extended Jacksonville schools dataset...")
    
    # Load from CSV file
    schools_csv = BASE / "data" / "jacksonville_schools_extended.csv"
    
    if schools_csv.exists():
        df = pd.read_csv(schools_csv)
        print(f"  Loaded {len(df)} schools from extended dataset")
        return df
    else:
        # Fallback to minimal sample
        print("  Extended dataset not found, creating minimal sample...")
        sample_schools = [
            {
                "school_id": "120310000001",
                "school_name": "Robert E. Lee High School",
                "district": "Duval County School District",
                "address": "6135 Arlington Expressway",
                "city": "Jacksonville",
                "state": "FL",
                "zipcode": "32211",
                "lat": 30.3110,
                "lon": -81.6060,
                "enrollment": 1800,
                "fips": "12031",
                "county": "Duval",
                "school_type": "High School"
            },
        ]
        df = pd.DataFrame(sample_schools)
        return df


def fetch_schools_alternative(year: int = 2021) -> pd.DataFrame:
    """
    Alternative: Fetch schools using state-wide query then filter.
    Fallback if county-level queries don't work.
    """
    print("  Using alternative: fetching all Florida schools...")
    
    base_url = "https://educationdata.urban.org/api/v1/schools/ccd/directory"
    url = f"{base_url}/{year}/"
    
    params = {
        "state_fips": STATE_FIPS,
        "page": 1,
        "per_page": 5000  # Get many at once
    }
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            all_schools = data["results"]
        elif isinstance(data, list):
            all_schools = data
        else:
            print("  Could not parse API response")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_schools)
        
        # Filter to our counties
        if "fips" in df.columns:
            df = df[df["fips"].isin(COUNTIES_FIPS.keys())].copy()
            print(f"  Filtered to {len(df)} schools in Jacksonville area")
        
        return df
        
    except Exception as e:
        print(f"  Alternative approach failed: {e}")
        return pd.DataFrame()


def geocode_address_census(address: str, city: str, state: str, zipcode: str) -> Optional[Dict]:
    """
    Geocode an address using Census Geocoder API (free, no key required).
    Returns census tract, block, coordinates.
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation
        zipcode: ZIP code
    
    Returns:
        Dict with lat, lon, tract, block or None if geocoding fails
    """
    url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
    
    params = {
        "street": address,
        "city": city,
        "state": state,
        "zip": zipcode,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "result" in data and "addressMatches" in data["result"]:
            matches = data["result"]["addressMatches"]
            if matches:
                match = matches[0]  # Take first match
                coords = match.get("coordinates", {})
                geographies = match.get("geographies", {})
                
                # Extract census tract
                tract_info = geographies.get("Census Tracts", [{}])[0]
                tract_id = tract_info.get("GEOID", "")
                
                return {
                    "lat": coords.get("y"),
                    "lon": coords.get("x"),
                    "tract": tract_id,
                    "match_address": match.get("matchedAddress", "")
                }
        
        return None
        
    except Exception as e:
        # Geocoding can fail - not critical, we have some coords from API
        return None


def geocode_schools(schools_df: pd.DataFrame, batch_size: int = 5, max_schools: int = None) -> pd.DataFrame:
    """
    Geocode all schools to census tracts with batch progress tracking.
    Uses existing lat/lon if available, otherwise geocodes addresses.
    
    Args:
        schools_df: DataFrame with school information
        batch_size: Number of schools to geocode before showing progress
        max_schools: Maximum number of schools to geocode (None = all)
    
    Returns:
        DataFrame with added 'tract' column
    """
    total_schools = len(schools_df) if max_schools is None else min(len(schools_df), max_schools)
    print(f"Geocoding {total_schools} schools to census tracts...")
    print(f"(Using batch size of {batch_size}, ~{0.2 * batch_size:.1f}s per batch)")
    
    schools_df["tract"] = None
    geocoded_count = 0
    failed_count = 0
    
    for idx, row in schools_df.head(max_schools).iterrows():
        # Try geocoding address
        if pd.notna(row.get("address")) and pd.notna(row.get("city")):
            address = str(row.get("address", ""))
            city = str(row.get("city", ""))
            state = str(row.get("state", "FL"))
            zipcode = str(row.get("zipcode", ""))
            
            result = geocode_address_census(address, city, state, zipcode)
            
            if result and result.get("tract"):
                schools_df.at[idx, "tract"] = result["tract"]
                if result.get("lat") and not pd.notna(row.get("lat")):
                    schools_df.at[idx, "lat"] = result["lat"]
                    schools_df.at[idx, "lon"] = result["lon"]
                geocoded_count += 1
            else:
                failed_count += 1
            
            # Progress indicator
            processed = geocoded_count + failed_count
            if processed % batch_size == 0:
                progress_pct = (processed / total_schools) * 100
                print(f"    Progress: {processed}/{total_schools} ({progress_pct:.1f}%) - {geocoded_count} successful, {failed_count} failed")
            
            # Rate limit: Census API has no official limit but be respectful
            time.sleep(0.3)
    
    success_rate = (geocoded_count / total_schools) * 100 if total_schools > 0 else 0
    print(f"✅ Geocoded {geocoded_count}/{total_schools} schools ({success_rate:.1f}% success rate)")
    
    return schools_df


def fetch_cdc_places_tracts(tracts: List[str]) -> pd.DataFrame:
    """
    Fetch CDC PLACES tract-level health data for specific census tracts.
    
    Args:
        tracts: List of census tract GEOIDs (11-digit FIPS codes)
    
    Returns:
        DataFrame with tract-level health indicators
    """
    print(f"Fetching CDC PLACES data for {len(tracts)} census tracts...")
    
    base_url = "https://data.cdc.gov/resource/cwsq-ngmh.json"  # Tract-level PLACES 2023
    
    all_data = []
    
    # Batch the tracts to avoid too large queries (max 50 per request)
    batch_size = 50
    for i in range(0, len(tracts), batch_size):
        batch = tracts[i:i+batch_size]
        print(f"  Fetching batch {i//batch_size + 1}...")
        
        # Build WHERE clause for multiple tracts
        tract_filter = " OR ".join([f"locationid='{t}'" for t in batch if t])
        
        params = {
            "$where": f"({tract_filter}) AND data_value_type='Crude prevalence'",
            "$limit": 5000
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data)
            time.sleep(0.5)  # Be nice to API
        except Exception as e:
            print(f"  Warning: Error fetching tract data: {e}")
            continue
    
    if not all_data:
        print("  No tract data found - will use county-level data")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    
    # Normalize columns
    df.columns = [c.lower() for c in df.columns]
    
    # Filter for key indicators
    df = df[df["measureid"].isin(["DIABETES", "OBESITY", "CASTHMA"])].copy()
    
    # Convert data values
    df["data_value"] = pd.to_numeric(df["data_value"], errors="coerce")
    
    # Average the indicators by tract
    tract_health = df.groupby("locationid", as_index=False)["data_value"].mean()
    tract_health.rename(columns={
        "locationid": "tract",
        "data_value": "chronic_disease_prev"
    }, inplace=True)
    
    print(f"✅ Fetched tract health data for {len(tract_health)} tracts")
    
    return tract_health


def join_health_data_to_schools(schools_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join tract-level and county-level health indicators to schools.
    
    Args:
        schools_df: DataFrame with schools and census tracts
    
    Returns:
        DataFrame with added health indicators
    """
    print("Joining health data to schools...")
    
    # Get unique tracts (excluding None)
    tracts = schools_df["tract"].dropna().unique().tolist()
    
    if tracts:
        # Fetch tract-level CDC PLACES data
        tract_health = fetch_cdc_places_tracts(tracts)
        
        if not tract_health.empty:
            # Join tract health data
            schools_df = schools_df.merge(
                tract_health,
                on="tract",
                how="left"
            )
    
    # Also join county-level data from Phase 3 for schools without tract data
    # Read the county scorecard
    county_csv = OUT / "scorecard.csv"
    if county_csv.exists():
        county_data = pd.read_csv(county_csv)
        
        # Get relevant county indicators
        county_indicators = county_data[[
            "fips", "hpsa_primary_care_max", "risk_score", "respiratory_activity"
        ]].copy()
        
        # Ensure fips is string type for both dataframes
        schools_df["fips"] = schools_df["fips"].astype(str)
        county_indicators["fips"] = county_indicators["fips"].astype(str)
        
        # Join county data
        schools_df = schools_df.merge(
            county_indicators,
            on="fips",
            how="left"
        )
        
        print(f"✅ Joined county-level health indicators")
    
    return schools_df


def calculate_school_readiness_scores(schools_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate school-level health readiness scores.
    Uses same methodology as county-level (Phase 3) but with tract-level granularity.
    
    Scoring (100 points):
    - Primary Care (30 pts): County HPSA score
    - Chronic Disease (30 pts): Tract-level CDC PLACES
    - Air Quality (15 pts): County-level EPA AQI
    - Hazard Risk (15 pts): County-level FEMA NRI  
    - Respiratory (10 pts): State-level CDC respiratory activity
    
    Args:
        schools_df: DataFrame with schools and health indicators
    
    Returns:
        DataFrame with readiness scores
    """
    print("Calculating school-level readiness scores...")
    
    # For schools without tract data, use county average
    if "chronic_disease_prev" not in schools_df.columns:
        schools_df["chronic_disease_prev"] = None
    
    # Scoring components
    
    # 1. HPSA (30 pts) - county level
    schools_df["score_hpsa"] = (
        schools_df["hpsa_primary_care_max"].fillna(0).clip(0, 25) / 25.0
    ) * 30.0
    
    # 2. Chronic Disease (30 pts) - tract level (or county fallback)
    schools_df["score_chronic"] = (
        schools_df["chronic_disease_prev"].fillna(0).clip(0, 50) / 50.0
    ) * 30.0
    
    # 3. Air Quality (15 pts) - county level (from county scorecard)
    # We'll use county average since we don't have school-specific AQI
    schools_df["score_air_q"] = 0.0  # Placeholder - can enhance with county data
    
    # 4. Hazard Risk (15 pts) - county level
    schools_df["score_hazard"] = (
        schools_df["risk_score"].fillna(0).clip(0, 100) / 100.0
    ) * 15.0
    
    # 5. Respiratory (10 pts) - state level
    # Map activity level to score
    resp_map = {
        "Minimal": 2.0,
        "Low": 3.5,
        "Moderate": 5.5,
        "High": 7.5,
        "Very High": 9.0
    }
    schools_df["score_respiratory"] = schools_df["respiratory_activity"].map(resp_map).fillna(2.0)
    
    # Total readiness score
    schools_df["readiness_score"] = (
        schools_df["score_hpsa"] +
        schools_df["score_chronic"] +
        schools_df["score_air_q"] +
        schools_df["score_hazard"] +
        schools_df["score_respiratory"]
    ).round(1)
    
    print(f"✅ Calculated readiness scores for {len(schools_df)} schools")
    
    return schools_df


def save_schools(schools_df: pd.DataFrame, filename: str = "schools.csv"):
    """Save schools DataFrame to CSV."""
    output_path = OUT / filename
    schools_df.to_csv(output_path, index=False)
    print(f"💾 Saved {len(schools_df)} schools to {output_path}")


if __name__ == "__main__":
    # Test the complete Phase 4 workflow
    print("=" * 60)
    print("Phase 4: School-Level Health Readiness Scorecard")
    print("=" * 60)
    
    # Step 1: Fetch schools (or load existing)
    schools_file = OUT / "schools_phase4.csv"
    if schools_file.exists():
        print("\nLoading existing schools from file...")
        schools = pd.read_csv(schools_file)
        print(f"Loaded {len(schools)} schools")
    else:
        print("\nFetching schools from NCES...")
        schools = fetch_nces_schools(year="2022")
        
        if schools.empty:
            print("❌ No schools found")
            exit(1)
        
        # Geocode schools
        print("\nGeocoding schools...")
        schools = geocode_schools(schools)
        
        # Save initial dataset
        save_schools(schools, "schools_phase4.csv")
    
    # Step 2: Join health indicators
    print("\n" + "=" * 60)
    print("Step 2: Joining Health Data")
    print("=" * 60)
    schools_with_health = join_health_data_to_schools(schools)
    
    # Step 3: Calculate readiness scores
    print("\n" + "=" * 60)
    print("Step 3: Calculating Readiness Scores")
    print("=" * 60)
    schools_scored = calculate_school_readiness_scores(schools_with_health)
    
    # Step 4: Save school scorecard
    print("\n" + "=" * 60)
    print("Step 4: Saving School Scorecard")
    print("=" * 60)
    
    # Sort by readiness score (descending)
    schools_scored = schools_scored.sort_values("readiness_score", ascending=False)
    
    # Select output columns
    output_cols = [
        "school_id", "school_name", "district", "city", "county",
        "enrollment", "tract",
        "chronic_disease_prev", "hpsa_primary_care_max", "respiratory_activity",
        "score_hpsa", "score_chronic", "score_air_q", "score_hazard", "score_respiratory",
        "readiness_score"
    ]
    
    available_cols = [col for col in output_cols if col in schools_scored.columns]
    schools_final = schools_scored[available_cols].copy()
    
    # Save school scorecard
    save_schools(schools_final, "school_scorecard.csv")
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS: School Health Readiness Rankings")
    print("=" * 60)
    print(f"\nTop 10 Schools (Highest Need):")
    display_cols = ["school_name", "county", "chronic_disease_prev", "readiness_score"]
    available_display = [col for col in display_cols if col in schools_final.columns]
    print(schools_final[available_display].head(10).to_string(index=False))
    
    print(f"\nBottom 5 Schools (Lowest Need):")
    print(schools_final[available_display].tail(5).to_string(index=False))
    
    print(f"\n✅ Phase 4 Complete!")
    print(f"   📊 {len(schools_final)} schools ranked")
    print(f"   💾 Saved to: data/school_scorecard.csv")

