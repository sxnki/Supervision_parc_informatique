
import json
import os
import random
from datetime import datetime, timedelta

def generate_machines():
  
    
    machines = []
    
    for i in range(1, 7):  # Crée 6 machines (i = 1 à 6)

        # DONNÉES ACTUELLES (dernière mesure)

        
        # Valeurs de CPU et Temp pour le cœur de la simulation
        current_cpu = random.randint(20, 90)
        current_temp = random.randint(40, 80)
        

        # CRÉER L'HISTORIQUE (12 derniers points)

        
        history = []
        
        # Crée des données pour les 12 dernières minutes
        for minute_ago in range(11, -1, -1):
          
            # Génère le timestamp
            timestamp = (datetime.now() - timedelta(minutes=minute_ago)).strftime('%H:%M')
            
            # Ajoute du bruit aux valeurs (variation réaliste)
            # CPU varie de ±10% par rapport à la valeur actuelle
            cpu_variation = current_cpu + random.randint(-10, 10)
            cpu_history = max(0, min(100, cpu_variation))  # Clamp entre 0 et 100
            
            # Temp varie de ±5°C
            temp_variation = current_temp + random.randint(-5, 5)
            temp_history = max(30, min(90, temp_variation))  # Clamp entre 30 et 90
            
            # Ajoute au historique
            history.append({
                'time': timestamp,
                'cpu': cpu_history,
                'temp': temp_history
            })
        
       
        # CRÉER LA MACHINE
        
        machine = {
            'nom': f'machine-{i:02d}',  # Format: machine-01, machine-02, etc.
            'ip': f'192.168.1.{10 + i}',  # IPs: 192.168.1.11, 192.168.1.12, etc.
            'cpu': current_cpu,  # Pourcentage CPU (0-100)
            'ram': random.randint(40, 85),  # Pourcentage RAM (40-85)
            'disque': random.randint(30, 80),  # Pourcentage disque (30-80)
            'temp': current_temp,  # Température en °C
            'debit': round(random.uniform(10, 100), 2),  # Débit en MB/s
            'history': history  # 12 points historiques
        }
        
        machines.append(machine)
    
    return machines
    
   


def get_machines_from_json(filename='data.json'):
    """
    FONCTION: Charge les machines depuis un fichier JSON
    
    PARAMÈTRE:
    - filename: Nom du fichier JSON (par défaut 'data.json')
    
    RETOUR:
    - Liste des machines si fichier existe
    - None si fichier n'existe pas
    
    FORMAT ATTENDU DU JSON:
    [
        {
            "nom": "machine-01",
            "ip": "192.168.1.11",
            "cpu": 45,
            "ram": 60,
            "disque": 30,
            "temp": 50,
            "debit": 45.5
        },
        ...
    ]
    
    NOTE: Le fichier JSON ne contient pas l'historique
    L'historique sera généré manuellement si besoin
    """
    
    try:
        # Vérifie si le fichier existe
        if not os.path.exists(filename):
            print(f"Fichier {filename} non trouvé")
            return None
        
        # Ouvre et lit le fichier JSON
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Données chargées depuis {filename}")
        return data
        
    except json.JSONDecodeError:
        # Erreur de lecture JSON
        print(f" Erreur: {filename} n'est pas un JSON valide")
        return None
    except Exception as e:
        # Autre erreur
        print(f" Erreur lecture {filename}: {e}")
        return None


# FONCTION PRINCIPALE: GET_MACHINES()


def get_machines():
    """
     FONCTION PRINCIPALE: Récupère les machines (JSON ou simulation)
    
    PRIORITÉ:
    1. Essaie de charger depuis data.json (données réelles)
    2. Si échoue → génère des machines simulées
    
    RETOUR: Liste des machines
    
    UTILISATION:
        machines = get_machines()
        for m in machines:
            print(f"{m['nom']}: CPU={m['cpu']}%")
    """
    
    print(" Chargement des données...")
    

    # ESSAIE D'ABORD LE FICHIER JSON

    
    machines = get_machines_from_json('./server/data.json')
    
    if machines is not None:
        # Fichier JSON trouvé et valide
        # Ajoute l'historique à chaque machine (s'il n'existe pas)
        # Garde le débit existant (calculé réellement par l'agent)
        for m in machines:
            if 'history' not in m:
                # Si pas d'historique, génère des données fictives
                m['history'] = generate_history()
            # Le débit est déjà présent depuis data.json (reçu de l'agent)
            if 'debit' not in m:
                m['debit'] = 0
        
        return machines
    

    # FALLBACK: GÉNÈRE DES MACHINES SIMULÉES
	#FAIS POUR UN REMIER TEST
    
    print("  data.json non trouvé, utilisation de données simulées")
    print(" Conseil: Crée data.json pour utiliser vos vraies données")
    
    return generate_machines()


# GÉNÉRER L'HISTORIQUE


def generate_history():
    """
    FONCTION: Génère un historique fictif pour une machine
    
    UTILITÉ:
    - Quand on charge data.json, les machines n'ont pas d'historique
    - Cette fonction crée 12 points de données fictives
    
    RETOUR: Liste de 12 points d'historique
    """
    
    history = []
    
    for minute_ago in range(11, -1, -1):
        timestamp = (datetime.now() - timedelta(minutes=minute_ago)).strftime('%H:%M')
        
        history.append({
            'time': timestamp,
            'cpu': random.randint(20, 90),
            'temp': random.randint(40, 80)
        })
    
    return history


# TEST DU MODULE


if __name__ == '__main__':
    """
     TEST: Si on exécute ce fichier directement
    
    COMMANDE:
        python machines.py
    
    AFFICHE: Les 6 machines avec leurs données
    """
    
    print("═" * 80)
    print("TEST: Affichage des machines")
    print("═" * 80)
    
    machines = get_machines()
    
    for m in machines:
        print(f"\n📱 {m['nom']} ({m['ip']})")
        print(f"   CPU: {m['cpu']}% | RAM: {m['ram']}% | Disque: {m['disque']}%")
        print(f"   Temp: {m['temp']}°C | Débit: {m.get('debit', 0)} MB/s")
        print(f"   Historique: {len(m.get('history', []))} points")
