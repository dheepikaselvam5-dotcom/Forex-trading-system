import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    balance REAL DEFAULT 100000
)
""")

cur.execute("""
CREATE TABLE trades(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    currency TEXT,
    action TEXT,
    amount REAL,
    price REAL,
    profit REAL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE alerts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    currency TEXT,
    target REAL,
    triggered INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE predictions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    currency TEXT,
    trend TEXT,
    suggestion TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
INSERT INTO users(username,password,role,balance)
VALUES('admin','admin123','admin',100000)
""")

conn.commit()
conn.close()
print("✅ Database initialized successfully")


