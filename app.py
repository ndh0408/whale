from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.secret_key = 'gia_nguyen_apt_secret_key'  # Change this in production
socketio = SocketIO(app, cors_allowed_origins="*")

# Store for selected winner
selected_winner = None

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == 'POST':
        names_text = request.form.get('names', '')
        # Split names by comma or newline and clean up
        names = [name.strip() for name in names_text.replace('\n', ',').split(',') if name.strip()]
        session['players'] = names
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
    return redirect(url_for('index'))

@app.route('/remove_winner/<winner>')
def remove_winner(winner):
    players = session.get('players', [])
    if winner in players:
        players.remove(winner)
        session['players'] = players
    return redirect(url_for('wheel'))

@app.route('/admin_wheel')
def admin_wheel():
    players = session.get('players', [])
    return render_template('admin_wheel.html', players=players)

@app.route('/set_winner', methods=['POST'])
def set_winner():
    global selected_winner
    data = request.get_json()
    if data and 'winner' in data:
        selected_winner = data['winner']
        # Emit the winner to all connected clients
        socketio.emit('winner_selected', {'winner': selected_winner})
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/get_selected_winner')
def get_selected_winner():
    global selected_winner
    winner = selected_winner
    selected_winner = None  # Clear after getting
    return jsonify({'winner': winner})

if __name__ == '__main__':
    socketio.run(app, debug=True) 