from flask import Flask, redirect, url_for, render_template, flash, request, send_from_directory, Markup
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


@app.route('/images/<path:path>')
def send_image(path):
    return send_from_directory('images', path)


@app.route('/')
def show_entries():
    return render_template('show_results.html')


@app.route('/show', methods=['POST'])
def show_results():
    payload = {
        'method': 'query',
        'params': [request.form['question'], 10],
        'jsonrpc': '2.0',
        'id': 0,
    }

    window_size = int(request.form['window_size'])
    response = requests.post(backend_url, data=json.dumps(payload), headers=backend_headers).json()
    # print response

    # response['result'][4][1]['is_answer'] = 1

    for paragraph in response['result']:
        answer_indices = [i for i, x in enumerate(paragraph) if x['is_answer'] == 1]

        for ai in answer_indices:
            paragraph[ai]['sentence'] = '<answer>' + paragraph[ai]['sentence'] + '</answer>'

        if window_size and answer_indices:
            for ai in answer_indices:
                for i in xrange(window_size):
                    neg_i = max(ai - i - 1, 0)
                    pos_i = min(ai + i + 1, len(paragraph) - 1)

                    if paragraph[neg_i]['is_answer'] == 0:
                        paragraph[neg_i]['sentence'] = '<window>' + paragraph[neg_i]['sentence'] + '</window>'
                    if paragraph[pos_i]['is_answer'] == 0:
                        paragraph[pos_i]['sentence'] = '<window>' + paragraph[pos_i]['sentence'] + '</window>'

        paragraph_text = ' '.join(i['sentence'] for i in paragraph)

        # for sentence in paragraph:
        #     if sentence['is_answer'] == 0:
        #         paragraph_text += sentence['sentence'] + ' '
        #     else:
        #         paragraph_text += '<window>' + sentence['sentence'] + '</window> '
        flash(Markup(paragraph_text))

    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(settings['frontend_host'], settings['frontend_port'])
