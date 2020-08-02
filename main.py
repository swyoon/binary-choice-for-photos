import os
import random
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev'
project = 'woong-bodyprofile'
project_dir = os.path.join('projects', project)
img_dir = os.path.join(project_dir, 'photos')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('main'))
    else:
        return render_template('index.html')

@app.route('/main')
def main():
    """main page"""
    return render_template('main.html', username=session['username'])


@app.route('/photo', methods=['GET', 'POST'])
def show_photo():
    '''
    c.execute("create table woong_bodyprofile (username text, winner text, loser text, time timestamp)")
    '''
    username = session['username']
    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("select count(*) from woong_bodyprofile where username=?",
                  [username])
        n_records = c.fetchall()[0][0]

        c.execute("select count(*) from woong_bodyprofile")
        n_total_records = c.fetchall()[0][0]

        c.execute("select username, count(*) from woong_bodyprofile group by username")
        rank_data = c.fetchall()

        total_people = len(rank_data)
        # set([username for name, cnt in rank_data])
        if n_records > 0:
            l = [name for name, tp in sorted(rank_data, key=lambda x: x[1], reverse=True)]
            rank = l.index(username)
            rank += 1  # start from 1
        else:
            rank = total_people + 1
            total_people += 1

    """return photo ids"""
    l_img_files = os.listdir(img_dir)
    total_num_img = len(l_img_files)
    img1 = random.choice(l_img_files)
    img2 = random.choice(l_img_files)
    img1 = 'static/' + img_dir + '/' + img1
    img2 = 'static/' + img_dir + '/' + img2
    print(img1, img2)

    return {'photo1': img1, 'photo2': img2, 'num_data': n_records, 'total_num_data': n_total_records,
            'total_num_img': total_num_img, 'rank': rank, 'total_people': total_people}


@app.route('/click', methods=['GET', 'POST'])
def click():
    """receive result"""
    data = request.get_json()
    username = session['username']
    winner = data['winner'].replace('\\', '/').split('/')[-1]
    loser = data['loser'].replace('\\', '/').split('/')[-1]

    with sqlite3.connect('data.db') as conn:
        c = conn.cursor()
        c.execute("insert into woong_bodyprofile values (?, ?, ?, ?)",
                  [username, winner, loser, datetime.now()])
        conn.commit()

    return ('', 204)
