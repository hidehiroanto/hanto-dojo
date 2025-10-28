#!/usr/bin/env python3

import flask
import html
import os

app = flask.Flask(__name__)
flag = open('/flag').read().strip()

html_template = '''
<!doctype html>
<html lang=en>
    <head>
        <title>Calculator</title>
        <style>
            body {{
                background-color: white;
            }}
        </style>
    </head>
    <body>
        <h1>Calculator</h1>
        <p>Welcome to my calculator!</p>
        <p>Flag length: {{{{ flag|length }}}}</p>
        <form>
            <label for="expression">Please enter your expression here:</label><br>
            <input type="text" id="expression" name="expression" value="{{{{ expression|default('7 * 7') }}}}"><br>
            <input type="submit" value="Submit">
        </form>
        {{% if expression is defined %}}
        <p>Expression: {{{{ expression }}}}</p>
        <p>Result: {{{{ {expression} }}}}</p>
        {{% endif %}}
    </body>
</html>
'''

@app.route('/')
def challenge_get():
    expression = flask.request.args.get('expression')
    if not expression:
        return flask.render_template_string(html_template.format(expression=''), flag=flag)
    escaped_expression = html.escape(expression).replace('{{', '').replace('}}', '').strip()
    if len(escaped_expression) > 8:
        flask.abort(400, 'Sorry, this application does not support evaluating expressions longer than 8 characters.')
    return flask.render_template_string(html_template.format(expression=escaped_expression), flag=flag, expression=escaped_expression)

app.secret_key = os.urandom(8)
app.run('0.0.0.0', 80)
