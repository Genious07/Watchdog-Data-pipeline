# Deployment Guide for Data Quality Watchdog

## Quick Start

1. **Extract the ZIP file** to your local machine
2. **Push to GitHub** repository
3. **Deploy to Vercel** with environment variables
4. **Configure GitHub Actions** for hourly monitoring (optional)
5. **Configure services** (MongoDB, SendGrid, Grafana)

## Monitoring Options

- **Daily Monitoring**: Vercel Cron (Hobby plan compatible)
- **Hourly Monitoring**: GitHub Actions (free alternative)
- **High-Frequency**: Vercel Pro plan ($20/month)

## Detailed Steps

### 1. GitHub Setup

```bash
# Extract and navigate to project
unzip data-quality-watchdog-clean.zip
cd data-quality-watchdog/

# Initialize git repository
git init
git add .
git commit -m "Initial commit: Data Quality Watchdog"

# Push to GitHub
git remote add origin https://github.com/yourusername/data-quality-watchdog.git
git push -u origin main
```

### 2. Vercel Deployment

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect Python runtime
5. Add environment variables in Vercel dashboard:



6. Click "Deploy"
7. Note your deployment URL (e.g., `https://your-project.vercel.app`)

### 3. GitHub Actions Setup (Recommended for Hourly Monitoring)

1. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Add the following secret:
   - **Name**: `VERCEL_ENDPOINT`
   - **Value**: `https://your-vercel-deployment-url.vercel.app`
4. Click **Add secret**

The GitHub Actions workflow will now run automatically every hour!

### 4. Monitoring Configuration

#### Option A: Daily Monitoring (Vercel Hobby Plan)
- **Schedule**: Daily at midnight UTC (`0 0 * * *`)
- **Cost**: Free
- **Setup**: Automatic with Vercel deployment

#### Option B: Hourly Monitoring (GitHub Actions)
- **Schedule**: Every hour (`0 * * * *`)
- **Cost**: Free (2000 minutes/month limit)
- **Setup**: Add `VERCEL_ENDPOINT` secret (step 3 above)

#### Option C: High-Frequency Monitoring (Vercel Pro)
- **Schedule**: Configurable (up to every minute)
- **Cost**: $20/month
- **Setup**: Upgrade Vercel plan + update `vercel.json`

### 5. Service Configuration

#### MongoDB Atlas (Free Tier)
- Already configured with provided credentials
- Database: `quality_monitor`
- Collection: `quality_metrics`

#### SendGrid (Free Tier)
- Already configured with provided API key
- From: `satwiks788@gmail.com`
- To: `satwikloveshim213@gmail.com`

#### Grafana Cloud (Optional)
1. Sign up at [grafana.com](https://grafana.com)
2. Add MongoDB datasource using provided connection string
3. Import dashboard from `docs/grafana_dashboard.json`

### 6. Testing

After deployment, test both monitoring methods:

```bash
# Test Vercel endpoint directly
curl https://your-vercel-url.vercel.app/api/monitor?force=true

# Test GitHub Actions workflow
# Go to GitHub > Actions tab > "Data Quality Monitor" > "Run workflow"
```

### 7. Monitoring

#### Vercel Monitoring
- **Logs**: Vercel dashboard > Functions tab
- **Cron Jobs**: Vercel dashboard > Cron tab

#### GitHub Actions Monitoring
- **Workflow Runs**: GitHub repository > Actions tab
- **Logs**: Click on individual workflow runs
- **Notifications**: GitHub will email you on workflow failures

#### Data Quality Monitoring
- **MongoDB**: Validation results and metrics
- **Email Alerts**: Failure notifications via SendGrid
- **Grafana**: Visual dashboard for data quality trends

## File Structure

```
├── .github/workflows/
│   ├── ci.yml                     # Continuous Integration
│   └── data-quality-monitor.yml   # Hourly monitoring workflow
├── api/monitor.py                 # Main Vercel function
├── src/
│   ├── alert.py                  # SendGrid email alerts
│   ├── db.py                     # MongoDB operations
│   ├── validator.py              # Data validation logic
│   └── great_expectations/       # GE configuration
├── tests/                        # Unit tests
├── docs/grafana_dashboard.json   # Grafana dashboard
├── requirements.txt              # Python dependencies
├── vercel.json                   # Vercel configuration (daily cron)
└── README.md                     # Project documentation
```

## Customization

### Modify GitHub Actions Frequency

Edit `.github/workflows/data-quality-monitor.yml`:

```yaml
on:
  schedule:
    # Every 30 minutes
    - cron: '0,30 * * * *'
    
    # Every 15 minutes
    - cron: '0,15,30,45 * * * *'
    
    # Every 6 hours
    - cron: '0 */6 * * *'
```

### Add Additional Notifications

Add Slack/Discord webhooks to GitHub Actions:

```yaml
- name: Notify Slack on Failure
  if: failure()
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"❌ Data quality check failed!"}' \
      ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Adapt for Different APIs

1. Update `TARGET_API_URL` environment variable
2. Modify `ingest_data()` in `src/validator.py`
3. Adjust Great Expectations validations
4. Update Grafana dashboard queries

## Troubleshooting

### Vercel Issues
- **Function timeout**: Check Vercel logs for errors
- **MongoDB connection**: Verify connection string and network access
- **Email alerts**: Check SendGrid API key and email addresses

### GitHub Actions Issues
- **Workflow not running**: Check cron syntax and repository settings
- **Authentication errors**: Verify `VERCEL_ENDPOINT` secret is set correctly
- **Rate limiting**: GitHub Actions has 2000 minutes/month limit on free tier

### Data Quality Issues
- **Validation failures**: Review Great Expectations logs in function output
- **API errors**: Check Binance API status and rate limits
- **Database errors**: Verify MongoDB Atlas connection and permissions

## Cost Analysis

| Option | Cost | Frequency | Pros | Cons |
|--------|------|-----------|------|------|
| Vercel Hobby + GitHub Actions | Free | Hourly | No cost, reliable | GitHub Actions limits |
| Vercel Pro | $20/month | Up to 1 minute | Native integration | Monthly cost |
| External Cron Service | $5-10/month | Configurable | Flexible | Additional service |

**Recommended**: Start with GitHub Actions for hourly monitoring, upgrade to Vercel Pro if you need higher frequency.

