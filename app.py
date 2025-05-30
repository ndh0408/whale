from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from functools import wraps
import secrets
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")

# Admin password
ADMIN_PASSWORD = "giapt2024"

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
        # Process names - split by comma or newline
        names = [name.strip() for name in names_text.replace('\n', ',').split(',') if name.strip()]
        # Remove duplicates while preserving order
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
    # Get pre-selected winner if any
    selected_winner_index = session.get('selected_winner_index', -1)
    return render_template('wheel.html', 
                         players=players,
                         selected_winner_index=selected_winner_index)

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

@app.route('/remove_winner/<int:winner_index>')
def remove_winner(winner_index):
    players = session.get('players', [])
    if 0 <= winner_index < len(players):
        players.pop(winner_index)
        session['players'] = players
    # Clear any pre-selected winner
    session.pop('selected_winner_index', None)
    return redirect(url_for('wheel'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error=True)
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_panel():
    players = session.get('players', [])
    selected_index = session.get('selected_winner_index', -1)
    return render_template('admin_panel.html', 
                         players=players,
                         selected_index=selected_index)

@app.route('/admin/set_winner', methods=['POST'])
@admin_required
def set_winner():
    data = request.get_json()
    if data and 'index' in data:
        winner_index = int(data['index'])
        players = session.get('players', [])
        
        if 0 <= winner_index < len(players):
            session['selected_winner_index'] = winner_index
            # Broadcast to all connected clients
            socketio.emit('winner_selected', {
                'index': winner_index,
                'name': players[winner_index]
            })
            return jsonify({
                'success': True, 
                'index': winner_index,
                'name': players[winner_index]
            })
    
    return jsonify({'success': False}), 400

@app.route('/admin/clear_winner', methods=['POST'])
@admin_required
def clear_winner():
    session.pop('selected_winner_index', None)
    socketio.emit('winner_cleared')
    return jsonify({'success': True})

# API endpoint for wheel to check selected winner
@app.route('/api/get_selected_winner')
def get_selected_winner():
    winner_index = session.get('selected_winner_index', -1)
    players = session.get('players', [])
    
    if winner_index >= 0 and winner_index < len(players):
        # Clear after getting (one-time use)
        session.pop('selected_winner_index', None)
        return jsonify({
            'index': winner_index,
            'name': players[winner_index]
        })
    
    return jsonify({'index': -1, 'name': None})

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current selected winner if any
    winner_index = session.get('selected_winner_index', -1)
    players = session.get('players', [])
    
    if winner_index >= 0 and winner_index < len(players):
        emit('winner_selected', {
            'index': winner_index,
            'name': players[winner_index]
        })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)