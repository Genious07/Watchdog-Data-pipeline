# Grafana Dashboard Setup Guide - Showcase Ready

This guide will help you set up a professional, showcase-ready Grafana dashboard for the Data Quality Watchdog system.

## 🎯 Dashboard Overview

The dashboard provides a comprehensive view of your data quality monitoring system with:

- **Real-time Status**: Current validation status and quality score
- **Trend Analysis**: Quality metrics over time with thresholds
- **Historical Data**: Detailed validation history and patterns
- **System Health**: Uptime statistics and monitoring metrics
- **Visual Appeal**: Professional dark theme with color-coded indicators

## 📊 Dashboard Panels

### Row 1: Key Metrics (Top KPIs)
1. **Current Status** - Pass/Fail indicator with color coding
2. **Data Quality Score** - Gauge showing percentage with thresholds
3. **Validation Results Breakdown** - Pie chart of passed vs failed checks
4. **Checks (24h)** - Count of validations in last 24 hours

### Row 2: Trend Analysis
5. **Data Quality Trend** - Time series with quality percentage over time
6. **Validation Success/Failure** - Bar chart showing pass/fail pattern

### Row 3: Detailed Information
7. **Recent Validation History** - Table with latest 20 validation runs
8. **Quality Metrics Summary** - Bar chart with 1h/24h/7d averages
9. **System Health** - Overall system statistics and uptime

## 🚀 Setup Instructions

### Step 1: Sign Up for Grafana Cloud

1. Go to [grafana.com](https://grafana.com)
2. Click "Get started for free"
3. Create your account
4. Choose "Grafana Cloud" (free tier includes 10k metrics)

### Step 2: Create MongoDB Data Source

1. In Grafana, go to **Configuration** > **Data Sources**
2. Click **Add data source**
3. Search for and select **MongoDB**
4. Configure the connection:
   ```
   Name: MongoDB Data Quality
   Host: satwikloveshim.dxg2yfg.mongodb.net
   Port: 27017
   Database: quality_monitor
   Username: satwikloveshim213
   Password: ZAQX1ZZNgtNEQL7G
   Authentication Database: admin
   SSL: Enabled
   ```
5. Click **Save & Test**

### Step 3: Import the Dashboard

1. Go to **Dashboards** > **Import**
2. Upload the `grafana_dashboard.json` file from the `docs/` folder
3. Select your MongoDB data source when prompted
4. Click **Import**

### Step 4: Configure Refresh and Time Range

1. Set auto-refresh to **30 seconds** (top-right dropdown)
2. Set time range to **Last 24 hours** for best showcase view
3. Enable **Live** mode for real-time updates

## 🎨 Customization for Showcase

### Color Scheme and Thresholds

The dashboard uses a professional color scheme:
- **Green**: Successful validations (≥95% quality)
- **Yellow**: Warning zone (80-95% quality)
- **Red**: Failed validations (<80% quality)

### Panel Descriptions

Each panel includes helpful descriptions that appear on hover, making the dashboard self-explanatory for viewers.

### Professional Styling

- **Dark theme** for modern appearance
- **Consistent spacing** and grid layout
- **Color-coded indicators** for quick status assessment
- **Meaningful titles** with emojis for visual appeal

## 📈 Generating Sample Data for Demo

To populate the dashboard with realistic data for showcase:

### Option 1: Run Multiple Validations
```bash
# Trigger multiple validations manually
for i in {1..10}; do
  curl "https://your-vercel-url.vercel.app/api/monitor?force=true"
  sleep 60
done
```

### Option 2: Use GitHub Actions
Enable the GitHub Actions workflow to run every 15 minutes temporarily:
```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
```

### Option 3: Historical Data Simulation
Add this script to generate historical data points:

```python
# historical_data_generator.py
import pymongo
from datetime import datetime, timedelta
import random

client = pymongo.MongoClient("your_mongodb_uri")
db = client.quality_monitor
collection = db.quality_metrics

# Generate 48 hours of hourly data
for i in range(48):
    timestamp = datetime.utcnow() - timedelta(hours=i)
    
    # Simulate realistic data quality metrics
    success = random.choice([True, True, True, False])  # 75% success rate
    n_expectations = 8
    n_success = random.randint(6, 8) if success else random.randint(4, 7)
    n_failed = n_expectations - n_success
    percent_valid = (n_success / n_expectations) * 100
    
    doc = {
        "timestamp": timestamp,
        "success": success,
        "n_expectations": n_expectations,
        "n_success": n_success,
        "n_failed": n_failed,
        "percent_valid": percent_valid,
        "content_hash": f"hash_{i}",
        "stored_at": timestamp
    }
    
    collection.insert_one(doc)

print("Historical data generated successfully!")
```

## 🔧 Troubleshooting

### Common Issues

#### MongoDB Connection Failed
- Verify connection string and credentials
- Check if your IP is whitelisted in MongoDB Atlas
- Ensure SSL is enabled

#### No Data Appearing
- Confirm data exists in MongoDB collection
- Check time range settings (last 24h)
- Verify collection name matches (`quality_metrics`)

#### Panels Not Loading
- Check MongoDB data source configuration
- Verify query syntax in panel settings
- Look for errors in browser console

### Query Examples

Test these queries in MongoDB to verify data:

```javascript
// Check latest validation
db.quality_metrics.find().sort({timestamp: -1}).limit(1)

// Count total validations
db.quality_metrics.count()

// Average quality score (last 24h)
db.quality_metrics.aggregate([
  {$match: {timestamp: {$gte: new Date(Date.now() - 24*60*60*1000)}}},
  {$group: {_id: null, avg_quality: {$avg: "$percent_valid"}}}
])
```

## 🎬 Showcase Tips

### For Live Demos
1. **Set 30-second refresh** for real-time updates
2. **Use full-screen mode** (press F11)
3. **Point out key metrics** during presentation
4. **Show historical trends** to demonstrate system reliability

### For Screenshots
1. **Ensure recent data** is available
2. **Use 24-hour time range** for good data density
3. **Highlight success metrics** (green indicators)
4. **Show variety** in the validation history table

### For Stakeholder Presentations
1. **Start with overview** (top row KPIs)
2. **Drill into trends** (time series charts)
3. **Show reliability** (system health panel)
4. **Demonstrate alerting** (mention email notifications)

## 📱 Mobile Responsiveness

The dashboard is optimized for:
- **Desktop displays** (primary use case)
- **Tablet viewing** (responsive grid)
- **Mobile access** (stacked panels)

## 🔄 Maintenance

### Regular Updates
- **Monitor data retention** in MongoDB
- **Update time ranges** as data grows
- **Adjust thresholds** based on system performance
- **Add new panels** for additional metrics

### Performance Optimization
- **Limit query time ranges** for faster loading
- **Use aggregation pipelines** for complex calculations
- **Cache frequently accessed data**
- **Monitor Grafana resource usage**

This dashboard provides a professional, comprehensive view of your data quality monitoring system that's perfect for showcasing to stakeholders, clients, or in portfolio presentations.

