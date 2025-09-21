# sync_excel_to_db.py
import pandas as pd
import sqlite3

EXCEL_FILE = "Knowledge_Index.xlsx"
DB_FILE = "knowledge.db"
TABLE_NAME = "Knowledge"

# Read Excel
df = pd.read_excel(EXCEL_FILE).fillna("")

# Map Excel columns to DB columns
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
df["filepath"] = ""  # Excel entries have no local file

# Connect to DB
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create table if not exists
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
    filepath TEXT
)
""")

# Create FTS table
cursor.execute("""
CREATE VIRTUAL TABLE IF NOT EXISTS Knowledge_fts USING fts5(
    title, summary, notes, keywords, description, content='Knowledge', content_rowid='id'
)
""")

# Insert / overwrite
df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

# Populate FTS
cursor.execute("INSERT INTO Knowledge_fts(Knowledge_fts) VALUES('rebuild')")
conn.commit()
conn.close()
print(f"Excel synced: {len(df)} entries added to {TABLE_NAME}")
