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

## Noyau et fonctionnalités  minimal  (indispensable)
- Agent pour récupérer CPU, RAM, disque, état de la connexion Internet  
- Envoi des données au serveur  
- Serveur Flask qui reçoit les données  
- Dashboard simple affichant l’état des machines  
- Détection et mise en évidence des anomalies (ex.temp CPU > 80°C et RAM > 80%, disque presque plein)

## Fonctionnalités supplémentaires
- Graphiques interactifs des métriques (CPU/RAM/Disque/Reseaux)  

## Dépendances
- Agent -> psutil : pour récupérer CPU, RAM, espace disque  
- Envoi des données -> requests : pour transmettre les informations au serveur  
- Serveur -> Flask : pour recevoir les données et afficher le dashboard  
- Graphiques -> Plotly : pour visualiser CPU, RAM et disque
- Détection d’anomalies -> code custom : pour identifier les machines avec CPU/RAM élevés ou disque presque plein

## Priorités des fonctionnalités (ordre décroissant)
  - Agent récupérant CPU/RAM/Disque  
  - Envoi des données au serveur  
  - Serveur Flask  
  - Dashboard simple  
  - Détection et mise en évidence des anomalies  
  - Graphiques interactifs  
