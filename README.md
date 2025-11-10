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

+----+----------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-------------+
| ID | Fonctionnalité                         | Description                                                                                                                        | Dépendance  |
+----+----------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-------------+
| F1 | Agent de récupération des métriques    | Récupère les informations CPU, RAM, disque et état de la connexion Internet sur chaque machine                                     | —           |
| F2 | Envoi des données au serveur           | Transmet périodiquement les données collectées par l’agent au serveur central                                                     | F1          |
| F3 | Serveur Flask                          | Reçoit et gère les données envoyées par les agents                                                                                | F2          |
| F4 | Dashboard simple                       | Affiche l’état global du parc (machines surveillées, métriques principales)                                                       | F3          |
| F5 | Détection et mise en évidence anomalies| Analyse les données reçues pour identifier les anomalies (CPU/RAM/disque élevés)                                                  | F3          |
| F6 | Graphiques interactifs                 | Visualise les métriques sous forme de graphiques dynamiques                                                                       | F3, F4      |
+----+----------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-------------+

