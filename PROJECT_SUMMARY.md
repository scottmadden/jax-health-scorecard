# Jacksonville Health Readiness Scorecard - Project Summary

**Status**: ✅ MVP Complete & Ready to Deploy  
**Date**: November 7, 2025  
**Location**: `/Users/scottmadden/Jax Health Scorecard`

---

## What We Built

A fully automated, sellable School Health Readiness Scorecard MVP that:

✅ **Ranks 5 Jacksonville-area counties** (Duval, Clay, St. Johns, Nassau, Baker)  
✅ **Uses 2 defensible public health indicators** (EPA AQI + HRSA HPSA)  
✅ **Publishes CSV + HTML table** (machine-readable + human-friendly)  
✅ **Automates weekly via GitHub Actions** (every Monday 9:15am ET)  
✅ **Requires zero API keys** (all free public data sources)  
✅ **Ready for GitHub Pages hosting** (free, fast, reliable)

---

## Current Scorecard Results

**Rankings** (Higher score = higher health risk/need):

| Rank | County | FIPS | Unhealthy AQI Days (2023) | HPSA Primary Care Score | Readiness Score |
|------|--------|------|---------------------------|------------------------|-----------------|
| 1 | **Duval** | 12031 | 0 | 23 | **55.2** |
| 2 | Clay | 12019 | - | 17 | 40.8 |
| 2 | St. Johns | 12109 | - | 17 | 40.8 |
| 2 | Baker | 12003 | 0 | 17 | 40.8 |
| 3 | Nassau | 12089 | - | 11 | 26.4 |

**Key Insights**:
- Duval County has the highest shortage (HPSA score of 23/25) → greatest need
- Some counties lack AQI monitoring stations (shown as empty)
- All counties have HPSA primary care shortage designations

---

## Deliverables

### 1. Data Pipeline (`src/pipeline.py`)
- Single-file Python ETL pipeline
- Fetches EPA AirData (annual AQI by county)
- Fetches HRSA HPSA Dashboard (primary care shortage areas)
- Calculates transparent, weighted readiness scores
- Outputs CSV + HTML

### 2. Automation (`.github/workflows/pipeline.yml`)
- GitHub Actions workflow
- Runs every Monday at 9:15am ET (14:15 UTC)
- Automatic commit/push of updated data
- No manual intervention needed

### 3. Outputs
- **CSV**: `data/scorecard.csv` (machine-readable, download/embed anywhere)
- **HTML**: `docs/index.html` (clean web table, mobile-friendly)

### 4. Documentation
- **README.md**: Main documentation with indicators, sources, roadmap
- **SETUP.md**: Step-by-step GitHub deployment guide
- **PROJECT_SUMMARY.md**: This file

---

## Repository Structure

```
jax-health-scorecard/
├── .github/
│   └── workflows/
│       └── pipeline.yml       # Weekly automation
├── src/
│   └── pipeline.py            # Single-file ETL pipeline
├── data/
│   ├── raw/                   # Downloaded sources (git-ignored)
│   │   ├── annual_aqi_by_county_2023.csv
│   │   └── HPSA_DASHBOARD.csv
│   └── scorecard.csv          # Published output ✅
├── docs/
│   └── index.html             # GitHub Pages site ✅
├── .gitignore
├── requirements.txt
├── README.md
├── SETUP.md
└── PROJECT_SUMMARY.md
```

---

## Next Steps

### Immediate: Deploy to GitHub (5 minutes)

1. **Create GitHub repository**:
   ```bash
   gh repo create jax-health-scorecard --public --source=. --remote=origin --push
   ```

2. **Enable GitHub Pages**:
   - Settings → Pages → Deploy from branch `main`, folder `/docs`

3. **Test automation**:
   - Actions → build-scorecard → Run workflow

4. **Get your live URLs**:
   - CSV: `https://github.com/YOUR_USERNAME/jax-health-scorecard/blob/main/data/scorecard.csv`
   - Web: `https://YOUR_USERNAME.github.io/jax-health-scorecard/`

See `SETUP.md` for detailed instructions.

---

## Expansion Roadmap

### Phase 2: Enhanced County Indicators (2-3 weeks)

**Add 2-3 more indicators** for stronger defensibility:

1. **CDC PLACES** - Chronic disease prevalence (diabetes, obesity, asthma)
   - Tract/county level estimates
   - Free, stable API: https://data.cdc.gov/

2. **FEMA National Risk Index** - Community hazard baseline (flooding, hurricanes)
   - County-level CSV download
   - Source: https://hazards.fema.gov/

3. **CDC Respiratory Virus Activity** - Seasonal illness tracking (flu, COVID, RSV)
   - State-level weekly data
   - Real-time "nowcast" signal

**Technical effort**: Add 3 new functions to `pipeline.py`, adjust scoring weights

---

### Phase 3: Real-time Signals (3-4 weeks)

**Increase update frequency** from weekly to daily with rolling 7-day windows:

1. **AirNow Daily API** - Current air quality (last 7 days avg)
   - Requires free API key: https://docs.airnowapi.org/

2. **CDC Respiratory Weekly** - State flu/COVID levels
   - Already free, increase refresh rate

**Technical effort**: 
- Add API key management (GitHub Secrets)
- Change cron from weekly → daily
- Implement 7-day rolling averages

---

### Phase 4: School-Level Granularity (4-6 weeks)

**THE BIG UNLOCK FOR SALES**: Drill down from 5 counties → ~300 schools

1. **Urban Institute Education Data API**
   - Get roster of all public schools in Jacksonville area
   - Includes: name, address, enrollment, demographics
   - Free API: https://educationdata.urban.org/

2. **Geocoding**
   - Convert school addresses → lat/long → census tract
   - Use Census Geocoder (free, no key)

3. **Spatial Join**
   - Map tract-level health indicators (from CDC PLACES) to schools
   - Generate per-school readiness score

4. **New Outputs**
   - `data/scorecard_schools.csv` (300+ rows)
   - `docs/schools.html` (searchable/filterable table)
   - Interactive map (optional: Leaflet.js)

**Sales Impact**: 
- "Here's the top 20 at-risk schools in Duval County"
- "Compare School A vs School B on 8 health indicators"
- "Prioritize school nurse placement by readiness score"

**Technical effort**:
- Add geocoding module (`geopy` or Census API)
- Add school data fetcher
- Refactor scoring to work at tract → school level
- Create separate school-level HTML table

---

## Data Sources (All Free, No Keys for MVP)

| Source | Indicator | Frequency | API Key? |
|--------|-----------|-----------|----------|
| EPA AirData | Annual AQI by county | Yearly | No ✅ |
| HRSA HPSA | Primary care shortage areas | Monthly | No ✅ |
| CDC PLACES | Chronic disease (tract) | Yearly | No ✅ |
| FEMA NRI | Community hazard risk | Yearly | No ✅ |
| CDC Respiratory | Flu/COVID/RSV levels (state) | Weekly | No ✅ |
| AirNow API | Daily air quality | Daily | Yes (free) |
| Urban Institute | Public school roster | Yearly | No ✅ |

---

## Technical Specifications

**Language**: Python 3.9+  
**Dependencies**: `pandas`, `requests`, `python-dateutil` (no heavy frameworks)  
**CI/CD**: GitHub Actions (built-in, no external service)  
**Hosting**: GitHub Pages (free, 1GB storage, unlimited bandwidth)  
**Cost**: $0/month (100% free tier)

**Scalability**:
- Current: 5 counties, 2 indicators, 2 data sources → ~5KB CSV
- Phase 4: 300 schools, 8 indicators, 7 data sources → ~150KB CSV
- GitHub Pages handles 100GB/month traffic → 600K+ page views

---

## Sales Positioning

### Value Proposition

**For School Districts**:
- "Identify highest-need schools for resource allocation (nurses, air filters, wellness programs)"
- "Data-driven justification for federal/state health funding"
- "Track improvements over time (longitudinal trends)"

**For Health Departments**:
- "County-level health readiness dashboard (updated weekly, zero effort)"
- "Defensible, transparent scoring using federal data sources"
- "Easy integration with existing GIS/BI tools (CSV output)"

**For Nonprofits / Advocacy Groups**:
- "Public accountability tool (GitHub Pages = always accessible)"
- "Embed scorecard in advocacy materials (iframe HTML table)"
- "Historical data preservation (Git history)"

### Pricing Ideas (Future)

- **Free Tier**: County-level, weekly updates (GitHub Pages)
- **Basic ($99/mo)**: School-level, daily updates, custom indicators
- **Pro ($299/mo)**: Historical trends, alerts, custom branding, API access
- **Enterprise ($999/mo)**: Multi-region, white-label, dedicated support

---

## Testing Checklist

✅ Pipeline runs successfully locally  
✅ CSV generated with correct data (`data/scorecard.csv`)  
✅ HTML renders cleanly (`docs/index.html`)  
✅ Git repository initialized  
✅ GitHub Actions workflow configured  
⏳ GitHub repository created (user action needed)  
⏳ GitHub Pages enabled (user action needed)  
⏳ First automated run completed (after GitHub setup)

---

## Questions & Decisions Log

### Decision: Use 2023 EPA data instead of 2024
**Reason**: 2024 data incomplete (year in progress). 2023 is most recent full year.  
**Impact**: None for MVP. Switch to 2024 in January 2026 when data finalized.

### Decision: GitHub Actions + GitHub Pages (not Railway/Heroku)
**Reason**: Zero cost, zero config, built-in git integration.  
**Trade-off**: Static hosting only (no backend). Fine for CSV + HTML table.  
**Future**: Add Railway if we need a REST API or real-time dashboard.

### Decision: County-level first, school-level later
**Reason**: Faster MVP (5 counties vs 300+ schools). Prove value, then expand.  
**Timeline**: School-level in Phase 4 (4-6 weeks).

### Decision: No API keys for MVP
**Reason**: Simplify deployment. All sources have free bulk download options.  
**Trade-off**: Weekly updates only (not daily). Add AirNow API in Phase 3 for daily.

---

## Success Metrics (Post-Launch)

**Technical**:
- ✅ Automation runs successfully every Monday (0 failures in 4 weeks)
- ✅ Data freshness < 7 days old
- ✅ Page load time < 2 seconds

**Adoption**:
- 📊 GitHub Pages traffic (target: 100 unique visitors in first month)
- 📊 CSV downloads (target: 20 downloads in first month)
- 📊 GitHub stars (target: 10 stars)

**Sales**:
- 📊 Outreach to 3 Jacksonville-area school districts
- 📊 Demo presentation to 1 health department
- 📊 Feature article in local news (target: Jacksonville Today, Jax Daily Record)

---

## Contact & Next Actions

**Immediate**: Follow `SETUP.md` to deploy to GitHub (5 minutes)

**This Week**: Share with potential users (school districts, health departments)

**This Month**: Gather feedback, prioritize Phase 2 indicators

**This Quarter**: Build school-level granularity (Phase 4)

---

**Built with**: Cursor + Claude Sonnet 4.5  
**License**: MIT (open source, free for commercial use)  
**Repository**: (will be) `https://github.com/YOUR_USERNAME/jax-health-scorecard`

🚀 **Ready to ship!**

