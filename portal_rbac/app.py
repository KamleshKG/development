
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime

from utils.rbac import can_sync_plugins, can_review, can_play, can_view_reports
from utils.loader import scan_plugins, load_questions_json, load_tasks_json
from utils.store import run_schema, init_admin, upsert_plugin, upsert_question, upsert_task, get_conn, hash_pw

DB_PATH = "portal.db"

# --- Robust PLUGINS_DIR (works without secrets.toml) ---
try:
    PLUGINS_DIR = st.secrets["PLUGINS_DIR"]
except Exception:
    PLUGINS_DIR = os.environ.get("PLUGINS_DIR", "plugins")

st.set_page_config(page_title="RBAC Gamified Portal (Plugins)", page_icon="🧩", layout="wide")
st.title("🧩 RBAC Gamified Portal — Plugins (Questions + Tasks)")

if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.subheader("Setup")
    if st.button("Initialize DB", key="btn_init_db"):
        run_schema("schema.sql")
        init_admin()
        st.success("DB ready. Admin default: admin / admin123")

    st.subheader("Auth")
    if st.session_state.user:
        st.write(f"Logged in as **{st.session_state.user['username']}** ({st.session_state.user['role']})")
        if st.button("Logout", key="btn_logout"):
            st.session_state.user = None
    else:
        u = st.text_input("Username", key="login_username")
        p = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="btn_login"):
            with get_conn() as conn:
                c = conn.cursor()
                c.execute("SELECT id, password_hash, role FROM users WHERE username=?", (u,))
                row = c.fetchone()
            if row and row[1] == hash_pw(p):
                st.session_state.user = {"id": row[0], "username": u, "role": row[2]}
                st.success(f"Welcome {u}")
            else:
                st.error("Invalid credentials")
        st.divider()
        st.caption("New here? Register below.")
        ru = st.text_input("New username", key="reg_username")
        rp = st.text_input("New password", type="password", key="reg_password")
        role = st.selectbox("Role", ["player","manager","admin","auditor"], index=0, key="reg_role")
        if st.button("Register", key="btn_register"):
            with get_conn() as conn:
                try:
                    conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                                 (ru, hash_pw(rp), role))
                    conn.commit()
                    st.success("Registered. Login now.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")

tabs = st.tabs(["Play", "Tasks", "Review", "Admin", "Reports"])

# --- Tab: Admin (Sync plugins) ---
with tabs[3]:
    st.header("Admin — Plugin Packs")
    if not st.session_state.user or not can_sync_plugins(st.session_state.user["role"]):
        st.info("Admin only.")
    else:
        st.write(f"Plugins folder: `{PLUGINS_DIR}`")
        if st.button("Scan & Sync Plugins", key="btn_sync_plugins"):
            count_q = count_t = 0
            for item in scan_plugins(PLUGINS_DIR):
                code = item["code"]
                pid = upsert_plugin(code, code)
                if item["questions_path"]:
                    data = load_questions_json(item["questions_path"])
                    for q in data["questions"]:
                        upsert_question(pid, q)
                        count_q += 1
                if item["tasks_path"]:
                    data = load_tasks_json(item["tasks_path"])
                    for t in data["tasks"]:
                        upsert_task(pid, t, created_by=st.session_state.user["id"])
                        count_t += 1
            st.success(f"Synced: {count_q} questions, {count_t} tasks")

        with get_conn() as conn:
            dfp = pd.read_sql_query("SELECT id, code, title, is_enabled FROM plugins", conn)
            st.dataframe(dfp)

# --- Tab: Play (Questions) ---
with tabs[0]:
    st.header("Play — Questions")
    if not st.session_state.user or not can_play(st.session_state.user["role"]):
        st.info("Login as player/manager/admin to play.")
    else:
        with get_conn() as conn:
            dplugs = pd.read_sql_query("SELECT code FROM plugins WHERE is_enabled=1 ORDER BY code", conn)
        plug = st.selectbox("Plugin", dplugs["code"].tolist() if not dplugs.empty else [], key="play_plugin")
        level = st.selectbox("Level", ["Beginner","Intermediate","Advanced"], index=2, key="play_level")
        count = st.slider("Questions", 5, 20, 10, key="play_count")
        if st.button("Load Questions", key="btn_load_questions"):
            with get_conn() as conn:
                query = (
                    "SELECT q.id, q.question_id, q.level, q.question, "
                    "q.option_1,q.option_2,q.option_3,q.option_4,q.option_5, "
                    "q.correct_options, q.is_multi_select, q.hint, q.rationale "
                    "FROM questions q "
                    "JOIN plugins p ON p.id=q.plugin_id "
                    "WHERE p.code=? AND q.level=? "
                    "ORDER BY RANDOM() "
                    "LIMIT ?"
                )
                dfq = pd.read_sql_query(query, conn, params=(plug, level, count))
            st.session_state.qset = dfq

        if "qset" in st.session_state and not st.session_state.qset.empty:
            for _, r in st.session_state.qset.iterrows():
                st.markdown(f"**[{r['question_id']}] {r['question']}**  \\n_Level: {r['level']}_")
                options = [r['option_1'], r['option_2'], r['option_3'], r['option_4'], r['option_5']]
                options = [o for o in options if isinstance(o, str) and o.strip()]
                selected = []
                if r["is_multi_select"]:
                    for idx, o in enumerate(options, 1):
                        if st.checkbox(o, key=f"q{r['id']}_{idx}"):
                            selected.append(f"option_{idx}")
                else:
                    pick = st.radio(f"Choose one (Q{r['id']})", options, key=f"radio_{r['id']}")
                    if pick:
                        idx = options.index(pick) + 1
                        selected = [f"option_{idx}"]
                cols = st.columns(3)
                with cols[0]:
                    if st.button(f"Hint {r['id']}", key=f"hint_{r['id']}"):
                        st.info(r["hint"] or "No hint")
                with cols[1]:
                    if st.button(f"Submit {r['id']}", key=f"submit_{r['id']}"):
                        correct = set([x.strip() for x in r["correct_options"].split(",") if x.strip()])
                        chosen = set(selected)
                        good = (correct == chosen)
                        delta = 10 if good else -2
                        with get_conn() as conn:
                            conn.execute(
                                "INSERT INTO attempts (user_id, question_db_id, is_correct, selected_options, score_delta) VALUES (?,?,?,?,?)",
                                (st.session_state.user["id"], int(r["id"]), 1 if good else 0, ",".join(selected), delta)
                            )
                            conn.execute(
                                "INSERT INTO leaderboard (user_id, total_score) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET total_score = total_score + excluded.total_score, last_updated=CURRENT_TIMESTAMP",
                                (st.session_state.user["id"], delta)
                            )
                            conn.commit()
                        if good:
                            st.success(f"Correct! (+{delta})")
                        else:
                            st.error(f"Not quite ({delta})")
                        st.caption(f"Rationale: {r['rationale']}")

# --- Tab: Tasks (Submit Evidence) ---
with tabs[1]:
    st.header("Tasks — Submit Evidence")
    if not st.session_state.user or not can_play(st.session_state.user["role"]):
        st.info("Login as player/manager/admin to submit tasks.")
    else:
        with get_conn() as conn:
            dplugs = pd.read_sql_query("SELECT code FROM plugins WHERE is_enabled=1 ORDER BY code", conn)
        plug = st.selectbox("Plugin", dplugs["code"].tolist() if not dplugs.empty else [], key="tasks_plugin")
        level = st.selectbox("Level", ["Beginner","Intermediate","Advanced"], index=2, key="tasks_level")
        with get_conn() as conn:
            query = (
                "SELECT t.id, p.code as plugin, t.code, t.title, t.description, t.level, t.points, t.require_attachment "
                "FROM tasks t JOIN plugins p ON p.id=t.plugin_id "
                "WHERE p.code=? AND t.level=? "
                "ORDER BY t.code"
            )
            dft = pd.read_sql_query(query, conn, params=(plug, level))
        if dft.empty:
            st.info("No tasks — Admin must sync plugin packs.")
        else:
            evidence_dir = Path("evidence"); evidence_dir.mkdir(exist_ok=True)
            for _, t in dft.iterrows():
                st.markdown(f"**[{t['code']}] {t['title']}** — _{t['plugin']} · {t['level']} · {t['points']} pts_")
                st.write(t["description"])
                with st.expander("Submit evidence", expanded=False):
                    text = st.text_area("What you did (steps/commands/links):", key=f"txt_{t['id']}")
                    up = st.file_uploader("Attach proof", key=f"file_{t['id']}")
                    if st.button(f"Submit {t['code']}", key=f"btn_submit_task_{t['id']}"):
                        saved_path = None
                        if up is not None:
                            fname = f"{st.session_state.user['id']}-{t['id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{up.name}"
                            pth = evidence_dir / fname
                            pth.write_bytes(up.read())
                            saved_path = str(pth)
                        with get_conn() as conn:
                            conn.execute(
                                "INSERT INTO task_submissions (task_id, user_id, evidence_text, evidence_file, status) VALUES (?,?,?,?,?)",
                                (int(t["id"]), st.session_state.user["id"], text, saved_path, "submitted")
                            )
                            conn.commit()
                        st.success("Submitted for review!")

# --- Tab: Review (Managers) ---
with tabs[2]:
    st.header("Review — Approve/Reject/Request Changes")
    if not st.session_state.user or not can_review(st.session_state.user["role"]):
        st.info("Managers/Admins only.")
    else:
        with get_conn() as conn:
            query = (
                "SELECT s.id, u.username, p.code as plugin, t.code, t.title, "
                "s.evidence_text, s.evidence_file, s.status, s.submitted_at "
                "FROM task_submissions s "
                "JOIN tasks t ON t.id=s.task_id "
                "JOIN plugins p ON p.id=t.plugin_id "
                "JOIN users u ON u.id=s.user_id "
                "WHERE s.status IN ('submitted','needs_changes') "
                "ORDER BY s.submitted_at ASC"
            )
            dfr = pd.read_sql_query(query, conn)
        if dfr.empty:
            st.info("No pending submissions.")
        else:
            for _, r in dfr.iterrows():
                st.markdown(f"**#{r['id']}** — {r['username']} → [{r['plugin']}/{r['code']}] {r['title']} · {r['status']} · {r['submitted_at']}")
                if r["evidence_text"]:
                    st.write(f"**Evidence:** {r['evidence_text']}")
                if r["evidence_file"] and Path(r["evidence_file"]).exists():
                    st.download_button("Download attachment", data=Path(r["evidence_file"]).read_bytes(), file_name=Path(r["evidence_file"]).name, key=f"dl_{r['id']}")
                comment = st.text_input(f"Reviewer comment #{r['id']}", key=f"c_{r['id']}")
                award = st.number_input(f"Award points #{r['id']}", min_value=0, max_value=1000, value=100, step=10, key=f"p_{r['id']}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"Approve #{r['id']}", key=f"approve_{r['id']}"):
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE task_submissions SET status='approved', reviewer_id=?, reviewer_comment=?, score_awarded=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?",
                                (st.session_state.user["id"], comment, int(award), int(r["id"]))
                            )
                            # award
                            conn.execute(
                                "INSERT INTO task_points (user_id, total_task_points) VALUES ((SELECT user_id FROM task_submissions WHERE id=?), ?) ON CONFLICT(user_id) DO UPDATE SET total_task_points = total_task_points + excluded.total_task_points, last_updated=CURRENT_TIMESTAMP",
                                (int(r["id"]), int(award))
                            )
                            conn.execute(
                                "INSERT INTO leaderboard (user_id, total_score) VALUES ((SELECT user_id FROM task_submissions WHERE id=?), ?) ON CONFLICT(user_id) DO UPDATE SET total_score = total_score + excluded.total_score, last_updated=CURRENT_TIMESTAMP",
                                (int(r["id"]), int(award))
                            )
                            conn.commit()
                        st.success("Approved!")
                with c2:
                    if st.button(f"Reject #{r['id']}", key=f"reject_{r['id']}"):
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE task_submissions SET status='rejected', reviewer_id=?, reviewer_comment=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?",
                                (st.session_state.user["id"], comment, int(r["id"]))
                            )
                            conn.commit()
                        st.warning("Rejected.")
                with c3:
                    if st.button(f"Needs Changes #{r['id']}", key=f"needs_changes_{r['id']}"):
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE task_submissions SET status='needs_changes', reviewer_id=?, reviewer_comment=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?",
                                (st.session_state.user["id"], comment, int(r["id"]))
                            )
                            conn.commit()
                        st.info("Requested changes.")

# --- Tab: Reports (Auditor) ---
with tabs[4]:
    st.header("Reports — Audit & Exports")
    if not st.session_state.user or not can_view_reports(st.session_state.user["role"]):
        st.info("Admins/Managers/Auditors only.")
    else:
        with get_conn() as conn:
            df_users = pd.read_sql_query("SELECT id, username, role, created_at FROM users", conn)
            df_attempts = pd.read_sql_query("SELECT * FROM attempts ORDER BY attempted_at DESC LIMIT 200", conn)
            df_subs = pd.read_sql_query("SELECT * FROM task_submissions ORDER BY submitted_at DESC LIMIT 200", conn)
        st.subheader("Users")
        st.dataframe(df_users)
        st.subheader("Recent Attempts")
        st.dataframe(df_attempts)
        st.subheader("Recent Task Submissions")
        st.dataframe(df_subs)
        st.download_button("Export Attempts CSV", data=df_attempts.to_csv(index=False), file_name="attempts.csv", key="dl_attempts")
        st.download_button("Export Task Submissions CSV", data=df_subs.to_csv(index=False), file_name="task_submissions.csv", key="dl_subs")
