
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

DB_PATH = "portal.db"
CERTS_DIR = Path("certificates"); CERTS_DIR.mkdir(exist_ok=True)
EVIDENCE_DIR = Path("evidence"); EVIDENCE_DIR.mkdir(exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def run_base_schema():
    base = Path("schema.sql").read_text()
    with get_conn() as conn:
        conn.executescript(base)

def run_task_schema():
    ext = Path("schema_tasks.sql").read_text()
    with get_conn() as conn:
        conn.executescript(ext)

def init_admin():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1;")
        if not cur.fetchone():
            cur.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)",
                        ("admin", hash_pw("admin123"), "admin"))
            conn.commit()

def login(username, password):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, role, password_hash FROM users WHERE username=?", (username,))
        row = cur.fetchone()
    if row and row[2] == hash_pw(password):
        return {"id": row[0], "role": row[1], "username": username}
    return None

def register(username, password, role="player"):
    with get_conn() as conn:
        try:
            conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                         (username, hash_pw(password), role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def ensure_plugin(code, title=None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM plugins WHERE code=?", (code,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO plugins (code, title, is_enabled) VALUES (?,?,1)", (code, title or code))
        conn.commit()
        return cur.lastrowid

def import_tasks_csv(csv_path="tasks_template.csv"):
    df = pd.read_csv(csv_path)
    with get_conn() as conn:
        for _, r in df.iterrows():
            plugin_id = ensure_plugin(r["plugin"], r["plugin"])
            conn.execute(
                "INSERT OR IGNORE INTO tasks (plugin_id, code, title, description, level, points, require_attachment) VALUES (?,?,?,?,?,?,?)",
                (plugin_id, r["code"], r["title"], r["description"], r["level"], int(r["points"]), 1 if str(r["require_attachment"]) in ["1","true","True"] else 0)
            )
        conn.commit()

def list_tasks(plugin_code=None, level=None):
    with get_conn() as conn:
        cur = conn.cursor()
        q = "SELECT t.id, p.code, t.code, t.title, t.description, t.level, t.points, t.require_attachment FROM tasks t JOIN plugins p ON p.id=t.plugin_id WHERE 1=1"
        args = []
        if plugin_code:
            q += " AND p.code=?"; args.append(plugin_code)
        if level:
            q += " AND t.level=?"; args.append(level)
        q += " ORDER BY t.level, t.code"
        cur.execute(q, args)
        return cur.fetchall()

def submit_task(task_id, user_id, evidence_text, file_bytes, filename):
    saved_path = None
    if file_bytes and filename:
        fname = f"{user_id}-{task_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{filename}"
        saved = EVIDENCE_DIR / fname
        saved.write_bytes(file_bytes)
        saved_path = str(saved)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO task_submissions (task_id, user_id, evidence_text, evidence_file, status) VALUES (?,?,?,?,?)",
            (task_id, user_id, evidence_text, saved_path, "submitted")
        )
        conn.commit()

def my_task_submissions(user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id, s.task_id, t.code, t.title, s.status, s.submitted_at, s.score_awarded FROM task_submissions s JOIN tasks t ON t.id=s.task_id WHERE s.user_id=? ORDER BY s.submitted_at DESC",
            (user_id,)
        )
        return cur.fetchall()

def review_queue():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id, u.username, t.code, t.title, s.evidence_text, s.evidence_file, s.status, s.submitted_at FROM task_submissions s JOIN tasks t ON t.id=s.task_id JOIN users u ON u.id=s.user_id WHERE s.status IN ('submitted','needs_changes') ORDER BY s.submitted_at ASC"
        )
        return cur.fetchall()

def set_submission_status(submission_id, reviewer_id, status, comment, award_points):
    with get_conn() as conn:
        conn.execute(
            "UPDATE task_submissions SET status=?, reviewer_id=?, reviewer_comment=?, score_awarded=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, reviewer_id, comment, award_points, submission_id)
        )
        if status == "approved" and award_points and award_points > 0:
            conn.execute(
                "INSERT INTO task_points (user_id, total_task_points) VALUES ((SELECT user_id FROM task_submissions WHERE id=?), ?) ON CONFLICT(user_id) DO UPDATE SET total_task_points = total_task_points + excluded.total_task_points, last_updated = CURRENT_TIMESTAMP",
                (submission_id, award_points)
            )
            conn.execute(
                "INSERT INTO leaderboard (user_id, total_score) VALUES ((SELECT user_id FROM task_submissions WHERE id=?), ?) ON CONFLICT(user_id) DO UPDATE SET total_score = total_score + excluded.total_score, last_updated = CURRENT_TIMESTAMP",
                (submission_id, award_points)
            )
        conn.commit()

def get_my_task_points(user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(total_task_points,0) FROM task_points WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else 0

st.set_page_config(page_title="🎮 Gamified Portal + Tasks", page_icon="🧩", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

st.title("🧩 Gamified Question + Task Portal")
st.caption("Plugins: DevSecOps, DevOps, DataOps, AIOps, MLOps, Kubernetes, OpenShift ... with Task submissions & approvals")

with st.sidebar:
    if st.button("Initialize DB (base + tasks)"):
        run_base_schema()
        run_task_schema()
        init_admin()
        st.success("DB ready. Admin login: admin/admin123")
    if st.session_state.user:
        st.write(f"Logged in as **{st.session_state.user['username']}** ({st.session_state.user['role']})")

tab_auth, tab_tasks, tab_my_subs, tab_review, tab_task_points = st.tabs(["Login/Signup", "Task Catalog", "My Submissions", "Manager Review", "My Task Points"])

with tab_auth:
    st.subheader("Login")
    lu = st.text_input("Username", key="lu")
    lp = st.text_input("Password", type="password", key="lp")
    if st.button("Login"):
        u = login(lu, lp)
        if u:
            st.session_state.user = u
            st.success(f"Welcome {u['username']} ({u['role']})")
        else:
            st.error("Invalid credentials")
    st.divider()
    st.subheader("Register")
    ru = st.text_input("New username", key="ru")
    rp = st.text_input("New password", type="password", key="rp")
    role = st.selectbox("Role", ["player","manager","admin"])
    if st.button("Register"):
        ok = register(ru, rp, role=role)
        st.success("Registered! Please login.") if ok else st.error("Username exists.")

with tab_tasks:
    st.subheader("Task Catalog")
    plugin = st.selectbox("Plugin", ["All","DevSecOps","DevOps","DataOps","AIOPS","MLOps","Kubernetes","OpenShift"])
    level = st.selectbox("Level", ["All","Beginner","Intermediate","Advanced"], index=3)
    plug = None if plugin=="All" else plugin
    lvl = None if level=="All" else level

    rows = list_tasks(plugin_code=plug, level=lvl)
    if not rows:
        st.info("No tasks yet. Import tasks via CSV in the Admin panel of the other app or write to DB.")
    else:
        for (tid, pcode, tcode, title, desc, lvl, pts, req_att) in rows:
            st.markdown(f"**[{tcode}] {title}** — _{pcode} · {lvl} · {pts} pts_")
            st.write(desc)
            if st.session_state.user and st.session_state.user["role"] in ["player","admin","manager"]:
                with st.expander("Submit evidence"):
                    text = st.text_area("What you did (commands, steps, links):", key=f"txt_{tid}")
                    up = st.file_uploader("Attach proof (screenshot/log/archive)", key=f"file_{tid}")
                    if st.button(f"Submit Task {tcode}", key=f"sub_{tid}"):
                        b = up.read() if up else None
                        name = up.name if up else None
                        submit_task(tid, st.session_state.user["id"], text, b, name)
                        st.success("Submitted for review!")

with tab_my_subs:
    st.subheader("My Submissions")
    if not st.session_state.user:
        st.info("Login to view your submissions.")
    else:
        subs = my_task_submissions(st.session_state.user["id"])
        if not subs:
            st.info("No submissions yet.")
        else:
            for sid, tid, code, title, status, when, points in subs:
                st.markdown(f"**[{code}] {title}** — Status: **{status}** · Points: **{points}** · Submitted: {when}")

with tab_review:
    st.subheader("Manager Review")
    if not st.session_state.user or st.session_state.user["role"] not in ["manager","admin"]:
        st.info("Managers/Admins only.")
    else:
        queue = review_queue()
        if not queue:
            st.info("No pending submissions.")
        else:
            for (sid, username, code, title, text, file_path, status, when) in queue:
                st.markdown(f"**Submission #{sid}** — {username} → [{code}] {title} · {status} · {when}")
                if text:
                    st.write(f"**Evidence**: {text}")
                if file_path and Path(file_path).exists():
                    st.download_button("Download attachment", data=Path(file_path).read_bytes(), file_name=Path(file_path).name)
                st.write("Review decision:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    comment = st.text_input(f"Comment #{sid}", key=f"c_{sid}")
                with col2:
                    award = st.number_input(f"Award Points #{sid}", min_value=0, max_value=1000, value=100, step=10, key=f"p_{sid}")
                with col3:
                    st.caption(" ")
                dcol1, dcol2, dcol3 = st.columns(3)
                with dcol1:
                    if st.button(f"Approve #{sid}"):
                        set_submission_status(sid, st.session_state.user["id"], "approved", comment, int(award))
                        st.success("Approved!")
                with dcol2:
                    if st.button(f"Reject #{sid}"):
                        set_submission_status(sid, st.session_state.user["id"], "rejected", comment, 0)
                        st.warning("Rejected!")
                with dcol3:
                    if st.button(f"Needs changes #{sid}"):
                        set_submission_status(sid, st.session_state.user["id"], "needs_changes", comment, 0)
                        st.info("Requested changes.")

with tab_task_points:
    st.subheader("My Task Points & Milestones")
    if not st.session_state.user:
        st.info("Login to view.")
    else:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(total_task_points,0) FROM task_points WHERE user_id=?", (st.session_state.user["id"],))
            row = cur.fetchone()
            pts = row[0] if row else 0
        st.metric("Total Task Points", pts)
        milestones = [(100, "Bronze Tasker"), (300, "Silver Tasker"), (600, "Gold Tasker"), (1000, "Platinum Tasker")]
        achieved = [name for threshold, name in milestones if pts >= threshold]
        if achieved:
            st.success("🎉 Milestones unlocked: " + ", ".join(achieved))
        else:
            st.info("Complete tasks to unlock milestones!")

if not Path(DB_PATH).exists():
    run_base_schema()
    run_task_schema()
    init_admin()
