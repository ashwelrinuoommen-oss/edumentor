"""
EduMentor Signup Page (Phase 1).
Delegates to the unified authentication system in login.py with signup mode.
"""

import streamlit as st
from edumentor.pages.login import render_login_page
from edumentor.orchestrator import EduMentorOrchestrator


def render_signup_page(orch: EduMentorOrchestrator):
    """
    Renders the sign up view for new students.
    """
    st.session_state["auth_mode"] = "signup"
    render_login_page(orch)
