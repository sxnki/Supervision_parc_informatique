# Supervision de parc informatique

## Groupe ABM
- Nom du groupe : ABM
- Membres :
	-Delhoum Ahmed
	-Nouali Meziane
	-Yassine Bakadir

## Description du projet
Le projet consiste à réaliser un outil qui supervise un parc informatique. 
Chaque machine surveillée dispose d'un agent qui envoie régulièrement des informations au serveur 
(CPU, RAM, espace disque,état de la connexion Internet).
Le serveur expose une page web (dashboard) affichant l'état du parc, en priorisant les machines avec des anomalies.

| ID   | Fonctionnalité                             | Description                                                                                                                      | Dépendance |
|------|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-------------|
| F1   | Agent de récupération des métriques         | Récupère les informations CPU, RAM, disque et état de la connexion Internet sur chaque machine                                   | —           |
| F2   | Envoi des données au serveur                | Transmet périodiquement les données collectées par l’agent au serveur central                                                   | F1          |
| F3   | Serveur Flask                               | Reçoit et gère les données envoyées par les agents                                                                              | F2          |
| F4   | Dashboard simple                            | Affiche l’état global du parc (machines surveillées, métriques principales)                                                     | F3          |
| F5   | Détection et mise en évidence des anomalies | Analyse les données reçues pour identifier les anomalies (CPU/RAM/disque élevés)                                                | F3          |
| F6   | Graphiques interactifs                      | Visualise les métriques sous forme de graphiques dynamiques                                                                     | F3, F4      |

| ID   | Fonctionnalité additionnelle               | Description                                                                                                               | Dépendance |
|------|---------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|-------------|
| F7   | Historique des métriques                   | Enregistre les données CPU/RAM/Disque/Réseau dans une base de données pour permettre un suivi temporel                    | F1, F2, F3  |
| F8   | Alertes en temps réel                      | Envoie un e-mail ou une notification (Slack, Telegram, etc.) en cas d’anomalie détectée                                   | F5          |
| F9   | Authentification sur le dashboard           | Protège l’accès au tableau de bord via un login/mot de passe                                                              | F3, F4      |
| F10  | Filtrage et tri des machines                | Permet de trier et filtrer les machines par taux d’utilisation CPU/RAM, état du disque, ou statut de connexion             | F4          |
| F11  | Export des rapports                         | Génère des rapports PDF ou CSV contenant l’état du parc et les anomalies détectées                                        | F3, F4, F5  |



---

## Points d'entree (run)
- `python3 server/server.py` : lance le serveur API agents (port 5000) / routes `/agent-login`, `/agent-logout`, `/metrics`, `/data`, `/health`.
- `python3 app.py` : lance le serveur dashboard (port 8080) avec `/api/login`, `/api/data`, `/api/export-csv`, pages `login`/`dashboard`.
- `python3 agent_local.py` : lance l'agent sur une machine a superviser (doit pointer vers le serveur API en 5000 par defaut il pointe sur le local link 127.0.0.1/5000 meme machine que le server).
- Frontend : dashboard servi par `app.py` (`templates/dashboard.html`, JS dans `static/script.js`).

---

## Routes principales
| Route | Methode | Role | Securite |
| --- | --- | --- | --- |
| `/agent-login` | POST | Authentifier un agent (hostname/user/pass) et renvoyer un token | Creds agents + token genere |
| `/agent-logout` | POST | Invalider un token agent | Token Bearer |
| `/metrics` | POST | Reception metriques agent, mise a jour `data.json` + historique | Token Bearer requis |
| `/api/data` | GET | Donnees machines (dashboard, app.py 8080) | Session utilisateur |
| `/api/export-csv` | GET | Export CSV des donnees courantes (app.py 8080) | Session utilisateur |
| `/api/login` | POST | Authentification dashboard (app.py 8080) | Session |
| `/api/logout` | POST | Deconnexion dashboard (app.py 8080) | Session |
| `/health` | GET | Ping du serveur | Public |

---


## Architecture et fichiers
```
supervison_parts/
├─ server/
│  ├─ server.py              # create_app, blueprints (app server)
│  ├─ data.json              # donnees machines (courant + historique 12 points)
│  ├─ agents_credentials.json# credentials agents (hostname/username/password)
│  ├─ routes/
│  │  ├─ auth_route.py       # /agent-login, /agent-logout, verify_agent_token
│  │  ├─ upload_route.py     # /metrics (token obligatoire), persistance + historique
│  │  └─ data_route.py       # /data, /health
│  └─ utils/
│     └─ anomaly_detector.py # detection anomalies (seuils CPU/RAM/Disque)
├─ agent_local.py            # agent collecte/envoi (auth + metrics) (appa gent local)
├─ app.py                    # routes dashboard (/api/login, /api/logout, /api/data, /api/export-csv) (dashboard)
├─ machines.py               # lecture data.json ou generation simulee (fallback)
├─ static/script.js          # frontend (fetch /api/data, graphiques, modals)
├─ templates/login.html      # page de connexion
├─ templates/dashboard.html  # dashboard
├─ requirements.txt          # dependances
└─ README.md             # documentation
```


## Repartition des taches (trace)
- **Ahmed** : `agent_local.py` (collecte metriques, IP locale), boucle d'envoi.
- **Yassine** : Routes serveur API (upload/data/health) et `server/server.py` (sauf auth agents), gestion de la persistance `data.json`.
- **Meziane** : 
  - `app.py` (complet) : dashboard, routes API, export CSV, anomalies
  - `machines.py` : lecture data.json, fallback simulateur pour un test, vérification existence données réelles
  - Auth agents : login/logout + token Bearer (`/agent-login`, `/agent-logout`)
  - Authentification des routes agent→server : vérification Bearer token sur `/metrics`
  - Auth dashboard : sessions (`/api/login`, `/api/logout`)
  - Frontend HTML/CSS : authentification, vérification existence data.json
  - Frontend JS (`script.js`) : rafraîchissement données, graphiques Chart.js
  - Historique réel (12 points CPU/Temp)


---


## Bibliotheques utilisees
### Frameworks / extensions
- **Flask** : serveur web, routes, sessions, templates.
- **Flask-Cors** : CORS pour appels JS.

### Libs externes
- **psutil** : CPU, RAM, disque, reseau, temperatures (agent).
- **requests** : appels HTTP depuis l'agent.
- **Chart.js** (frontend) : rendu des graphes.

### Standard Python (principales)
- **json** (lecture/ecriture `data.json`, credentials agents)
- **os / pathlib** (chemins de fichiers)
- **secrets** (generation de tokens)
- **datetime** (timestamp des points d'historique)
- **random** (donnees simulees fallback)
- **socket** (recuperer IP locale dans l'agent)
- **time** (intervalle d'envoi metriques)

---

## Flux general
1. L'agent lit ses credentials (`AGENT_HOSTNAME/USERNAME/PASSWORD`), appelle `/agent-login` (serveur API 5000), recoit un token Bearer.
2. L'agent envoie periodiquement `/metrics` (serveur API 5000) avec `Authorization: Bearer <token>` et les metriques collectees.
3. Le serveur API valide le token, ecrit/actualise `server/data.json` et ajoute un point d'historique (12 derniers points CPU/Temp).
4. Le dashboard (app.py en 8080) lit `server/data.json` via `/api/data` toutes les 5s, affiche cartes + graphes (Chart.js).
5. `/api/export-csv` (dashboard) permet de telecharger les donnees courantes en CSV.
> Pour des donnees temps reel, il faut lancer **les deux** : `server/server.py` (API agents) et `app.py` (dashboard). Sans le serveur API, le dashboard n'aura pas de nouvelles mesures (sauf fallback simulateur).

---


## Schéma du flux

```
[Agent] ---- POST /agent-login ----> [API Server :5000]
  |                                      |
  |--(Token Bearer reçu)-----------------|
  |
[Agent] ---- POST /metrics (Bearer) ----> [API Server :5000] ----> server/data.json
                                                       
[Dashboard :8080] <---- GET /api/data ---- [API Server :5000]
```

Ce schéma résume l’authentification côté agent, l’envoi sécurisé des métriques vers le serveur API (port 5000) avec persistance dans `server/data.json`, puis la lecture des données par le dashboard (port 8080) via `/api/data`.

---


## Bibliotheques utilisees et justifications

### Frameworks / extensions
- **Flask** : serveur web, routes, sessions, templates.
- **Flask-Cors** : CORS pour appels JS.

### Libs externes
- **psutil** : CPU, RAM, disque, reseau, temperatures (agent).
- **requests** : appels HTTP depuis l'agent.
- **Chart.js** (frontend) : rendu des graphes.

### Standard Python (principales)
- **json** (lecture/ecriture `data.json`, credentials agents)
- **os / pathlib** (chemins de fichiers)
- **secrets** (generation de tokens)
- **datetime** (timestamp des points d'historique)
- **random** (donnees simulees fallback)
- **socket** (recuperer IP locale + hostname de la machine; `psutil` ne fournit pas cela directement) ( par meziane)
- **time** (intervalle d'envoi metriques)

---

## Imports detailles par fichier (Meziane)

### app.py - Dashboard Web
**Imports :**
```python
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from machines import get_machines
from server.utils.anomaly_detector import check_anomalies
import csv
from io import StringIO
```

**Justifications :**
- **Flask** : Classe principale pour creer l'application web (dashboard).
- **render_template** : Rendu des pages HTML (login.html, dashboard.html) avec Jinja2.
- **request** : Recupere les donnees POST/GET des formulaires et appels AJAX.
- **redirect, url_for** : Redirections entre pages (login -> dashboard).
- **session** : Gestion des sessions utilisateur (authentification dashboard simple avec cookies).
- **jsonify** : Conversion Python dict -> JSON pour les reponses API (`/api/data`, `/api/login`).
- **make_response** : Creation de reponses HTTP personnalisees (headers CSV pour le telechargement).
- **get_machines** : Fonction importee de `machines.py` pour charger les donnees machines (reel ou simule).
- **check_anomalies** : Fonction importee pour detecter les depassements de seuils (CPU/RAM/Disque).
- **csv** : Module standard pour generer le fichier CSV d'export.
- **StringIO** : Buffer memoire pour creer le CSV sans fichier temporaire sur disque.

**Pourquoi ces choix :**
- Session Flask simple au lieu de JWT : dashboard usage interne, leger et natif.
- CSV genere cote serveur : garantit exactitude des donnees exportees (meme source que l'affichage).
- StringIO pour CSV : evite I/O disque, export direct en memoire -> reponse HTTP.

---

### machines.py - Gestion donnees
**Imports :**
```python
import json
import os
import random
from datetime import datetime, timedelta
```

**Justifications :**
- **json** : Lecture/ecriture de `server/data.json` (donnees reelles des agents).
- **os** : Verification existence fichier (`os.path.exists`), chemins relatifs.
- **random** : Generation de donnees simulees (CPU, RAM, debit aleatoires) pour tests sans agents actifs.
- **datetime, timedelta** : Timestamp des points historiques simules (format HH:MM).

**Pourquoi ces choix :**
- Fallback simulateur : permet de tester le dashboard sans deployer d'agents.
- JSON natif : pas besoin de base de donnees pour ce projet simple, fichier JSON suffit.
- random pour realisme : donnees simulees varient pour tester les graphiques et anomalies.

---

### server/routes/auth_route.py - Authentification agents
**Imports :**
```python
from flask import Blueprint, request, current_app, jsonify
import json
import os
import secrets
from datetime import datetime
```

**Justifications :**
- **Blueprint** : Modularite Flask, route auth separee du reste (reutilisable).
- **request** : Recupere les credentials JSON envoyes par l'agent (hostname/user/pass).
- **current_app** : Acces a la config Flask (non utilise ici mais pattern standard).
- **jsonify** : Reponse JSON (token, erreur auth).
- **json** : Lecture de `agents_credentials.json` pour valider identifiants.
- **os** : Chemin vers `agents_credentials.json` (relatif au fichier routes/).
- **secrets** : Generation cryptographiquement sure de tokens (`token_urlsafe(32)`).
- **datetime** : Timestamp de creation du token (pour log/debug/expiration future).

**Pourquoi ces choix :**
- **secrets au lieu de sessions Flask** : 
  - API REST stateless (pas de cookies).
  - Clients non-web (agent Python) ne gerent pas facilement les cookies Flask.
  - Token Bearer dans header HTTP = standard API (Authorization: Bearer <token>).
  - Controle granulaire (invalidation, expiration custom, multi-agents).
  - Separation auth dashboard (sessions) vs auth agents (tokens).
- **secrets vs random** : random n'est pas cryptographiquement sur, secrets l'est (important pour securite tokens).
- **Stockage memoire (active_tokens dict)** : simple pour ce projet, mais persistance (Redis/DB) recommandee en production.

---

### Comparaison tokens manuels vs Flask natif

| Aspect | Tokens manuels (secrets) | Sessions Flask |
|--------|-------------------------|----------------|
| **Usage** | API REST, clients non-web | Applications web navigateur |
| **Transport** | Header HTTP (Bearer) | Cookie HTTP |
| **Stateless** | Oui (sauf stockage tokens) | Non (session cote serveur) |
| **Client** | Facile (requests library) | Complexe (gestion cookies) |
| **Controle** | Total (expiration custom, revocation) | Limite (expire session Flask) |
| **Securite** | secrets = crypto sure | Flask signe cookies (itsdangerous) |
| **Production** | Ajouter JWT/expiration | Production-ready natif |

**Conclusion :** Pour agents machines (API REST), tokens manuels adaptes. Pour dashboard web, sessions Flask suffisantes.

---



## Modules et fonctions cles
### server/routes/auth_route.py
- `agent_login()` : verifie credentials agents (`agents_credentials.json`), genere token (`secrets.token_urlsafe`), stocke en memoire `active_tokens`.
- `agent_logout()` : invalide un token.
- `verify_agent_token(token)` : valide le token (utilise par `/metrics`).

### server/routes/upload_route.py
- `upload_metrics()` : requiert `Authorization: Bearer <token>`. Met a jour `data.json`, ajoute un point d'historique (HH:MM:SS, CPU, Temp) et conserve les 12 derniers.

### server/routes/data_route.py
- `get_data()` : retourne `data.json` (historique inclus).
- `health()` : ping serveur.

### agent_local.py
- `authenticate_agent()` : POST `/agent-login`, recupere/stocker le token.
- `calculate_network_speed()` : debit en Mbps (delta bytes_sent/recv / temps * 8 / 1024^2).
- `collect_metrics()` : CPU, RAM, disque, temp (psutil), IP locale, debit.
- `send_metrics()` : POST `/metrics` avec Bearer; reauth si 401.
- `main()` : boucle 5s (auth, collecte, envoi).

### app.py
- `/api/login`, `/api/logout` : auth dashboard (sessions).
- `/api/data` : donnees pour le frontend.
- `/api/export-csv` : export CSV.
- templates `login` et `dashboard` (Jinja).

### static/script.js - Frontend Dashboard
**Usage de Bootstrap & Chart.js :**

Bootstrap (CDN v5.3.2) est utilise pour le layout et design responsive du dashboard :
- **Grille Bootstrap (col-md-4, row, container-fluid)** : Affichage des cartes machines en 3 colonnes.
- **Cartes (card, card-body, card-title)** : Conteneurs pour afficher infos machines; couleur rouge (bg-danger) si anomalies, gris (bg-secondary) sinon.
- **Boutons (btn, btn-primary, btn-outline-success, ms-2)** : Boutons "Details", "Exporter CSV", "Se deconnecter"; espacements Bootstrap.
- **Modal Bootstrap** : Affichage des details machines dans une fenetre modale.

Chart.js (CDN v3.9.1) genere les graphiques :
- **Bar chart CPU/Temperature** : Comparaison visuelle entre machines.
- **Line chart Details** : Historique temps reel (12 points) pour une machine (modal).

**Fonctions JavaScript :**
- `fetchData()` : Appel API `/api/data` toutes les 5s pour rechargement automatique.
- `renderMachinesList()` : Creation cartes machines avec classes Bootstrap dynamiques.
- `renderOverviewCharts()` : Generation graphiques CPU/Temp avec Chart.js.
- `showDetails(machineName)` : Affichage modal avec historique reel.
- `exportCSV()` : Appel `/api/export-csv` pour telecharger donnees.
- Logout via `/api/logout` puis redirection vers login.

**Pourquoi Bootstrap + Chart.js :**
- Bootstrap evite ecrire CSS complet, fournit design coherent (theme sombre, responsive).
- Chart.js pour graphiques interactifs sans jQuery lourd, API simple.
- CDN : pas d'installation, charge rapide, compatibilite navigateur garantie.
- **Aucune dependance lourde** : Pas de jQuery, pas de frameworks lourds (React/Vue/Angular). Utilisation de vanilla JavaScript avec Fetch API (natif). Cela maintient la frontend legere, rapide a charger, et facile a maintenir pour un petit projet.

### machines.py
- `get_machines()` : charge `server/data.json` (reel) ou fallback simule (`generate_machines`). Plus de generation d'historique fictif quand des donnees reelles existent.
  - **Detection donnees reelles** : verifie l'existence et validite de `server/data.json`; si le fichier contient des entrees avec horodatage et metriques (CPU, RAM, debit), c'est une donnee reelle d'agent. Sinon, fallback au simulateur.
- `generate_machines()` : donnees simulees + historique simule pour tests.
  - **Fallback automatique** : le simulateur n'est utilise que si aucun agent n'a encore genere de donnees. Des qu'un agent envoie des mesures valides, le simulateur s'arrete automatiquement et les donnees reelles remplacent les simulations.

### server/utils/anomaly_detector.py
- `check_anomalies(sample)` : seuils (CPU>=88%, RAM>=80%, Disque>=90%).

---

## Securite et tokens (agents)
- Credentials agents : `server/agents_credentials.json` (hostname/username/password).
- Login agent : `/agent-login` -> token Bearer (secrets), stocke en memoire (`active_tokens`).
- Acces metriques : `/metrics` refuse sans token valide (401).
- **Perte de token apres redemarrage serveur** : Les tokens stockes en memoire sont perdus si le serveur redémarre. Cela necesssite une **reconnexion automatique côté agent** : `agent_local.py` gère un 401 en reappelant `authenticate_agent()` pour obtenir un nouveau token. Aucune intervention manuelle requise.
- **Expiration des tokens** : Actuellement pas de limite temporelle. Amelioration possible : ajouter un timestamp dans `active_tokens`, puis valider que `datetime.now() - token_timestamp < timedelta(hours=24)` par exemple. Ou utiliser JWT avec expiration auto.
- Ameliorations possibles : expiration de token (itsdangerous/JWT), persistance tokens (Redis/DB), hash des mots de passe agents.

---

### Justificatifs des choix techniques (Meziane)

#### Choix d'architecture
- **Auth dashboard via session simple** : Suffisant pour limiter l'acces au tableau de bord; plus leger qu'un SSO/JWT pour l'usage local demande. Sessions Flask natives (cookies) parfaites pour navigation web.
- **Auth agents par token Bearer** : 
  - Evite l'envoi repete des mots de passe (une fois au login, token ensuite).
  - Permet rejet rapide (401) si token manquant/invalid.
  - Standard API REST pour clients non-web.
  - Generation avec `secrets.token_urlsafe()` (cryptographiquement sur).
  - Controle total sur cycle de vie (creation, invalidation, expiration future).
- **Separation des ports 5000/8080** : Isole ingestion securisee (agents) et service utilisateur (dashboard), facilite tests et debug.

#### Choix de donnees
- **Export CSV cote serveur** : Garantie d'exactitude (meme source que le dashboard), evite logique CSV dans navigateur, format universel pour analyse externe.
- **Historique reel (12 points)** : Fournit des graphes coherents sans generer faux historiques; fenetre courte pour rester legere en memoire/disque; timestamp precis (HH:MM:SS).
- **Seuils anomalies fixes** : Choix rapide pour mettre en evidence machines a risque; ajustables facilement dans `anomaly_detector.py` si contexte change.

#### Choix de bibliotheques
- **secrets au lieu de random** : `random` n'est pas cryptographiquement sur, `secrets` l'est (tokens imprevisibles).
- **secrets au lieu de JWT** : Simplicite pour ce projet (pas de dependance externe), mais JWT recommande en production (expiration auto, signature verifiable).
- **StringIO pour CSV** : Evite I/O disque, export direct en memoire vers reponse HTTP (performances).
- **json au lieu de SQLite** : Projet simple avec peu de machines, JSON suffit et plus leger. Migration vers DB possible si volumetrie augmente.

---

## Utilisation rapide
1) `pip install -r requirements.txt`
2) Lancer serveur API agents : `python3 server/server.py` (port 5000)
3) Lancer agent : `python3 agent_local.py` (adapter credentials/URL si besoin)
4) Lancer dashboard : `python3 app.py` (port 8080) puis ouvrir http://localhost:8080 (login dashboard requis)

      Agent → API Server (5000) → data.json → Dashboard (8080)

---

## Notes
- L'historique affiche est reel des que les agents envoient des mesures. Sans `data.json`, les donnees sont simulees (tests).
- Les tokens agents sont en memoire (reset au redemarrage du serveur). Ajouter une persistance si besoin


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Développement détaillé – Contribution de Yassine:
### server/server.py – Serveur API agents

Imports :

```python
from flask import Flask
from flask_cors import CORS
from routes.auth_route import auth_bp
from routes.upload_route import upload_bp
from routes.data_route import data_bp
```

Justifications :
J’utilise Flask pour créer l’API REST dédiée aux agents de supervision. Flask-Cors est activé afin d’autoriser les appels HTTP provenant d’agents exécutés sur des machines distantes. Les blueprints auth_bp, upload_bp et data_bp permettent de découper l’API en modules distincts et cohérents.

Pourquoi ces choix :
J’ai choisi une architecture basée sur une application factory avec create_app afin de centraliser l’initialisation du serveur. La séparation en blueprints améliore fortement la lisibilité du code, facilite la maintenance et permet d’ajouter de nouvelles routes sans modifier le cœur du serveur. Cette organisation est proche de ce qui est utilisé en contexte professionnel.

---

### server/routes/upload_route.py – Réception et persistance des métriques

Imports :

```python
from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import os
from routes.auth_route import verify_agent_token
```

Justifications :
Blueprint est utilisé pour isoler la logique liée à la réception des métriques. request permet de récupérer les données JSON envoyées par l’agent. datetime est utilisé pour horodater chaque mesure. json et os permettent de lire et d’écrire dans le fichier data.json. verify_agent_token est appelé afin de sécuriser l’accès à la route /metrics.

Fonction principale :
La fonction upload_metrics vérifie systématiquement la présence d’un en-tête Authorization contenant un token Bearer valide. Si le token est absent ou invalide, la requête est rejetée avec un code 401. Lorsque le token est valide, les métriques envoyées par l’agent sont intégrées dans server/data.json. Les valeurs courantes de la machine sont mises à jour et un nouveau point est ajouté à l’historique, en conservant uniquement les douze derniers points.

Pourquoi ces choix :
La validation systématique du token empêche toute injection de données non autorisée. L’horodatage précis permet une visualisation temporelle cohérente dans le dashboard. La limitation à douze points garantit des graphes lisibles tout en réduisant l’occupation mémoire. L’utilisation d’un fichier JSON unique évite la complexité d’une base de données pour un projet académique de taille réduite.

---

### server/routes/data_route.py – Exposition des données et état du serveur

Imports :

```python
from flask import Blueprint, jsonify
import json
import os
```

Justifications :
Blueprint permet d’isoler les routes de consultation des données. json et os sont utilisés pour accéder au fichier data.json et vérifier son existence avant lecture.

Routes implémentées :
La route /data retourne l’intégralité du contenu de data.json au format JSON. La route /health renvoie une réponse simple confirmant que le serveur API est opérationnel.

Pourquoi ces choix :
La route /data constitue une source unique et cohérente pour le dashboard. La route /health permet de vérifier rapidement l’état du serveur lors des tests ou du débogage. La séparation stricte entre ingestion et exposition des données simplifie l’architecture globale.

---

### server/data.json – Modèle de persistance

Le fichier data.json a été conçu comme une structure centrale regroupant toutes les informations nécessaires au dashboard. Pour chaque machine identifiée par son hostname, il contient les métriques courantes ainsi qu’un historique temporel. Cette organisation garantit que les données affichées dans les cartes et celles utilisées pour les graphiques proviennent exactement de la même source.

Pourquoi ce choix :
Le format JSON est simple à manipuler, lisible et facile à déboguer. Il est suffisant pour un nombre limité de machines et permet une validation rapide par l’enseignant. Une migration vers une base de données resterait possible si la volumétrie augmentait.

---

### Sécurité et cohérence de l’API

L’ensemble des routes critiques que j’ai développées respecte un contrat d’API strict. Les agents doivent obligatoirement s’authentifier avant d’envoyer des métriques et les données reçues sont validées avant persistance. Les réponses HTTP sont cohérentes et directement exploitables par agent_local.py et app.py.

Cette approche garantit une intégration fluide avec l’authentification des agents et avec le dashboard, sans couplage fort entre les composants.

---

### Justificatifs des choix techniques

Architecture serveur :
J’ai mis en place une API REST dédiée aux agents afin de séparer clairement la supervision machine de l’interface utilisateur. L’utilisation de blueprints Flask permet une organisation modulaire et pédagogique. L’application factory create_app centralise toute l’initialisation du serveur.

Gestion des données :
Le choix du JSON comme format de persistance est volontairement simple et adapté au cadre académique. L’historique glissant limite la taille des données stockées. Les mises à jour sont faites de manière cohérente afin d’éviter toute désynchronisation entre données courantes et historiques.

Intégration avec le reste du projet :
Les routes développées sont totalement compatibles avec l’authentification des agents et avec le dashboard. Les données exposées sont directement consommables par machines.py et par le frontend sans transformation supplémentaire. Le flux agent → serveur → dashboard est clair, traçable et stable.

---

### Conclusion sur ma contribution

Ma contribution constitue le socle serveur du projet de supervision. J’ai conçu et implémenté une API robuste, sécurisée et cohérente, assurant la réception fiable des métriques, leur persistance et leur exposition au dashboard. Cette partie garantit la stabilité du système, la clarté des flux de données et une séparation nette des responsabilités, éléments essentiels pour un projet de supervision réaliste et correctement évalué sur le plan académique.
.
