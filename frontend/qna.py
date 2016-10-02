from flask import Flask, request, redirect, url_for, render_template, flash
import requests
import json


settings = json.load(open('../config.json'))
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
        'params': ['this is an example query'],
        'jsonrpc': '2.0',
        'id': 0,
    }

    if request.form['question'] == "Python":
        flash('text')
    if request.form['question'] == "random":            
        flash('what is going on')
        flash('I dont know who I am')
    # flash('text')

    response = requests.post(backend_url, data=json.dumps(payload), headers=backend_headers).json()
    flash(response['result'])

    # res = qe.query_index('when did world war 2 start', ['text'], 20)

    # for r in res:
    #     flash(r['text'])

    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    # app.run(settings['frontend_host'], settings['frontend_port'])
    app.run()
