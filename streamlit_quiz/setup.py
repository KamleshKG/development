import os
import sqlite3

def create_dirs_and_files():
    """Creates the necessary directory structure and populates it with sample data."""

    # Create directories
    if not os.path.exists("quizzes"):
        os.makedirs("quizzes")
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # Create sample JSON quiz files with multiple-select options
    devops_quiz_data = [
        {
            "question": "Which of the four DORA metrics are focused on delivery speed?",
            "options": ["Deployment Frequency", "Mean Time to Recovery (MTTR)", "Change Failure Rate", "Lead Time for Changes"],
            "answer": ["Deployment Frequency", "Lead Time for Changes"],
            "is_multi_select": True,
            "hint": "Think about the two metrics that measure how quickly changes are delivered.",
            "rationale": "Deployment Frequency and Lead Time for Changes are the two metrics that measure how fast an organization can deliver changes to production."
        },
        {
            "question": "A team has a high Deployment Frequency but a low Change Failure Rate. This suggests they are succeeding at which aspect of DevOps?",
            "options": ["Speed, but not stability.", "Stability, but not speed.", "Both speed and stability.", "Neither speed nor stability."],
            "answer": ["Both speed and stability."],
            "is_multi_select": False,
            "hint": "Analyze what each of the two DORA metrics, Deployment Frequency and Change Failure Rate, indicates.",
            "rationale": "High Deployment Frequency represents speed, and a low Change Failure Rate represents stability, indicating success in both areas."
        }
    ]

    devsecops_quiz_data = [
        {
            "question": "In a DevSecOps pipeline, what is the primary purpose of a Static Application Security Testing (SAST) tool?",
            "options": ["To analyze running applications for vulnerabilities in real-time.", "To find security vulnerabilities by analyzing the source code before the application is built.", "To check for known vulnerabilities in third-party libraries and dependencies."],
            "answer": ["To find security vulnerabilities by analyzing the source code before the application is built."],
            "is_multi_select": False,
            "hint": "Think about the 'static' part of the name—it's about analyzing code when it's not running.",
            "rationale": "SAST tools analyze source code or binary code for security flaws without executing the application, making them ideal for early-stage pipeline integration."
        }
    ]

    # Write quiz data to files
    with open("quizzes/devops.json", "w") as f:
        json.dump(devops_quiz_data, f, indent=2)
    with open("quizzes/devsecops.json", "w") as f:
        json.dump(devsecops_quiz_data, f, indent=2)

    # Create setup_database.py
    db_setup_script = """
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
"""
    with open("setup_database.py", "w") as f:
        f.write(db_setup_script)

    print("File structure and sample quizzes created.")
    print("Now, run 'python setup_database.py' to create the database.")

if __name__ == '__main__':
    import json
    create_dirs_and_files()