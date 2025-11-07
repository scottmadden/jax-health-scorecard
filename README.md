# Jax Health Readiness Scorecard (MVP)

**Automated weekly county-level health readiness scores for Jacksonville-area counties**

This MVP ranks Duval, Clay, St. Johns, Nassau, and Baker counties on timely, defensible public-health indicators using free, stable government data sources.

## Current Indicators

### 1. Air Quality Stress
- **Source**: EPA AirData Annual AQI by County
- **Metric**: Count of unhealthy-or-worse AQI days (2023, most recent complete year)
- **Weight**: 40 points max (capped at 30 days)
- **URL**: https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_county_YYYY.zip

### 2. Primary Care Shortage
- **Source**: HRSA Health Professional Shortage Area (HPSA) Dashboard
- **Metric**: Maximum Primary Care HPSA score in county (0-25 scale)
- **Weight**: 60 points max
- **URL**: https://data.hrsa.gov/DataDownload/DD_Files/HPSA_DASHBOARD.csv

## Scoring

**Readiness Score** = Air Quality Score (0-40) + HPSA Score (0-60)

- **Higher score = higher risk/need**
- Transparent, linear scaling
- Easily adjustable weights for future refinement

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

### Phase 2: Enhanced Indicators
- **CDC PLACES**: Small-area chronic disease estimates (tract/county level)
- **FEMA National Risk Index**: Community hazard baseline (county CSV)
- **CDC Respiratory Virus Activity**: State-level weekly surveillance for nowcasting

### Phase 3: Real-time Signals
- **AirNow Daily API**: Rolling 7-day AQI averages (requires free API key)
- **CDC Respiratory Activity Levels**: Weekly state trends

### Phase 4: School-Level Granularity
- **Urban Institute Education Data API**: Public school roster
- Geocode schools to counties/census tracts
- Map county/tract signals down to individual schools

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
**Status**: MVP Ready ✅

