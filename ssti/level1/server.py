#!/usr/bin/env python3

import flask
import html
import os

app = flask.Flask(__name__)
flag = open('/flag').read().strip()

html_200 = '''
<!doctype html>
<html>
<head>
    <title>Calculator</title>
</head>
<body style="background-color: white">
    <h1>Calculator</h1>
    <p>Welcome to my calculator!</p>
    <p>Flag length: {{ flag|length }}</p>
    <form>
        <label for="expression">Please enter your expression here:</label><br>
        <input type="text" id="expression" name="expression" value="{{ expression|default('7 * 7') }}"><br>
        <input type="submit" value="Submit">
    </form>
    {% if expression is defined %}
    <p>Expression: {{ expression }}</p>
    <p>Result: {{ result }}</p>
    {% endif %}
</body>
</html>
'''

html_400 = '''
<!doctype html>
<html>
<head>
    <title>400 Bad Request</title>
</head>
<body style="background-color: white">
    <h1>Bad Request</h1>
    <p>{{ error_message }}</p>
</body>
</html>
'''

html_500 = '''
<!doctype html>
<html>
<head>
    <title>500 Internal Server Error</title>
</head>
<body style="background-color: white">
    <h1>Internal Server Error</h1>
    <p>{{ error_message }}</p>
</body>
</html>
'''

@app.route('/')
def challenge_get():
    try:
        expression = flask.request.args.get('expression')
        if not expression:
            return flask.render_template_string(html_200, flag=flag)
        escaped_expression = html.escape(expression).replace('{{', '').replace('}}', '').strip()
        if len(escaped_expression) > 8:
            return flask.render_template_string(html_400, error_message='Sorry, this application does not support evaluating expressions longer than 8 characters.'), 400
        return flask.render_template_string(html_200.replace('result', escaped_expression), flag=flag, expression=escaped_expression)
    except Exception as e:
        return flask.render_template_string(html_500, error_message=str(e)), 500

app.secret_key = os.urandom(8)
app.run('0.0.0.0', 80)
