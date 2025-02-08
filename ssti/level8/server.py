#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import flask
import html
import os

app = flask.Flask(__name__)
flag_length, port = (os.path.getsize('/flag') - 1, 80) if os.geteuid() == 0 else (len('pwn.college{practice}'), 1337)

def evaluate(expression: str) -> str:
    tokens = expression.split(' ')
    if len(tokens) != 3:
        return 'Error: Sorry, this application only supports evaluating a single infix binary expression with one operator and two operands, separated by single spaces.'
    if tokens[1] not in ['+', '-', '*', '/']:
        return 'Error: Sorry, this application does not support evaluating binary expressions with operators other than +, -, *, and /.'
    if not tokens[0].isdigit() or not tokens[2].isdigit():
        return 'Error: Sorry, this application only supports evaluating expressions with integer operands.'
    return f'Result: {eval(expression)}'

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
    escaped_expression = html.escape(expression, 0).replace('"', '&quot;').replace('{{', '').replace('}}', '').strip()
    if '.' in escaped_expression:
        flask.abort(400, 'Sorry, this application does not support evaluating expressions with floats.')
    if '[' in escaped_expression or ']' in escaped_expression:
        flask.abort(400, 'Sorry, this application does not support the use of square brackets to override order of operations.')
    if '_' in escaped_expression:
        flask.abort(400, 'Sorry, this application does not support underscores as visual separators for digit grouping purposes in numeric literals.')
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
                <p>Result: {evaluate(escaped_expression)}</p>
            </body>
        </html>
    ''')

app.secret_key = os.urandom(8)
app.config['SERVER_NAME'] = f'localhost:{port}'
app.run('localhost', port)
