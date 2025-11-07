# Jax Health Readiness Scorecard (Phase 2)

**Automated weekly county-level health readiness scores for Jacksonville-area counties**

This scorecard ranks Duval, Clay, St. Johns, Nassau, and Baker counties on 5 evidence-based public health indicators using free, stable government data sources.

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

### 5. Respiratory Virus Activity (10 points - future)
- **Source**: CDC Respiratory Virus Surveillance
- **Metric**: State-level flu/COVID/RSV activity levels
- **Status**: Planned for Phase 3

## Scoring (Phase 2)

**Readiness Score** (0-100) = Primary Care (30) + Chronic Disease (30) + Air Quality (15) + Hazard Risk (15) + Respiratory (10)

- **Higher score = higher risk/need**
- Balanced weighting: healthcare access + chronic disease = 60%, environmental factors = 40%
- Transparent, evidence-based methodology

## Data Outputs

- **CSV**: `/data/scorecard.csv` – machine-readable weekly snapshot
- **HTML Table**: `/docs/index.html` – simple web view (GitHub Pages)

## Automation

- **Schedule**: Every Monday at 9:15am ET (14:15 UTC)
- **Platform**: GitHub Actions (`.github/workflows/pipeline.yml`)
- **Hosting**: GitHub Pages (free, no keys required)

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

### ✅ Phase 2: Enhanced Indicators (COMPLETED)
- ✅ **CDC PLACES**: County-level chronic disease prevalence (diabetes, obesity, asthma)
- ✅ **FEMA National Risk Index**: Community hazard risk baseline
- ⏳ **CDC Respiratory Virus Activity**: State-level weekly surveillance (placeholder ready)

### Phase 3: Real-time Signals (Next)
- **AirNow Daily API**: Rolling 7-day AQI averages (requires free API key)
- **CDC Respiratory Activity Levels**: Active weekly state flu/COVID/RSV tracking
- **Increase refresh frequency**: Daily updates instead of weekly

### Phase 4: School-Level Granularity (Goal)
- **Urban Institute Education Data API**: Public school roster with locations
- **Geocoding**: Map schools to census tracts
- **School-level scoring**: Assign tract/county indicators to 300+ individual schools
- **Enhanced visualization**: Interactive maps and school search

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
**Status**: Phase 2 Complete ✅ (5 indicators, enhanced scoring)

