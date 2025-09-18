
import sqlite3, hashlib
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = "portal.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def run_schema(schema_path: str = "schema.sql"):
    sql = Path(schema_path).read_text()
    with get_conn() as conn:
        conn.executescript(sql)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def init_admin():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1;")
        if not c.fetchone():
            c.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)",
                      ("admin", hash_pw("admin123"), "admin"))
            conn.commit()

def upsert_plugin(code: str, title: Optional[str] = None) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM plugins WHERE code=?", (code,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO plugins (code, title, is_enabled) VALUES (?,?,1)", (code, title or code))
        conn.commit()
        return cur.lastrowid

def upsert_question(plugin_id: int, q: Dict[str, Any]) -> None:
    options = q.get("options", [])
    opts = options + [""] * (5 - len(options))
    correct_labels = []
    for idx in q.get("correct_options", []):
        correct_labels.append(f"option_{idx}")
    correct_options = ",".join(correct_labels)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO questions (plugin_id, question_id, level, question, option_1, option_2, option_3, option_4, option_5, correct_options, is_multi_select, hint, rationale, tags) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(plugin_id, question_id) DO UPDATE SET "
            "level=excluded.level, question=excluded.question, option_1=excluded.option_1, option_2=excluded.option_2, option_3=excluded.option_3, option_4=excluded.option_4, option_5=excluded.option_5, "
            "correct_options=excluded.correct_options, is_multi_select=excluded.is_multi_select, hint=excluded.hint, rationale=excluded.rationale, tags=excluded.tags",
            (plugin_id, q["question_id"], q["level"], q["question"],
             opts[0], opts[1], opts[2], opts[3], opts[4],
             correct_options, 1 if q.get("is_multi_select") else 0,
             q.get("hint",""), q.get("rationale",""), ",".join(q.get("tags",[])))
        )
        conn.commit()

def upsert_task(plugin_id: int, t: Dict[str, Any], created_by: Optional[int] = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO tasks (plugin_id, code, title, description, level, points, require_attachment, created_by) "
            "VALUES (?,?,?,?,?,?,?,?) "
            "ON CONFLICT(plugin_id, code) DO UPDATE SET "
            "title=excluded.title, description=excluded.description, level=excluded.level, points=excluded.points, require_attachment=excluded.require_attachment",
            (plugin_id, t["code"], t["title"], t["description"], t["level"],
             int(t.get("points",50)), 1 if t.get("require_attachment", True) else 0, created_by)
        )
        conn.commit()
