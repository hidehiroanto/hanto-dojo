#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import flask
import jinja2
import os
import psutil

host, port = ('myoboku.zan', 80) if os.geteuid() == 0 else ('localhost', 1337)

def peer_process_of(fd: int) -> psutil.Process:
    server_conn = next(conn for conn in psutil.Process().net_connections() if conn.fd == fd)
    client_conn = next(conn for conn in psutil.net_connections() if conn.raddr == server_conn.laddr and conn.laddr == server_conn.raddr)
    return psutil.Process(client_conn.pid)

app = flask.Flask(__name__)

@app.route('/')
@app.route('/index.html')
def welcome_home():
    return flask.render_template('index.html.jinja')

@app.route('/.sage/paths/<path:path>')
def get_path(path):
    if peer_process_of(flask.request.input_stream.fileno()).uids().effective != 0:
        flask.abort(400, 'Only members of Root (根) are allowed to access the hidden paths of Mount Myōboku.')
    if 'sage' not in flask.request.headers.get('User-Agent'):
        flask.abort(403, 'You have not yet mastered Sage Mode.')
    return flask.send_from_directory(os.path.join('.sage', 'paths'), path)

app.secret_key = os.urandom(8)
app.jinja_options['bytecode_cache'] = jinja2.FileSystemBytecodeCache(os.path.join(app.root_path, '.sage', 'cache'))
app.config['SERVER_NAME'] = f'{host}:{port}'
app.run(host, port)
