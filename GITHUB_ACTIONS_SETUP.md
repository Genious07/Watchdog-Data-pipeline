# GitHub Actions Setup for Hourly Data Quality Monitoring

This guide explains how to set up GitHub Actions to trigger your Vercel-deployed data quality monitor every hour, bypassing Vercel Hobby plan cron limitations.

## Why GitHub Actions?

- **Free**: 2000 minutes/month on GitHub free tier
- **Flexible**: Configurable schedules (hourly, every 30 minutes, etc.)
- **Reliable**: GitHub's infrastructure ensures consistent execution
- **No Upgrade Required**: Works with Vercel Hobby plan

## Setup Steps

### 1. Deploy to Vercel First

Make sure your application is deployed to Vercel and working:
```bash
# Test your Vercel endpoint
curl https://your-project.vercel.app/api/monitor?force=true
```

### 2. Add GitHub Repository Secret

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add:
   - **Name**: `VERCEL_ENDPOINT`
   - **Value**: `https://your-project.vercel.app`
5. Click **Add secret**

### 3. Workflow Configuration

The workflow file `.github/workflows/data-quality-monitor.yml` is already included:

```yaml
name: Data Quality Monitor

on:
  schedule:
    # Run every hour at minute 0
    - cron: '0 * * * *'
  workflow_dispatch:
    # Allow manual triggering

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
    - name: Trigger Data Quality Check
      run: |
        curl -X GET "${{ secrets.VERCEL_ENDPOINT }}/api/monitor?force=true" \
          -H "Content-Type: application/json" \
          -w "HTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
          --fail-with-body || {
            echo "❌ Data quality check failed"
            exit 1
          }
        echo "✅ Data quality check completed successfully"
    
    - name: Notify on Failure
      if: failure()
      run: |
        echo "Data quality monitoring failed at $(date)"
        # Additional notification logic can be added here
```

### 4. Test the Setup

#### Manual Test
1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **Data Quality Monitor** workflow
4. Click **Run workflow** > **Run workflow**
5. Monitor the execution in real-time

#### Automatic Test
- The workflow will run automatically every hour
- Check the **Actions** tab to see execution history

## Monitoring and Alerts

### GitHub Actions Notifications

GitHub will automatically:
- Email you when workflows fail
- Show status badges in your repository
- Provide detailed logs for debugging

### Custom Notifications

Add additional notification methods to the workflow:

#### Slack Notification
```yaml
- name: Notify Slack on Failure
  if: failure()
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"❌ Data quality check failed at $(date)"}' \
      $SLACK_WEBHOOK
```

#### Discord Notification
```yaml
- name: Notify Discord on Failure
  if: failure()
  env:
    DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK_URL }}
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"content":"❌ Data quality check failed at $(date)"}' \
      $DISCORD_WEBHOOK
```

## Schedule Customization

Modify the cron schedule in `.github/workflows/data-quality-monitor.yml`:

```yaml
on:
  schedule:
    # Every 30 minutes
    - cron: '0,30 * * * *'
    
    # Every 15 minutes
    - cron: '0,15,30,45 * * * *'
    
    # Every 6 hours
    - cron: '0 */6 * * *'
    
    # Twice daily (9 AM and 9 PM UTC)
    - cron: '0 9,21 * * *'
    
    # Business hours only (9 AM - 5 PM UTC, weekdays)
    - cron: '0 9-17 * * 1-5'
```

## Troubleshooting

### Common Issues

#### Workflow Not Running
- **Check cron syntax**: Use [crontab.guru](https://crontab.guru) to validate
- **Repository settings**: Ensure Actions are enabled in repository settings
- **Branch protection**: Workflow must be on default branch (usually `main`)

#### Authentication Errors
- **Secret not set**: Verify `VERCEL_ENDPOINT` secret exists and is correct
- **URL format**: Ensure URL includes `https://` and no trailing slash

#### Rate Limiting
- **GitHub Actions**: 2000 minutes/month on free tier
- **Vercel**: No specific limits on Hobby plan for API calls
- **Binance API**: Rate limits apply to the target API

### Debugging Steps

1. **Check workflow logs**:
   - Go to Actions tab > Click failed workflow > View logs

2. **Test endpoint manually**:
   ```bash
   curl -v https://your-project.vercel.app/api/monitor?force=true
   ```

3. **Verify secret**:
   - Repository Settings > Secrets > Verify `VERCEL_ENDPOINT` exists

4. **Check Vercel logs**:
   - Vercel dashboard > Functions > View logs

## Cost and Limits

### GitHub Actions (Free Tier)
- **Minutes**: 2000/month
- **Storage**: 500 MB
- **Concurrent jobs**: 20

### Usage Calculation
- **Hourly monitoring**: ~30 seconds per run = 15 hours/month
- **Every 30 minutes**: ~30 hours/month
- **Every 15 minutes**: ~60 hours/month

### Optimization Tips
- Use `timeout-minutes: 5` to prevent stuck workflows
- Cache dependencies if installing packages
- Use `fail-fast: false` for matrix builds

## Advanced Configuration

### Multiple Environments
```yaml
strategy:
  matrix:
    environment: [staging, production]
steps:
- name: Trigger Check
  run: |
    curl "${{ secrets[format('VERCEL_ENDPOINT_{0}', matrix.environment)] }}/api/monitor?force=true"
```

### Conditional Execution
```yaml
- name: Skip on weekends
  if: github.event.schedule == '0 * * * *' && (github.event.schedule != '0 * * * 0,6')
```

### Retry Logic
```yaml
- name: Trigger with Retry
  run: |
    for i in {1..3}; do
      if curl "${{ secrets.VERCEL_ENDPOINT }}/api/monitor?force=true"; then
        break
      fi
      echo "Attempt $i failed, retrying..."
      sleep 30
    done
```

This setup provides a robust, free alternative to Vercel Pro plan cron jobs while maintaining the same functionality and reliability.

