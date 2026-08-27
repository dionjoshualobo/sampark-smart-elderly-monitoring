from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from database import (
    acknowledge_alert,
    create_alert,
    create_health_record,
    get_latest_alert,
    get_health_record,
    get_latest_health_record,
    init_db,
    list_alerts,
    list_health_records,
    update_alert_notification,
)
from email_notifier import gmail_status, send_caretaker_email
from assistant_web import handle_assistant_message
from risk_engine import predict_risk


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

app = Flask(__name__)
CORS(app)


PAGES = {
    "dashboard": PROJECT_DIR / "dashboard" / "index.html",
    "watch": PROJECT_DIR / "wearable_simulator" / "watch.html",
    "phone": PROJECT_DIR / "phone_voice" / "index.html",
}


def serve_page(page_key):
    page_path = PAGES[page_key]
    if not page_path.exists():
        return jsonify({"error": f"{page_key} page not found"}), 404
    return send_file(page_path)


@app.before_request
def setup_database():
    init_db()


@app.get("/")
def home():
    return jsonify(
        {
            "app": "SAMPARK Backend",
            "status": "running",
            "pages": {
                "dashboard": "/dashboard",
                "watch_simulator": "/watch",
                "phone_voice": "/phone",
            },
            "endpoints": {
                "create_health_record": "POST /health-data",
                "list_health_records": "GET /health-data",
                "latest_health_record": "GET /health-data/latest",
                "list_alerts": "GET /alerts",
                "latest_alert": "GET /alerts/latest",
                "acknowledge_alert": "POST /alerts/<id>/acknowledge",
                "emergency_alert": "POST /emergency",
                "email_status": "GET /email-status",
                "assistant_message": "POST /assistant-message",
                "predict_without_saving": "POST /predict",
            },
        }
    )


@app.get("/dashboard")
def dashboard_page():
    return serve_page("dashboard")


@app.get("/watch")
def watch_page():
    return serve_page("watch")


@app.get("/phone")
def phone_page():
    return serve_page("phone")


@app.post("/health-data")
def save_health_data():
    payload = request.get_json(silent=True) or {}
    record = create_health_record(payload)
    return jsonify(record), 201


@app.get("/health-data")
def health_records():
    return jsonify({"records": list_health_records()})


@app.get("/health-data/latest")
def latest_health_record():
    record = get_latest_health_record()
    if record is None:
        return jsonify({"error": "No health records found"}), 404
    return jsonify(record)


@app.get("/health-data/<int:record_id>")
def health_record(record_id):
    record = get_health_record(record_id)
    if record is None:
        return jsonify({"error": "Health record not found"}), 404
    return jsonify(record)


@app.get("/alerts")
def alerts():
    return jsonify({"alerts": list_alerts()})


@app.get("/alerts/latest")
def latest_alert():
    alert = get_latest_alert()
    if alert is None:
        return jsonify({"error": "No alerts found"}), 404
    return jsonify(alert)


@app.post("/alerts/<int:alert_id>/acknowledge")
def acknowledge(alert_id):
    alert = acknowledge_alert(alert_id)
    if alert is None:
        return jsonify({"error": "Alert not found"}), 404
    return jsonify({"alert": alert})


@app.get("/email-status")
def email_status():
    return jsonify(gmail_status())


@app.post("/emergency")
def emergency():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "Emergency reported by SAMPARK voice assistant.")
    source = payload.get("source", "voice_assistant")

    alert = create_alert(
        None,
        "High",
        "Emergency",
        f"Emergency from {source}: {message}",
        bypass_cooldown=True,
    )

    email_result = send_caretaker_email(
        "SAMPARK Emergency Alert",
        (
            "SAMPARK detected an emergency.\n\n"
            f"Source: {source}\n"
            f"Message: {message}\n\n"
            "Please check on the elderly person immediately."
        ),
    )
    status = "sent" if email_result["sent"] else "simulated"
    alert = update_alert_notification(alert["id"], status)

    return jsonify({"alert": alert, "email": email_result}), 201


@app.post("/assistant-message")
def assistant_message():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()
    session_id = payload.get("session_id", "web-default")
    source = payload.get("source", "web_voice")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    result = handle_assistant_message(message, session_id=session_id, source=source)
    return jsonify(result)


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    result = predict_risk(payload)
    return jsonify(result)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
