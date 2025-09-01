# Data Quality Watchdog for Financial Market Data

This project implements a serverless data pipeline that actively monitors the quality of financial market data from an API. It provides a robust framework for automated data ingestion, validation, and real-time monitoring, complete with a live dashboard and alerting system.

The pipeline fetches OHLCV (Open, High, Low, Close, Volume) data for BTC/USDT, validates it against a predefined set of data quality rules, and logs the results. This ensures data integrity and reliability for any downstream applications or analysis.

### Live Dashboard

A live snapshot of the monitoring dashboard can be viewed here:

**[View Live Grafana Dashboard](https://satwik07.grafana.net/dashboard/snapshot/vYpeQtkBQEkNM7LugUHizjSEGPXIuZDT)**

-----

## Key Features

  * **Automated Data Ingestion**: Periodically fetches OHLCV data from the CryptoCompare API.
  * **Efficient Change Detection**: Uses content hashing (`SHA-256`) to identify changes in the source data, preventing redundant validations and conserving resources.
  * **Comprehensive Data Validation**: Leverages the Great Expectations framework to perform a suite of data quality checks, ensuring data is accurate, complete, and reliable.
  * **Real-time Alerting**: Automatically sends email notifications via SendGrid when data quality issues or system errors are detected.
  * **Data Persistence**: Stores validation results and summaries in a MongoDB database for historical analysis and trend monitoring.
  * **Insightful Dashboarding**: Results are visualized in a Grafana dashboard, providing at-a-glance insights into data quality metrics, trends, and system health.
  * **CI/CD and Scheduled Monitoring**: Includes GitHub Actions for continuous integration and for triggering the monitoring pipeline on a schedule.

-----

## Architecture

The system is designed as an event-driven, serverless pipeline. A cron job, managed by GitHub Actions, triggers the process on a recurring schedule. This initiates a request to the monitoring endpoint hosted on Render.

```
┌─────────────────┐      ┌────────────────┐      ┌─────────────────┐
│ GitHub Actions  │──────▶│ Render Service │──────▶│ CryptoCompare   │
│ (Scheduled Cron)│      │ (API Endpoint) │      │ API (OHLCV Data)│
└─────────────────┘      └────────────────┘      └─────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Great            │
                         │ Expectations     │
                         │ Validation       │
                         └──────────────────┘
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                 ┌──────────────┐    ┌──────────────┐
                 │ MongoDB      │    │ SendGrid     │
                 │ Atlas        │    │ Alerts       │
                 │              │    │ (Email)      │
                 └──────────────┘    └──────────────┘
                         │
                         ▼
                 ┌──────────────┐
                 │ Grafana      │
                 │ Cloud        │
                 │ Dashboard    │
                 └──────────────┘
```

-----

## Technology Stack

  * **Backend**: Python, Flask
  * **Data Validation**: Great Expectations
  * **Database**: MongoDB
  * **Alerting**: SendGrid
  * **Deployment**: Render
  * **CI/CD & Automation**: GitHub Actions
  * **Data Visualization**: Grafana

-----

## Getting Started

### Prerequisites

  * Python 3.11+
  * MongoDB Atlas account
  * SendGrid account
  * Render account
  * Grafana Cloud account

### Local Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/watchdog-data-pipeline.git
    cd watchdog-data-pipeline
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory and populate it with your credentials. You can use `.env.example` as a template.

    ```bash
    cp .env.example .env
    ```

4.  **Run the application locally:**

    ```bash
    flask run
    ```

    The application will be available at `http://127.0.0.1:5000`.

5.  **Trigger a validation check:**
    Access `http://127.0.0.1:5000/api/monitor?force=true` in your browser or via `curl`.

### Deployment on Render

This application can be deployed as a Web Service on Render.

1.  **Create a new Web Service on Render** and connect it to your forked repository.
2.  **Set the Start Command**: `gunicorn app:app`
3.  **Add Environment Variables**: In the Render dashboard, add the environment variables defined in your `.env` file.
4.  **Deploy**. Render will automatically deploy your application.

### Scheduled Monitoring with GitHub Actions

The monitoring pipeline is triggered by a scheduled workflow in GitHub Actions.

1.  In your GitHub repository, go to **Settings \> Secrets and variables \> Actions**.
2.  Create a new repository secret named `RENDER_ENDPOINT`.
3.  Set the value to your Render service URL (e.g., `https://your-app-name.onrender.com`).
4.  The workflow in `.github/workflows/data-quality-monitor.yml` will now trigger your deployed service hourly.

-----

## Testing

The project includes a suite of unit tests. To run them:

```bash
pytest -v
```

To run tests with coverage:

```bash
pytest --cov=src
```

-----

## Customization

### Adapting for a Different API

1.  Update the `TARGET_API_URL` environment variable.
2.  Modify the `ingest_data()` function in `src/validator.py` to correctly parse the new API response.
3.  Adjust the Great Expectations suite in `src/great_expectations/expectations/ohlcv_suite.json` to match the new data schema and quality requirements.

### Modifying Monitoring Frequency

You can change the cron schedule in `.github/workflows/data-quality-monitor.yml`:

```yaml
# Every 15 minutes (for demos)
- cron: '*/15 * * * *'

# Every 30 minutes
- cron: '0,30 * * * *'

# Business hours only (9-5, Mon-Fri)
- cron: '0 9-17 * * 1-5'
```
