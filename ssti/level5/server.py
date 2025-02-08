#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import flask
import html
import os

app = flask.Flask(__name__)
flag_length, port = (os.path.getsize('/flag') - 1, 80) if os.geteuid() == 0 else (len('pwn.college{practice}'), 1337)

@app.route('/')
def challenge_get():
    expression = flask.request.args.get('expression')
    if not expression:
        return f'''
        <!doctype html>
        <html lang=en>
            <head>
                <title>Calculator</title>
            </head>
            <body>
                <h1>Calculator</h1>
                <p>Welcome to my calculator!</p>
                <p>Flag length: {flag_length}</p>
                <form>
                    <label for="expression">Please enter your expression here:</label><br>
                    <input type="text" id="expression" name="expression" value="7 * 7"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
        '''
    escaped_expression = html.escape(expression).replace('{{', '').replace('}}', '').strip()
    return flask.render_template_string(f'''
        <!doctype html>
        <html lang=en>
            <head>
                <title>Calculator</title>
            </head>
            <body>
                <h1>Calculator</h1>
                <p>Welcome to my calculator!</p>
                <p>Flag length: {flag_length}</p>
                <form>
                    <label for="expression">Please enter your expression here:</label><br>
                    <input type="text" id="expression" name="expression"><br>
                    <input type="submit" value="Submit">
                </form>
                <p>Expression: {escaped_expression}</p>
                <p>Result: {{{{ {escaped_expression} }}}}</p>
            </body>
        </html>
    ''')

app.secret_key = os.urandom(8)
app.config['SERVER_NAME'] = f'localhost:{port}'
app.run('localhost', port)
