from flask import Blueprint, request, jsonify, current_app
import json, os, time
from server.utils.anomaly_detector import check_anomalies
from server.utils.alert_manager import notify 

bp = Blueprint("upload", __name__)


@bp.post("/upload")
def upload():
    payload = request.get_json(force=True, silent=True) or {}
    payload["timestamp"] = time.time()

    data_file = current_app.config["DATA FILE"]

    data = []

    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
        except Exception:
            data = []


    data.append(payload)
    with open(data_file, "w") as f:
        json.dump(data, f, indent=2)

    anomalies = check_anomalies(payload)
    notify(anomalies, payload)
    return jsonify({"status": "ok", "anomalies":anomalies})

