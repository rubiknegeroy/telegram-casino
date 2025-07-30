import sqlite3

conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS gifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    emoji TEXT,
    rarity TEXT,
    image TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    image TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS case_gifts (
    case_id INTEGER,
    gift_id INTEGER,
    chance INTEGER,
    PRIMARY KEY (case_id, gift_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    gift_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (gift_id) REFERENCES gifts(id)
)
''')

conn.commit()

def get_balance(user_id):
    cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
    conn.commit()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()[0]

def add_balance(user_id, amount):
    cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def remove_balance(user_id, amount):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]
    if balance >= amount:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        return True
    return False

def add_gift_to_inventory(user_id, gift_id):
    cursor.execute("INSERT INTO inventory (user_id, gift_id) VALUES (?, ?)", (user_id, gift_id))
    conn.commit()

def get_inventory(user_id):
    cursor.execute('''
        SELECT gifts.name, gifts.emoji, gifts.rarity
        FROM inventory
        JOIN gifts ON inventory.gift_id = gifts.id
        WHERE inventory.user_id = ?
    ''', (user_id,))
    return cursor.fetchall()
