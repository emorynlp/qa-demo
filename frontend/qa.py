from flask import Flask, redirect, url_for, render_template, flash, request
import requests
import json


settings = json.load(open('config.json'))
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config.update(dict(
    SECRET_KEY=settings['frontend_key'],
))

backend_url = 'http://' + settings['backend_host'] + ':' + settings['backend_port']
backend_headers = {'content-type': 'application/json'}


@app.route('/')
def show_entries():
    return render_template('show_results.html')


@app.route('/show', methods=['POST'])
def show_results():
    payload = {
        'method': 'query',
        'params': [request.form['question']],
        'jsonrpc': '2.0',
        'id': 0,
    }

    response = requests.post(backend_url, data=json.dumps(payload), headers=backend_headers).json()

    # flash(response['result'])

    for i in response['result']:
        flash(i['text'])

    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(settings['frontend_host'], settings['frontend_port'])
