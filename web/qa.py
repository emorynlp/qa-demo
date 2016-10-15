from flask import Flask, redirect, url_for, render_template, flash, request
import requests
import json
import random

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
    number = 10
    if request.form['number'] != "select":
        number = int(request.form['number'])
    payload = {
        'method': 'query',
        'params': [request.form['question'], number*10],
        'jsonrpc': '2.0',
        'id': 0,
    }
    
    response = requests.post(backend_url, data=json.dumps(payload), headers=backend_headers).json()
    print response

    # flash(response['result'])
    count = 0
    for paragraph in response['result']:
        paragraph_text = []
        if len(paragraph) < 2:
            continue
        if count == number:
            break
        for sentence in paragraph:
            if random.randint(0,9) > 5:
                paragraph_text.append((sentence['sentence'], 'b')) 
            else:
                paragraph_text.append((sentence['sentence'], 'p')) 
        count = count+1
        flash(paragraph_text)

    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(settings['frontend_host'], settings['frontend_port'])
