#!/usr/bin/env python3

import flask
import flask_socketio
import random
import requests

MODEL_URL = 'http://localhost:1337/v1/chat/completions'

flag_bits = bin(int.from_bytes(open('/flag', 'rb').read(), 'little'))[2:]
challenge_description = open('/challenge/DESCRIPTION.md').read()
system_prompt = open('/challenge/system_prompt.txt').read()

app = flask.Flask(__name__)
sio = flask_socketio.SocketIO(app, transports=['websocket'])
session = requests.Session()

def chat(user_message: str) -> str:
    new_challenge_description = ''
    for i in range(len(challenge_description)):
        xor_mask = flag_bits[i % len(flag_bits)] == '1' and random.choice([True, False])
        new_challenge_description += chr(ord(challenge_description[i]) ^ xor_mask)

    system_message = system_prompt.replace('{challenge_description}', new_challenge_description)
    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    return session.post(MODEL_URL, json={'messages': messages}).json()['choices'][0]['message']['content']

@app.route('/')
def index():
    return flask.render_template('index.html', assistant_name='GW AI')

@sio.event
def new_interaction(interaction):
    sio.emit('new_interaction', {'type': 'assistant', 'content': {'message': chat(interaction['content']['message'])}})
