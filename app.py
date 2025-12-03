from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from machines import get_machines
from server.utils.anomaly_detector import check_anomalies


app = Flask(__name__)
app.secret_key = "change_this_secret_for_prod"


# Login via AJAX
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if username == 'admin' and password == 'louvre':
        session['user'] = username
        return jsonify({'success': True, 'message': 'Connecté avec succès', 'redirect': '/dashboard'})

    return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401


# Logout via AJAX
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Déconnecté'})


# Page Login
@app.route('/')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# Page Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# API data
@app.route('/api/data')
def api_data():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    # recuperrer les machines
    data = get_machines()

    # Annoter chaque machine avec les anomalies détectées côté serveur
    annotated = []
    for m in data:
        try:
            anomalies = check_anomalies(m)
        except Exception:
            anomalies = {}
        m['anomalies'] = anomalies
        m['anomalie'] = bool(anomalies)
        annotated.append(m)

    return jsonify(annotated)


# Vérifier authentification
@app.route('/api/auth-status')
def auth_status():
    return jsonify({'authenticated': 'user' in session})


# Déconnexion
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

<<<<<<< HEAD

if __name__ == "__main__":
=======
    # Ajouter date_heure formatée
    


@app.get("/export/pdf")
def export_pdf():
    DATA_FILE = os.path.join(os.path.dirname(__file__), "server","data.json")

    # Lire les données
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            machines = json.load(f)
    else:
        machines = []

    # Ajouter anomalie et date_heure  date et herus affiche pas bien
    for m in machines:
        m["anomalie"] = bool(check_anomalies(m))
        ts = m.get("timestamp", None)
        if ts:
            m["date_heure"] = datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")
        else:
            m["date_heure"] = "N/A"


    # Créer le PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Rapport Supervision", ln=True, align="C")
    pdf.ln(5)

    headers = ["Date/Heure", "Hostname", "CPU", "RAM", "Disk", "Anomalie"]
    pdf.set_font("Arial", "B", 10)
    for h in headers:
        pdf.cell(38, 7, h, 1, 0, "C")
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for m in machines:
        pdf.cell(38, 7, m.get("date_heure", ""), 1)
        pdf.cell(38, 7, str(m.get("nom", "")), 1)
        pdf.cell(38, 7, str(m.get("cpu", "")), 1)
        pdf.cell(38, 7, str(m.get("ram", "")), 1)
        pdf.cell(38, 7, str(m.get("disque", "")), 1)
        pdf.cell(38, 7, str(m.get("anomalie", "")), 1)
        pdf.ln()

    # ⚡ Ici le truc correct pour BytesIO
    pdf_output = pdf.output(dest='S').encode('latin1')  # retourne le PDF en bytes
    pdf_bytes = BytesIO(pdf_output)

    return send_file(
        pdf_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="machines.pdf"
    )
    #créer le fichier csv !!

if __name__=="__main__":
>>>>>>> 8b72958b6b92130ed761df86b61c18fcd4872060
    app.run(debug=True, port=8080)
