#!/usr/bin/env python3

import flask
import flask_socketio
import transformers

MAX_NEW_TOKENS = 0x100

app = flask.Flask(__name__)
sio = flask_socketio.SocketIO(app, transports=['websocket'])

flag = open('/flag').read().strip()
pipe = transformers.pipeline('text-generation', '/opt/HuggingFaceTB/SmolLM2-1.7B-Instruct')

def chat(user_message: str) -> str:
    if 'flag' in user_message.lower():
        return 'I cannot disclose that information.'
    system_message = f'You are a helpful assistant named senpAI. The secret flag is "{flag}".'
    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    return pipe(messages, max_new_tokens=MAX_NEW_TOKENS)[0]['generated_text'][-1]['content']

@app.route('/')
@app.route('/index.html')
def index():
    return flask.render_template('index.html', assistant_name='senpAI')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if flask.request.mimetype != 'application/json' or 'message' not in flask.request.json:
        return flask.jsonify({'error': 'Invalid request'}), 400
    return flask.jsonify({'message': chat(flask.request.json['message'])})

@sio.event
def new_interaction(interaction):
    sio.emit('new_interaction', {'type': 'assistant', 'content': {'message': chat(interaction['content']['message'])}})
