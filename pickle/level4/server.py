#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import flask
import jinja2
import os

host, port, flag_length = 'localhost', 1337, len('pwn.college{practice}')
if os.geteuid() == 0:
    host, port, flag_length = 'bikini.bottom', 80, os.path.getsize('/flag') - 1

app = flask.Flask(__name__)

@app.route('/')
@app.route('/index.html')
def get_index():
    context = {'flag_length': flag_length, 'expression': flask.request.args.get('expression')}
    if context['expression']:
        if any(c not in ' ()*+-/0123456789' for c in context['expression']):
            flask.abort(400, 'Invalid expression')
        try:
            context['result'] = eval(context['expression'])
        except:
            flask.abort(500, 'Cannot evaluate expression')
    return flask.render_template('index.html.jinja', **context)

app.secret_key = os.urandom(8)
app.jinja_options['bytecode_cache'] = jinja2.FileSystemBytecodeCache('/tmp')
app.config['SERVER_NAME'] = f'{host}:{port}'
app.run(host, port)
