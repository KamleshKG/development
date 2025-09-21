#!/usr/bin/env python3
# excel_to_sqlite.py
import pandas as pd
import sqlite3
import os
import hashlib
from pathlib import Path
from utils import init_db

DB_PATH = "knowledge.db"          # path to SQLite DB used by the app
EXCEL_PATH = "Knowledge_Index.xlsx"  # your excel file (update if different)
FILES_DIR = "KnowledgeBase"       # folder where project stores files
PLACEHOLDER_TEMPLATE = "# {title}\\n\\nSource: {source}\\n\\nSummary:\\n{summary}\\n\\nKeywords: {keywords}\\n"

def row_hash_for_empty_content(row):
    # produce stable hash for rows without extracted content
    s = f"{row.get('Title','')}\n{row.get('Source (PDF/Link)','')}\n{row.get('Summary (3 bullets)','')}"
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def ensure_folder(category):
    p = Path(FILES_DIR) / category
    p.mkdir(parents=True, exist_ok=True)
    return p

def insert_if_not_exists(conn, title, summary, content, keywords, category, filepath, source):
    cur = conn.cursor()
    if content:
        h = hashlib.sha256(content.encode('utf-8')).hexdigest()
    else:
        h = row_hash_for_empty_content({"Title": title, "Source (PDF/Link)": source, "Summary (3 bullets)": summary})
    cur.execute("SELECT id FROM docs WHERE hash = ?", (h,))
    if cur.fetchone():
        return False
    cur.execute(
        "INSERT INTO docs (title, summary, content, keywords, category, filepath, source, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (title, summary, content, keywords, category, filepath, source, h)
    )
    rowid = cur.lastrowid
    cur.execute("INSERT INTO docs_fts(rowid, title, summary, content, keywords, filepath) VALUES (?, ?, ?, ?, ?, ?)",
                (rowid, title, summary or "", content or "", keywords or "", filepath or ""))
    conn.commit()
    return True

def make_placeholder_file(category, title, source, summary, keywords):
    folder = ensure_folder(category)
    safe_name = "".join(c if c.isalnum() or c in " -_." else "_" for c in title)[:100]
    fname = f"{safe_name}.md"
    path = folder / fname
    if path.exists():
        # append a counter if there is a clash
        i = 1
        while (folder / f"{safe_name}_{i}.md").exists():
            i += 1
        path = folder / f"{safe_name}_{i}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(PLACEHOLDER_TEMPLATE.format(title=title, source=source, summary=summary or "", keywords=keywords or ""))
    return str(path)

def main():
    if not Path(EXCEL_PATH).exists():
        print(f"Excel file not found at {EXCEL_PATH}. Put your Knowledge_Index.xlsx in the project root.")
        return
    df = pd.read_excel(EXCEL_PATH, dtype=str).fillna("")
    conn = init_db(DB_PATH)

    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        title = row.get("Title","").strip() or "Untitled"
        category = row.get("Category","Misc").strip() or "Misc"
        source = row.get("Source (PDF/Link)","").strip()
        summary = row.get("Summary (3 bullets)","").strip()
        keywords = row.get("Keywords","").strip()
        # If source is a local file path and exists, set filepath to it; else if it's a URL create placeholder md
        filepath = ""
        if source:
            if source.lower().startswith("http://") or source.lower().startswith("https://"):
                filepath = make_placeholder_file(category, title, source, summary, keywords)
            else:
                # treat as local path relative to project root or absolute
                p = Path(source)
                if not p.is_absolute():
                    p = Path(FILES_DIR) / source
                if p.exists():
                    filepath = str(p.resolve())
                else:
                    # create placeholder note containing the link/original source text
                    filepath = make_placeholder_file(category, title, source, summary, keywords)
        else:
            filepath = make_placeholder_file(category, title, source, summary, keywords)

        # content is empty at import; actual extracted text will be filled if you run ingest_bulk or upload via Streamlit
        content = ""
        ok = insert_if_not_exists(conn, title, summary, content, keywords, category, filepath, source)
        if ok:
            inserted += 1
        else:
            skipped += 1

    print(f"Inserted {inserted} rows, skipped {skipped} (duplicates).")

if __name__ == "__main__":
    main()
