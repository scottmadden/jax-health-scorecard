# Phase 2 Release Notes

**Release Date**: November 7, 2025  
**Version**: Phase 2 - Enhanced Indicators

---

## 🎉 What's New

### New Health Indicators (3 added)

1. **Chronic Disease Prevalence (30 points)**
   - Source: CDC PLACES (Local Data for Better Health)
   - Metrics: Average prevalence of diabetes, obesity, and current asthma
   - Updates: Annually from CDC
   - Impact: Major scoring component revealing population health burden

2. **Hazard Risk Assessment (15 points)**
   - Source: FEMA National Risk Index
   - Metrics: Composite risk score for natural hazards (hurricanes, flooding, etc.)
   - Updates: Annually from FEMA
   - Impact: Environmental risk baseline for emergency preparedness

3. **Respiratory Virus Activity (10 points - ready for Phase 3)**
   - Placeholder integrated into scoring system
   - Will track state-level flu/COVID/RSV activity
   - Status: Code framework complete, data integration pending

### Enhanced Scoring System

**Old (Phase 1)**: 100 points
- Air Quality: 40 points
- Primary Care Access: 60 points

**New (Phase 2)**: 100 points
- Primary Care Access: 30 points (30%)
- Chronic Disease: 30 points (30%)
- Air Quality: 15 points (15%)
- Hazard Risk: 15 points (15%)
- Respiratory Virus: 10 points (10% - future)

**Rationale**: More balanced assessment emphasizing healthcare + chronic disease burden (60%) with environmental factors (40%).

---

## 📊 New Rankings (Phase 2)

| Rank | County | Score | Key Findings |
|------|--------|-------|--------------|
| 1 | Duval | 57.6 | High HPSA (23/25) + High chronic disease (34.7%) |
| 2 | Clay | 50.4 | Highest chronic disease prevalence (35.7%) |
| 3 | Baker | 50.4 | Moderate HPSA + Moderate chronic disease (24.8%) |
| 4 | Nassau | 43.2 | Lower HPSA (11/25) + Moderate chronic disease (21.2%) |
| 5 | St. Johns | 35.8 | **Lowest chronic disease** (10.3% - best in region!) |

### Key Insights

- **St. Johns County** emerges as healthiest with only 10.3% chronic disease prevalence (67% lower than Clay County)
- **Clay County** has the highest chronic disease burden despite moderate healthcare access
- **Duval County** remains highest-need due to severe healthcare shortage + high chronic disease
- **Chronic disease data** adds significant nuance not visible in Phase 1 rankings

---

## 🔧 Technical Changes

### New Data Sources
- CDC PLACES API (Socrata Open Data)
- FEMA NRI via ArcGIS REST API
- No API keys required (free public endpoints)

### Pipeline Enhancements
- Added 2 new fetch functions: `fetch_cdc_places_county()`, `fetch_fema_nri()`
- Enhanced error handling with fallback data
- Progress logging during data fetch
- Updated HTML output with legend explaining scoring breakdown

### File Changes
- `src/pipeline.py`: +120 lines (new fetch functions + scoring rebalance)
- `docs/index.html`: Enhanced table with 5 indicators + scoring legend
- `data/scorecard.csv`: 4 new columns (chronic_disease_prev, risk_score, risk_rating, score_chronic, score_hazard)

---

## 🚀 Performance

- **Pipeline execution**: ~8-12 seconds (was ~5-7 seconds in Phase 1)
- **Data download**: One-time FEMA NRI cache (~17MB, subsequent runs use cache)
- **API calls**: 5 HTTP requests (EPA, HRSA, CDC PLACES, FEMA NRI + fallback)
- **Cost**: Still $0/month (all free public APIs)

---

## 🐛 Known Issues

1. **FEMA NRI showing "Not Rated"**
   - ArcGIS API may not be returning risk ratings correctly
   - Impact: Hazard scores default to 0 (no impact on rankings for now)
   - Fix planned: Alternative FEMA endpoint or CSV fallback

2. **Missing AQI data for some counties**
   - Clay, St. Johns, Nassau lack EPA monitoring stations
   - Impact: 0 points for air quality (neutral, not negative)
   - Not fixable: EPA doesn't monitor every county

---

## 📖 Documentation Updates

- ✅ README.md: Updated with Phase 2 indicators + scoring
- ✅ HTML table: Added legend explaining 5-indicator breakdown
- ✅ CSV output: Expanded with new data columns
- ⏳ PROJECT_SUMMARY.md: Update pending

---

## 🎯 Next Steps

### Immediate
- [x] Test locally
- [x] Update documentation
- [ ] Push to GitHub
- [ ] Monitor first automated run

### Phase 3 Priorities
1. Activate CDC Respiratory Virus tracking (state-level)
2. Add AirNow Daily API for real-time air quality
3. Increase update frequency from weekly → daily
4. Add historical trend visualization

### Phase 4 Goals
- School-level granularity (300+ schools)
- Interactive map visualization
- Custom alerting system
- API for programmatic access

---

## 🙏 Data Sources & Credits

- **CDC PLACES**: Centers for Disease Control and Prevention
- **FEMA NRI**: Federal Emergency Management Agency
- **EPA AirData**: Environmental Protection Agency
- **HRSA HPSA**: Health Resources and Services Administration

All data sources remain free, public, and programmatically accessible.

---

**Questions?** Open an issue at https://github.com/scottmadden/jax-health-scorecard

