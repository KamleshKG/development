import streamlit as st
import json
import os
import sqlite3
import pandas as pd
from fpdf import FPDF
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="DevOps Quiz Dashboard",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)


# --- Database Connection and Functions ---
def get_db_connection():
    return sqlite3.connect('quiz_app.db')


def get_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def add_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def save_quiz_progress(user_id, topic, q_index, score, questions_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM quiz_sessions WHERE user_id = ? AND quiz_topic = ?", (user_id, topic))
    session = cursor.fetchone()

    if session:
        cursor.execute(
            "UPDATE quiz_sessions SET current_question_index = ?, score = ?, questions_data = ? WHERE id = ?",
            (q_index, score, json.dumps(questions_data), session[0]))
    else:
        cursor.execute(
            "INSERT INTO quiz_sessions (user_id, quiz_topic, current_question_index, score, questions_data) VALUES (?, ?, ?, ?, ?)",
            (user_id, topic, q_index, score, json.dumps(questions_data)))
    conn.commit()
    conn.close()


def load_quiz_progress(user_id, topic):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT current_question_index, score, questions_data FROM quiz_sessions WHERE user_id = ? AND quiz_topic = ?",
        (user_id, topic))
    progress = cursor.fetchone()
    conn.close()
    if progress:
        return progress[0], progress[1], json.loads(progress[2])
    return 0, 0, None


def get_all_scores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, qs.quiz_topic, qs.score, COUNT(DISTINCT qs.id)
        FROM quiz_sessions qs
        JOIN users u ON qs.user_id = u.id
        GROUP BY u.username, qs.quiz_topic
    ''')
    scores = cursor.fetchall()
    conn.close()
    return scores


# --- PDF Certificate Generation ---
def create_certificate(username, topic, score_percent):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 48)
    pdf.set_text_color(220, 50, 50)
    pdf.cell(0, 50, 'Certificate of Completion', 0, 1, 'C')

    pdf.set_font('Arial', '', 24)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, f'This certifies that', 0, 1, 'C')

    pdf.set_font('Arial', 'B', 36)
    pdf.cell(0, 10, username, 0, 1, 'C')

    pdf.set_font('Arial', '', 24)
    pdf.cell(0, 20, f'has successfully completed the', 0, 1, 'C')

    pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 10, f'{topic} Quiz', 0, 1, 'C')

    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 20, f'with a score of {score_percent:.2f}%', 0, 1, 'C')

    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output


# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None
if "quiz_in_progress" not in st.session_state:
    st.session_state.quiz_in_progress = False
if "show_explanation" not in st.session_state:
    st.session_state.show_explanation = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}
if "user_answers" not in st.session_state:
    st.session_state.user_answers = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False


# --- Quiz Data Management ---
def load_quiz_data():
    """Scans the quizzes/ directory and loads all JSON quiz files with their associated roles."""
    quiz_data = {}
    quiz_dir = "quizzes"

    if not os.path.exists(quiz_dir):
        st.warning(f"The '{quiz_dir}' directory was not found. Please run the setup script.")
        return quiz_data

    for filename in os.listdir(quiz_dir):
        if filename.endswith(".json"):
            topic_name = os.path.splitext(filename)[0].replace("_", " ").title()
            filepath = os.path.join(quiz_dir, filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)

                    # Ensure the JSON file has the expected keys
                    if "questions" in data and "roles" in data:
                        quiz_data[topic_name] = {
                            "roles": data["roles"],
                            "questions": data["questions"]
                        }
                    else:
                        st.error(f"Invalid format in file: {filename}. Missing 'roles' or 'questions' key.")
                except json.JSONDecodeError:
                    st.error(f"Error decoding JSON from file: {filename}.")

    return quiz_data

# --- Quiz App Functions ---
def show_quiz_selection():
    """Allows the user to select a quiz topic, filtered by their role."""
    st.title("Select Your Quiz Topic")

    # Get the user's role
    current_user_role = st.session_state.role

    # Filter topics based on the user's role
    available_topics = []
    for topic, data in st.session_state.quiz_data.items():
        if current_user_role in data["roles"]:
            available_topics.append(topic)

    if not available_topics:
        st.info(f"No quiz topics found for your role: **{current_user_role}**.")
        return

    selected_topic = st.selectbox("Choose a topic:", available_topics)
    st.session_state.current_topic = selected_topic

    progress = load_quiz_progress(st.session_state.user_id, selected_topic)

    if progress and progress[2] is not None:
        q_index, score, _ = progress
        st.info(f"You have an ongoing quiz for this topic. You are on question {q_index + 1} with a score of {score}.")

        if st.button("Resume Quiz"):
            st.session_state.current_question_index = q_index
            st.session_state.score = score
            st.session_state.quiz_in_progress = True
            st.rerun()

    if st.button("Start New Quiz"):
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.quiz_in_progress = True
        st.rerun()


def show_quiz_question():
    topic = st.session_state.current_topic

    # Access the list of questions from the new structure
    quiz_questions = st.session_state.quiz_data[topic]["questions"]
    q_index = st.session_state.current_question_index

    if q_index < len(quiz_questions):
        question_data = quiz_questions[q_index]
        is_multi_select = question_data.get("is_multi_select", False)

        st.header(f"Question {q_index + 1}/{len(quiz_questions)}: {topic}")
        st.subheader(question_data["question"])

        if is_multi_select:
            st.session_state.user_answers = []
            for option in question_data["options"]:
                if st.checkbox(option, key=f"{topic}_{q_index}_{option}"):
                    st.session_state.user_answers.append(option)
        else:
            st.session_state.user_answers = st.radio(
                "Choose one answer:",
                question_data["options"],
                index=None
            )

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.button("Submit Answer", key=f"submit_{q_index}")
        with col2:
            hint_button = st.button("Show Hint", key=f"hint_{q_index}")

        if submit_button:
            st.session_state.submitted = True
            check_answer(question_data, is_multi_select)

        if hint_button:
            st.info(question_data.get("hint", "No hint available."))

        if st.session_state.submitted:
            st.markdown("---")
            st.markdown(f"**Correct Answer(s):** {', '.join(question_data['answer'])}")
            st.markdown(f"**Explanation:** {question_data.get('rationale', 'No rationale provided.')}")

            if st.button("Next Question", key=f"next_q_{q_index}"):
                st.session_state.current_question_index += 1
                st.session_state.submitted = False
                save_quiz_progress(st.session_state.user_id, topic, st.session_state.current_question_index,
                                   st.session_state.score, quiz_questions)
                st.rerun()
    else:
        total_questions = len(quiz_questions)
        score_percent = (st.session_state.score / total_questions) * 100

        st.balloons()
        st.title("Quiz Complete! 🏆")
        st.success(f"Your final score: {st.session_state.score} out of {total_questions} ({score_percent:.2f}%)")

        st.markdown("---")

        score_df = pd.DataFrame({
            'Topic': [st.session_state.current_topic],
            'Score': [st.session_state.score],
            'Total Questions': [total_questions],
            'Percentage': [f"{score_percent:.2f}%"]
        })
        st.download_button(
            label="Download Score Report 📄",
            data=score_df.to_csv().encode('utf-8'),
            file_name=f"{st.session_state.username}_{st.session_state.current_topic}_score.csv",
            mime="text/csv"
        )

        if score_percent >= 80:
            st.balloons()
            st.success("Congratulations on your excellent score! Here is your certificate.")

            pdf_data = create_certificate(st.session_state.username, st.session_state.current_topic, score_percent)
            st.download_button(
                label="Download Certificate 🏅",
                data=pdf_data,
                file_name=f"{st.session_state.username}_{st.session_state.current_topic}_certificate.pdf",
                mime="application/pdf"
            )

        if st.button("Take Another Quiz"):
            st.session_state.quiz_in_progress = False
            st.session_state.submitted = False
            st.rerun()


def check_answer(question_data, is_multi_select):
    if is_multi_select:
        user_selection = sorted(st.session_state.user_answers)
        correct_answers = sorted(question_data["answer"])
        if user_selection == correct_answers:
            st.session_state.score += 1
            st.success("Correct! 🎉")
        else:
            st.error("Incorrect. 😥")
    else:
        if st.session_state.user_answers == question_data["answer"][0]:
            st.session_state.score += 1
            st.success("Correct! 🎉")
        else:
            st.error("Incorrect. 😥")


# --- Admin Panel ---
def admin_panel():
    st.title("Admin Dashboard")
    st.markdown("---")

    st.subheader("User Management")
    with st.form("add_user_form"):
        st.write("Add a New User")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["user", "admin"])
        if st.form_submit_button("Add User"):
            if add_user(new_username, new_password, new_role):
                st.success(f"User '{new_username}' added successfully!")
            else:
                st.error(f"User '{new_username}' already exists.")

    st.subheader("Current Users")
    users = get_all_users()
    if users:
        users_df = pd.DataFrame(users, columns=['Username', 'Role'])
        st.dataframe(users_df)

        user_to_delete = st.selectbox("Select user to delete:", [u[0] for u in users], key='delete_user_select')
        if st.button("Delete Selected User"):
            if user_to_delete and user_to_delete != st.session_state.username:
                delete_user(user_to_delete)
                st.success(f"User '{user_to_delete}' deleted.")
                st.rerun()
            else:
                st.error("Cannot delete yourself or a non-selected user.")
    else:
        st.info("No users found.")

    st.markdown("---")

    st.subheader("Scoreboard")
    scores = get_all_scores()
    if scores:
        scores_df = pd.DataFrame(scores, columns=['Username', 'Quiz Topic', 'Score', 'Total Questions'])
        scores_df['Percentage'] = (scores_df['Score'] / scores_df['Total Questions'] * 100).round(2)
        st.dataframe(scores_df)
        st.download_button(
            label="Download All Scores 📊",
            data=scores_df.to_csv().encode('utf-8'),
            file_name="all_quiz_scores.csv",
            mime="text/csv"
        )
    else:
        st.info("No quiz scores available yet.")


# --- Main Application Logic ---
if not st.session_state.quiz_data:
    st.session_state.quiz_data = load_quiz_data()

st.sidebar.title("Navigation")
if st.session_state.logged_in:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.session_state.role == "admin":
        st.sidebar.info("You are an admin.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.quiz_in_progress = False
        st.session_state.role = None
        st.session_state.user_id = None
        st.rerun()

    if st.session_state.role == "admin":
        admin_panel()
    elif st.session_state.quiz_in_progress:
        show_quiz_question()
    else:
        show_quiz_selection()
else:
    st.title("DevOps Quiz Dashboard 🤖")
    st.subheader("Login to start your quiz journey!")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = get_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.role = user[2]
                st.success(f"Welcome, {st.session_state.username}! 🎉")
                st.rerun()
            else:
                st.error("Invalid username or password.")