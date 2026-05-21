import sqlite3
import os

# 💡 파일이 실행되는 위치를 기준으로 messenger.db 절대 경로 설정
db_path = os.path.join(os.path.dirname(__file__), 'messenger.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 회원 정보(users) 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# 2. 실시간 메시지(messages) 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 3. 테스트 계정 삽입 (이미 있으면 무시하고 넘어감)
try:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('test', '1234'))
except sqlite3.IntegrityError:
    pass

conn.commit()
conn.close()
print("DB 초기화 완료! 테스트 계정: test / 1234")
