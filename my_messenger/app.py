from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit  # 💡 실시간 통신 라이브러리 추가
import sqlite3
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.secret_key = 'messenger_secret_key_1234'
socketio = SocketIO(app)  # 💡 Flask 앱에 웹소켓 기능 연결

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

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return "<script>alert('회원가입이 완료되었습니다! 로그인 해주세요.'); location.href='/';</script>"
    except sqlite3.IntegrityError:
        conn.close()
        return "<script>alert('이미 존재하는 아이디입니다.'); history.back();</script>"

# 💡 대화창을 열 때 과거에 나눈 메시지 기록도 DB에서 가져오도록 수정
@app.route('/index')
def index_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages ORDER BY timestamp ASC").fetchall()
    conn.close()
    return render_template('index.html', username=session['username'], messages=messages)

# --- 💡 [핵심] 사용자가 전송 버튼을 눌렀을 때 실행되는 실시간 이벤트 수신기 ---
@socketio.on('send_message')
def handle_message(data):
    if 'username' not in session:
        return

    sender = session['username']
    content = data.get('content')
    
    if content:
        # 1. DB에 실시간 대화 내용 저장
        conn = get_db_connection()
        conn.execute("INSERT INTO messages (sender, content) VALUES (?, ?)", (sender, content))
        conn.commit()
        conn.close()
        
        # 2. 접속 중인 모든 사람에게 즉시 메시지 전달 (브로드캐스팅)
        emit('receive_message', {
            'sender': sender,
            'content': content
        }, broadcast=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # 💡 allow_unsafe_werkzeug=True 옵션을 추가하여 배포 서버 오류를 통과시킵니다.
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
