import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'agency.db'

def setup_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Hash the master password
    username = 'nova'
    password = 'url7856nv'
    password_hash = generate_password_hash(password)

    # Insert or update the master admin
    try:
        cursor.execute('''
            INSERT INTO admins (username, password_hash)
            VALUES (?, ?)
        ''', (username, password_hash))
        print(f"Admin '{username}' successfully created.")
    except sqlite3.IntegrityError:
        # User already exists, update their password just in case
        cursor.execute('''
            UPDATE admins 
            SET password_hash = ? 
            WHERE username = ?
        ''', (password_hash, username))
        print(f"Admin '{username}' already exists. Password updated.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_admin()
