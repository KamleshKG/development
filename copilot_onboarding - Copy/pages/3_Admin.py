import streamlit as st
from models.db_utils import get_all_users, set_user_role

user = st.session_state.get('user')
if not user or user['role'] != 'admin':
    st.warning("Admin access only.")
    st.stop()

st.title("Admin Panel")
users = get_all_users()
for uid, uname, role in users:
    st.write(f"{uname} ({role})")
    new_role = st.selectbox(f"Set role for {uname}", ['user', 'admin'], index=['user', 'admin'].index(role), key=uname)
    if st.button(f"Update {uname}", key=f"btn_{uname}"):
        set_user_role(uid, new_role)
        st.success(f"Role updated for {uname}")

