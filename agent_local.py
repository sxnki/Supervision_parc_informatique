import psutil
import requests
import time
import socket

SERVER_URL = "http://127.0.0.1:5000/metrics"  # URL du serveur Flask
INTERVAL = 5  # intervalle d'envoi en secondes

# Variables pour calculer le debit
last_network_sent = None
last_network_recv = None
last_time = None
last_debit = 0.0

def get_local_ip():
    """Methode simple pour recuperer l'IP locale."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def calculate_network_speed():
    """Calcule le debit reseau en Mbps (megabits par seconde)"""
    global last_network_sent, last_network_recv, last_time, last_debit
    
    current_time = time.time()
    net_stats = psutil.net_io_counters()
    current_sent = net_stats.bytes_sent
    current_recv = net_stats.bytes_recv
    
    if last_network_sent is None:
        last_network_sent = current_sent
        last_network_recv = current_recv
        last_time = current_time
        last_debit = 0.0
        print("[INFO] Premiere mesure reseau initialisee")
        return 0.0
    
    time_diff = current_time - last_time
    
    if time_diff < 1.0:
        return last_debit
    
    sent_diff = max(0, current_sent - last_network_sent)
    recv_diff = max(0, current_recv - last_network_recv)
    total_bytes = sent_diff + recv_diff
    
    debit_mbps = (total_bytes * 8 / (1024.0 * 1024.0)) / time_diff
    debit_mbps = max(0, round(debit_mbps, 2))
    
    last_network_sent = current_sent
    last_network_recv = current_recv
    last_time = current_time
    last_debit = debit_mbps
    
    return debit_mbps

def collect_metrics():
    """Collecte les metriques systeme du poste local"""
    ip = get_local_ip()

    temp = 0
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for entries in temps.values():
                if entries:
                    temp = entries[0].current
                    break
    except Exception:
        temp = 0

    debit = calculate_network_speed()

    return {
        "hostname": socket.gethostname(),
        "ip": ip,
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "temp": temp,
        "debit": debit
    }

def send_metrics(data):
    """Envoie les metriques collectees au serveur central Flask."""
    try:
        requests.post(SERVER_URL, json=data, timeout=5)
        print("[OK] Donnees envoyees")
    except Exception as e:
        print(f"[ERREUR] Envoi impossible: {e}")

def main():
    print("Agent de supervision lance...")
    print("Initialisation des mesures reseau (attente 5 secondes)...")
    calculate_network_speed()
    print("Attente de 5 secondes avant premier envoi...")
    time.sleep(5)
    
    while True:
        metrics = collect_metrics()
        print(f"Metriques collectees: {metrics}")
        send_metrics(metrics)
        print(f"Attente de {INTERVAL}s avant prochain envoi...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
