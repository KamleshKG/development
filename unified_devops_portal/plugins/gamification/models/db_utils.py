import sqlite3
import json
import os
from pathlib import Path

class GamificationDB:
    def __init__(self, db_path='gamification.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        with self.get_connection() as conn:
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
                description TEXT,
                points INTEGER DEFAULT 0
            )
            ''')
            
            # User progress table
            c.execute('''
            CREATE TABLE IF NOT EXISTS user_milestones (
                user_id INTEGER,
                milestone_id INTEGER,
                achieved INTEGER DEFAULT 0,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(milestone_id) REFERENCES milestones(id),
                UNIQUE(user_id, milestone_id)
            )
            ''')
            
            # Load quests from JSON
            self.load_quests(conn)
            
            conn.commit()
    
    def load_quests(self, conn):
        c = conn.cursor()
        
        # Load quests from JSON files
        quests_path = Path(__file__).parent / 'quests'
        for quest_file in quests_path.glob('*.json'):
            with open(quest_file, 'r') as f:
                quest_data = json.load(f)
            
            for quest_line in quest_data['quest_lines']:
                for milestone in quest_line['milestones']:
                    # Insert or update milestone
                    c.execute('''
                    INSERT OR REPLACE INTO milestones (id, name, description, points)
                    VALUES (?, ?, ?, ?)
                    ''', (milestone['id'], milestone['name'], milestone['description'], milestone.get('points', 0)))
    
    def get_user(self, username, password):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id, username, role FROM users WHERE username=? AND password=?', 
                     (username, password))
            return c.fetchone()
    
    def get_user_progress(self, user_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
            SELECT m.id, m.name, m.description, m.points, 
                   COALESCE(um.achieved, 0) as achieved,
                   um.achieved_at
            FROM milestones m
            LEFT JOIN user_milestones um ON m.id = um.milestone_id AND um.user_id = ?
            ORDER BY m.id
            ''', (user_id,))
            return c.fetchall()
    
    # ... (Keep your other methods like set_milestone, get_leaderboard, etc.) ...