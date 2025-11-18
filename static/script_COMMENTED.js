/*
═══════════════════════════════════════════════════════════════════════════════
SCRIPT.JS - LOGIQUE DU DASHBOARD (JAVASCRIPT)
═══════════════════════════════════════════════════════════════════════════════

📋 OBJECTIF:
   Gérer la logique du dashboard:
   - Récupérer les données des machines
   - Afficher les machines sous forme de cartes
   - Créer les graphiques
   - Gérer les exports (CSV, PDF)
   - Gérer la déconnexion

🔄 FLUX GÉNÉRAL:
   1. Page charge → DOMContentLoaded déclenche
   2. Attache les événements aux boutons
   3. Appelle fetchData() pour charger les machines
   4. setInterval(fetchData, 5000) rafraîchit toutes les 5 secondes
   5. Utilisateur intéragit (détails, export, logout)

═══════════════════════════════════════════════════════════════════════════════
*/

// ═══════════════════════════════════════════════════════════════════════════════
// VARIABLES GLOBALES
// ═══════════════════════════════════════════════════════════════════════════════

// Stocke la liste des machines récupérées de l'API
let machines = [];

// Seuils d'alerte pour les anomalies
// Une machine est en anomalie si CPU > 80% ou Temp > 75°C
const THRESH = {
    cpu: 80,      // Seuil d'alerte CPU (80%)
    temp: 75,     // Seuil d'alerte température (75°C)
    ram: 80,      // Seuil d'alerte RAM (80%)
    disque: 90    // Seuil d'alerte disque (90%)
};

// ═══════════════════════════════════════════════════════════════════════════════
// ÉVÉNEMENT: PAGE CHARGÉE (DOMContentLoaded)
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    /*
    🔔 EVENT: DOMContentLoaded
    Se déclenche une seule fois quand le HTML est complètement chargé
    (Mais pas encore les images)
    
    À ce moment:
    - Tous les éléments HTML sont disponibles en JavaScript
    - On peut attacher les événements
    - On peut faire les appels API
    */
    
    // ─────────────────────────────────────────────────────────────────────────
    // GESTION LOGOUT
    // ─────────────────────────────────────────────────────────────────────────
    
    const logoutBtn = document.getElementById('logoutBtn');
    // Récupère le bouton "Se déconnecter"
    
    if (logoutBtn) {
        // Si le bouton existe (au cas où)
        logoutBtn.addEventListener('click', async () => {
            /*
            🔔 EVENT: Click sur le bouton logout
            */
            try {
                // Envoie une requête AJAX vers /api/logout
                const response = await fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                // Récupère la réponse JSON
                const data = await response.json();
                
                if (data.success) {
                    // ✅ Déconnexion réussie
                    // Redirige vers la page de login
                    window.location.href = '/';  // Revenir à localhost:8080/
                }
            } catch (error) {
                console.error('Erreur logout:', error);
            }
        });
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // GESTION BOUTONS EXPORT
    // ─────────────────────────────────────────────────────────────────────────
    
    // Bouton "Exporter CSV"
    const exportCsvBtn = document.getElementById('export-csv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', exportCSV);
        // Quand on clique, appelle la fonction exportCSV()
    }
    
    // Bouton "Exporter PDF"
    const exportPdfBtn = document.getElementById('export-pdf');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', exportPDF);
        // Quand on clique, appelle la fonction exportPDF()
    }
    
    // ─────────────────────────────────────────────────────────────────────────
    // CHARGEMENT DES DONNÉES ET RAFRAÎCHISSEMENT AUTOMATIQUE
    // ─────────────────────────────────────────────────────────────────────────
    
    // Première charge des données
    fetchData();
    
    // Rafraîchir les données toutes les 5 secondes (5000 ms)
    setInterval(fetchData, 5000);
    /*
    setInterval(fonction, délai):
    - Exécute 'fonction' tous les 'délai' millisecondes
    - Ici: fetchData() tous les 5000 ms (5 secondes)
    
    EFFET: Les données se mettent à jour en temps réel
    */
});

// ═══════════════════════════════════════════════════════════════════════════════
// CHARGEMENT DES DONNÉES
// ═══════════════════════════════════════════════════════════════════════════════

async function fetchData() {
    /*
    📡 FONCTION: Récupère les données des machines du serveur
    
    FLUX:
    1. Fait fetch('/api/data') au serveur Flask
    2. Récupère la liste des machines en JSON
    3. Appelle renderMachinesList() pour afficher les cartes
    4. Appelle renderOverviewCharts() pour les graphiques
    
    ASYNC/AWAIT:
    - async: La fonction est asynchrone (peut prendre du temps)
    - await: Attend que fetch() retourne avant de continuer
    - Permet de ne pas bloquer l'interface utilisateur
    */
    
    try {
        // Envoie une requête GET vers /api/data
        const res = await fetch('/api/data');
        
        // Si statut 401 (non authentifié)
        if (res.status === 401) {
            // La session a expiré, redirige vers le login
            window.location.href = '/';
            return;  // Arrête la fonction
        }
        
        // Récupère les données en JSON
        machines = await res.json();
        // 'machines' est maintenant la liste complète des machines
        // Format: [{ nom, ip, cpu, ram, disque, temp, etat, history }, ...]
        
        // Affiche les machines sous forme de cartes
        renderMachinesList();
        
        // Affiche les graphiques (CPU et Temp)
        renderOverviewCharts();
        
    } catch(e) {
        // En cas d'erreur (problème réseau, crash serveur, etc.)
        console.error('Erreur fetch:', e);
        // console.error: Affiche l'erreur dans la console du navigateur
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// AFFICHAGE DES MACHINES
// ═══════════════════════════════════════════════════════════════════════════════

function renderMachinesList() {
    /*
    🎨 FONCTION: Affiche les machines sous forme de cartes Bootstrap
    
    LOGIQUE:
    1. Vide le conteneur (#machinesList)
    2. Trie les machines (anomalies en premier)
    3. Pour chaque machine: crée une carte HTML
    4. Injecte dans le DOM
    
    RENDU:
    Les machines s'affichent dans <div id="machinesList" class="row g-3">
    Sous forme de colonnes de 3 (col-md-4)
    */
    
    // Récupère le conteneur
    const container = document.getElementById('machinesList');
    
    // Le vide complètement
    container.innerHTML = '';

    // ─────────────────────────────────────────────────────────────────────────
    // TRI: ANOMALIES EN PREMIER
    // ─────────────────────────────────────────────────────────────────────────
    
    // Trie les machines
    const sortedMachines = machines.sort((a, b) => {
        // Vérifie si chaque machine a une anomalie
        const aAnomaly = a.cpu > THRESH.cpu || a.temp > THRESH.temp;
        const bAnomaly = b.cpu > THRESH.cpu || b.temp > THRESH.temp;
        
        // Retrie: true (1) avant false (0) → les anomalies d'abord
        return bAnomaly - aAnomaly;
        
        /*
        EXEMPLE:
        - Machine 1: CPU=85% (anomalie) → true → 1
        - Machine 2: CPU=50% (ok) → false → 0
        
        1 - 0 = 1 → Machine 1 avant Machine 2 ✅
        */
    });

    // ─────────────────────────────────────────────────────────────────────────
    // CRÉE UNE CARTE POUR CHAQUE MACHINE
    // ─────────────────────────────────────────────────────────────────────────
    
    for (const m of sortedMachines) {
        // Pour chaque machine 'm' dans la liste
        
        // Crée une colonne
        const col = document.createElement('div');
        col.className = 'col-md-4';  // Largeur: 33% (1/3 de l'écran)
        
        // Crée une carte (card)
        const card = document.createElement('div');
        card.className = 'card text-light';
        
        // ─────────────────────────────────────────────────────────────────────
        // COULEUR: RED SI ANOMALIE, GRIS SI OK
        // ─────────────────────────────────────────────────────────────────────
        
        const hasAnomaly = m.cpu > THRESH.cpu || m.temp > THRESH.temp;
        // Vérifie si la machine a une anomalie
        
        if (hasAnomaly) {
            card.classList.add('bg-danger');  // Rouge si anomalie
        } else {
            card.classList.add('bg-secondary');  // Gris si ok
        }

        // ─────────────────────────────────────────────────────────────────────
        // COULEUR DU BADGE (CONNECTÉE/DÉCONNECTÉE)
        // ─────────────────────────────────────────────────────────────────────
        
        const statusBadge = m.etat === 'connectée' 
            ? '<span class="badge bg-success">connectée</span>'      // Vert si connectée
            : '<span class="badge bg-secondary">déconnectée</span>'; // Gris si déconnectée

        // ─────────────────────────────────────────────────────────────────────
        // CONTENU DE LA CARTE (HTML)
        // ─────────────────────────────────────────────────────────────────────
        
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${m.nom}</h5>
                <p class="card-text"><small>${m.ip}</small></p>
                <div class="mb-2">
                    <div>CPU: ${m.cpu}%</div>
                    <div>RAM: ${m.ram}%</div>
                    <div>Disque: ${m.disque}%</div>
                    <div>Temp: ${m.temp}°C</div>
                </div>
                ${statusBadge}
                <button class="btn btn-sm btn-primary ms-2" onclick="showDetails('${m.nom}')">Détails</button>
            </div>
        `;
        /*
        Template HTML:
        - ${m.nom}: Remplace par le nom de la machine
        - ${m.cpu}, ${m.ram}, etc.: Remplace par les valeurs
        - ${statusBadge}: Injecte le badge connectée/déconnectée
        - onclick="showDetails('machine-01')": Appelle showDetails au clic
        */
        
        // Ajoute la carte à la colonne
        col.appendChild(card);
        
        // Ajoute la colonne au conteneur
        container.appendChild(col);
    }
    
    /*
    RÉSULTAT FINAL:
    <div id="machinesList">
        <div class="col-md-4">
            <div class="card bg-danger">
                <!-- Contenu machine 1 -->
            </div>
        </div>
        <div class="col-md-4">
            <div class="card bg-secondary">
                <!-- Contenu machine 2 -->
            </div>
        </div>
        ...
    </div>
    */
}

// ═══════════════════════════════════════════════════════════════════════════════
// GRAPHIQUES
// ═══════════════════════════════════════════════════════════════════════════════

function renderOverviewCharts() {
    /*
    📊 FONCTION: Crée les graphiques CPU et Température
    
    LIBRAIRIE: Chart.js
    Type de graphique: Bar chart (graphique en barres)
    
    DONNÉES:
    - X: Noms des machines (machine-01, machine-02, etc.)
    - Y: Pourcentages (CPU% ou Temp°C)
    */
    
    // Récupère les noms des machines pour l'axe X
    const labels = machines.map(m => m.nom);
    // Exemple: ["machine-01", "machine-02", "machine-03", ...]
    
    // Récupère les valeurs CPU pour l'axe Y
    const cpuData = machines.map(m => m.cpu);
    // Exemple: [45, 85, 30, 60, 50, 75]
    
    // Récupère les valeurs Température pour l'axe Y
    const tempData = machines.map(m => m.temp);
    // Exemple: [50, 70, 40, 55, 48, 65]

    // ─────────────────────────────────────────────────────────────────────────
    // GRAPHIQUE CPU
    // ─────────────────────────────────────────────────────────────────────────
    
    const overviewCPUChart = document.getElementById('overviewCPUChart');
    // Récupère le canvas où dessiner le graphique
    
    const overviewTempChart = document.getElementById('overviewTempChart');
    // Récupère le canvas pour la température
    
    if (!overviewCPUChart || !overviewTempChart) {
        // Si les canvas n'existent pas, arrête
        return;
    }

    // Récupère le contexte 2D du canvas CPU
    const ctxCPU = overviewCPUChart.getContext('2d');
    
    // Détruit le graphique précédent (s'il existe)
    if (window.cpuChart) window.cpuChart.destroy();
    
    // Crée un nouveau graphique Chart.js
    window.cpuChart = new Chart(ctxCPU, {
        type: 'bar',  // Type: graphique en barres
        data: {
            labels,  // Noms des machines sur X
            datasets: [{
                label: 'CPU (%)',  // Légende
                data: cpuData,     // Valeurs
                backgroundColor: 'rgba(54,162,235,0.7)'  // Couleur bleue
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100  // Maximum 100% sur l'axe Y
                }
            }
        }
    });

    // ─────────────────────────────────────────────────────────────────────────
    // GRAPHIQUE TEMPÉRATURE
    // ─────────────────────────────────────────────────────────────────────────
    
    const ctxTemp = overviewTempChart.getContext('2d');
    if (window.tempChart) window.tempChart.destroy();
    
    window.tempChart = new Chart(ctxTemp, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Temp (°C)',
                data: tempData,
                backgroundColor: 'rgba(255,99,132,0.7)'  // Couleur rouge
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 120  // Maximum 120°C
                }
            }
        }
    });
    
    /*
    RÉSULTAT: Deux graphiques s'affichent avec les données
    - Graphique CPU: barres bleues
    - Graphique Température: barres rouges
    - Les graphiques se mettent à jour automatiquement toutes les 5 secondes
    */
}

// ═══════════════════════════════════════════════════════════════════════════════
// DÉTAILS MACHINE (MODAL)
// ═══════════════════════════════════════════════════════════════════════════════

function showDetails(machineName) {
    /*
    📋 FONCTION: Affiche les détails d'une machine dans une modal
    
    MODAL: Fenêtre pop-up qui s'affiche au-dessus du contenu
    (Utilise Bootstrap)
    
    CONTENU:
    - Titre: Nom de la machine et IP
    - Graphique en ligne: Historique du CPU et Température
    */
    
    // Trouve la machine dans la liste
    const m = machines.find(x => x.nom === machineName);
    if (!m) return;  // Si pas trouvée, arrête
    
    // Extrait les données historiques
    const labels = (m.history || []).map(h => h.time);  // Timestamps
    const cpu = (m.history || []).map(h => h.cpu);      // Historique CPU
    const temp = (m.history || []).map(h => h.temp);    // Historique Temp

    // Crée une modal
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'detailsModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content bg-secondary text-light">
                <div class="modal-header">
                    <h5 class="modal-title">${m.nom} — ${m.ip || ''}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <canvas id="machineDetailChart"></canvas>
                </div>
            </div>
        </div>
    `;
    
    // Ajoute la modal au DOM
    document.body.appendChild(modal);
    
    // Affiche la modal (Bootstrap)
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Crée le graphique après un petit délai
    setTimeout(() => {
        const ctx = document.getElementById('machineDetailChart');
        if (ctx) {
            if (window.machineChart) window.machineChart.destroy();
            
            // Graphique en ligne (line chart)
            window.machineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,  // Timestamps sur l'axe X
                    datasets: [
                        {
                            label: 'CPU %',
                            data: cpu,
                            borderColor: 'rgba(54,162,235,1)',  // Bleu
                            fill: false
                        },
                        {
                            label: 'Temp °C',
                            data: temp,
                            borderColor: 'rgba(255,99,132,1)',  // Rouge
                            fill: false
                        }
                    ]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 120
                        }
                    }
                }
            });
        }
    }, 100);
    
    /*
    RÉSULTAT: Une modal s'ouvre avec:
    - Titre: machine-01 — 192.168.1.11
    - Graphique en ligne: CPU (bleu) et Temp (rouge)
    - L'historique se voit sur les 12 dernières minutes
    */
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────────
// EXPORT CSV
// ─────────────────────────────────────────────────────────────────────────

function exportCSV() {
    /*
    💾 FONCTION: Télécharge les données en fichier CSV
    
    FORMAT CSV:
    nom,ip,cpu,ram,disque,temp,etat
    machine-01,192.168.1.11,45,60,30,50,connectée
    machine-02,192.168.1.12,85,70,40,60,connectée
    ...
    
    PROCESSUS:
    1. Crée un tableau CSV (lignes et colonnes)
    2. Convertit en texte
    3. Crée un Blob (fichier binaire)
    4. Télécharge via un lien invisible
    */
    
    // Crée l'en-tête du CSV
    const rows = [['nom', 'ip', 'cpu', 'ram', 'disque', 'temp', 'etat']];
    
    // Ajoute chaque machine en tant que ligne
    for (const m of machines) {
        rows.push([m.nom, m.ip || '', m.cpu, m.ram, m.disque, m.temp, m.etat]);
    }
    
    // Convertit en texte CSV
    const csv = rows
        .map(r => r
            .map(c => '"' + String(c).replace(/"/g, '""') + '"')  // Échappe les guillemets
            .join(',')
        )
        .join('\n');  // Sépare les lignes par des retours à la ligne
    
    // Crée un Blob (fichier virtuel)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    
    // Crée une URL pour le Blob
    const url = URL.createObjectURL(blob);
    
    // Crée un lien invisible et clique dessus
    const a = document.createElement('a');
    a.href = url;
    a.download = 'machines.csv';  // Nom du fichier
    a.click();  // Simule un clic → téléchargement
    
    // Libère la mémoire
    URL.revokeObjectURL(url);
    
    /*
    RÉSULTAT: Un fichier 'machines.csv' est téléchargé
    L'utilisateur peut l'ouvrir dans Excel ou un éditeur texte
    */
}

// ─────────────────────────────────────────────────────────────────────────
// EXPORT PDF
// ─────────────────────────────────────────────────────────────────────────

function exportPDF() {
    /*
    📄 FONCTION: Génère et télécharge un PDF
    
    LIBRAIRIES:
    - jsPDF: Génère le PDF
    - jsPDF-AutoTable: Plugin pour créer un tableau
    
    CONTENU:
    - Titre: "Rapport - Supervision"
    - Tableau: Toutes les machines avec leurs données
    */
    
    // Récupère jsPDF depuis la fenêtre globale
    const { jsPDF } = window.jspdf;
    
    // Crée un nouveau document PDF
    const doc = new jsPDF();
    
    // En-tête du tableau
    const header = [['Nom', 'IP', 'CPU', 'RAM', 'Disque', 'Temp', 'État']];
    
    // Données du tableau (une machine par ligne)
    const body = machines.map(m => [
        m.nom,
        m.ip || '',
        m.cpu,
        m.ram,
        m.disque,
        m.temp,
        m.etat
    ]);
    
    // Ajoute un titre
    doc.text('Rapport - Supervision', 14, 16);
    
    // Ajoute un tableau (plugin autoTable)
    doc.autoTable({
        startY: 22,           // Position Y du tableau
        head: header,         // En-tête
        body: body            // Données
    });
    
    // Télécharge le PDF
    doc.save('rapport_supervision.pdf');
    
    /*
    RÉSULTAT: Un fichier PDF est téléchargé avec:
    - Titre en haut
    - Tableau avec toutes les machines
    - Colonnes: nom, IP, CPU, RAM, disque, température, état
    */
}

/*
═══════════════════════════════════════════════════════════════════════════════
RÉSUMÉ DE LA LOGIQUE
═══════════════════════════════════════════════════════════════════════════════

1️⃣  PAGE CHARGE:
   DOMContentLoaded → Attache événements + fetchData()

2️⃣  FETCH DATA (toutes les 5 secondes):
   fetch('/api/data') → Récupère machines → renderMachinesList() + renderOverviewCharts()

3️⃣  RENDU:
   - renderMachinesList(): Crée les cartes de chaque machine (rouge si anomalie)
   - renderOverviewCharts(): Crée les graphiques CPU et Temp

4️⃣  UTILISATEUR INTÉRAGIT:
   - Clique "Détails" → showDetails() → Modal avec historique
   - Clique "Exporter CSV" → exportCSV() → Télécharge machines.csv
   - Clique "Exporter PDF" → exportPDF() → Télécharge rapport.pdf
   - Clique "Se déconnecter" → fetch('/api/logout') → Retour à /

5️⃣  MISE À JOUR EN TEMPS RÉEL:
   Toutes les 5 secondes, fetchData() se réexécute
   → Données se mettent à jour
   → Cartes se mettent à jour
   → Graphiques se mettent à jour

═══════════════════════════════════════════════════════════════════════════════
*/
