import streamlit as st
from models.db_utils import get_user_progress, set_milestone

user = st.session_state.get('user')
if not user:
    st.warning("Please log in.")
    st.stop()

st.title("Your Milestones")

progress = get_user_progress(user['id'])
points = sum(1 for _, _, achieved in progress if achieved)
st.metric("Your Points", points)

# Find the first locked milestone
first_locked = None
for idx, (name, desc, achieved) in enumerate(progress):
    if not achieved and first_locked is None:
        first_locked = idx

# Use session state to track if a milestone was just completed
if 'milestone_just_completed' not in st.session_state:
    st.session_state['milestone_just_completed'] = False

for idx, (name, desc, achieved) in enumerate(progress):
    if achieved:
        st.success(f"🏅 {name} - {desc}")
    else:
        st.info(f"🔒 {name} - {desc}")
        if idx == first_locked:
            if st.button(f"Complete: {name}"):
                set_milestone(user['id'], idx + 1)
                st.session_state['milestone_just_completed'] = True
                st.session_state['just_completed_name'] = name
                st.rerun()

# Show celebration if milestone was just completed
if st.session_state.get('milestone_just_completed', False):
    st.balloons()
    st.success(f"Milestone '{st.session_state.get('just_completed_name', '')}' completed! 🎉")
    st.audio("assets/animations/success.mp3")
    st.info("Click the play button above to hear your celebration sound!")
    # Reset the flag so it only shows once
    st.session_state['milestone_just_completed'] = False