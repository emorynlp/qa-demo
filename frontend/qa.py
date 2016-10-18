from flask import Flask, render_template, request, send_from_directory, Markup, make_response
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


def process_query(question, window_size, page=1):
    payload = {
        'method': 'query',
        'params': [question, 10, page-1],
        'jsonrpc': '2.0',
        'id': 0,
    }

    response = requests.post(backend_url, data=json.dumps(payload), headers=backend_headers).json()

    paragraphs = []

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
        paragraphs.append(Markup(paragraph_text))

    return paragraphs


@app.route('/results', methods=['POST'])
def show_results():
    paragraphs = process_query(request.form['question'], int(request.form['window_size']), 1)

    response = make_response(render_template('show_results.html', paragraphs=paragraphs, page_active=1,
                                             question_string=request.form['question'],
                                             window_selected=int(request.form['window_size'])))
    response.set_cookie('question', value=request.form['question'])
    response.set_cookie('window_size', value=request.form['window_size'])
    return response


@app.route('/results/<int:page>', methods=['GET'])
def show_results_page(page):
    question = request.cookies.get('question')
    window_size = request.cookies.get('window_size')

    paragraphs = process_query(question, int(window_size), page)
    response = make_response(render_template('show_results.html', paragraphs=paragraphs, page_active=page,
                                             question_string=question,
                                             window_selected=int(window_size)))
    return response


if __name__ == '__main__':
    app.run(settings['frontend_host'], settings['frontend_port'])
