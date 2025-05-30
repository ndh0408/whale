from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from functools import wraps
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")

# Admin password - CHANGE THIS!
ADMIN_PASSWORD = "giapt2024"  # Đổi password này

# Store for selected winner - using session instead
# selected_winner = None

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        names_text = request.form.get('names', '')
        names = [name.strip() for name in names_text.replace('\n', ',').split(',') if name.strip()]
        seen = set()
        unique_names = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
        session['players'] = unique_names
        return redirect(url_for('players'))
    
    players = session.get('players', [])
    return render_template('players.html', players=players)

@app.route('/wheel')
def wheel():
    players = session.get('players', [])
    return render_template('wheel.html', players=players)

@app.route('/reset')
def reset():
    session.pop('players', None)
    session.pop('selected_winner', None)  # Clear selected winner
    return redirect(url_for('index'))

@app.route('/remove_winner/<winner>')
def remove_winner(winner):
    players = session.get('players', [])
    if winner in players:
        players.remove(winner)
        session['players'] = players
    return redirect(url_for('wheel'))

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_wheel'))
        else:
            return render_template('admin_login.html', error=True)
    return render_template('admin_login.html')

# Admin logout route
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# Admin panel - now protected
@app.route('/admin')
@admin_required
def admin_wheel():
    players = session.get('players', [])
    return render_template('admin_wheel.html', players=players)

@app.route('/set_winner', methods=['POST'])
@admin_required
def set_winner():
    data = request.get_json()
    if data and 'winner' in data:
        winner = data['winner']
        # Store in session instead of global variable
        session['selected_winner'] = winner
        print(f"Admin selected winner: {winner}")
        
        # Emit to all connected clients
        socketio.emit('winner_selected', {'winner': winner})
        
        return jsonify({'success': True, 'winner': winner})
    return jsonify({'success': False}), 400

@app.route('/get_selected_winner')
def get_selected_winner():
    # Get and clear selected winner from session
    winner = session.pop('selected_winner', None)
    print(f"Getting selected winner: {winner}")
    return jsonify({'winner': winner})

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current selected winner if any
    winner = session.get('selected_winner')
    if winner:
        emit('winner_selected', {'winner': winner})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)