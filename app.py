from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'gia_nguyen_apt_secret_key'  # Change this in production

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

if __name__ == '__main__':
    app.run(debug=True) 