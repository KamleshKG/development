# sync_excel_to_db.py
import pandas as pd
import sqlite3
from pathlib import Path

EXCEL_FILE = "Knowledge_Index.xlsx"
DB_FILE = "knowledge.db"
TABLE_NAME = "Knowledge"

# ---------------- Check Excel ----------------
excel_path = Path(EXCEL_FILE)
if not excel_path.exists():
    print(f"Error: {EXCEL_FILE} not found!")
    exit()

# ---------------- Read Excel ----------------
df = pd.read_excel(EXCEL_FILE).fillna("")

# Map Excel columns to DB schema
df = df.rename(columns={
    "Category": "category",
    "Company/Org": "company_org",
    "Title": "title",
    "Description": "description",
    "Link": "link",
    "Summary": "summary",
    "Notes": "notes",
    "Keywords": "keywords"
})

# Add missing columns
df["filepath"] = ""  # Excel entries have no local file
df["status"] = "Pending"  # Default status for self-study
if 'id' not in df.columns:
    df['id'] = None  # SQLite auto-generates primary key

# ---------------- Connect to SQLite ----------------
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ---------------- Create Knowledge Table ----------------
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY,
    category TEXT,
    company_org TEXT,
    title TEXT,
    description TEXT,
    link TEXT,
    summary TEXT,
    notes TEXT,
    keywords TEXT,
    filepath TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

# ---------------- Create FTS5 Table ----------------
cursor.execute(f"""
CREATE VIRTUAL TABLE IF NOT EXISTS Knowledge_fts USING fts5(
    title, summary, notes, keywords, description,
    content='{TABLE_NAME}', content_rowid='id'
)
""")

# ---------------- Insert / Overwrite ----------------
# Use 'replace' to refresh entire table while preserving id column
df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

conn.commit()
conn.close()
print(f"Sync complete! {len(df)} rows added to '{TABLE_NAME}' with FTS indexing.")
