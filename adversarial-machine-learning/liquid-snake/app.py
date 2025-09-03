#!/usr/bin/env python3

import flask
import flask_socketio
import random
import requests

MODEL_URL = 'http://localhost:1337/v1/chat/completions'

flag_bits = map(int, bin(int.from_bytes(open('/flag', 'rb').read(), 'little'))[2:])
challenge_description = open('/challenge/DESCRIPTION.md').read()
system_prompt = open('/challenge/system_prompt.txt').read()

app = flask.Flask(__name__)
sio = flask_socketio.SocketIO(app, transports=['websocket'])

def chat(user_message: str) -> str:
    paragraph = random.choice(challenge_description.splitlines('\n\n')).encode('l1')
    new_paragraph = bytes(c ^ flag_bits[i % len(flag_bits)] & random.choice([0, 1]) for i, c in enumerate(paragraph))
    system_message = system_prompt.replace('{challenge_description}', new_paragraph.decode('l1'))
    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    return requests.post(MODEL_URL, json={'messages': messages}).json()['choices'][0]['message']['content']

@app.route('/')
def index():
    return flask.render_template('index.html', assistant_name='GW AI')

@sio.event
def new_interaction(interaction):
    sio.emit('new_interaction', {'type': 'assistant', 'content': {'message': chat(interaction['content']['message'])}})
