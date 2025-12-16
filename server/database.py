import sqlite3
import hashlib

DB_NAME = "voting.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    fullname TEXT,
                    password_hash TEXT,
                    has_voted INTEGER DEFAULT 0
                 )''')
    conn.commit()
    conn.close()

def add_user(user_id, fullname, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (id, fullname, password_hash) VALUES (?, ?, ?)", (user_id, fullname, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(user_id, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE id=? AND password_hash=?", (user_id, password_hash))
    user = c.fetchone()
    conn.close()
    return user

def mark_user_voted(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET has_voted=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def has_user_voted(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT has_voted FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == 1:
        return True
    return False

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
