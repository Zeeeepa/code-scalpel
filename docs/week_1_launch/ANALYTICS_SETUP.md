# Analytics Setup Checklist
**January 6, 2026 | Week 1 Preparation**

> [20260108_FEATURE] Complete guide to setting up analytics infrastructure for launch tracking

---

## GitHub Analytics Setup

### GitHub Stars Tracker
**Purpose:** Real-time tracking of repository growth  
**Effort:** 15 minutes

**Steps:**
1. Create `.github/scripts/star_tracker.py`:
```python
#!/usr/bin/env python3
"""Track GitHub stars daily and log to CSV"""
import requests
import csv
from datetime import datetime

REPO = "yourusername/code-scalpel"  # Update
TOKEN = "your_github_token"  # Create at github.com/settings/tokens

def get_stars():
    headers = {"Authorization": f"token {TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}"
    resp = requests.get(url, headers=headers)
    return resp.json()['stargazers_count']

def log_stars(stars):
    with open('data/star_history.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), stars])

if __name__ == "__main__":
    stars = get_stars()
    log_stars(stars)
    print(f"Stars: {stars}")
```

2. Create GitHub Action `.github/workflows/track_stars.yml`:
```yaml
name: Track GitHub Stars
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install requests
      - run: python .github/scripts/star_tracker.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "📊 Update star history"
```

3. Create initial data file:
   - Path: `data/star_history.csv`
   - Headers: `timestamp,stars`
   - First row: `2026-01-06T00:00:00,0`

4. Commit and push

**Verification:**
- [ ] Action runs successfully
- [ ] CSV file updates daily
- [ ] Can view historical trend in GitHub

---

### GitHub Issues & Discussions Setup
**Purpose:** Organize feedback and questions  
**Effort:** 10 minutes

**Steps:**
1. **Enable Discussions:**
   - Settings → Features → Enable Discussions
   - Create categories:
     - General (announcements, off-topic)
     - Beta Feedback (user testing feedback)
     - Feature Requests (new ideas)
     - Help & Questions (support)

2. **Create Issue Templates:**
   - `.github/ISSUE_TEMPLATE/bug_report.md`
   - `.github/ISSUE_TEMPLATE/feature_request.md`
   - `.github/ISSUE_TEMPLATE/documentation.md`

3. **Create Discussion Pinned Post:**
   ```
   Welcome to Code Scalpel discussions! 

   👋 **Beta testers:** Use #beta-feedback to share your experience
   🐛 **Found a bug?** Use GitHub Issues
   💡 **Have an idea?** Use #feature-requests
   ❓ **Have a question?** Use #help-and-questions

   We read every post. Thanks for being part of this!
   ```

---

## PyPI Analytics Setup

### Basic Download Tracking
**Purpose:** Monitor package adoption  
**Effort:** 10 minutes

**Method 1: BigQuery (Official)**
1. Enable BigQuery access at [packaging.python.org](https://packaging.python.org/key_project_statistics/)
2. Run queries:
```sql
SELECT
  DATE(timestamp) as date,
  COUNT(*) as downloads
FROM
  `bigquery-public-data.pypi.file_downloads.file_downloads`
WHERE
  project = 'code-scalpel'
  AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY
  date
ORDER BY
  date DESC
```

3. Save results to CSV weekly

**Method 2: Simple Tracking Script**
```python
# scripts/track_pypi_downloads.py
import requests
from datetime import datetime

def get_download_stats():
    url = "https://pypistats.org/api/packages/code-scalpel/overall"
    resp = requests.get(url)
    data = resp.json()
    
    with open('data/pypi_downloads.json', 'a') as f:
        f.write(f'{{"timestamp": "{datetime.now().isoformat()}", "data": {data}}}\n')
    
    return data['data']

if __name__ == "__main__":
    stats = get_download_stats()
    print(f"Downloads (last 7 days): {stats['last_week']}")
    print(f"Downloads (all-time): {stats['last_month']}")
```

**Setup:** Add to GitHub Actions daily schedule

---

## Website Analytics Setup

### Google Analytics 4 (GA4)
**Purpose:** Track website traffic, user behavior  
**Effort:** 20 minutes

**Steps:**
1. Create Google Analytics account: [analytics.google.com](https://analytics.google.com)

2. Create new GA4 property:
   - Property name: "Code Scalpel"
   - Website URL: codescalpel.com (or your domain)
   - Industry: Software/Technology
   - Reporting timezone: America/Los_Angeles

3. Install tracking code on website:
   ```html
   <!-- Google Analytics -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```

4. Set up **key events to track:**
   - Signup for beta
   - Download documentation
   - View pricing page
   - Click GitHub link

5. Create **dashboards:**
   - Traffic overview (daily visitors)
   - Signup funnel
   - Content performance
   - Geographic distribution

6. Enable **real-time monitoring:**
   - Settings → Data Collection
   - Enable event tracking
   - Test with own traffic

**Verification:**
- [ ] Install tracking code on website
- [ ] View real-time data within 30 seconds of visit
- [ ] Verify key events firing
- [ ] Set up custom dashboard

---

## Metrics Tracking Spreadsheet

**Create: `data/metrics_tracking.csv`**

```csv
date,github_stars,pypi_downloads_week,pypi_downloads_total,website_visitors,blog_views,discord_members,beta_signups,twitter_followers,linkedin_followers,notes
2026-01-06,0,0,0,0,0,0,0,0,0,Starting baseline
2026-01-07,15,0,0,45,50,5,2,10,5,Blog posts published
2026-01-08,28,2,2,80,120,12,4,25,15,Demo video published
2026-01-09,45,5,8,150,250,28,8,55,35,Beta invites sent
2026-01-10,85,15,25,280,450,48,15,120,75,ProductHunt launch
2026-01-11,110,22,40,420,600,65,20,180,110,HN trending
2026-01-12,145,30,55,550,750,85,25,250,145,Weekend growth
```

**Daily Update Template:**
1. Update spreadsheet with actual numbers
2. Calculate daily growth rate
3. Compare to targets
4. Note any anomalies/drivers

---

## Dashboard Setup (Optional but Recommended)

### Option 1: GitHub Project Board
**Effort:** 5 minutes

Create a GitHub project with columns:
- 📊 Metrics to Track (manual updates)
- 🚀 Launch Activities (linked to issues)
- 📈 Results (track against targets)

---

### Option 2: Notion Dashboard
**Effort:** 30 minutes (one-time setup)

**Setup:**
1. Create Notion page: "Code Scalpel Launch Dashboard"
2. Create database with:
   - **Daily Metrics Table:** Stars, downloads, visitors, signups
   - **Content Calendar:** Blog posts, social posts, emails
   - **Activities Log:** What happened, when, results
   - **Feedback Tracker:** User feedback and themes

**Template:**
```
📅 JANUARY 2026 LAUNCH

📊 METRICS (TODAY)
- GitHub Stars: [number] 🎯 Target: 50
- Website Visitors: [number] 🎯 Target: 500
- Beta Signups: [number] 🎯 Target: 10
- Discord Members: [number] 🎯 Target: 30

📝 ACTIVITIES TODAY
- Blog Post 1 published
- Discord launched
- Twitter thread posted

🔗 LINKS
- GitHub: [link]
- ProductHunt: [link]
- Website Analytics: [link]
```

---

### Option 3: Google Sheets Dashboard
**Effort:** 20 minutes (simplest)

**Create sheet with:**
1. **Raw Data Tab:** Daily metrics (copied from CSV)
2. **Summary Tab:** Charts and trends
3. **Targets Tab:** Goals and progress
4. **Notes Tab:** Observations and decisions

**Formulas:**
```
=SPARKLINE(A2:A10) - shows trend chart
=QUERY(raw_data,"SELECT * WHERE date >= DATE '2026-01-06'") - recent data only
=(current-baseline)/baseline - growth rate
```

---

## Discord Analytics Setup

### Built-in Discord Stats
**Effort:** 5 minutes

- Settings → Server Statistics
- Enable activity logging
- View: Member count, message count, join patterns

### Simple Manual Tracking
**In spreadsheet, track:**
- Date | Members | Messages/day | Active users | Engagement rate

---

## Twitter/LinkedIn Analytics

### Twitter (Now X) Analytics
**Effort:** 5 minutes

1. Enable Analytics at [analytics.twitter.com](https://analytics.twitter.com)
2. Track weekly:
   - Impressions (reached)
   - Engagements (likes, replies, retweets)
   - Followers gained
   - Link clicks

### LinkedIn Analytics
**Effort:** 5 minutes

1. Go to LinkedIn analytics dashboard
2. Track weekly:
   - Post impressions
   - Engagement rate
   - Follower growth
   - Click-through rate

---

## Email Analytics Setup

### Email Tracking (Mailchimp/ConvertKit/Similar)
**Effort:** 15 minutes

1. Choose platform: Mailchimp (free) or ConvertKit (premium)
2. Create account: "Code Scalpel"
3. Set up welcome email template
4. Track metrics:
   - Open rate
   - Click rate
   - Unsubscribe rate
   - Conversions

---

## Weekly Reporting Template

**Every Friday, create a summary:**

```markdown
# Weekly Metrics Report - Week [X]

## 📊 Key Metrics

| Metric | Start | End | Growth | Target |
|--------|-------|-----|--------|--------|
| GitHub Stars | X | Y | +Z% | TARGET |
| PyPI Downloads | X | Y | +Z% | TARGET |
| Website Visitors | X | Y | +Z% | TARGET |

## 📈 Trends
- [Observation 1]
- [Observation 2]
- [Observation 3]

## 🎯 Wins
- [Achievement 1]
- [Achievement 2]

## ⚠️ Concerns
- [Issue 1]
- [Issue 2]

## 🔄 Next Week
- [Priority 1]
- [Priority 2]
- [Priority 3]

## 💡 Learnings
- [Learning 1]
- [Learning 2]
```

---

## Tools Summary

| Tool | Purpose | Cost | Setup Time |
|------|---------|------|-----------|
| GitHub Actions | Star tracking | Free | 15 min |
| GA4 | Website analytics | Free | 20 min |
| PyPI Stats | Download tracking | Free | 10 min |
| Google Sheets | Metrics dashboard | Free | 20 min |
| Notion | Project tracker | Free | 30 min |
| Twitter/LinkedIn | Social analytics | Free | 10 min |
| **Total** | **Complete system** | **Free** | **~2 hours** |

---

## Priority Order (Complete in This Order)

1. **Must Have (Day 1):**
   - [ ] Google Analytics installed
   - [ ] Metrics tracking spreadsheet created
   - [ ] Daily update process established

2. **Should Have (Day 1-2):**
   - [ ] GitHub star tracker set up
   - [ ] PyPI download tracker set up
   - [ ] Simple dashboard (Google Sheets)

3. **Nice to Have (Day 2-3):**
   - [ ] Notion dashboard
   - [ ] GitHub Discussions enabled
   - [ ] Twitter/LinkedIn analytics enabled

---

## Verification Checklist

- [ ] GA4 tracking code installed on website
- [ ] GA4 shows real-time traffic (test yourself)
- [ ] GitHub action runs and logs stars
- [ ] PyPI stats accessible
- [ ] Metrics spreadsheet updated with baseline
- [ ] Dashboard accessible to team
- [ ] Daily update process documented
- [ ] Weekly reporting template created

---

## Support References

- GA4 Help: [support.google.com/analytics](https://support.google.com/analytics)
- GitHub Actions: [docs.github.com/actions](https://docs.github.com/actions)
- PyPI Stats API: [pypistats.org](https://pypistats.org)

---

**Status:** ✅ Ready to Execute (Minimal Setup Time)  
**Estimated Total Time:** 2 hours one-time setup, 30 min daily updates  
**Most Important:** GA4 + Spreadsheet (rest are optional but valuable)
