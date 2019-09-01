import sqlite3


def get_user(username):
    conn = sqlite3.connect("medical.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def changeUserPassword(username, password):
    conn = sqlite3.connect("medical.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (password, username, ))
    conn.commit()
    conn.close()
