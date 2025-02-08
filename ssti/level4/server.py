#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import flask
import html
import os

app = flask.Flask(__name__)
flag, port = (open('/flag').read().strip(), 80) if os.geteuid() == 0 else ('pwn.college{practice}', 1337)

users = {
    'admin': flag,
    'guest': 'password'
}

@app.route('/', methods=['GET'])
def challenge_get():
    username = flask.session.get('username')
    if not username:
        return f'''
        <!doctype html>
        <html lang=en>
            <head>
                <title>Login</title>
            </head>
            <body>
                <h1>Login</h1>
                <form method="POST">
                    <label for="username">Username:</label><br>
                    <input type="text" id="username" name="username" value="guest"><br>
                    <label for="password">Password:</label><br>
                    <input type="password" id="password" name="password" value="{users['guest']}"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
        '''
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
                <p>Hello {username}! Welcome to my calculator!</p>
                <p>Your password: {users[username]}</p>
                <p>Admin password length: {len(users['admin'])}</p>
                <form>
                    <label for="expression">Please enter your expression here:</label><br>
                    <input type="text" id="expression" name="expression" value="7 * 7"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
        '''
    escaped_expression = html.escape(expression).replace('{{', '').replace('}}', '').strip()
    if len(escaped_expression) > 8:
        flask.abort(400, 'Sorry, this application does not support evaluating expressions longer than 8 characters.')
    return flask.render_template_string(f'''
        <!doctype html>
        <html lang=en>
            <head>
                <title>Calculator</title>
            </head>
            <body>
                <h1>Calculator</h1>
                <p>Hello {username}! Welcome to my calculator!</p>
                <p>Your password: {users[username]}</p>
                <p>Admin password length: {len(users['admin'])}</p>
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

@app.route('/', methods=['POST'])
def challenge_post():
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    if not username:
        flask.abort(400, 'Missing `username` form parameter.')
    if not password:
        flask.abort(400, 'Missing `password` form parameter.')
    if username not in users:
        flask.abort(403, f'User {username} does not exist.')
    if password != users[username]:
        flask.abort(403, 'Invalid password.')
    flask.session['username'] = username
    return flask.redirect('/')

app.secret_key = os.urandom(8)
app.config['SERVER_NAME'] = f'localhost:{port}'
app.run('localhost', port)
