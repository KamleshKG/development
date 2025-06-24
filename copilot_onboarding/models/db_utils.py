import sqlite3

DB_PATH = 'copilot.db'

def get_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

def get_milestones():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, description FROM milestones')
    milestones = c.fetchall()
    conn.close()
    return milestones

def get_user_progress(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT m.name, m.description, um.achieved
        FROM milestones m
        LEFT JOIN user_milestones um ON m.id = um.milestone_id AND um.user_id = ?
    ''', (user_id,))
    progress = c.fetchall()
    conn.close()
    return progress

def set_milestone(user_id, milestone_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO user_milestones (user_id, milestone_id, achieved)
        VALUES (?, ?, 1)
    ''', (user_id, milestone_id))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT u.username, SUM(um.achieved) as score
        FROM users u
        LEFT JOIN user_milestones um ON u.id = um.user_id
        GROUP BY u.username
        ORDER BY score DESC
    ''')
    leaderboard = c.fetchall()
    conn.close()
    return leaderboard

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users')
    users = c.fetchall()
    conn.close()
    return users

def set_user_role(user_id, role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET role=? WHERE id=?', (role, user_id))
    conn.commit()
    conn.close()