"""
Chat Message UI Component.
"""

import streamlit as st


def render_chat_bubble(role: str, content: str, student_initial: str = "A"):
    """Render formatted chat message bubble with friendly female teacher persona."""
    avatar = "👩‍🏫" if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)
