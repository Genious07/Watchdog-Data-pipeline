import os
import json
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from src.validator import ingest_data, detect_change, validate_data
from src.db import store_results
from src.alert import send_alert

# Load environment variables from a .env file for local development
load_dotenv()

# --- Configuration ---
# All sensitive and configurable values are loaded from environment variables
# for security and flexibility.
TARGET_API_URL = os.environ["TARGET_API_URL"]
MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DB = os.environ["MONGODB_DB"]
MONGODB_COLLECTION = os.environ["MONGODB_COLLECTION"]
EXPECTATION_SUITE_NAME = os.environ["EXPECTATION_SUITE_NAME"]
ALERT_FROM_EMAIL = os.environ["ALERT_FROM_EMAIL"]
ALERT_TO_EMAIL = os.environ["ALERT_TO_EMAIL"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]


def handler(request, response):
    """
    Main handler function for the serverless endpoint.

    This function performs the following steps:
    1. Fetches data from the target API with a retry mechanism.
    2. Calculates a hash of the data to detect changes.
    3. Validates the data against a suite of expectations.
    4. Stores the validation results in a MongoDB database.
    5. Sends an email alert if the validation fails.
    """
    try:
        # Determine if a validation should be forced, bypassing change detection
        query = request.url.split("?")[1] if "?" in request.url else ""
        force = "force=true" in query.lower()

        # --- Data Ingestion with Retries ---
        # Set up a session with a retry strategy for network resilience.
        # This helps handle temporary server errors from the API.
        session = requests.Session()
        retry = Retry(
            total=3,                # Total number of retries
            backoff_factor=1,       # Delay between retries (e.g., 1s, 2s, 4s)
            status_forcelist=[500, 502, 503, 504] # HTTP codes that trigger a retry
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        print(f"Fetching data from: {TARGET_API_URL}")
        api_response = session.get(TARGET_API_URL, timeout=10) # 10-second timeout

        # --- Initial API Response Check ---
        if api_response.status_code != 200:
            # Log the error for easier debugging before raising an exception
            print(f"API request failed with status code: {api_response.status_code}")
            print(f"Response content: {api_response.text}")
            raise Exception(f"API request failed: {api_response.status_code}")

        raw_data = api_response.content
        content_hash = hashlib.sha256(raw_data).hexdigest()

        # --- Change Detection ---
        # If not forced, check if the data has changed since the last run
        # to avoid redundant validations.
        if not force and not detect_change(content_hash):
            result = {"message": "No change detected, skipping validation."}
            response.status_code = 200
            response.headers["Content-Type"] = "application/json"
            response.send(json.dumps(result))
            return

        # --- Data Validation ---
        df = ingest_data(raw_data)
        validation_results = validate_data(df)

        # --- Summarize Validation Results ---
        success = validation_results["success"]
        n_expectations = len(validation_results["results"])
        n_success = sum(1 for r in validation_results["results"] if r["success"])
        n_failed = n_expectations - n_success
        percent_valid = (n_success / n_expectations * 100) if n_expectations > 0 else 100

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "n_expectations": n_expectations,
            "n_success": n_success,
            "n_failed": n_failed,
            "percent_valid": percent_valid,
            "content_hash": content_hash
        }

        # --- Storage and Alerting ---
        store_results(summary, validation_results)

        if not success or percent_valid < 95:
            failed_exps = [
                r["expectation_config"]["expectation_type"]
                for r in validation_results["results"]
                if not r["success"]
            ]
            send_alert(summary, failed_exps)

        # --- Final Response ---
        result = {"summary": summary}
        response.status_code = 200

    except Exception as e:
        # Catch any exception, log it, send an alert, and return a 500 error
        error_msg = {"error": str(e)}
        print(f"An error occurred: {str(e)}") # Log the error to the console
        send_alert(
            {"timestamp": datetime.utcnow().isoformat(), "error": str(e)}, []
        )
        response.status_code = 500
        result = error_msg

    # Set the response headers and send the JSON result
    response.headers["Content-Type"] = "application/json"
    response.send(json.dumps(result))
