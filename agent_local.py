import psutil
import requests
import time
import socket

SERVER_URL = "http://127.0.0.1:5000/metrics"  # URL du serveur Flask
INTERVAL = 10  # intervalle d'envoi en secondes

def get_local_ip():
    """Méthode simple pour récupérer l'IP locale.

    Ouvre un socket UDP vers une IP publique (ne transmet pas de données)
    et lit l'adresse locale utilisée. En cas d'échec retourne loopback.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def collect_metrics():
    "Collecte les métriques système du poste local"

    # Récupérer le nom d'hôte et l'IP locale (méthode simple)
    ip = get_local_ip()

    # Récupérer température CPU (si dispo)
    temps = psutil.sensors_temperatures()
    if temps:
        # On prend la première valeur trouvée
        for entries in temps.values():
            if entries:
                temp = entries[0].current
                break
        else:
            temp = 0
    else:
        temp = 0

    return {
        "hostname": socket.gethostname(),
        "ip": ip,
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network_sent": psutil.net_io_counters().bytes_sent,
        "network_recv": psutil.net_io_counters().bytes_recv,
        "temp": temp
    }

def send_metrics(data):
    "Envoie les métriques collectées au serveur central Flask."
    try:
        requests.post(SERVER_URL, json=data, timeout=5)
        print("[OK] Données envoyées")
    except Exception as e:
        print(f"[ERREUR] Envoi impossible : {e}")

def main():
    print("Agent de supervision lancé...\n")
    while True:
        metrics = collect_metrics()
        print(metrics)  # Affiche les données pour debug
        send_metrics(metrics)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
