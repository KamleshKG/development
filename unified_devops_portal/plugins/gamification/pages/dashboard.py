import streamlit as st
from plugins.gamification.models.db_utils import GamificationDB

def render(user):
    st.title("🎯 Your Learning Dashboard")
    
    db = GamificationDB()
    progress = db.get_user_progress(user['id'])
    
    total_points = sum(points for _, _, _, points, achieved, _ in progress if achieved)
    st.metric("Total Points", total_points)
    
    # Display progress
    for mid, name, desc, points, achieved, achieved_at in progress:
        if achieved:
            st.success(f"🏆 {name} - {desc} (+{points} points)")
            st.caption(f"Completed on: {achieved_at}")
        else:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.info(f"🔒 {name} - {desc}")
            with col2:
                if st.button("Complete", key=f"complete_{mid}"):
                    db.set_milestone(user['id'], mid)
                    st.rerun()