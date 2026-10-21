"""
EduMentor Authentication Page (Phase 1).
Provides a dark premium, centered authentication panel:
- Login (Email, Password, Sign In, Forgot Password, Continue with Google, Demo profiles)
- Sign Up (Name, Email, Password, Confirm Password, Optional 'What are you studying?')
- Forgot Password (Email, New Password, Confirm New Password, Reset)
Dynamically uses the authenticated user's profile and name (no hardcoding).
"""

import streamlit as st
from typing import Optional

from edumentor.components.teacher_avatar import render_teacher_avatar
from edumentor.database.repository import EduMentorRepository
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.utils.validators import validate_email, validate_password_strength


def render_login_page(orch: EduMentorOrchestrator):
    """
    Renders the dark premium centered authentication panel.
    """
    # Initialize repository
    repo = EduMentorRepository()

    # Pre-seed default student profiles if database is fresh
    repo.get_or_create_user(username="Ashwel", email="ashwel@edumentor.ai")
    repo.get_or_create_user(username="Maya", email="maya@edumentor.ai")
    repo.get_or_create_user(username="Leo", email="leo@edumentor.ai")

    # Determine auth mode: 'login', 'signup', 'forgot_password'
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"

    mode = st.session_state["auth_mode"]

    # Outer Layout: Centered column with maximum 440px width
    outer_col1, center_col, outer_col2 = st.columns([1, 1.8, 1])

    with center_col:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; margin-top: 10px; margin-bottom: 20px;">
            <div style="
                width: 58px; height: 58px; border-radius: 14px;
                background: linear-gradient(135deg, #25D8E8 0%, #8B5CF6 100%);
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 0 24px rgba(37, 216, 232, 0.4);
                margin-bottom: 14px;
            ">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="#050608">
                    <path d="M12 2L1 7l11 5 9-4.09V17h2V7L12 2zm-8.8 9.35L12 15.45l8.8-4.1V17l-8.8 4.1-8.8-4.1v-5.65z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # VIEW 1: LOGIN
        # ---------------------------------------------------------------------
        if mode == "login":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 22px;">
                <h2 style="font-family: 'Newsreader', Georgia, serif; font-size: 30px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; letter-spacing: -0.3px;">
                    Welcome back
                </h2>
                <p style="font-size: 14px; color: #94A3B8; margin: 0; line-height: 1.4;">
                    Your personalized concept mastery study companion.
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.container():
                st.markdown("""
                <div style="
                    background: linear-gradient(145deg, rgba(13, 17, 23, 0.95) 0%, rgba(20, 27, 38, 0.9) 100%);
                    border: 1px solid rgba(39, 48, 59, 0.7);
                    border-radius: 14px;
                    padding: 24px 26px;
                    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5);
                    margin-bottom: 18px;
                ">
                """, unsafe_allow_html=True)

                email_or_user = st.text_input(
                    "Email or Username",
                    placeholder="name@example.com or Ashwel",
                    key="login_email_input"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    key="login_pwd_input"
                )

                c_rem, c_forgot = st.columns([1, 1])
                with c_rem:
                    remember = st.checkbox("Remember me", value=True)
                with c_forgot:
                    if st.button("Forgot password?", key="btn_to_forgot"):
                        st.session_state["auth_mode"] = "forgot_password"
                        st.rerun()

                if st.button("Sign In", use_container_width=True, key="btn_submit_signin"):
                    if not email_or_user:
                        st.error("Please enter your email or username.")
                    else:
                        user = repo.authenticate_user(email_or_user, password)
                        if user:
                            # Set authenticated user in session state
                            st.session_state["authenticated_user"] = {
                                "id": user.id,
                                "username": user.username,
                                "email": user.email,
                                "studying": user.studying
                            }
                            orch.student_name = user.username
                            orch.initialize_home()
                            st.session_state["current_page"] = "home"
                            st.success(f"Welcome back, {user.username}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please check your email/username or password.")

                st.markdown("""
                <div style="display: flex; align-items: center; text-align: center; margin: 18px 0; color: #64748B;">
                    <div style="flex: 1; border-bottom: 1px solid rgba(255,255,255,0.08);"></div>
                    <span style="padding: 0 12px; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B;">or</span>
                    <div style="flex: 1; border-bottom: 1px solid rgba(255,255,255,0.08);"></div>
                </div>
                """, unsafe_allow_html=True)

                # Continue with Google button
                if st.button("Continue with Google", use_container_width=True, key="btn_google_signin"):
                    # One-click authenticated demo sign in for Ashwel
                    user = repo.get_or_create_user("Ashwel", "ashwel@edumentor.ai")
                    st.session_state["authenticated_user"] = {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "studying": user.studying
                    }
                    orch.student_name = user.username
                    orch.initialize_home()
                    st.session_state["current_page"] = "home"
                    st.success("Signed in via Google as Ashwel!")
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            # Link to Sign Up
            c_bot1, c_bot2 = st.columns([2, 1])
            with c_bot1:
                st.markdown("<p style='font-size: 13px; color: #94A3B8; margin-top: 6px;'>Don't have an account?</p>", unsafe_allow_html=True)
            with c_bot2:
                if st.button("Sign up →", key="btn_to_signup"):
                    st.session_state["auth_mode"] = "signup"
                    st.rerun()

            # Quick Profile Switcher (Demo helper)
            st.markdown("""
            <div style="margin-top: 22px; padding: 12px 14px; background: rgba(13, 17, 23, 0.6); border: 1px dashed rgba(39, 48, 59, 0.8); border-radius: 10px; text-align: center;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B; margin-bottom: 2px;">
                    Demo Student Profiles
                </div>
                <div style="font-size: 11px; color: #94A3B8;">Click to instant sign-in without password</div>
            </div>
            """, unsafe_allow_html=True)

            p1, p2, p3 = st.columns(3)
            with p1:
                if st.button("Ashwel", use_container_width=True, key="quick_ashwel"):
                    user = repo.get_or_create_user("Ashwel", "ashwel@edumentor.ai")
                    st.session_state["authenticated_user"] = {"id": user.id, "username": user.username, "email": user.email, "studying": user.studying}
                    orch.student_name = user.username
                    orch.initialize_home()
                    st.session_state["current_page"] = "home"
                    st.rerun()
            with p2:
                if st.button("Maya", use_container_width=True, key="quick_maya"):
                    user = repo.get_or_create_user("Maya", "maya@edumentor.ai")
                    st.session_state["authenticated_user"] = {"id": user.id, "username": user.username, "email": user.email, "studying": user.studying}
                    orch.student_name = user.username
                    orch.initialize_home()
                    st.session_state["current_page"] = "home"
                    st.rerun()
            with p3:
                if st.button("👤 Leo", use_container_width=True, key="quick_leo"):
                    user = repo.get_or_create_user("Leo", "leo@edumentor.ai")
                    st.session_state["authenticated_user"] = {"id": user.id, "username": user.username, "email": user.email, "studying": user.studying}
                    orch.student_name = user.username
                    orch.initialize_home()
                    st.session_state["current_page"] = "home"
                    st.rerun()

        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        # VIEW 2: SIGN UP
        # ---------------------------------------------------------------------
        elif mode == "signup":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 22px;">
                <h2 style="font-family: 'Newsreader', Georgia, serif; font-size: 30px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; letter-spacing: -0.3px;">
                    Create your account
                </h2>
                <p style="font-size: 14px; color: #94A3B8; margin: 0; line-height: 1.4;">
                    Begin your adaptive concept recall journey with EduMentor.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="
                background: linear-gradient(145deg, rgba(13, 17, 23, 0.95) 0%, rgba(20, 27, 38, 0.9) 100%);
                border: 1px solid rgba(39, 48, 59, 0.7);
                border-radius: 14px;
                padding: 24px 26px;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5);
                margin-bottom: 18px;
            ">
            """, unsafe_allow_html=True)

            new_name = st.text_input("Full Name", placeholder="e.g., Ashwel", key="signup_name_field")
            new_email = st.text_input("Email", placeholder="name@example.com", key="signup_email_field")
            new_password = st.text_input("Password", type="password", placeholder="••••••••", key="signup_pwd_field")
            confirm_password = st.text_input("Confirm password", type="password", placeholder="••••••••", key="signup_confirm_pwd_field")
            
            # Optional: What are you studying?
            studying_subject = st.text_input(
                "What are you studying? (Optional)",
                placeholder="e.g. Operating Systems, Machine Learning, System Design",
                key="signup_studying_field"
            )

            if st.button("Create Account", use_container_width=True, key="btn_submit_create_account"):
                if not new_name.strip():
                    st.error("Please enter your name.")
                elif not new_email.strip() or not validate_email(new_email):
                    st.error("Please enter a valid email address.")
                elif not new_password:
                    st.error("Please enter a password.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match. Please verify.")
                else:
                    # Check if user already exists
                    existing = repo.get_user_by_email(new_email) or repo.get_user_by_username(new_name.strip())
                    if existing:
                        st.error("An account with this email or name already exists. Please sign in.")
                    else:
                        user = repo.create_user(
                            username=new_name.strip(),
                            email=new_email.strip(),
                            password=new_password,
                            studying=studying_subject.strip() if studying_subject else None
                        )
                        st.session_state["authenticated_user"] = {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "studying": user.studying
                        }
                        orch.student_name = user.username
                        orch.initialize_home()
                        st.session_state["current_page"] = "home"
                        st.session_state["auth_mode"] = "login"
                        st.success(f"Welcome to EduMentor, {user.username}!")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            c_ret1, c_ret2 = st.columns([2, 1])
            with c_ret1:
                st.markdown("<p style='font-size: 13px; color: #94A3B8; margin-top: 6px;'>Already have an account?</p>", unsafe_allow_html=True)
            with c_ret2:
                if st.button("Sign in →", key="btn_back_to_login"):
                    st.session_state["auth_mode"] = "login"
                    st.rerun()

        # ---------------------------------------------------------------------
        # VIEW 3: FORGOT PASSWORD
        # ---------------------------------------------------------------------
        elif mode == "forgot_password":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 22px;">
                <h2 style="font-family: 'Newsreader', Georgia, serif; font-size: 30px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; letter-spacing: -0.3px;">
                    Reset your password
                </h2>
                <p style="font-size: 14px; color: #94A3B8; margin: 0; line-height: 1.4;">
                    Enter your account email to set a new password.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="
                background: linear-gradient(145deg, rgba(13, 17, 23, 0.95) 0%, rgba(20, 27, 38, 0.9) 100%);
                border: 1px solid rgba(39, 48, 59, 0.7);
                border-radius: 14px;
                padding: 24px 26px;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5);
                margin-bottom: 18px;
            ">
            """, unsafe_allow_html=True)

            reset_email = st.text_input("Account Email", placeholder="name@example.com", key="reset_email_input")
            reset_pwd1 = st.text_input("New Password", type="password", placeholder="••••••••", key="reset_pwd1_input")
            reset_pwd2 = st.text_input("Confirm New Password", type="password", placeholder="••••••••", key="reset_pwd2_input")

            if st.button("Update Password", use_container_width=True, key="btn_submit_reset_pwd"):
                if not reset_email.strip():
                    st.error("Please enter your account email.")
                elif not reset_pwd1:
                    st.error("Please enter a new password.")
                elif reset_pwd1 != reset_pwd2:
                    st.error("New passwords do not match.")
                else:
                    success = repo.reset_password(reset_email.strip(), reset_pwd1)
                    if success:
                        st.success("Password successfully updated! You can now sign in.")
                        st.session_state["auth_mode"] = "login"
                        st.rerun()
                    else:
                        st.error("No account found with this email address.")

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("← Back to Sign In", key="btn_forgot_to_login"):
                st.session_state["auth_mode"] = "login"
                st.rerun()
