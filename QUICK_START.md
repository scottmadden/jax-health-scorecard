# 🚀 Quick Start - Deploy in 5 Minutes

## Your MVP is Ready! ✅

Location: `/Users/scottmadden/Jax Health Scorecard`

---

## Deploy Now (Copy & Paste)

### Step 1: Create GitHub Repository (30 seconds)

```bash
cd "/Users/scottmadden/Jax Health Scorecard"
gh repo create jax-health-scorecard --public --source=. --remote=origin --push
```

**Don't have GitHub CLI?** Install: `brew install gh` then run `gh auth login`

---

### Step 2: Enable GitHub Pages (1 minute)

1. Open: https://github.com/YOUR_USERNAME/jax-health-scorecard/settings/pages
2. Set:
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs`
3. Click **Save**

**Your site will be live at**: `https://YOUR_USERNAME.github.io/jax-health-scorecard/`

---

### Step 3: Test Automation (1 minute)

1. Open: https://github.com/YOUR_USERNAME/jax-health-scorecard/actions
2. Click **build-scorecard** (left sidebar)
3. Click **Run workflow** → **Run workflow**
4. Wait 1-2 minutes for ✅ green checkmark

**Done!** Your scorecard updates every Monday at 9:15am ET automatically.

---

## What You Have

✅ **County Rankings** for Jacksonville area (Duval, Clay, St. Johns, Nassau, Baker)  
✅ **2 Health Indicators**: EPA Air Quality + HRSA Primary Care Shortage  
✅ **CSV Output**: `data/scorecard.csv` (machine-readable)  
✅ **HTML Table**: `docs/index.html` (web-friendly)  
✅ **Weekly Automation**: GitHub Actions (no manual work)  
✅ **Free Hosting**: GitHub Pages (unlimited bandwidth)

---

## Current Results (Nov 7, 2025)

| County | Readiness Score | Primary Care HPSA | Unhealthy AQI Days |
|--------|----------------|-------------------|-------------------|
| **Duval** | **55.2** (highest need) | 23/25 | 0 |
| Clay | 40.8 | 17/25 | - |
| St. Johns | 40.8 | 17/25 | - |
| Baker | 40.8 | 17/25 | 0 |
| Nassau | 26.4 | 11/25 | - |

**Key Insight**: Duval County has the highest primary care shortage (23/25 HPSA score)

---

## Files You Can Share Right Away

📄 **CSV for Analysis**: `data/scorecard.csv`  
🌐 **Web Table**: `docs/index.html` (view in browser)  
📋 **README**: Technical documentation  
📖 **PROJECT_SUMMARY**: Full roadmap & expansion plan

---

## Next Steps

### Immediate (Today)
- [ ] Deploy to GitHub (steps above)
- [ ] Share web link with 2-3 stakeholders
- [ ] Get initial feedback

### This Week
- [ ] Add to your portfolio/website
- [ ] Email Jacksonville school districts
- [ ] Post to LinkedIn/Twitter

### This Month (Phase 2)
- [ ] Add CDC PLACES (chronic disease data)
- [ ] Add FEMA National Risk Index (hazard baseline)
- [ ] Adjust scoring weights based on feedback

### Next Quarter (Phase 4)
- [ ] Expand to school-level (300+ schools)
- [ ] Add interactive map
- [ ] Create embeddable widget

---

## Get Help

- **Setup Issues**: See `SETUP.md` for detailed troubleshooting
- **Technical Details**: See `README.md` for data sources
- **Roadmap**: See `PROJECT_SUMMARY.md` for expansion plans

---

## Commands You'll Use

```bash
# Run pipeline locally
python3 src/pipeline.py

# Push updates
git add .
git commit -m "Update indicators"
git push

# View logs
git log --oneline

# Check status
git status
```

---

**Cost**: $0/month (100% free tier)  
**Maintenance**: 0 hours/week (fully automated)  
**Update Frequency**: Every Monday 9:15am ET

🎉 **You're done! Go deploy it.**

