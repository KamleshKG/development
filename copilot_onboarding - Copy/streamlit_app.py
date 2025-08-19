import streamlit as st
from models.db_utils import get_user, get_user_progress

st.set_page_config(page_title="Copilot Onboarding Game", layout="wide")

if 'user' not in st.session_state:
    st.session_state['user'] = None

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = get_user(username, password)
        if user:
            st.session_state['user'] = {'id': user[0], 'username': user[1], 'role': user[2]}
            st.success(f"Welcome, {user[1]}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state['user']:
    login()
else:
    # Sidebar: user info and logout
    st.sidebar.markdown(f"**Logged in as:** {st.session_state['user']['username']} ({st.session_state['user']['role']})")
    if st.sidebar.button("Logout"):
        st.session_state['user'] = None
        st.rerun()

    # Main content: welcome, animation, avatar
    st.title(f"Welcome, {st.session_state['user']['username']}! 🎉")
    st.balloons()
    # Show avatar (use a default if not present)
    avatar_path = f"assets/avatars/{st.session_state['user']['username'].lower()}.png"
    try:
        st.image(avatar_path, width=120)
    except Exception:
        st.image("assets/avatars/default.png", width=120)

    # --- Enhanced Progress Bar and Dynamic Message ---
    progress = get_user_progress(st.session_state['user']['id'])
    total = len(progress)
    completed = sum(1 for _, _, achieved in progress if achieved)
    percent = int((completed / total) * 100) if total else 0
    steps_left = total - completed

    st.progress(percent, text=f"Progress: {completed}/{total} milestones completed")

    if steps_left == 0:
        st.success("Congratulations! You have completed all milestones! 🏆")
    elif steps_left == 1:
        st.info("You're just 1 step away from your goal! 🚀")
    else:
        st.info(f"Only {steps_left} steps away from your goal!")

    st.write("Get started by selecting **Dashboard** or **Leaderboard** from the sidebar.")