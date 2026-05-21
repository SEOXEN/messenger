from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'messenger_secret_key_1234'

def get_db_connection():
    conn = sqlite3.connect('messenger.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def login_page():
    if 'username' in session:
        return redirect(url_for('index_page'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()

    if user:
        session['username'] = username
        return redirect(url_for('index_page'))
    else:
        return "<script>alert('로그인 실패! 아이디나 비밀번호를 확인하세요.'); history.back();</script>"

# --- 💡 회원가입 기능 추가 시작 ---

# 1. 회원가입 화면 보여주기
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# 2. 회원가입 데이터 처리 및 DB 저장
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    try:
        # DB에 유저가 입력한 아이디와 비번 추가
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return "<script>alert('회원가입이 완료되었습니다! 로그인 해주세요.'); location.href='/';</script>"
    except sqlite3.IntegrityError:
        # 아이디가 중복되었을 때 발생하는 에러 처리
        conn.close()
        return "<script>alert('이미 존재하는 아이디입니다.'); history.back();</script>"

# --- 💡 회원가입 기능 추가 끝 ---

@app.route('/index')
def index_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
