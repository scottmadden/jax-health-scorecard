#!/usr/bin/env python3
"""
Phase 5: Historical Trend Tracking
Tracks score changes over time for both counties and schools.
"""
import pandas as pd
import pathlib
import json
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parents[1]
OUT = BASE / "data"
HISTORY_DIR = OUT / "history"
HISTORY_DIR.mkdir(exist_ok=True)


def archive_current_scores():
    """
    Archive current county and school scores with timestamp.
    Creates a daily snapshot for historical analysis.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    
    # Archive county scorecard
    county_csv = OUT / "scorecard.csv"
    if county_csv.exists():
        archive_path = HISTORY_DIR / f"county_{timestamp}.csv"
        df = pd.read_csv(county_csv)
        df.to_csv(archive_path, index=False)
        print(f"📦 Archived county scores to {archive_path}")
    
    # Archive school scorecard
    school_csv = OUT / "school_scorecard.csv"
    if school_csv.exists():
        archive_path = HISTORY_DIR / f"schools_{timestamp}.csv"
        df = pd.read_csv(school_csv)
        df.to_csv(archive_path, index=False)
        print(f"📦 Archived school scores to {archive_path}")


def calculate_trends(entity_type="schools", lookback_days=7):
    """
    Calculate score changes over time.
    
    Args:
        entity_type: "schools" or "county"
        lookback_days: How many days back to compare
    
    Returns:
        DataFrame with trend information
    """
    # Get all historical files
    pattern = f"{entity_type}_*.csv"
    history_files = sorted(HISTORY_DIR.glob(pattern))
    
    if len(history_files) < 2:
        print(f"⚠️  Not enough historical data yet ({len(history_files)} snapshots)")
        return pd.DataFrame()
    
    # Load most recent
    latest = pd.read_csv(history_files[-1])
    
    # Load comparison (7 days ago or oldest available)
    compare_idx = max(0, len(history_files) - lookback_days - 1)
    previous = pd.read_csv(history_files[compare_idx])
    
    # Calculate changes
    if entity_type == "schools":
        merge_col = "school_id"
    else:
        merge_col = "fips"
    
    merged = latest.merge(
        previous[[merge_col, "readiness_score"]],
        on=merge_col,
        how="left",
        suffixes=("", "_prev")
    )
    
    merged["score_change"] = merged["readiness_score"] - merged["readiness_score_prev"]
    merged["pct_change"] = (merged["score_change"] / merged["readiness_score_prev"]) * 100
    
    # Identify biggest movers
    merged = merged.sort_values("score_change", ascending=False)
    
    return merged


def generate_trend_summary():
    """Generate JSON summary of trends for visualization."""
    
    # County trends
    county_trends = calculate_trends("county", lookback_days=7)
    
    # School trends
    school_trends = calculate_trends("schools", lookback_days=7)
    
    summary = {
        "generated_at": datetime.utcnow().isoformat(),
        "counties": {
            "total": len(county_trends),
            "biggest_increase": {},
            "biggest_decrease": {}
        },
        "schools": {
            "total": len(school_trends),
            "biggest_increase": {},
            "biggest_decrease": {}
        }
    }
    
    if not county_trends.empty:
        top_increase = county_trends.iloc[0]
        summary["counties"]["biggest_increase"] = {
            "name": top_increase["county"],
            "change": float(top_increase["score_change"])
        }
        
        top_decrease = county_trends.iloc[-1]
        summary["counties"]["biggest_decrease"] = {
            "name": top_decrease["county"],
            "change": float(top_decrease["score_change"])
        }
    
    if not school_trends.empty:
        top_increase = school_trends.iloc[0]
        summary["schools"]["biggest_increase"] = {
            "name": top_increase["school_name"],
            "county": top_increase["county"],
            "change": float(top_increase["score_change"])
        }
        
        top_decrease = school_trends.iloc[-1]
        summary["schools"]["biggest_decrease"] = {
            "name": top_decrease["school_name"],
            "county": top_decrease["county"],
            "change": float(top_decrease["score_change"])
        }
    
    # Save trends summary
    trends_path = OUT / "trends.json"
    with open(trends_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"📊 Generated trend summary: {trends_path}")
    
    return summary


if __name__ == "__main__":
    print("=" * 60)
    print("Historical Trend Tracking (Phase 5)")
    print("=" * 60)
    
    # Archive current scores
    archive_current_scores()
    
    # Try to generate trends
    print("\nCalculating trends...")
    summary = generate_trend_summary()
    
    print("\n✅ Trend tracking initialized!")
    print(f"   📁 Archives saved to: data/history/")
    print(f"   📊 Trend summary: data/trends.json")
    print("\n   💡 Run this daily to build historical data for week-over-week analysis")

