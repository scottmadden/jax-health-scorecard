# Setup Guide: Deploying to GitHub

This guide walks you through deploying your Jacksonville Health Readiness Scorecard to GitHub with automated weekly updates.

## Prerequisites

- GitHub account
- GitHub CLI (`gh`) installed (or use GitHub web interface)
- Git repository already initialized locally ✅

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

```bash
cd "/Users/scottmadden/Jax Health Scorecard"
gh repo create jax-health-scorecard --public --source=. --remote=origin --push
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `jax-health-scorecard`
3. Description: "Automated weekly county health readiness scores for Jacksonville-area counties"
4. Set to **Public**
5. Do NOT initialize with README (we already have one)
6. Click "Create repository"
7. Follow the instructions to push an existing repository:

```bash
cd "/Users/scottmadden/Jax Health Scorecard"
git remote add origin https://github.com/YOUR_USERNAME/jax-health-scorecard.git
git branch -M main
git push -u origin main
```

## Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll down to **Pages** section (left sidebar under "Code and automation")
4. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
5. Click **Save**

GitHub will build your site. After a minute or two, your scorecard will be live at:
```
https://YOUR_USERNAME.github.io/jax-health-scorecard/
```

## Step 3: Test the Automation

The GitHub Action is configured to run every Monday at 9:15am ET. You can manually trigger it to test:

1. Go to **Actions** tab in your repository
2. Click on **build-scorecard** workflow (left sidebar)
3. Click **Run workflow** button (right side)
4. Select `main` branch
5. Click **Run workflow**

The workflow will:
- Fetch latest EPA AQI and HRSA HPSA data
- Generate updated `data/scorecard.csv`
- Generate updated `docs/index.html`
- Commit and push changes automatically

## Step 4: Verify Everything Works

After the workflow completes (1-2 minutes):

1. Check the **Actions** tab for green checkmark ✅
2. View the commit history - you should see a new commit: "Update scorecard [skip ci]"
3. Visit your GitHub Pages site to see the live table
4. Download the CSV from: `https://github.com/YOUR_USERNAME/jax-health-scorecard/blob/main/data/scorecard.csv`

## Troubleshooting

### Workflow Fails with Permission Error

Make sure your repository has Actions with write permissions:
1. Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Save

### GitHub Pages Not Building

- Wait 2-3 minutes after enabling Pages
- Check Settings → Pages for any error messages
- Ensure `/docs/index.html` exists in the `main` branch

### Data Not Updating

- Check the Actions tab for error logs
- Verify the EPA and HRSA data sources are still available
- The workflow runs every Monday at 14:15 UTC (9:15am ET)

## Next Steps

### Immediate Enhancements

1. **Add more counties**: Edit `COUNTIES` list in `src/pipeline.py`
2. **Adjust scoring weights**: Modify scoring logic in `build_scorecard()` function
3. **Change update schedule**: Edit cron schedule in `.github/workflows/pipeline.yml`

### Phase 2: Additional Data Sources

Already documented in the main README.md:
- CDC PLACES (chronic disease estimates)
- FEMA National Risk Index (hazard baseline)
- CDC Respiratory Virus Activity (nowcast)

### Phase 3: School-Level Granularity

Use Urban Institute Education Data API to:
1. Get public school roster with locations
2. Geocode schools to census tracts
3. Map tract-level health indicators to schools
4. Generate school-level scorecard

## Repository Structure

```
jax-health-scorecard/
├── .github/workflows/
│   └── pipeline.yml          # Weekly automation (GitHub Actions)
├── src/
│   └── pipeline.py           # ETL pipeline (single file)
├── data/
│   ├── raw/                  # Downloaded source files (cached, git-ignored)
│   └── scorecard.csv         # Published output (committed)
├── docs/
│   └── index.html            # GitHub Pages site
├── .gitignore
├── requirements.txt
├── README.md                 # Main documentation
└── SETUP.md                  # This file
```

## Support

For questions or issues:
1. Check the Actions logs for error details
2. Review the data source documentation (links in README.md)
3. Open an issue in the GitHub repository

---

**Status**: Ready to deploy! 🚀

