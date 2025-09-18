# Streamlit Gaming Portal — Tasks + Dashboard

## Run locally
pip install streamlit pandas matplotlib
streamlit run streamlit_gamified_portal_tasks.py
# In another terminal:
streamlit run streamlit_leadership_dashboard.py

## Docker
docker build -t gamified-portal:latest .
docker run -p 8501:8501 -v $PWD:/app gamified-portal:latest

## Files
- streamlit_gamified_portal_tasks.py — main app (quizzes + tasks + approvals)
- streamlit_leadership_dashboard.py — leadership/manager dashboard
- schema.sql + schema_tasks.sql — DB schemas
- questions_template.csv + tasks_template.csv — import templates
