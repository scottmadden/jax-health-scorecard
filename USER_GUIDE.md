# User Guide - Jacksonville Health Scorecard

**Quick guide to understanding and using the scorecard**

---

## 📊 What Is This?

The Jacksonville Health Readiness Scorecard is an automated tool that ranks schools and counties in the Jacksonville area on health indicators that affect student wellbeing.

**Two Views:**
1. **County View** - Compare 5 counties at a glance
2. **School View** - Rank 93 individual K-12 schools

---

## 🎯 How to Use the Scorecard

### **County Scorecard** (Start Here)

**URL:** https://scottmadden.github.io/jax-health-scorecard/

**What you see:**
- 5 Jacksonville-area counties ranked by health readiness
- Higher score = higher health risk/need
- Current FL respiratory virus activity (statewide)

**How to read it:**
- **Duval (50.4)**: Highest need - greatest healthcare shortage + chronic disease
- **Nassau (27.9)**: Lowest need - best healthcare access + lowest disease burden

**Use cases:**
- Compare counties for regional planning
- See aggregate health trends
- Link to detailed school data

---

### **School Scorecard** (Detailed View)

**URL:** https://scottmadden.github.io/jax-health-scorecard/schools.html

**Features:**

**1. Search Box**
- Type school name (e.g., "Pinedale")
- Type city (e.g., "Orange Park")
- Type district (e.g., "Duval")
- Results filter instantly

**2. County Filter**
- Dropdown: Select a specific county
- See only schools from that county
- Useful for district-specific analysis

**3. Score Filter**
- **High Need (45+)**: Urgent intervention recommended
- **Medium Need (30-45)**: Moderate attention needed
- **Low Need (<30)**: Relatively healthy

**4. Sortable Columns**
- Click any column header to sort
- Click again to reverse order
- Examples:
  - Sort by "Chronic Disease" → See disease burden
  - Sort by "Enrollment" → See largest schools
  - Sort by "Readiness Score" → See ranked order

---

## 📈 Understanding the Scores

### **Readiness Score (0-100 points)**

**Total = 100 points maximum:**
- Primary Care Access: 30 pts
- Chronic Disease: 30 pts
- Air Quality: 15 pts
- Hazard Risk: 15 pts
- Respiratory Virus: 10 pts

**Interpretation:**
- **45-100**: High need - Priority intervention recommended
- **30-44**: Medium need - Monitoring and moderate support
- **0-29**: Low need - Maintain current programs

### **What the Indicators Mean**

**1. Primary Care Access (0-30 points)**
- Source: HRSA Health Professional Shortage Area (HPSA)
- Measures: Availability of doctors/primary care in county
- Higher score = Harder to access healthcare
- Example: Duval 27.6 (severe shortage), Nassau 13.2 (less shortage)

**2. Chronic Disease Prevalence (0-30 points)**
- Source: CDC PLACES (census tract level)
- Measures: % of population with diabetes, obesity, or asthma
- Higher score = More chronic disease in neighborhood
- Example: Darnell-Cookman tract 31.5%, St. Augustine tract 16.4%

**3. Air Quality (0-15 points)**
- Source: EPA AirData
- Measures: Days with unhealthy air quality
- Higher score = More air pollution
- Note: Not all counties have monitoring stations

**4. Hazard Risk (0-15 points)**
- Source: FEMA National Risk Index
- Measures: Risk of natural disasters (hurricanes, flooding)
- Higher score = Greater hazard exposure
- Note: Currently showing limited data

**5. Respiratory Virus Activity (0-10 points)**
- Source: CDC Respiratory Surveillance
- Measures: State-wide flu/COVID/RSV activity
- Higher score = More respiratory illness circulating
- Same for all schools (statewide measure)

---

## 🔍 Finding Specific Information

### **"Which schools need school nurses most?"**

1. Go to school scorecard
2. Filter by "High Need (45+)"
3. Sort by Readiness Score (descending)
4. Top 10 schools = highest priority

**Current answer:** Darnell-Cookman, Lavilla, Raines HS (all Duval, 45-48 scores)

### **"Which elementary schools have the highest chronic disease?"**

1. Search for "Elementary"
2. Click "Chronic Disease %" column header
3. Schools with highest % appear at top

**Current answer:** Pinedale Elem (22.9%), Highlands Elem (21.7%)

### **"How does my school compare to others in the county?"**

1. Filter by your county (e.g., "Clay")
2. Find your school in the list
3. Note your rank among county schools

**Example:** Orange Park HS ranks #1 in Clay County (33.6 score)

### **"Which county is healthiest overall?"**

1. Go to county scorecard
2. Look at bottom of table (lowest scores)

**Current answer:** Nassau County (27.9 score) - lowest need

---

## 📥 Downloading the Data

### **CSV Downloads (For Your Own Analysis)**

**County Data:**
https://github.com/scottmadden/jax-health-scorecard/blob/main/data/scorecard.csv

**School Data:**
https://github.com/scottmadden/jax-health-scorecard/blob/main/data/school_scorecard.csv

### **What's in the CSV?**

**School CSV (93 rows, 16 columns):**
- School ID, name, district, location
- Enrollment, census tract
- Chronic disease %, HPSA score
- Individual indicator scores (0-30 pts each)
- Total readiness score (0-100 pts)

**How to use:**
- Open in Excel/Google Sheets
- Join with your own data (test scores, attendance, budgets)
- Create custom visualizations
- Run statistical analyses
- Build custom reports

---

## ❓ Frequently Asked Questions

**Q: How often does the data update?**
A: Daily at 9:15am ET. All 5 indicators refresh, though some (like chronic disease) only change annually.

**Q: Why does my school not have tract data?**
A: Geocoding failed for that address. The school uses county-level data instead (less precise but still valid).

**Q: Can I get data for my city/state?**
A: Not yet, but the code is open source! Fork the GitHub repo and adapt it for your region.

**Q: How reliable is this data?**
A: Very. All sources are federal agencies (CDC, EPA, HRSA, FEMA) with established data collection methodologies.

**Q: Can I embed this in my website?**
A: Yes! Use an iframe:
```html
<iframe src="https://scottmadden.github.io/jax-health-scorecard/schools.html" 
        width="100%" height="800" frameborder="0"></iframe>
```

**Q: Who pays for this?**
A: Nobody! It runs on free GitHub infrastructure ($0/month). Open source MIT license.

**Q: Why are all Nassau schools low-need?**
A: Nassau County genuinely has better health indicators—lower chronic disease, better healthcare access, etc.

**Q: What if I want custom indicators?**
A: Contact the developer (see GitHub repo). The system is modular and can be extended.

---

## 🛠️ For Developers

**Want to run this yourself or customize it?**

```bash
# Clone repository
git clone https://github.com/scottmadden/jax-health-scorecard.git
cd jax-health-scorecard

# Install dependencies
pip install -r requirements.txt

# Run county scorecard
python src/pipeline.py

# Run school scorecard
python src/schools.py

# Generate HTML
python src/schools_html.py

# Outputs:
# - data/scorecard.csv (counties)
# - data/school_scorecard.csv (schools)
# - docs/index.html (county table)
# - docs/schools.html (school table)
```

**Customize:**
- Edit `src/pipeline.py` to add indicators
- Modify `COUNTIES` list for different regions
- Adjust scoring weights in `build_scorecard()`
- Update `src/schools_html.py` for UI changes

**Deploy your own:**
- Fork the GitHub repo
- Enable GitHub Pages (Settings → Pages)
- GitHub Actions runs automatically

---

## 📞 Support & Contact

**Questions? Issues? Suggestions?**

- **GitHub Issues:** https://github.com/scottmadden/jax-health-scorecard/issues
- **Email:** [Add your contact]
- **LinkedIn:** [Add your profile]

**Want custom deployment for your district/region?**
Professional services available. Contact for pricing.

---

## 🎓 Educational Use

**Teachers & Students:**
- Download CSV for statistics/data science projects
- Analyze correlations (health vs academic performance)
- Map visualizations with school coordinates
- Time-series analysis (once historical data accumulates)

**Researchers:**
- All methodology documented
- Open-source code available
- Reproducible pipeline
- Cite as: "Jacksonville Health Scorecard, Scott Madden, 2025"

---

**Last Updated**: November 9, 2025  
**Schools**: 93 (38 elementary, 13 middle, 42 high)  
**Counties**: 5 (Duval, Clay, St. Johns, Nassau, Baker)  
**Update Frequency**: Daily at 9:15am ET

