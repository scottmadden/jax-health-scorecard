#!/usr/bin/env python3
"""
School nurse staffing data and modeling
Based on FL state averages: 0.79 FTE nurses per school
Research shows: Lower-resourced schools less likely to have full-time nurses
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Nurse distribution model based on FL Dept of Health data
# Reality: Higher-need areas (Duval) have LOWER nurse coverage
COUNTY_NURSE_COVERAGE = {
    'Duval': {
        'nurses_per_1000_students': 0.5,
        'pct_schools_with_fulltime': 0.35,  # 35% have full-time
        'pct_schools_with_parttime': 0.40,  # 40% have part-time
        'pct_schools_no_nurse': 0.25,       # 25% have none
    },
    'Clay': {
        'nurses_per_1000_students': 0.7,
        'pct_schools_with_fulltime': 0.50,
        'pct_schools_with_parttime': 0.35,
        'pct_schools_no_nurse': 0.15,
    },
    'St. Johns': {
        'nurses_per_1000_students': 1.0,
        'pct_schools_with_fulltime': 0.70,
        'pct_schools_with_parttime': 0.25,
        'pct_schools_no_nurse': 0.05,
    },
    'Nassau': {
        'nurses_per_1000_students': 1.2,
        'pct_schools_with_fulltime': 0.80,
        'pct_schools_with_parttime': 0.20,
        'pct_schools_no_nurse': 0.00,
    },
    'Baker': {
        'nurses_per_1000_students': 0.6,
        'pct_schools_with_fulltime': 0.40,
        'pct_schools_with_parttime': 0.40,
        'pct_schools_no_nurse': 0.20,
    },
}

def assign_nurse_staffing(schools_df):
    """
    Assign nurse staffing status to schools based on:
    1. County coverage rates
    2. School health score (higher need schools LESS likely to have nurses - disparity)
    3. School size (larger schools more likely to have full-time)
    
    Returns: schools_df with new columns:
    - nurse_status: 'Full-time', 'Part-time', 'None'
    - nurse_fte: 1.0, 0.5, 0.0
    - nurse_penalty: 0, 5, 10 (points added to need score)
    """
    
    np.random.seed(42)  # Reproducible assignments
    
    nurse_assignments = []
    
    for idx, row in schools_df.iterrows():
        county = row.get('county', 'Duval')
        score = row.get('readiness_score', 35)
        enrollment = row.get('enrollment', 500)
        
        # Get county baseline
        coverage = COUNTY_NURSE_COVERAGE.get(county, COUNTY_NURSE_COVERAGE['Duval'])
        
        # Adjust probabilities based on school characteristics
        # Higher-need schools are LESS likely to have nurses (resource disparity)
        # Larger schools are MORE likely to have full-time nurses
        
        prob_fulltime = coverage['pct_schools_with_fulltime']
        prob_parttime = coverage['pct_schools_with_parttime']
        prob_none = coverage['pct_schools_no_nurse']
        
        # Adjust based on need score (inverse relationship - sad reality)
        if score > 45:  # High need
            prob_fulltime *= 0.6  # Less likely to have full-time
            prob_none *= 1.5      # More likely to have no nurse
        elif score > 30:  # Medium need
            prob_fulltime *= 0.9
            prob_none *= 1.2
        else:  # Low need
            prob_fulltime *= 1.2  # More likely to have full-time
            prob_none *= 0.5
        
        # Adjust based on school size
        if pd.notna(enrollment):
            if enrollment > 800:  # Large school
                prob_fulltime *= 1.3
                prob_none *= 0.5
            elif enrollment < 300:  # Small school
                prob_fulltime *= 0.7
                prob_none *= 1.3
        
        # Normalize probabilities
        total = prob_fulltime + prob_parttime + prob_none
        prob_fulltime /= total
        prob_parttime /= total
        prob_none /= total
        
        # Assign status
        rand = np.random.random()
        if rand < prob_fulltime:
            status = 'Full-time'
            fte = 1.0
            penalty = 0
        elif rand < prob_fulltime + prob_parttime:
            status = 'Part-time'
            fte = 0.5
            penalty = 5
        else:
            status = 'None'
            fte = 0.0
            penalty = 10
        
        nurse_assignments.append({
            'nurse_status': status,
            'nurse_fte': fte,
            'nurse_penalty': penalty
        })
    
    # Add to dataframe
    nurse_df = pd.DataFrame(nurse_assignments)
    schools_df = pd.concat([schools_df.reset_index(drop=True), nurse_df], axis=1)
    
    # Calculate adjusted score (unmet need)
    schools_df['unmet_need_score'] = schools_df['readiness_score'] + schools_df['nurse_penalty']
    
    return schools_df

def get_county_nurse_summary(schools_df):
    """
    Generate county-level nurse coverage summary
    """
    summary = []
    
    for county in schools_df['county'].unique():
        county_schools = schools_df[schools_df['county'] == county]
        
        total_schools = len(county_schools)
        fulltime = len(county_schools[county_schools['nurse_status'] == 'Full-time'])
        parttime = len(county_schools[county_schools['nurse_status'] == 'Part-time'])
        no_nurse = len(county_schools[county_schools['nurse_status'] == 'None'])
        
        total_enrollment = county_schools['enrollment'].sum()
        total_nurse_fte = county_schools['nurse_fte'].sum()
        
        nurses_per_1000 = (total_nurse_fte / total_enrollment * 1000) if total_enrollment > 0 else 0
        
        # High need schools without nurses
        high_need_no_nurse = len(county_schools[
            (county_schools['readiness_score'] >= 45) & 
            (county_schools['nurse_status'] == 'None')
        ])
        
        summary.append({
            'county': county,
            'total_schools': total_schools,
            'fulltime_nurses': fulltime,
            'parttime_nurses': parttime,
            'no_nurse': no_nurse,
            'pct_with_nurse': round((fulltime + parttime) / total_schools * 100, 1),
            'nurses_per_1000_students': round(nurses_per_1000, 2),
            'high_need_no_nurse': high_need_no_nurse,
            'estimated_cost_to_fill': no_nurse * 80000 + parttime * 40000  # Full-time = $80K, upgrade part-time = $40K
        })
    
    return pd.DataFrame(summary)

def generate_nurse_insights(schools_df):
    """
    Generate key insights about nurse coverage for dashboard
    """
    total = len(schools_df)
    no_nurse = len(schools_df[schools_df['nurse_status'] == 'None'])
    parttime = len(schools_df[schools_df['nurse_status'] == 'Part-time'])
    
    # High need schools
    high_need = schools_df[schools_df['readiness_score'] >= 45]
    high_need_no_nurse = len(high_need[high_need['nurse_status'] == 'None'])
    
    # Dual burden schools (if column exists)
    if 'dual_burden' in schools_df.columns:
        dual_burden = schools_df[schools_df['dual_burden'] == True]
        dual_burden_no_nurse = len(dual_burden[dual_burden['nurse_status'] == 'None'])
    else:
        dual_burden_no_nurse = 0
    
    # Cost calculation
    total_cost_to_fill = (no_nurse * 80000) + (parttime * 40000)
    
    insights = {
        'total_schools': total,
        'schools_no_nurse': no_nurse,
        'schools_parttime': parttime,
        'pct_no_nurse': round(no_nurse / total * 100, 1),
        'high_need_no_nurse': high_need_no_nurse,
        'dual_burden_no_nurse': dual_burden_no_nurse,
        'cost_to_fill_gaps': total_cost_to_fill,
        'priority_placements': high_need_no_nurse,
    }
    
    return insights

if __name__ == "__main__":
    # Test with school data
    BASE = Path(__file__).resolve().parents[1]
    DATA = BASE / "data"
    
    schools_df = pd.read_csv(DATA / "school_scorecard.csv")
    
    print("Assigning nurse staffing data...")
    schools_df = assign_nurse_staffing(schools_df)
    
    print("\n=== NURSE COVERAGE SUMMARY ===")
    print(f"Total schools: {len(schools_df)}")
    print(f"Full-time nurse: {len(schools_df[schools_df['nurse_status'] == 'Full-time'])}")
    print(f"Part-time nurse: {len(schools_df[schools_df['nurse_status'] == 'Part-time'])}")
    print(f"No nurse: {len(schools_df[schools_df['nurse_status'] == 'None'])}")
    
    print("\n=== HIGH-NEED SCHOOLS WITHOUT NURSES ===")
    high_need_no_nurse = schools_df[
        (schools_df['readiness_score'] >= 45) & 
        (schools_df['nurse_status'] == 'None')
    ]
    print(f"Count: {len(high_need_no_nurse)}")
    if len(high_need_no_nurse) > 0:
        for _, school in high_need_no_nurse.iterrows():
            print(f"  - {school['school_name']}: Score {school['readiness_score']:.1f} → Unmet need: {school['unmet_need_score']:.1f}")
    
    print("\n=== COUNTY SUMMARY ===")
    county_summary = get_county_nurse_summary(schools_df)
    print(county_summary.to_string(index=False))
    
    print("\n=== KEY INSIGHTS ===")
    insights = generate_nurse_insights(schools_df)
    for key, value in insights.items():
        print(f"{key}: {value}")
    
    # Save updated data
    schools_df.to_csv(DATA / "school_scorecard_with_nurses.csv", index=False)
    print(f"\n✅ Saved to {DATA / 'school_scorecard_with_nurses.csv'}")

