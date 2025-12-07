from flask import Blueprint, request, current_app, jsonify
from . import auth_route
import json, os
from datetime import datetime

bp = Blueprint("upload", __name__)

@bp.post("/metrics")
def upload_metrics():
    """
    Route POST /metrics
    - Recoit les donnees JSON d'une machine authentifiee
    - Met a jour data.json avec ces donnees
    
    Headers requis:
    - Authorization: Bearer <token>
    """
    # Verifier le token d'authentification
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    
    is_valid, hostname = auth_route.verify_agent_token(token)
    if not is_valid:
        return jsonify({"error": "Authentification requise - token invalide"}), 401
    
    data_file = current_app.config["DATA FILE"]
    incoming = request.get_json()

    # Verifie les donnees
    if not incoming or "hostname" not in incoming:
        return jsonify({"error": "Donnees invalides"}), 400

    # Transforme les champs pour correspondre au format dashboard
    incoming_data = {
        "nom": incoming.get("hostname", "inconnu"),
        "ip": incoming.get("ip",0),
        "cpu": incoming.get("cpu", 0),
        "ram": incoming.get("ram", 0),
        "disque": incoming.get("disk", 0),
        "temp": incoming.get("temp",0),
        "debit": incoming.get("debit", 0)
    }

    # Lit les anciennes données
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            try:
                machines = json.load(f)
            except json.JSONDecodeError:
                machines = []
    else:
        machines = []

    # Met à jour ou ajoute la machine ( par meziane pour manipuler les machines)
    updated = False
    for i, m in enumerate(machines):
        if m["nom"] == incoming_data["nom"]:
            # Conserve et enrichit l'historique si présent
            existing_history = m.get("history", [])
            new_point = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "cpu": incoming_data["cpu"],
                "temp": incoming_data["temp"]
            }
            history = (existing_history + [new_point])[-12:]
            incoming_data["history"] = history

            machines[i] = incoming_data  # remplace l'entrée existante
            updated = True
            break
    if not updated:
        # Crée un historique initial avec la première mesure réelle
        incoming_data["history"] = [{
            "time": datetime.now().strftime("%H:%M:%S"),
            "cpu": incoming_data["cpu"],
            "temp": incoming_data["temp"]
        }]
        machines.append(incoming_data)

    # Sauvegarde dans data.json
    with open(data_file, "w") as f:
        json.dump(machines, f, indent=2)

    return jsonify({"status": "ok"})
