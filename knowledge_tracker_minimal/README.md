# Personal Knowledge Tracker (Open Source - Minimal)

Lightweight personal knowledge base using **SQLite + FTS5 + Streamlit + Tesseract OCR**.
Ideal for local, private, open-source setup. No server required.

## Features
- Bulk ingest PDFs and screenshots (OCR + PDF text extraction)
- Streamlit UI to upload single items, edit summaries/tags, and save
- Full-text search (FTS5) and simple filters
- Stores files on disk and metadata in SQLite
- MIT Licensed (open-source)

## Requirements
- Python 3.9+
- Tesseract OCR installed on your system (https://github.com/tesseract-ocr/tesseract)

Python dependencies (install with pip):
```bash
pip install -r requirements.txt
```

## Quick start
1. Unzip or clone the project.
2. Create a folder `KnowledgeBase/` and put subfolders `APIs, SystemDesign, Cloud_DevOps, CaseStudies, Misc` (optional).
3. Put your PDFs / screenshots in the folders.
4. Run bulk ingest (one-time or whenever you add many files):
   ```bash
   python ingest_bulk.py --base-folder KnowledgeBase --db knowledge.db
   ```
5. Run the Streamlit UI:
   ```bash
   streamlit run streamlit_app.py -- --db knowledge.db --files-dir KnowledgeBase
   ```

## Files
- `ingest_bulk.py` — batch ingestion script (PDF + image OCR)
- `streamlit_app.py` — Streamlit app for upload, edit, search
- `utils.py` — helper functions
- `requirements.txt` — Python packages
- `LICENSE` — MIT license
- `knowledge.db` — (created after first run)

## Notes
- Tesseract path: on many systems Tesseract is on PATH. If not, set `TESSERACT_CMD` env var or edit `utils.py`.
- For privacy, this runs fully locally. No cloud calls.

MIT Licensed — feel free to fork and adapt.
