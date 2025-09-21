#!/usr/bin/env python3
# create_placeholders.py
import pandas as pd
from pathlib import Path
import os

EXCEL_PATH = "Knowledge_Index.xlsx"
FILES_DIR = "KnowledgeBase"
TEMPLATE = "# {title}\\n\\nSource: {source}\\n\\nSummary:\\n{summary}\\n\\nKeywords: {keywords}\\n"

def ensure_folder(category):
    p = Path(FILES_DIR) / category
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_md(category, title, source, summary, keywords):
    folder = ensure_folder(category)
    safe = "".join(c if c.isalnum() or c in " -_." else "_" for c in title)[:100]
    path = folder / f"{safe}.md"
    i = 1
    while path.exists():
        path = folder / f"{safe}_{i}.md"
        i += 1
    with open(path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(title=title, source=source, summary=summary, keywords=keywords))
    return path

def main():
    df = pd.read_excel(EXCEL_PATH, dtype=str).fillna("")
    for _, row in df.iterrows():
        title = row.get("Title","Untitled")
        category = row.get("Category","Misc")
        source = row.get("Source (PDF/Link)","")
        summary = row.get("Summary (3 bullets)","")
        keywords = row.get("Keywords","")
        p = write_md(category, title, source, summary, keywords)
        print("Wrote:", p)

if __name__=="__main__":
    main()
