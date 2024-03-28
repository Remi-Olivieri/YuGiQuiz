from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import random
import threading
import time
import datetime

list_cards = os.listdir("static/Images/")
current_image = random.choice(list_cards)
next_image = random.choice(list_cards)
date_de_derniere_image = datetime.datetime.now()
pseudo = ""
suivant = False
moderator = None
connected_players = []
player_scores = {}
TIME = 5

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*")

app.secret_key = '123'
CORS(app)

@app.route('/')
def index():
    global pseudo
    pseudo = session.get('pseudo') 
    if pseudo:
        return render_template('index.html', pseudo=pseudo)
    else:
        return redirect(url_for('connexion'))

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    global moderator
    if request.method == 'POST':
        pseudo = request.form.get('pseudo')
        if pseudo:
            if moderator is None:
                moderator = "♛ " + pseudo
                session['pseudo'] = "♛ " + pseudo
            else:
                session['pseudo'] = pseudo
            return redirect(url_for('index'))
    return render_template('connexion.html')

@app.route('/get_card')
def get_card():
    return jsonify({'image_name': current_image, 'next_image_name': next_image})


@app.route('/show_answer', methods=['POST'])
def show_answer():
    data = request.json
    image_name = data['answer']
    user_answer = data['user_answer']
    return jsonify({'answer': image_name.split('.')[0], 'user_answer': user_answer})

@app.route('/check_session')
def check_session():
    username = session.get('pseudo')
    global pseudo
    is_moderator = (pseudo == moderator) if moderator else False
    if username:
        return jsonify({'pseudo': username, 'is_moderator': is_moderator}), 200
    else:
        return jsonify({'pseudo': None}), 401

@app.route('/suivant', methods=['POST'])
def set_suivant():
    global suivant
    suivant = True
    return "OK"

@socketio.on('updateScore')
def handle_update_score(data):
    global player_scores

    player_id = data['playerId']
    operation = data['operation']

    if operation == 'increase':
        player_scores[player_id] = player_scores.get(player_id, 0) + 1
    elif operation == 'decrease':
        player_scores[player_id] = max(0, player_scores.get(player_id, 0) - 1)
    emit('updateScores', {'scores': player_scores}, broadcast=True)
    
@socketio.on('checkScores')
def check_scores():
    emit('updateScores', {'scores': player_scores}, broadcast=True)
    
@socketio.on('userAnswer')
def handle_user_answer(user_answer):
    emit('showAnswer', user_answer, broadcast=True)

@app.route('/r_time')
def get_remaining_time():
    maintenant = datetime.datetime.now()
    return jsonify({'rtime': TIME - (maintenant - date_de_derniere_image).total_seconds()})

@socketio.on('suivant')
def emit_nouvelle_image():
    socketio.emit('nouvelle_image', {'OK': True})
    
@socketio.on('connect')
def handle_connect():
    username = session.get('pseudo')
    if username and username not in connected_players:
        connected_players.append(username)
    socketio.emit('updatePlayersList', {'players': connected_players})

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('pseudo')
    if username and username in connected_players:
        connected_players.remove(username)
    socketio.emit('updatePlayersList', {'players': connected_players})
    
@socketio.on('checkPlayers')
def check_players():
    socketio.emit('updatePlayersList', {'players': connected_players})

def tache_periodique():
    global current_image, next_image, date_de_derniere_image, suivant
    while True:
        maintenant = datetime.datetime.now()
        if (maintenant - date_de_derniere_image).total_seconds() >= TIME and suivant:
            current_image = next_image
            next_image = random.choice(list_cards)
            date_de_derniere_image = maintenant
            suivant = False
        time.sleep(0.1)

if __name__ == '__main__':
    thread = threading.Thread(target=tache_periodique)
    thread.daemon = True
    thread.start()
    socketio.run(app,host='0.0.0.0', port=5000, debug=True)