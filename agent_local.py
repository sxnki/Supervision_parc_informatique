import psutil
import requests
import time
import socket

SERVER_URL = "http://127.0.0.1:5000/metrics"   # URL du serveur Flask
INTERVAL = 10  # intervalle d'envoi en secondes

def collect_metrics():
    """Collecte les métriques système du poste local."""
    return {
        "hostname": socket.gethostname(),
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network_sent": psutil.net_io_counters().bytes_sent,
        "network_recv": psutil.net_io_counters().bytes_recv
    }

def send_metrics(data):
    """Envoie les métriques collectées au serveur central Flask."""
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