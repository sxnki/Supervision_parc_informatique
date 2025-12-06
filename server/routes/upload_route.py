from flask import Blueprint, request, current_app, jsonify
import json, os

bp = Blueprint("upload", __name__)

@bp.post("/metrics")
def upload_metrics():
    """
    Route POST /metrics
    - Reçoit les données JSON d'une machine
    - Met à jour data.json avec ces données
    - Formate les données pour correspondre au dashboard
    """
    data_file = current_app.config["DATA FILE"]
    incoming = request.get_json()

    # Vérifie les données ( ajouterpar meziane pour verification )
    if not incoming or "hostname" not in incoming:
        return jsonify({"error": "Données invalides"}), 400

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
            machines[i] = incoming_data  # remplace l'entrée existante
            updated = True
            break
    if not updated:
        machines.append(incoming_data)

    # Sauvegarde dans data.json
    with open(data_file, "w") as f:
        json.dump(machines, f, indent=2)

    return jsonify({"status": "ok"})
