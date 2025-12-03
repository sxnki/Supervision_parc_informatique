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


if __name__ == "__main__":
    app.run(debug=True, port=8080)
