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

load_dotenv()

# --- Configuration ---
TARGET_API_URL = os.environ["TARGET_API_URL"]
MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DB = os.environ["MONGODB_DB"]
MONGODB_COLLECTION = os.environ["MONGODB_COLLECTION"]
EXPECTATION_SUITE_NAME = os.environ["EXPECTATION_SUITE_NAME"]
ALERT_FROM_EMAIL = os.environ["ALERT_FROM_EMAIL"]
ALERT_TO_EMAIL = os.environ["ALERT_TO_EMAIL"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]


def handler(request, response):
    try:
        query = request.url.split("?")[1] if "?" in request.url else ""
        force = "force=true" in query.lower()

        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        print(f"Fetching data from: {TARGET_API_URL}")
        api_response = session.get(TARGET_API_URL, timeout=30)

        if api_response.status_code != 200:
            print(f"API request failed with status code: {api_response.status_code}")
            print(f"Response content: {api_response.text}")
            raise Exception(f"API request failed: {api_response.status_code}")

        raw_data = api_response.content
        
        data = json.loads(raw_data)
        if data.get("Response") == "Error":
            error_message = data.get("Message", "Unknown API error")
            print(f"API returned an error: {error_message}")
            raise Exception(f"API Error: {error_message}")

        # --- FIXED ---
        # Corrected the typo from sha2d56 to sha256.
        content_hash = hashlib.sha256(raw_data).hexdigest()

        if not force and not detect_change(content_hash):
            result = {"message": "No change detected, skipping validation."}
            response.status_code = 200
            response.headers["Content-Type"] = "application/json"
            response.send(json.dumps(result))
            return

        df = ingest_data(raw_data)
        validation_results = validate_data(df)

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

        store_results(summary, validation_results)

        if not success or percent_valid < 95:
            failed_exps = [
                r["expectation_config"]["expectation_type"]
                for r in validation_results["results"]
                if not r["success"]
            ]
            send_alert(summary, failed_exps)

        result = {"summary": summary}
        response.status_code = 200

    except Exception as e:
        error_msg = {"error": str(e)}
        print(f"An error occurred: {str(e)}")
        send_alert(
            {"timestamp": datetime.utcnow().isoformat(), "error": str(e)}, []
        )
        response.status_code = 500
        result = error_msg

    response.headers["Content-Type"] = "application/json"
    response.send(json.dumps(result))
