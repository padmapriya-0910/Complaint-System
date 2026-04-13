import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# USERS TABLE
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT,
    role TEXT,
    verified INTEGER
)''')

# COMPLAINTS TABLE
c.execute('''CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    category TEXT,
    description TEXT,
    location TEXT,
    priority TEXT,
    date TEXT,
    status TEXT
)''')

conn.commit()
conn.close()

print("Database created successfully!")