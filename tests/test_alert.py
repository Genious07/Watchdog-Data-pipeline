import os
from src.alert import send_alert


def test_send_alert(mocker):
    mocker.patch("sendgrid.SendGridAPIClient.send")
    os.environ["SENDGRID_API_KEY"] = "test"
    os.environ["ALERT_FROM_EMAIL"] = "test@from.com"
    os.environ["ALERT_TO_EMAIL"] = "test@to.com"
    send_alert(
        {"timestamp": "now", "success": False, "content_hash": "hash"},
        ["exp1"]
    )
    # Assert no exception
    assert True
