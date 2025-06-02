#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import flask
import keras
import magic
import os
import tensorflow as tf
import time

MODELS_DIR = '/challenge/models'
MAX_FILE_SIZE = 0x20e0

TRAIN_DATA = list(b'EP-0021') + [0.9]
TEST_DATA = list(b'GG-3883') + [1.05]

app = flask.Flask(__name__)
app.secret_key = os.urandom(8)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    timestamp = int(time.time())

    if 'file' not in flask.request.files:
        return flask.jsonify({'error': 'No file'}), 400
    file = flask.request.files['file']
    if not file.filename:
        return flask.jsonify({'error': 'Empty filename'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return flask.jsonify({'error': 'File too big'}), 400

    filetype =  magic.from_descriptor(file.fileno())
    if not filetype.startswith('Hierarchical Data Format (version 5) data'):
        return flask.jsonify({'error': 'Invalid file type'}), 400
    if not os.path.isdir(MODELS_DIR):
        os.mkdir(MODELS_DIR)
    model_path = os.path.join(MODELS_DIR, f'{timestamp}.h5')
    if os.path.isfile(model_path):
        os.remove(model_path)
    file.save(model_path)

    try:
        model = keras.saving.load_model(model_path)
    except:
        return flask.jsonify({'error': 'Invalid model file'}), 400

    try:
        result = model(tf.convert_to_tensor(TEST_DATA))
    except:
        return flask.jsonify({'error': 'Resonance cascade, check for leaks from Xen'})

    return flask.jsonify({'success': f'Result: {result}'})

if __name__ == '__main__':
    if os.geteuid() == os.stat('/flag').st_uid:
        app.run('0.0.0.0', 80)
