from flask import Blueprint, request, current_app, jsonify
import json
import os
import secrets
from datetime import datetime

bp = Blueprint("auth", __name__)

# Stockage des tokens actifs en memoire (en production, utiliser Redis ou une BD)
active_tokens = {}

@bp.post("/agent-login")
def agent_login():
    """
    Route POST /agent-login
    - Authentifie un agent (machine)
    - Retourne un token d'authentification
    
    Body attendu:
    {
      "hostname": "machine-01",
      "username": "agent1",
      "password": "password123"
    }
    """
    incoming = request.get_json()
    
    if not incoming:
        return jsonify({"error": "Donnees manquantes"}), 400
    
    hostname = incoming.get("hostname")
    username = incoming.get("username")
    password = incoming.get("password")
    
    if not hostname or not username or not password:
        return jsonify({"error": "hostname, username et password requis"}), 400
    
    # Charger les credentials des agents (fichier dans server/agents_credentials.json)
    agents_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents_credentials.json")
    
    try:
        with open(agents_file, "r") as f:
            agents_data = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Erreur lecture credentials: {e}"}), 500
    
    # Verifier les credentials
    agent_found = False
    for agent in agents_data.get("agents", []):
        if (agent.get("hostname") == hostname and 
            agent.get("username") == username and 
            agent.get("password") == password):
            agent_found = True
            break
    
    if not agent_found:
        return jsonify({"error": "Authentification echouee - identifiants invalides"}), 401
    
    # Generer un token unique
    token = secrets.token_urlsafe(32)
    
    # Stocker le token avec l'hostname et timestamp
    active_tokens[token] = {
        "hostname": hostname,
        "username": username,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"[AUTH] Agent authentifie: {hostname} (user: {username})")
    
    return jsonify({
        "success": True,
        "token": token,
        "message": "Authentification reussie"
    }), 200

@bp.post("/agent-logout")
def agent_logout():
    """
    Route POST /agent-logout
    - Deconnecte un agent et invalide son token
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if token in active_tokens:
        hostname = active_tokens[token]["hostname"]
        del active_tokens[token]
        print(f"[AUTH] Agent deconnecte: {hostname}")
        return jsonify({"success": True, "message": "Deconnexion reussie"}), 200
    
    return jsonify({"error": "Token invalide"}), 401

def verify_agent_token(token):
    """
    Verifie si un token est valide
    Retourne (True, hostname) si valide, (False, None) sinon
    """
    if token in active_tokens:
        return True, active_tokens[token]["hostname"]
    return False, None
