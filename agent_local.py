import psutil
import requests
import time
import socket

SERVER_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{SERVER_URL}/agent-login"
METRICS_URL = f"{SERVER_URL}/metrics"
INTERVAL = 5

# Credentials de l'agent (a adapter selon la machine)
AGENT_HOSTNAME = socket.gethostname()
AGENT_USERNAME = "agent_sinkis"
AGENT_PASSWORD = "password123"

# Variables pour calculer le debit et garder le token
last_network_sent = None
last_network_recv = None
last_time = None
last_debit = 0.0
agent_token = None

def get_local_ip():
    """Recupere l'adresse IP locale."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def authenticate_agent():
    """Authentifie l'agent et retourne un token."""
    global agent_token
    
    auth_data = {
        "hostname": AGENT_HOSTNAME,
        "username": AGENT_USERNAME,
        "password": AGENT_PASSWORD
    }
    
    try:
        resp = requests.post(LOGIN_URL, json=auth_data, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            agent_token = data.get("token")
            print(f"[AUTH] Agent authentifie avec succes - Token: {agent_token[:20]}...")
            return True
        else:
            print(f"[AUTH] Erreur authentification: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[AUTH] Erreur connexion: {e}")
        return False

def calculate_network_speed():
    """Calcule le debit reseau en Mbps."""
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
    """Collecte les metriques systeme."""
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
        "hostname": AGENT_HOSTNAME,
        "ip": ip,
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "temp": temp,
        "debit": debit
    }

def send_metrics(data):
    """Envoie les metriques avec le token d'authentification."""
    global agent_token
    
    if not agent_token:
        print("[ERREUR] Pas de token - authentification requise")
        return False
    
    headers = {
        "Authorization": f"Bearer {agent_token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(METRICS_URL, json=data, headers=headers, timeout=5)
        if resp.status_code == 200:
            print("[OK] Donnees envoyees")
            return True
        else:
            print(f"[ERREUR] Envoi echoue: {resp.status_code}")
            if resp.status_code == 401:
                print("[AUTH] Token invalide - reauthentification requise")
                agent_token = None
            return False
    except Exception as e:
        print(f"[ERREUR] Envoi impossible: {e}")
        return False

def main():
    global agent_token
    
    print("Agent de supervision lance...")
    print(f"Hostname: {AGENT_HOSTNAME}")
    print("Authentification aupres du serveur...")
    
    # Authentifier l'agent
    if not authenticate_agent():
        print("[ERREUR] Impossible de s'authentifier - arret de l'agent")
        return
    
    print("Initialisation des mesures reseau...")
    calculate_network_speed()
    print("Attente de 5 secondes avant premier envoi...")
    time.sleep(5)
    
    while True:
        metrics = collect_metrics()
        print(f"Metriques collectees: CPU={metrics['cpu']}%, RAM={metrics['ram']}%, Debit={metrics['debit']}Mbps")
        
        if not send_metrics(metrics):
            # Si erreur d'authentification, essayer de se reauthentifier
            if agent_token is None:
                print("[AUTH] Tentative de reauthentification...")
                if authenticate_agent():
                    send_metrics(metrics)
        
        print(f"Attente de {INTERVAL}s avant prochain envoi...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
