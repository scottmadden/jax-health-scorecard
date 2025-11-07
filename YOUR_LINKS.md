# 🔗 Your Personal Links - scottmadden

## After Deployment

### GitHub Repository
📦 **Code & Data**: https://github.com/scottmadden/jax-health-scorecard

### Live Outputs (after enabling GitHub Pages)
🌐 **Web Table**: https://scottmadden.github.io/jax-health-scorecard/  
📊 **CSV Download**: https://github.com/scottmadden/jax-health-scorecard/blob/main/data/scorecard.csv  
📊 **Raw CSV Link**: https://raw.githubusercontent.com/scottmadden/jax-health-scorecard/main/data/scorecard.csv

### Management
⚙️ **Settings**: https://github.com/scottmadden/jax-health-scorecard/settings  
📄 **Pages Setup**: https://github.com/scottmadden/jax-health-scorecard/settings/pages  
🤖 **Actions/Automation**: https://github.com/scottmadden/jax-health-scorecard/actions  
📈 **Insights/Traffic**: https://github.com/scottmadden/jax-health-scorecard/graphs/traffic

---

## 🚀 Deploy Now (3 Options)

### Option 1: Use the Deploy Script (Easiest)
```bash
cd "/Users/scottmadden/Jax Health Scorecard"
chmod +x DEPLOY.sh
./DEPLOY.sh
```

### Option 2: Manual Command (Single Line)
```bash
cd "/Users/scottmadden/Jax Health Scorecard" && gh repo create jax-health-scorecard --public --source=. --remote=origin --push
```

### Option 3: Via GitHub Web Interface
1. Go to https://github.com/new
2. Name: `jax-health-scorecard`
3. Public repository
4. Don't initialize (we have files already)
5. Create repository
6. Run these commands:
```bash
cd "/Users/scottmadden/Jax Health Scorecard"
git remote add origin https://github.com/scottmadden/jax-health-scorecard.git
git branch -M main
git push -u origin main
```

---

## 📧 Share Links (after deployment)

### Quick Demo Email Template

**Subject**: Jacksonville County Health Scorecard - Live Demo

Hi [Name],

I've built an automated health readiness scorecard for Jacksonville-area counties (Duval, Clay, St. Johns, Nassau, Baker).

**View Live**: https://scottmadden.github.io/jax-health-scorecard/  
**Download CSV**: https://github.com/scottmadden/jax-health-scorecard/blob/main/data/scorecard.csv  
**GitHub Repo**: https://github.com/scottmadden/jax-health-scorecard

Key features:
- Ranks counties on EPA Air Quality + HRSA Primary Care Shortage
- Updates automatically every Monday
- Free, transparent federal data sources
- Expandable to school-level granularity

Current insight: Duval County has the highest primary care shortage (HPSA score 23/25).

Would love your feedback!

Best,  
Scott

---

## 🎯 Embed in Your Website/Portfolio

### Simple iframe
```html
<iframe 
  src="https://scottmadden.github.io/jax-health-scorecard/" 
  width="100%" 
  height="600" 
  frameborder="0">
</iframe>
```

### Link with preview
```markdown
[Jacksonville Health Scorecard](https://scottmadden.github.io/jax-health-scorecard/)
![Scorecard Preview](https://scottmadden.github.io/jax-health-scorecard/)
```

---

## 📊 Track Usage (after deployment)

- **Stars**: https://github.com/scottmadden/jax-health-scorecard/stargazers
- **Forks**: https://github.com/scottmadden/jax-health-scorecard/network/members
- **Traffic**: https://github.com/scottmadden/jax-health-scorecard/graphs/traffic (only you can see)

---

## 🔧 Update Your Scorecard Later

```bash
cd "/Users/scottmadden/Jax Health Scorecard"

# Make changes to src/pipeline.py
# ... edit file ...

# Run locally to test
python3 src/pipeline.py

# Commit and push
git add .
git commit -m "Add new indicator"
git push

# Automation will run next Monday, or trigger manually:
# → https://github.com/scottmadden/jax-health-scorecard/actions
```

---

**Ready when you are!** Run `./DEPLOY.sh` to get started. 🚀

