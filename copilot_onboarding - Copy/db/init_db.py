import sqlite3

conn = sqlite3.connect('copilot.db')
c = conn.cursor()

# Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# Milestones table
c.execute('''
CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT
)
''')

# User progress table
c.execute('''
CREATE TABLE IF NOT EXISTS user_milestones (
    user_id INTEGER,
    milestone_id INTEGER,
    achieved INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(milestone_id) REFERENCES milestones(id)
)
''')

# Add 5 users and 1 admin
users = [
    ('User1', 'pass1', 'user'),
    ('User2', 'pass2', 'user'),
    ('User3', 'pass3', 'user'),
    ('User4', 'pass4', 'user'),
    ('User5', 'pass5', 'user'),
    ('Admin', 'adminpass', 'admin')
]
for u in users:
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', u)
    except:
        pass

# Add milestones
milestones = [
    ('First Suggestion', 'Accept your first Copilot suggestion'),
    ('5 Suggestions', 'Accept 5 Copilot suggestions'),
    ('First Bug Fix', 'Fix a bug using Copilot'),
    ('First Test', 'Write a unit test with Copilot'),
    ('Streak 3 Days', 'Use Copilot 3 days in a row')
]
for m in milestones:
    try:
        c.execute('INSERT INTO milestones (name, description) VALUES (?, ?)', m)
    except:
        pass

conn.commit()
conn.close()
