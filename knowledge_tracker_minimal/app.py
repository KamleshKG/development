# app.py - Knowledge Tracker with Sample Case Studies
import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image
import tempfile
from pathlib import Path

DB_FILE = "knowledge.db"
FILES_DIR = "KnowledgeBase"

# ------------------- DB Helper Functions -------------------

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Knowledge (
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
    conn.commit()
    conn.close()

def insert_doc(category, company_org, title, description, link, summary, notes, keywords, filepath):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Knowledge(category, company_org, title, description, link, summary, notes, keywords, filepath)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (category, company_org, title, description, link, summary, notes, keywords, filepath))
    conn.commit()
    conn.close()

def update_status(entry_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Knowledge SET status=? WHERE id=?", (status, entry_id))
    conn.commit()
    conn.close()

# ------------------- Sample Case Studies -------------------

def add_sample_case_studies():
    conn = get_conn()
    cur = conn.cursor()
    # Check if any Case Studies exist
    cur.execute("SELECT COUNT(*) FROM Knowledge WHERE LOWER(REPLACE(category,' ','_')) IN ('casestudies','cloud_devops')")
    count = cur.fetchone()[0]
    if count == 0:
        # Add 3 sample entries
        sample_entries = [
            ("CaseStudies", "Etsy", "Etsy Continuous Delivery", "Accelerating Deployments", "https://etsy.com",
             "Weekly releases → 50+ deploys/day", "Pipeline automation, cultural shift", "CI/CD, Etsy, deployment automation", ""),
            ("CaseStudies", "Netflix", "Simian Army & Chaos Engineering", "Resilience Testing", "https://netflixtechblog.com",
             "Chaos testing embedded in CI/CD", "Failure injection, automated recovery", "Netflix, CI/CD, chaos engineering", ""),
            ("Cloud_DevOps", "Amazon", "Two-Pizza Teams & Deployment Autonomy", "End-to-end pipeline ownership", "https://aws.amazon.com",
             "Small teams own build/deploy pipelines", "Microservices, team autonomy", "Amazon, DevOps, microservices", "")
        ]
        for entry in sample_entries:
            cur.execute("""
                INSERT INTO Knowledge(category, company_org, title, description, link, summary, notes, keywords, filepath)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, entry)
        conn.commit()
    conn.close()

# ------------------- File Processing -------------------

def save_uploaded_file(uploaded_file, category):
    dest_dir = os.path.join(FILES_DIR, category)
    os.makedirs(dest_dir, exist_ok=True)
    tmp_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name
    dest_path = os.path.join(dest_dir, uploaded_file.name)
    os.replace(tmp_path, dest_path)
    return dest_path

# ------------------- Streamlit App -------------------

def main():
    init_db()
    add_sample_case_studies()   # <-- Add sample test cases
    st.set_page_config(page_title='Knowledge Tracker', layout='wide')
    st.title("One-Stop Knowledge Tracker")

    tab1, tab2, tab3, tab4 = st.tabs(["Add / Upload", "Case Studies", "All Knowledge", "Dashboard / Self-Study"])

    # ---------------- Add / Upload ----------------
    with tab1:
        st.header("Add / Upload Knowledge")
        st.markdown("""
            Upload PDF or Image files or manually add knowledge entries.
            Fill out Title, Category, Summary, Notes, Keywords, Link, and Organization.
            Once saved, the entries will appear in Case Studies and All Knowledge tabs.
        """)
        uploaded = st.file_uploader("Upload PDF or Image", type=['pdf','png','jpg','jpeg'])
        title = st.text_input("Title")
        category = st.selectbox("Category", ["APIs","SystemDesign","Cloud_DevOps","CaseStudies","Misc"])
        summary = st.text_area("Summary (2-3 bullets)")
        notes = st.text_area("Notes / Description")
        keywords = st.text_input("Keywords (comma separated)")
        link = st.text_input("Link / Source URL")
        company_org = st.text_input("Company / Organization (Optional)")

        if st.button("Save Entry"):
            filepath = ""
            if uploaded:
                filepath = save_uploaded_file(uploaded, category)
            if not title:
                st.error("Title is required!")
            else:
                insert_doc(category, company_org, title, notes, link, summary, notes, keywords, filepath)
                st.success("Entry saved successfully!")

    # ---------------- Case Studies ----------------
    with tab2:
        st.header("Case Studies")
        st.markdown("Browse all uploaded case studies (Category: CaseStudies / Cloud_DevOps).")
        conn = get_conn()
        df = pd.read_sql("""
            SELECT * FROM Knowledge
            WHERE LOWER(REPLACE(category,' ','_')) IN ('casestudies','cloud_devops')
            ORDER BY id DESC
        """, conn)
        conn.close()
        if df.empty:
            st.info("No Case Studies found.")
        else:
            for idx, row in df.iterrows():
                st.subheader(row['title'])
                if row['company_org']:
                    st.write("Organization:", row['company_org'])
                st.write("Summary:", row['summary'])
                st.write("Notes:", row['notes'])
                st.write("Keywords:", row['keywords'])
                if row['link']:
                    st.markdown(f"[Source]({row['link']})")
                if row['filepath'] and Path(row['filepath']).exists():
                    if row['filepath'].lower().endswith('.pdf'):
                        st.write("PDF File:", row['filepath'])
                    else:
                        try:
                            img = Image.open(row['filepath'])
                            st.image(img, use_column_width=True)
                        except:
                            st.write("Preview not available.")
                row_id = row['id'] if row['id'] is not None else f"noid_{idx}"
                if st.button(f"Mark as Reviewed {row_id}", key=f"case_{row_id}"):
                    if row['id'] is not None:
                        update_status(row['id'], "Reviewed")
                        st.experimental_rerun()

    # ---------------- All Knowledge ----------------
    with tab3:
        st.header("All Knowledge Entries")
        st.markdown("Browse all knowledge entries across all categories.")
        conn = get_conn()
        df_all = pd.read_sql("SELECT * FROM Knowledge ORDER BY id DESC", conn)
        conn.close()
        if df_all.empty:
            st.info("No entries found.")
        else:
            for idx, row in df_all.iterrows():
                st.subheader(row['title'])
                st.write("Category:", row['category'])
                if row['company_org']:
                    st.write("Organization:", row['company_org'])
                st.write("Summary:", row['summary'])
                st.write("Notes:", row['notes'])
                st.write("Keywords:", row['keywords'])
                st.write("Status:", row['status'])
                if row['link']:
                    st.markdown(f"[Source]({row['link']})")
                if row['filepath'] and Path(row['filepath']).exists():
                    if row['filepath'].lower().endswith('.pdf'):
                        st.write("PDF File:", row['filepath'])
                    else:
                        try:
                            img = Image.open(row['filepath'])
                            st.image(img, use_column_width=True)
                        except:
                            st.write("Preview not available.")
                row_id = row['id'] if row['id'] is not None else f"noid_{idx}"
                if st.button(f"Mark as Reviewed {row_id}", key=f"all_{row_id}"):
                    if row['id'] is not None:
                        update_status(row['id'], "Reviewed")
                        st.experimental_rerun()

    # ---------------- Dashboard / Self-Study ----------------
    with tab4:
        st.header("Dashboard / Self-Study Progress")
        st.markdown("Visual summary of your knowledge tracker progress and entries.")
        if df_all.empty:
            st.info("No entries yet. Add or upload knowledge first.")
        else:
            st.subheader("Entries Count by Category")
            st.bar_chart(df_all['category'].value_counts())

            st.subheader("Self-Study Progress (Pending vs Reviewed)")
            st.bar_chart(df_all['status'].value_counts())

            st.subheader("Entries by Company / Organization")
            st.table(df_all['company_org'].value_counts())

            st.subheader("Quick Self-Study Marking")
            for idx, row in df_all.iterrows():
                row_id = row['id'] if row['id'] is not None else f"noid_{idx}"
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(row['title'], "-", row['category'])
                with col2:
                    if st.button(f"Mark as Reviewed {row_id}", key=f"dash_{row_id}"):
                        if row['id'] is not None:
                            update_status(row['id'], "Reviewed")
                            st.experimental_rerun()

if __name__ == "__main__":
    main()
