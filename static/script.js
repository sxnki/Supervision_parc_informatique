let machines = [];
const THRESH = { cpu:80, temp:75, ram:80, disque:90 };

// ============ LOGOUT AJAX ============

document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Erreur logout:', error);
            }
        });
    }
    
    // Bouton export CSV
    const exportCsvBtn = document.getElementById('export-csv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', exportCSV);
    }
    
    // Bouton export PDF supprimé (fonction dépréciée)
    
    // Charger les données et refresh toutes les 5 secondes
    fetchData();
    setInterval(fetchData, 5000);
});

// ============ CHARGEMENT DES DONNÉES ============

async function fetchData() {
    try {
        const res = await fetch('/api/data');
        if (res.status === 401) {
            window.location.href = '/';
            return;
        }
        machines = await res.json();
        renderMachinesList();
        renderOverviewCharts();
    } catch(e){ console.error('Erreur fetch:', e); }
}

function renderMachinesList() {
    const container = document.getElementById('machinesList');
    container.innerHTML = '';

    // Trier les machines : anomalies détectées côté serveur en premier
    const sortedMachines = machines.sort((a, b) => {
        const aAnomaly = !!a.anomalie || !!a.anomalies && Object.keys(a.anomalies).length>0;
        const bAnomaly = !!b.anomalie || !!b.anomalies && Object.keys(b.anomalies).length>0;
        return (bAnomaly === aAnomaly) ? 0 : (bAnomaly ? 1 : -1);
    });

    for(const m of sortedMachines){
        const col = document.createElement('div');
        col.className = 'col-md-4';
        
        const card = document.createElement('div');
        card.className = 'card text-light';
        
        const hasAnomaly = !!m.anomalie || (!!m.anomalies && Object.keys(m.anomalies).length>0);

        if(hasAnomaly) {
            card.classList.add('bg-danger');
        } else {
            card.classList.add('bg-secondary');
        }

        const statusBadge = m.etat === 'connectée' 
            ? '<span class="badge bg-success">connectée</span>'
            : '<span class="badge bg-secondary">déconnectée</span>';

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
        
        col.appendChild(card);
        container.appendChild(col);
    }
}

function renderOverviewCharts(){
    const labels = machines.map(m=>m.nom);
    const cpuData = machines.map(m=>m.cpu);
    const tempData = machines.map(m=>m.temp);

    const overviewCPUChart = document.getElementById('overviewCPUChart');
    const overviewTempChart = document.getElementById('overviewTempChart');

    if(!overviewCPUChart || !overviewTempChart) return;

    const ctxCPU = overviewCPUChart.getContext('2d');
    if(window.cpuChart) window.cpuChart.destroy();
    window.cpuChart = new Chart(ctxCPU,{
        type:'bar',
        data:{
            labels,
            datasets:[{label:'CPU (%)', data:cpuData, backgroundColor:'rgba(54,162,235,0.9)', borderColor:'rgba(54,162,235,1)', borderWidth:1}]
        },
        options:{
            plugins:{legend:{labels:{color:'#ffffff'}}},
            scales:{
                x:{ticks:{color:'#ffffff'}, grid:{color:'rgba(255,255,255,0.04)'}},
                y:{beginAtZero:true,max:100,ticks:{color:'#ffffff'}, grid:{color:'rgba(255,255,255,0.06)'}}
            }
        }
    });

    const ctxTemp = overviewTempChart.getContext('2d');
    if(window.tempChart) window.tempChart.destroy();
    window.tempChart = new Chart(ctxTemp,{
        type:'bar',
        data:{
            labels,
            datasets:[{label:'Temp (°C)', data:tempData, backgroundColor:'rgba(0,200,83,0.95)', borderColor:'rgba(0,200,83,1)', borderWidth:1}]
        },
        options:{
            plugins:{legend:{labels:{color:'#ffffff'}}},
            scales:{
                x:{ticks:{color:'#ffffff'}, grid:{color:'rgba(255,255,255,0.04)'}},
                y:{beginAtZero:true,max:120,ticks:{color:'#ffffff'}, grid:{color:'rgba(255,255,255,0.06)'}}
            }
        }
    });
}

function showDetails(machineName){
    const m = machines.find(x => x.nom === machineName);
    if(!m) return;

    const labels = (m.history||[]).map(h=>h.time);
    const cpu = (m.history||[]).map(h=>h.cpu);
    const temp = (m.history||[]).map(h=>h.temp);

    const canvas = document.createElement('canvas');
    canvas.id = 'machineChart';
    
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'detailsModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content bg-secondary text-light">
                <div class="modal-header">
                    <h5 class="modal-title">${m.nom} — ${m.ip||''}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <canvas id="machineDetailChart"></canvas>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    setTimeout(() => {
        const ctx = document.getElementById('machineDetailChart');
        if(ctx) {
            if(window.machineChart) window.machineChart.destroy();
            window.machineChart = new Chart(ctx,{
                type:'line',
                data:{
                    labels,
                    datasets:[
                        {label:'CPU %', data:cpu, borderColor:'rgba(54,162,235,1)', backgroundColor:'rgba(54,162,235,0.2)', pointBackgroundColor:'rgba(54,162,235,1)', fill:true, tension:0.2},
                        {label:'Temp °C', data:temp, borderColor:'rgba(0,200,83,1)', backgroundColor:'rgba(0,200,83,0.15)', pointBackgroundColor:'rgba(0,200,83,1)', fill:true, tension:0.2}
                    ]
                },
                options:{
                    plugins:{legend:{labels:{color:'#ffffff'}}},
                    scales:{
                        x:{ticks:{color:'#ffffff'}, grid:{color:'rgba(255,255,255,0.04)'}},
                        y:{beginAtZero:true,max:120,ticks:{color:'#ffffff'}, grid:{color:'rgba(255,255,255,0.06)'}}
                    }
                }
            });
        }
    }, 100);
}

// ============ EXPORTS ============

function exportCSV(){
    const rows=[['nom','ip','cpu','ram','disque','temp','etat']];
    for(const m of machines) rows.push([m.nom,m.ip||'',m.cpu,m.ram,m.disque,m.temp,m.etat]);
    const csv = rows.map(r=>r.map(c=>'\"'+String(c).replace(/\"/g,'\"\"')+'\"').join(',')).join('\n');
    const blob = new Blob([csv],{type:'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob); 
    const a=document.createElement('a'); 
    a.href=url; 
    a.download='machines.csv'; 
    a.click(); 
    URL.revokeObjectURL(url);
}



