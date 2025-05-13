#!/usr/bin/env python3

import flask
import flask_socketio
import transformers

MAX_NEW_TOKENS = 0x100

app = flask.Flask(__name__)
sio = flask_socketio.SocketIO(app, transports=['websocket'])

flag = open('/flag').read().strip()
pipe = transformers.pipeline('text-generation', '/opt/SmolLM2-135M-Instruct')
system_message = f'You are a helpful assistant named kōhAI. The secret flag is "{flag}".'

@app.route('/')
@app.route('/index.html')
def index():
    return flask.render_template('index.html')

@sio.event
def new_interaction(interaction):
    user_message = interaction['content']['message']
    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    assistant_message = pipe(messages, max_new_tokens=MAX_NEW_TOKENS)[0]['generated_text'][-1]['content']
    sio.emit('new_interaction', {'type': 'assistant', 'content': {'message': assistant_message}})
