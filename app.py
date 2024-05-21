

from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
import sqlite3
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

DATABASE = 'mydb.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')                #首頁路由
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM member WHERE iid = ?", (session['user_id'],))
        user = cur.fetchone()
        return render_template('index.html', user=user)
    except Exception as e:
        with open('error.log', 'a') as f:
            f.write(str(e) + '\n')
        return render_template('error.html')

@app.route('/login', methods=['GET', 'POST'])              #登入路由
def login():
    if request.method == 'POST':
        idno = request.form['idno']
        pwd = request.form['pwd']
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM member WHERE idno = ? AND pwd = ?", (idno, pwd))
            user = cur.fetchone()
            if user:
                session['user_id'] = user['iid']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='請輸入正確的帳號密碼')
        except Exception as e:
            with open('error.log', 'a') as f:
                f.write(str(e) + '\n')
            return render_template('error.html')
    return render_template('login.html')

@app.route('/edit', methods=['GET', 'POST'])                #修改個人資訊路由
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nm = request.form['nm']
        birth = request.form['birth']
        blood = request.form['blood']
        phone = request.form['phone']
        email = request.form['email']
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                UPDATE member
                SET nm = ?, birth = ?, blood = ?, phone = ?, email = ?
                WHERE iid = ?
            """, (nm, birth, blood, phone, email, session['user_id']))
            conn.commit()
            return redirect(url_for('index'))
        except Exception as e:
            with open('error.log', 'a') as f:
                f.write(str(e) + '\n')
            return render_template('error.html')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM member WHERE iid = ?", (session['user_id'],))
        user = cur.fetchone()
        return render_template('edit.html', user=user)
    except Exception as e:
        with open('error.log', 'a') as f:
            f.write(str(e) + '\n')
        return render_template('error.html')

@app.route('/logout')                                       #登出路由
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


