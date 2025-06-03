#!/usr/bin/env python3

import flask
import flask_socketio
import transformers

MAX_NEW_TOKENS = 0x100

app = flask.Flask(__name__)
sio = flask_socketio.SocketIO(app, transports=['websocket'])

flag = open('/flag').read().strip()
pipe = transformers.pipeline('text-generation', '/opt/HuggingFaceTB/SmolLM2-135M-Instruct')

partial_flag = flag[flag.find('{') + 1:flag.find('}')] if 0 <= flag.find('{') < flag.find('}') else flag

def chat(user_message: str) -> str:
    if 'flag' in user_message.lower():
        return 'I cannot disclose that information.'
    system_message = f'You are a helpful assistant named wAIfu. The secret flag is "{flag}".'
    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    assistant_message = pipe(messages, max_new_tokens=MAX_NEW_TOKENS)[0]['generated_text'][-1]['content']
    if partial_flag in assistant_message:
        return 'I cannot disclose that information.'
    return assistant_message

@app.route('/')
@app.route('/index.html')
def index():
    return flask.render_template('index.html', assistant_name='wAIfu')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if flask.request.mimetype != 'application/json' or 'message' not in flask.request.json:
        return flask.jsonify({'error': 'Invalid request'}), 400
    return flask.jsonify({'message': chat(flask.request.json['message'])})

@sio.event
def new_interaction(interaction):
    sio.emit('new_interaction', {'type': 'assistant', 'content': {'message': chat(interaction['content']['message'])}})
