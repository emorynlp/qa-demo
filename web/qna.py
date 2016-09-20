import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config.update(dict(
    #DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    #USERNAME='admin',
    #PASSWORD='default'
))

fin  = open('sample.txt')
l = []
for line in fin:
    l.append(line)

print l

@app.route('/')
def show_entries():
    #flash('what are you looking for')
    return render_template('show_results.html')

@app.route('/show', methods=['POST'])
def show_results():
    
    if request.form['question'] == "Python":
        flash(l)
    if request.form['question'] == "random":
            
        flash('what is going on')
        flash('I dont know who I am')
    flash("hello, how are you")
    #return render_template('show_entries.html', entries=entries)
    return redirect(url_for('show_entries'))