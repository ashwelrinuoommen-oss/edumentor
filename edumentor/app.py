"""
EduMentor — Adaptive Concept Recall Mastery
Target Streamlit Application Entrypoint.
"Your notes. Your recall. Your mastery."
Phase 2 Main Workspace & Floating Navigation.
"""

import sys
import os
import streamlit as st

# Ensure repository root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.pages.home import render_home_page
from edumentor.pages.history import render_history_page
from edumentor.pages.progress import render_progress_page
from edumentor.pages.settings import render_settings_page
from edumentor.pages.login import render_login_page
from edumentor.pages.signup import render_signup_page

# Set page configuration with dark theme and wide canvas
st.set_page_config(
    page_title="EduMentor — AI Study Companion Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS INJECTION (PHASE 27 MAIN INTERFACE VISUAL DESIGN)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Hide Default Streamlit Chrome */
#MainMenu, header, footer, .stDeployButton, div[data-testid="stDecoration"] {
  display: none !important;
  visibility: hidden !important;
}

/* Base Canvas: Dark Cinematic Space */
.stApp {
  background-color: #050608 !important;
  color: #F5F7FA !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
  background-image: 
    radial-gradient(circle at 50% 8%, rgba(37, 216, 232, 0.09) 0%, transparent 42%),
    radial-gradient(circle at 85% 82%, rgba(139, 92, 246, 0.06) 0%, transparent 38%) !important;
  background-attachment: fixed !important;
}

/* Main Container Constraint */
.block-container {
  max-width: 1020px !important;
  padding-top: 1.2rem !important;
  padding-bottom: 5rem !important;
}

/* Headings Typography */
h1, h2, h3, .editorial-heading {
  font-family: 'Newsreader', Georgia, serif !important;
  color: #F5F7FA !important;
  font-weight: 600 !important;
  letter-spacing: -0.015em !important;
}

h4, h5, h6 {
  font-family: 'Inter', sans-serif !important;
  color: #F5F7FA !important;
  font-weight: 600 !important;
}

p, span, label, div {
  color: #F5F7FA;
}

/* Floating / Anchored Navbar Container: Dark Translucent Surface */
.floating-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 58px;
  background: rgba(13, 17, 23, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid #27303B;
  border-radius: 14px;
  padding: 0 20px;
  margin-bottom: 22px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-glyph {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(135deg, #25D8E8 0%, #8B5CF6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 14px rgba(37, 216, 232, 0.4);
}

.brand-title {
  font-family: 'Newsreader', Georgia, serif;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: linear-gradient(180deg, #FFFFFF 0%, #CCD6E0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}

/* Streamlit Buttons: Vibrant Cyan/Violet Gradient Primary */
.stButton > button,
button[kind="primary"],
button[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg, #25D8E8 0%, #8B5CF6 100%) !important;
  color: #050608 !important;
  font-weight: 700 !important;
  font-size: 13.5px !important;
  border-radius: 10px !important;
  border: none !important;
  padding: 8px 18px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 14px rgba(37, 216, 232, 0.25) !important;
}

.stButton > button:hover,
button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(37, 216, 232, 0.45) !important;
}

.stButton > button:active {
  transform: translateY(0.5px) !important;
}

/* Secondary Button Modifier */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
  background: rgba(13, 17, 23, 0.85) !important;
  color: #9AA4B2 !important;
  font-weight: 500 !important;
  border: 1px solid #27303B !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover,
button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
  background: rgba(22, 27, 34, 0.95) !important;
  color: #F5F7FA !important;
  border-color: #25D8E8 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(37, 216, 232, 0.2) !important;
}

/* Streamlit Chat Message & Input Overrides */
div[data-testid="stChatMessage"] {
  background-color: transparent !important;
  padding: 0.5rem 0 !important;
}

div[data-testid="stChatMessageContent"] {
  background: #0D1117 !important;
  border: 1px solid #27303B !important;
  border-radius: 12px !important;
  padding: 14px 18px !important;
  font-size: 14.5px !important;
  color: #F5F7FA !important;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="stChatInput"] {
  border-radius: 12px !important;
  background-color: #0D1117 !important;
  border: 1px solid #27303B !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
}

div[data-testid="stChatInput"]:focus-within {
  border-color: #25D8E8 !important;
  box-shadow: 0 0 0 2px rgba(37, 216, 232, 0.2) !important;
}

div[data-testid="stChatInput"] textarea {
  color: #F5F7FA !important;
  font-family: inherit !important;
  font-size: 14.5px !important;
}

/* Streamlit Inputs Overrides */
input[type="text"], input[type="password"], textarea, .stTextInput > div > div > input {
  background-color: #0D1117 !important;
  color: #F5F7FA !important;
  border: 1px solid #27303B !important;
  border-radius: 8px !important;
}

input:focus, textarea:focus {
  border-color: #25D8E8 !important;
  box-shadow: 0 0 0 2px rgba(37, 216, 232, 0.2) !important;
}

/* Streamlit Expanders, Popovers, and Tabs */
div[data-testid="stExpander"] {
  background-color: #0D1117 !important;
  border: 1px solid #27303B !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
}

div[data-testid="stPopoverBody"] {
  background-color: #0D1117 !important;
  color: #F5F7FA !important;
  border: 1px solid #27303B !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45) !important;
}

button[data-baseweb="tab"] {
  color: #9AA4B2 !important;
  font-weight: 500 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
  color: #25D8E8 !important;
  font-weight: 700 !important;
  border-bottom-color: #25D8E8 !important;
}

/* Metrics Overrides */
div[data-testid="stMetric"] {
  background: #0D1117 !important;
  border: 1px solid #27303B !important;
  border-radius: 10px !important;
  padding: 12px 16px !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
}

div[data-testid="stMetricLabel"] {
  color: #9AA4B2 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
}

div[data-testid="stMetricValue"] {
  color: #25D8E8 !important;
  font-family: 'Newsreader', Georgia, serif !important;
  font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


def main():
    # Initialize Orchestrator in session state
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = EduMentorOrchestrator(student_name="Ashwel")
        st.session_state.orchestrator.initialize_home()

    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    orch: EduMentorOrchestrator = st.session_state.orchestrator

    # Auto-sync LLM config from .env if provider was demo or unconfigured
    if hasattr(orch, "llm_config") and (orch.llm_config.provider == "demo" or not orch.llm_config.api_key):
        from edumentor.llm import get_default_config
        fresh_cfg = get_default_config()
        if fresh_cfg.provider != "demo" and fresh_cfg.api_key:
            orch.llm_config = fresh_cfg

    # Check authentication state (Phase 1)
    authenticated_user = st.session_state.get("authenticated_user")

    # -------------------------------------------------------------------------
    # CASE 1: NOT AUTHENTICATED -> RENDER PROFESSIONAL AUTHENTICATION EXPERIENCE
    # -------------------------------------------------------------------------
    if not authenticated_user:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin: 15px 0 20px 0;">
            <div class="brand-glyph" style="background: linear-gradient(135deg, #25D8E8 0%, #8B5CF6 100%); width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 14px rgba(37, 216, 232, 0.4);">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="#050608">
                <path d="M12 2L1 7l11 5 9-4.09V17h2V7L12 2zm-8.8 9.35L12 15.45l8.8-4.1V17l-8.8 4.1-8.8-4.1v-5.65z"/>
              </svg>
            </div>
            <div class="brand-title" style="font-family: 'Newsreader', Georgia, serif; font-size: 21px; font-weight: 700; letter-spacing: 0.03em; color: #F5F7FA;">EDUMENTOR</div>
        </div>
        """, unsafe_allow_html=True)

        render_login_page(orch)
        return

    # -------------------------------------------------------------------------
    # CASE 2: AUTHENTICATED -> RENDER MAIN EDU MENTOR WORKSPACE (PHASE 2)
    # -------------------------------------------------------------------------
    student_name = authenticated_user.get("username", "Ashwel")
    if orch.student_name != student_name:
        orch.student_name = student_name
        orch.initialize_home()

    # Small Floating Navigation Bar:
    # 52–60px high, rounded, translucent, bordered, and subtle
    # EDUMENTOR | Home History Progress Settings | Ashwel ▾
    nav_col1, nav_col2, nav_col3 = st.columns([2.4, 3.8, 2.2])

    with nav_col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; height: 48px;">
            <div class="brand-glyph" style="background: linear-gradient(135deg, #25D8E8 0%, #8B5CF6 100%); width: 32px; height: 32px; border-radius: 9px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 14px rgba(37, 216, 232, 0.4);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="#050608">
                <path d="M12 2L1 7l11 5 9-4.09V17h2V7L12 2zm-8.8 9.35L12 15.45l8.8-4.1V17l-8.8 4.1-8.8-4.1v-5.65z"/>
              </svg>
            </div>
            <div>
              <div class="brand-title" style="font-family: 'Newsreader', Georgia, serif; font-size: 19px; font-weight: 700; letter-spacing: 0.03em; color: #F5F7FA; line-height: 1;">EDUMENTOR</div>
              <div style="font-size: 10px; font-weight: 600; color: #25D8E8; letter-spacing: 0.06em; text-transform: uppercase;">Concept Mastery</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with nav_col2:
        # Centered Navigation Links: Home | History | Progress | Settings
        tab1, tab2, tab3, tab4 = st.columns(4)
        active_page = st.session_state.current_page

        with tab1:
            t1 = "primary" if active_page == "home" else "secondary"
            if st.button("Home", key="nav_home", type=t1, use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with tab2:
            t2 = "primary" if active_page == "history" else "secondary"
            if st.button("History", key="nav_history", type=t2, use_container_width=True):
                st.session_state.current_page = "history"
                st.rerun()
        with tab3:
            t3 = "primary" if active_page == "progress" else "secondary"
            if st.button("Progress", key="nav_progress", type=t3, use_container_width=True):
                st.session_state.current_page = "progress"
                st.rerun()
        with tab4:
            t4 = "primary" if active_page == "settings" else "secondary"
            if st.button("Settings", key="nav_settings", type=t4, use_container_width=True):
                st.session_state.current_page = "settings"
                st.rerun()

    with nav_col3:
        # Right Side: User Profile with "Ashwel ▾"
        with st.popover(f"{student_name} ▾", use_container_width=True):
            st.markdown(f"**Signed in as:** `{student_name}`")
            if authenticated_user.get("email"):
                st.caption(authenticated_user.get("email"))
            if authenticated_user.get("studying"):
                st.markdown(f"**Focus:** {authenticated_user.get('studying')}")
            st.markdown("---")
            if st.button("Sign Out", key="popover_sign_out", use_container_width=True):
                st.session_state["authenticated_user"] = None
                st.session_state["current_page"] = "home"
                st.session_state["auth_mode"] = "login"
                st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Page Dispatcher
    page = st.session_state.current_page
    if page == "home":
        render_home_page(orch)
    elif page == "history":
        render_history_page(orch)
    elif page == "progress":
        render_progress_page(orch)
    elif page == "settings":
        render_settings_page(orch)
    elif page == "login":
        render_login_page(orch)
    elif page == "signup":
        render_signup_page(orch)
    else:
        render_home_page(orch)


if __name__ == "__main__":
    main()
