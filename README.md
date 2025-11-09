# Jax Health Readiness Scorecard (Phase 4)

**Automated DAILY health readiness scores for 51 individual schools + 5 counties**

This scorecard provides tract-level health precision for Jacksonville-area schools, enabling data-driven resource allocation at the school level. Ranks 51 schools across Duval, Clay, St. Johns, Nassau, and Baker counties.

## Current Indicators (Phase 2)

### 1. Primary Care Access (30 points)
- **Source**: HRSA Health Professional Shortage Area (HPSA) Dashboard
- **Metric**: Maximum Primary Care HPSA score in county (0-25 scale)
- **URL**: https://data.hrsa.gov/DataDownload/DD_Files/HPSA_DASHBOARD.csv

### 2. Chronic Disease Prevalence (30 points)
- **Source**: CDC PLACES (Local Data for Better Health)
- **Metric**: Average prevalence of diabetes, obesity, and asthma
- **URL**: https://data.cdc.gov/resource/duw2-7jbt.json

### 3. Air Quality Stress (15 points)
- **Source**: EPA AirData Annual AQI by County
- **Metric**: Count of unhealthy-or-worse AQI days (2023)
- **URL**: https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_county_YYYY.zip

### 4. Hazard Risk (15 points)
- **Source**: FEMA National Risk Index
- **Metric**: Composite risk score for natural hazards
- **URL**: https://hazards.fema.gov/nri/data-resources

### 5. Respiratory Virus Activity (10 points) ✅ **ACTIVE**
- **Source**: CDC Respiratory Virus Surveillance (FluView)
- **Metric**: State-level flu/COVID/RSV activity levels (Minimal/Low/Moderate/High/Very High)
- **Status**: **Live in Phase 3** - Updates daily with state-wide respiratory illness activity

## Scoring (Phase 2)

**Readiness Score** (0-100) = Primary Care (30) + Chronic Disease (30) + Air Quality (15) + Hazard Risk (15) + Respiratory (10)

- **Higher score = higher risk/need**
- Balanced weighting: healthcare access + chronic disease = 60%, environmental factors = 40%
- Transparent, evidence-based methodology

## Data Outputs (Phase 4)

### County-Level
- **CSV**: `/data/scorecard.csv` – 5 counties with aggregate indicators
- **HTML**: `/docs/index.html` – County comparison table

### School-Level ✨ NEW
- **CSV**: `/data/school_scorecard.csv` – 51 schools with tract-level health data
- **HTML**: `/docs/schools.html` – Interactive, searchable school table
- **Features**: Search, filter by county/score, sortable columns, responsive design

## Automation (Phase 3)

- **Schedule**: **Daily** at 9:15am ET (14:15 UTC) - Real-time health signals
- **Platform**: GitHub Actions (`.github/workflows/pipeline.yml`)
- **Hosting**: GitHub Pages (free)
- **Optional**: Add `AIRNOW_API_KEY` GitHub secret for real-time air quality data

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run pipeline
python src/pipeline.py

# Outputs:
# - data/scorecard.csv
# - docs/index.html
```

### GitHub Setup

1. **Create repository**:
```bash
git init
git add .
git commit -m "MVP: pipeline + action"
gh repo create jax-health-scorecard --public --source=. --remote=origin --push
```

2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: Deploy from branch
   - Branch: `main`, Folder: `/docs`
   - Save

3. **Manual trigger** (first run):
   - Go to Actions → `build-scorecard` → Run workflow

## Roadmap

### ✅ Phase 4: School-Level Granularity (COMPLETED)
- ✅ **51 individual schools ranked**: Expanded from 5 counties to 51 schools
- ✅ **Census tract geocoding**: 72.5% success rate (37/51 schools mapped)
- ✅ **Tract-level health data**: CDC PLACES chronic disease by neighborhood
- ✅ **Interactive HTML table**: Search, filter, sort functionality
- ✅ **School statistics dashboard**: Total schools, geocoding rate, averages
- ✅ **Dual navigation**: County ↔ School seamless switching

### Phase 5: Polish & Promote (Next)
- Historical trend tracking (week-over-week score changes)
- Email alerting system (notify when scores spike)
- Interactive map visualization (Leaflet.js with school markers)
- Custom report generation (PDF exports)
- Enhanced analytics dashboard (charts, graphs)
- Marketing & outreach to stakeholders

## Data Sources & Credits

All data sources are free, public, and programmatically accessible:

- **EPA**: Environmental Protection Agency AirData system
- **HRSA**: Health Resources and Services Administration
- **CDC**: Centers for Disease Control and Prevention
- **FEMA**: Federal Emergency Management Agency

## Technical Stack

- **Language**: Python 3.11+
- **Dependencies**: pandas, requests, python-dateutil
- **CI/CD**: GitHub Actions
- **Hosting**: GitHub Pages
- **No API keys required** (for MVP)

## Architecture

```
jax-health-scorecard/
├── src/
│   └── pipeline.py          # Single-file ETL pipeline
├── data/
│   ├── raw/                 # Downloaded source files (cached)
│   └── scorecard.csv        # Published scorecard
├── docs/
│   └── index.html           # Public web table
├── .github/
│   └── workflows/
│       └── pipeline.yml     # Weekly automation
├── requirements.txt
└── README.md
```

## License

MIT License - free for commercial and non-commercial use.

## Contact

For questions or partnership inquiries about expanding to school-level data or additional indicators, please open an issue in this repository.

---

**Last Updated**: November 2025  
**Status**: Phase 4 Complete ✅ (51 schools ranked, tract-level precision, interactive search/filter)

