# Supervision de Parc Informatique

## Groupe ABM

**Membres:**
- Delhoum Ahmed
- Yassine Bakadir
- Nouali Meziane

---

## Description du Projet

Outil de supervision d'un parc informatique permettant de monitorer en temps reel les ressources 
(CPU, RAM, Disque, Debit reseau) de plusieurs machines. Chaque machine execute un agent qui 
envoie periodiquement ses metriques a un serveur Flask. Le serveur expose un dashboard web 
affichant l'etat global du parc et mettant en evidence les anomalies detectees.

---

## 1. Bibliotheques Utilisees

### 1.1 Flask (>= 3.0)
**Description:** Framework web Python leger et facile d'utilisation
**Raison du choix:** Ideal pour creer rapidement un serveur HTTP avec des routes et gestion des sessions
**Modules importes:**
- `Flask` - Initialisation de l'application
- `render_template` - Rendu des templates HTML (login, dashboard)
- `request` - Gestion des donnees des requetes POST/GET
- `redirect, url_for` - Redirection entre pages
- `session` - Gestion des sessions utilisateur
- `jsonify` - Conversion des donnees en JSON
- `make_response` - Creation de reponses HTTP personnalisees

**Utilisation dans le projet:**
- Serveur principal exposant les routes API
- Gestion des sessions d'authentification
- Routes pour le login, logout, dashboard, API data

---

### 1.2 Flask-Cors (>= 4.0)
**Description:** Extension Flask pour gerer Cross-Origin Resource Sharing
**Raison du choix:** Permet au frontend JavaScript d'effectuer des requetes vers le backend
**Modules importes:**
- `CORS` - Fonction pour autoriser les requetes cross-origin

**Utilisation dans le projet:**
- Autorisation des appels API du navigateur vers le serveur (http://localhost:8080)

---

### 1.3 psutil (>= 5.9)
**Description:** Bibliotheque Python pour acceder aux informations systeme
**Raison du choix:** Fournit un acces facile aux metriques CPU, RAM, disque et reseau
**Modules importes:**
- `psutil.cpu_percent()` - Pourcentage d'utilisation CPU
- `psutil.virtual_memory()` - Informations sur la RAM
- `psutil.disk_usage()` - Espace disque utilise
- `psutil.net_io_counters()` - Statistiques reseau (bytes envoyes/recus)
- `psutil.sensors_temperatures()` - Temperature du CPU

**Utilisation dans le projet:**
- Collecte des metriques systeme dans l'agent (agent_local.py)
- Mesure de la bande passante reseau

---

### 1.4 requests (>= 2.31)
**Description:** Bibliotheque Python pour effectuer des requetes HTTP
**Raison du choix:** Syntaxe simple et fiable pour envoyer des donnees en POST
**Modules importes:**
- `requests.post()` - Envoi de donnees en POST
- `requests.get()` - Recuperation de donnees en GET

**Utilisation dans le projet:**
- Envoi des metriques de l'agent au serveur (POST /metrics)
- Communication entre agent_local.py et app.py

---

## 2. Structure du Projet

### 2.1 Arborescence Complete

```
supervison_parts/
├── agent_local.py                 # Agent de collecte des metriques
├── app.py                         # Serveur Flask principal
├── machines.py                    # Gestion des donnees machines
├── groupe.csv                     # Donnees des membres du groupe
├── requirements.txt               # Dependances Python
├── server/
│   ├── server.py                  # Initialisation du serveur Flask
│   ├── data.json                  # Fichier JSON - donnees des machines
│   ├── routes/
│   │   ├── data_route.py          # Routes pour recuperer les donnees
│   │   └── upload_route.py        # Route pour recevoir metriques de l'agent
│   └── utils/
│       └── anomaly_detector.py    # Detection des anomalies
├── static/
│   └── script.js                  # Frontend JavaScript
└── templates/
    ├── login.html                 # Page de connexion
    └── dashboard.html             # Page du dashboard
```

### 2.2 Description Detaillee des Fichiers

#### Fichiers Racine

| Fichier | Type | Description | Fonction Principale |
|---|---|---|---|
| `agent_local.py` | Python | Agent collecteur de metriques systeme | `main()` - Boucle d'execution |
| `app.py` | Python | Serveur Flask principal avec routes API | `api_data()` - Retourne donnees |
| `machines.py` | Python | Gestion des donnees machines (JSON ou simulation) | `get_machines()` - Charge donnees |
| `groupe.csv` | CSV | Informations des membres du groupe | Documentation |
| `requirements.txt` | TXT | Dependances Python | Configuration |

#### Dossier server/

| Fichier | Type | Description |
|---|---|---|
| `server.py` | Python | Initialisation app Flask avec blueprints |
| `data.json` | JSON | Stockage des metriques des machines |

#### Dossier server/routes/

| Fichier | Fonction | Route | Description |
|---|---|---|---|
| `data_route.py` | `get_data()` | GET /data | Retourne donnees depuis data.json |
| `data_route.py` | `health()` | GET /health | Health check du serveur |
| `upload_route.py` | `upload_metrics()` | POST /metrics | Recoit metriques de l'agent |

#### Dossier server/utils/

| Fichier | Fonction | Description |
|---|---|---|
| `anomaly_detector.py` | `check_anomalies()` | Detecte anomalies (CPU, RAM, Disque) |

#### Dossier static/

| Fichier | Description |
|---|---|
| `script.js` | Frontend JavaScript (graphiques, fetch, auth) |

#### Dossier templates/

| Fichier | Description | Route |
|---|---|---|
| `login.html` | Page de connexion | GET / |
| `dashboard.html` | Dashboard avec metriques | GET /dashboard |

---

## 3. Modules et Fonctions du Projet

### A. agent_local.py (Agent de Collecte)
| Fonction | Description | Utilite |
|---|---|---|
| `get_local_ip()` | Recupere l'IP locale de la machine | Identification de la machine dans les donnees envoyees |
| `calculate_network_speed()` | Calcule le debit reseau en Mbps (envoi + reception) | Mesure de la bande passante utilisee |
| `collect_metrics()` | Collecte CPU, RAM, Disque, Temp, IP, nom d'hote | Rassemble toutes les metriques systeme |
| `send_metrics(data)` | Envoie les metriques en POST au serveur | Transmet les donnees toutes les 5 secondes |
| `main()` | Boucle principale de l'agent | Execution periodique de la collecte et l'envoi |

### B. machines.py (Gestion des Donnees)
| Fonction | Description | Utilite |
|---|---|---|
| `generate_machines()` | Genere des donnees simulees de 6 machines | Permet de tester sans agent reel |
| `generate_history()` | Cree un historique fictif de 12 points | Fournit des donnees pour les graphiques |
| `get_machines_from_json(filename)` | Charge les machines depuis data.json | Recupere les vraies donnees des agents |
| `get_machines()` | Charge depuis JSON ou genere des donnees simulees | Fonction principale utilisee par le serveur |

### C. app.py (Serveur Flask Principal)
| Fonction | Description | Utilite |
|---|---|---|
| `api_login()` | Route POST /api/login - Authentification | Verif username/password et creation de session |
| `api_logout()` | Route POST /api/logout - Deconnexion | Supprime la session utilisateur |
| `login()` | Route GET / - Affiche la page login | Redirection vers le dashboard si authentifie |
| `dashboard()` | Route GET /dashboard - Affiche le dashboard | Page principale avec les metriques |
| `api_data()` | Route GET /api/data - Retourne les donnees JSON | Donnees brutes pour le frontend JavaScript |
| `auth_status()` | Route GET /api/auth-status - Verifie l'authentification | Verifie si l'utilisateur est connecte |
| `export_csv()` | Route GET /api/export-csv - Export CSV | Telecharge les donnees en fichier CSV |

### D. server/routes/upload_route.py (Reception des Metriques)
| Fonction | Description | Utilite |
|---|---|---|
| `upload_metrics()` | Route POST /metrics - Recoit les donnees de l'agent | Recupere et sauvegarde les metriques dans data.json |

### E. server/routes/data_route.py (Acces aux Donnees)
| Fonction | Description | Utilite |
|---|---|---|
| `get_data()` | Route GET /data - Retourne data.json | Permet au serveur d'acceder aux donnees |
| `health()` | Route GET /health - Health check | Verifie que le serveur est operationnel |

### F. server/utils/anomaly_detector.py (Detection d'Anomalies)
| Fonction | Description | Utilite |
|---|---|---|
| `check_anomalies(sample)` | Detecte si CPU/RAM/Disque depassent les seuils | Identifie les machines problematiques (seuils: CPU>=88%, RAM>=80%, Disque>=90%) |

### G. static/script.js (Frontend JavaScript)
Gere l'affichage dynamique du dashboard avec:
- Authentification et deconnexion
- Chargement periodique des donnees (toutes les 5s)
- Affichage des cartes machines
- Generation de graphiques (Chart.js)
- Affichage des details d'une machine (modal)
- Export CSV

---

## 4. Repartition des Taches

### Ahmed (Delhoum Ahmed)
- **Fonction 1:** `agent_local.py` - `get_local_ip()` - Recuperation de l'adresse IP locale
- **Fonction 2:** `agent_local.py` - `collect_metrics()` - Collecte des metriques systeme

### Yassine (Yassine Bakadir)
- **Fonction 3:** `machines.py` - `generate_machines()` - Generation de donnees simulees
- **Fonction 5:** `machines.py` - `get_machines()` - Logique principale de chargement des donnees
- **Fonction 7:** `app.py` - `api_data()` - Endpoint d'acces aux donnees du dashboard

### Meziane (Nouali Meziane)

#### Fonctions Realisees:
- **Fonction 4:** `machines.py` - `generate_history()` - Creation de l'historique fictif de 12 points pour les graphiques
- **Fonction 6:** `server/utils/anomaly_detector.py` - `check_anomalies()` - Detection des anomalies sur CPU/RAM/Disque
- **Fonction 9:** `server/routes/upload_route.py` - `upload_metrics()` - Reception et sauvegarde des metriques envoyees par l'agent
- **Fonction 10:** `app.py` - `api_login()` et `api_logout()` - Authentification utilisateur sur le dashboard
- **Fonction 11:** `app.py` - `export_csv()` - Export des donnees en fichier CSV

#### Taches Restantes et Retouches pour Meziane:
- **Validation des donnees:** Verifier et optimiser la fonction `upload_metrics()` pour mieux valider les donnees entrees (verifier les types, les limites de CPU/RAM/Disque)
- **Test de l'export CSV:** Tester l'export CSV avec differentes donnees et s'assurer que tous les champs sont inclus correctement
- **Ajustement des seuils:** Verifier que les seuils d'anomalies dans `check_anomalies()` (CPU>=88%, RAM>=80%, Disque>=90%) sont adaptes au contexte
- **Securite de l'authentification:** S'assurer que la fonction `api_login()` est robuste et que les donnees de session sont bien protegees
- **Gestion des erreurs:** Ajouter une meilleure gestion des erreurs dans toutes les fonctions pour eviter les crashes du serveur

---

## Installation et Utilisation

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
pip install -r requirements.txt
```

### Lancement du Serveur
```bash
python3 app.py
```

### Lancement de l'Agent
```bash
python3 agent_local.py
```

### Acces au Dashboard
- URL: http://localhost:8080/
- Identifiants par defaut: admin / louvre

---
