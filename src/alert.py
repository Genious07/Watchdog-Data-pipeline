import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_alert(summary, failed_exps):
    from_email = os.environ["ALERT_FROM_EMAIL"]
    to_email = os.environ["ALERT_TO_EMAIL"]
    api_key = os.environ["SENDGRID_API_KEY"]

    # Determine subject based on whether it's an error or a validation failure
    if "error" in summary:
        subject = "Data Quality Error: Exception Occurred"
    else:
        subject = "Data Quality Alert: Validation Failed"

    # Safely build the content string
    content = f"""
    Timestamp: {summary.get("timestamp", "N/A")}
    Success: {summary.get("success", "N/A")}
    Percent Valid: {summary.get("percent_valid", "N/A")}%
    Failed Expectations: {', '.join(failed_exps) if failed_exps else 'None'}
    Content Hash: {summary.get("content_hash", "N/A")}
    """
    if "error" in summary:
        content += f'\nError: {summary["error"]}'

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    if response.status_code != 202:
        print(f"Alert failed: {response.status_code}")
