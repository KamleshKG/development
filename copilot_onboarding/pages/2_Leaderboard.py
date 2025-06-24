import streamlit as st
from models.db_utils import get_leaderboard

user = st.session_state.get('user')
if not user or user['role'] != 'admin':
    st.warning("Leaderboard is visible to admin only.")
    st.stop()

st.title("All Users Progress (Admin Only)")
leaderboard = get_leaderboard()
st.table(
    [{"User": username, "Points": score if score else 0} for username, score in leaderboard]
)