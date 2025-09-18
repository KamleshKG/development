# RBAC Streamlit Gamified Portal — Plugin Packs

## Structure
- `app.py` — Streamlit app (RBAC, quizzes, tasks, review, reports)
- `schema.sql` — DB schema (SQLite by default; swap to Postgres later)
- `utils/` — rbac, store, loader modules
- `plugins/<plugin>/questions.json`, `plugins/<plugin>/tasks.json` — content packs
- `schemas/` — JSON Schemas (docs)
- `Dockerfile`

## Run
pip install streamlit pandas
cd portal_rbac
streamlit run app.py

Sidebar → Initialize DB → Admin login (`admin`/`admin123`) → Admin tab → Scan & Sync Plugins
