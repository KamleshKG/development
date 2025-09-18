
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DB_PATH = "portal.db"

st.set_page_config(page_title="Leadership Dashboard", page_icon="📊", layout="wide")
st.title("📊 Leadership Dashboard — Gamified CI/CD Portal")

@st.cache_data
def load_df(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)

if not Path(DB_PATH).exists():
    st.warning("Database not found. Launch the main app and initialize the DB first.")
    st.stop()

tables = load_df("SELECT name FROM sqlite_master WHERE type='table'")["name"].tolist()

total_users = load_df("SELECT COUNT(*) as n FROM users")["n"].iloc[0] if "users" in tables else 0
total_questions = load_df("SELECT COUNT(*) as n FROM questions")["n"].iloc[0] if "questions" in tables else 0
total_tasks = load_df("SELECT COUNT(*) as n FROM tasks")["n"].iloc[0] if "tasks" in tables else 0
pending_reviews = load_df("SELECT COUNT(*) as n FROM task_submissions WHERE status IN ('submitted','needs_changes')")["n"].iloc[0] if "task_submissions" in tables else 0
approved_subs = load_df("SELECT COUNT(*) as n FROM task_submissions WHERE status='approved'")["n"].iloc[0] if "task_submissions" in tables else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Users", total_users)
c2.metric("Questions", total_questions)
c3.metric("Tasks", total_tasks)
c4.metric("Pending Reviews", pending_reviews)
c5.metric("Approved Submissions", approved_subs)

st.divider()

st.subheader("Top 10 — Total Score")
top10 = load_df(
    "SELECT u.username, COALESCE(l.total_score,0) as total_score "
    "FROM users u LEFT JOIN leaderboard l ON l.user_id=u.id "
    "ORDER BY total_score DESC LIMIT 10"
) if "users" in tables else pd.DataFrame()
if top10.empty:
    st.info("No leaderboard data yet.")
else:
    fig = plt.figure()
    plt.bar(top10["username"], top10["total_score"])
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Score")
    plt.title("Top 10 Users by Total Score")
    st.pyplot(fig)

st.divider()

st.subheader("Review SLAs — Time to Approval (Hours)")
if "task_submissions" in tables:
    df_approved = load_df(
        "SELECT submitted_at, reviewed_at FROM task_submissions WHERE status='approved' AND submitted_at IS NOT NULL AND reviewed_at IS NOT NULL"
    )
    if df_approved.empty:
        st.info("No approved submissions yet.")
    else:
        df_approved["submitted_at"] = pd.to_datetime(df_approved["submitted_at"])
        df_approved["reviewed_at"] = pd.to_datetime(df_approved["reviewed_at"])
        df_approved["hours"] = (df_approved["reviewed_at"] - df_approved["submitted_at"]).dt.total_seconds() / 3600
        st.write(f"Median hours to approval: **{df_approved['hours'].median():.2f}**")
        fig2 = plt.figure()
        plt.hist(df_approved["hours"], bins=10)
        plt.xlabel("Hours"); plt.ylabel("Count"); plt.title("Distribution of Time-to-Approval")
        st.pyplot(fig2)
else:
    st.info("No submissions table yet.")

st.divider()

st.subheader("Task Funnel")
funnel = load_df("SELECT status, COUNT(*) as n FROM task_submissions GROUP BY status") if "task_submissions" in tables else pd.DataFrame()
if funnel.empty:
    st.info("No task submissions yet.")
else:
    st.dataframe(funnel)
    fig3 = plt.figure()
    plt.bar(funnel["status"], funnel["n"])
    plt.ylabel("Count")
    plt.title("Submissions by Status")
    st.pyplot(fig3)

st.divider()

st.subheader("Approvals by Plugin")
if set(["task_submissions","tasks","plugins"]).issubset(set(tables)):
    per_plugin = load_df(
        "SELECT p.code as plugin, COUNT(*) as approvals FROM task_submissions s JOIN tasks t ON t.id=s.task_id "
        "JOIN plugins p ON p.id=t.plugin_id WHERE s.status='approved' GROUP BY p.code ORDER BY approvals DESC"
    )
    if per_plugin.empty:
        st.info("No approvals yet.")
    else:
        fig4 = plt.figure()
        plt.bar(per_plugin["plugin"], per_plugin["approvals"])
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Approvals")
        plt.title("Approved Submissions per Plugin")
        st.pyplot(fig4)
else:
    st.info("Insufficient tables for per-plugin view.")

st.divider()

st.subheader("Exports")
df_attempts = load_df("SELECT * FROM attempts ORDER BY attempted_at DESC LIMIT 500") if "attempts" in tables else pd.DataFrame()
st.download_button("Export Attempts (CSV)", data=df_attempts.to_csv(index=False), file_name="attempts_export.csv")
df_subs = load_df("SELECT * FROM task_submissions ORDER BY submitted_at DESC LIMIT 500") if "task_submissions" in tables else pd.DataFrame()
st.download_button("Export Task Submissions (CSV)", data=df_subs.to_csv(index=False), file_name="task_submissions_export.csv")
