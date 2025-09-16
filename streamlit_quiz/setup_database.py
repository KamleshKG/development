
import sqlite3

def setup_db():
    conn = sqlite3.connect('quiz_app.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Create quiz_sessions table to track user progress
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            quiz_topic TEXT,
            current_question_index INTEGER,
            score INTEGER,
            questions_data TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Insert an admin user for initial setup
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ('admin', 'password123', 'admin'))

    # Insert a regular user
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ('user1', 'user123', 'user'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_db()
    print("Database and tables created successfully with default admin and user accounts.")
