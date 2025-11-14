from flask import Blueprint, jsonify, current_app
import json, os

bp = Blueprint("data", __name__)

@bp.get("/data")
def get_data():
    data_file = current_app.config["DATA FILE"]
    if not os.path.exists(data_file):
        return jsonify([])
    with open(data_file, "r") as f:
        data = json.load(f)
    return jsonify(data)

@bp.get("/health")
def health():
    return jsonify({"status":"running"})


