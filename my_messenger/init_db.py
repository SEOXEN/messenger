import sqlite3

conn = sqlite3.connect('messenger.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
try:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('test', '1234'))
    conn.commit()
    print("DB 초기화 완료! 테스트 계정: test / 1234")
except:
    print("이미 DB가 존재합니다.")
conn.close()
