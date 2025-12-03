# Analyse des briques logicielles utilisées dans mon projet de supervision

Dans ce document, je présente les différentes briques logicielles que  on étudiées et comparées pour réaliser les fonctionnalités de mon projet de supervision système. L’objectif est d’expliquer les possibilités, les limites et les implications de chaque choix technique.

---

## 1. Collecte des métriques système (CPU, RAM, disque, réseau, température, hostname, IP)

###    Briques logicielles possibles

#### **1) `psutil` (librairie tierce Python)**
- **Service rendu** : permet de récupérer l’utilisation CPU, RAM, disque, réseau, et parfois la température.
- **Limites** :
  - Les températures ne sont pas disponibles sur toutes les machines.
  - Certaines métriques dépendent du système d’exploitation.
- **Installation** : très simple (`pip install psutil`).
- **Facilité d’utilisation** : API claire et fonctionnelle.
- **Compatibilité** : Windows, Linux, macOS (mais températures surtout sous Linux).
- **Maintenance** : très active, librairie fiable.
- **Communauté & documentation** : excellente.

#### **2) `socket` (librairie standard)**
- **Service rendu** : récupérer le hostname et l’IP locale.
- **Limites** :
  - Ne donne pas l’adresse IP publique.
- **Installation** : aucune (standard).
- **Facilité d’utilisation** : simple.
- **Compatibilité** : totale.
- **Maintenance** : intégrée à Python.

#### **3) `requests` (librairie tierce)**
- **Service rendu** : envoi des métriques au serveur Flask.
- **Limites** :
  - Erreurs réseau à gérer (timeouts, refus de connexion).
- **Installation** : `pip install requests`.
- **Facilité d’utilisation** : API intuitive.
- **Compatibilité** : universelle.
- **Maintenance & communauté** : très solides.

---

## 2. Stockage et mise à jour des données machines

###    Briques logicielles évaluées

#### **1) Fichier JSON (librairie standard : `json`)**
- **Service rendu** : stockage simple et rapide.
- **Limites** :
  - Risque d’écrasement si plusieurs accès simultanés.
  - Pas idéal pour de grosses quantités de données.
- **Installation** : standard.
- **Facilité d’utilisation** : simple.
- **Compatibilité** : parfaite.

#### **2) Base de données SQLite**
- **Avantages** :
  - Fiable pour les écritures fréquentes.
  - Pas de corruption de fichier.
- **Limites** :
  - Plus complexe à mettre en place.
- **Situation actuelle** :   on a choisi JSON pour commencer, car suffisant pour le projet.

---

## 3. Serveur web & API pour la supervision

###    Briques logicielles

#### **1) Flask**
- **Service rendu** :
  - API REST pour recevoir les métriques.
  - Gestion des sessions (login).
  - Serveur web pour afficher le dashboard.
- **Limites** :
  - Plus simple que Django mais moins structuré.
- **Installation** : `pip install flask`.
- **Facilité d’utilisation** : très accessible.
- **Compatibilité** : Linux, Windows, macOS.
- **Maintenance** : excellente.
- **Communauté** : énorme.

#### **2) Bootstrap (front-end)**
- **Service rendu** : mise en page responsive, propre et moderne.
- **Limites** :
  - Styles parfois limités si customisation poussée.
- **Installation** : CDN (aucune installation nécessaire).
- **Communauté** : très active.

#### **3) Chart.js**
- **Service rendu** : graphiques pour CPU/Temp en temps réel.
- **Limites** :
  - Demande un rafraîchissement manuel (pas de websockets).
- **Installation** : via CDN.
- **Utilisation** : simple.
- **Documentation** : très bonne.

---

## 4. Export CSV & PDF des données

###    Briques logicielles étudiées

#### **1) Export CSV (JavaScript)**
- **Méthode utilisée** : génération locale via Blob.
- **Avantages** :
  - Simple et sans dépendance.
- **Limites** :
  - Pas de mise en forme avancée.

#### **2) Export PDF**
 on étudié deux approches :

##### **Option A : jsPDF (côté navigateur)**
- **Service rendu** : génère un PDF directement dans le navigateur.
- **Limites** :
  - Mise en page plus limitée.
  - Mauvaise gestion des longues tables.
- **Communauté** : correcte.

##### **Option B : FPDF (côté serveur)**
- **Service rendu** :
  - Génération côté serveur, meilleure gestion des tableaux.
  - Gestion plus propre pour un usage professionnel.
- **Limites** :
  - Mise en page manuelle.
- **Installation** : `pip install fpdf`.
- **Documentation** : suffisante.

   **  on a choisi FPDF côté serveur** car plus fiable pour exporter un rapport complet.

---

## 5. Détection d’anomalies (CPU, RAM, temp…)

###    Briques logicielles

#### **1) Système maison en Python**
- Comparaison des valeurs avec des seuils prédéfinis.
- Très simple, aucun module nécessaire.
- Limites : pas d’apprentissage automatique.

#### **2) Possibilités évaluées (mais non retenues)**
- `scikit-learn` → détection avancée mais surdimensionnée.
- `tensorflow` → inutile pour ce cas.

   **  on a choisi une détection simple**, suffisante pour ce projet.

---

## 6. Authentification utilisateur

###    Briques logicielles

#### **Flask session**
- **Service rendu** : gestion d’un utilisateur connecté.
- **Limites** :
  - Nécessite une clé secrète.
- **Installation** : incluse dans Flask.
- **Utilisation** : simple.

#### **Ajax côté front (Fetch API)**
- Utilisé pour login/logout sans recharger la page.

---

# Conclusion générale

Pour chaque fonctionnalité,   on a étudié plusieurs options, puis choisi les briques qui étaient :

- les plus simples à intégrer,
- les plus robustes,
- bien documentées,
- adaptées à un projet étudiant mais évolutives.

Le projet repose aujourd’hui sur :

- **psutil** pour la collecte,
- **Flask** pour le serveur et l’API,
- **JSON** pour le stockage immédiat,
- **Bootstrap + Chart.js** pour l’interface,
- **FPDF** pour l’export PDF,
- **Fetch API + JavaScript** pour le front,
- **Détection d’anomalies maison**.
