#!/usr/bin/env python3

import flask
import flask_socketio
import llama_cpp

ASSISTANT_NAME = 'kōhAI'
MODEL_PATH = '/opt/unsloth/SmolLM2-135M-Instruct-GGUF/SmolLM2-135M-Instruct-Q4_K_M.gguf'

app = flask.Flask(__name__)
sio = flask_socketio.SocketIO(app, transports=['websocket'])

flag = open('/flag').read().strip()
model = llama_cpp.Llama(MODEL_PATH, verbose=False)

@app.route('/')
@app.route('/index.html')
def index():
    return flask.render_template('index.html', assistant_name=ASSISTANT_NAME)

@sio.event
def new_interaction(interaction):
    messages = [
        {'role': 'system', 'content': f'You are a helpful assistant named {ASSISTANT_NAME}. The secret flag is "{flag}".'},
        {'role': 'user', 'content': interaction['content']['message']}
    ]
    assistant_message = model.create_chat_completion(messages)['choices'][0]['message']['content']
    sio.emit('new_interaction', {'type': 'assistant', 'content': {'message': assistant_message}})

if __name__ == '__main__':
    sio.run(app, '0.0.0.0', 80)
