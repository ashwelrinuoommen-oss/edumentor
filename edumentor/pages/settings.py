"""
EduMentor Settings Page.
Configure LLM providers, API keys, SM-2 algorithms, and semantic evaluation thresholds.
"""

import os
import streamlit as st
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.llm import LLMConfig, test_llm_connection
from edumentor.components.notification import render_banner
from edumentor.components.teacher_avatar import (
    render_teacher_avatar,
    get_available_avatar_states,
    get_avatar_state_config
)


def render_settings_page(orch: EduMentorOrchestrator):
    """
    Renders the settings and configuration page.
    """
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 700; color: #FFFFFF;">
            System Settings & Providers
        </div>
        <div style="font-size: 14px; color: #94A3B8; margin-top: 4px;">
            Configure AI provider abstraction (Claude / GPT / Gemini / Ollama / Demo), API keys, and SM-2 scheduling parameters
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_llm, tab_sm2, tab_avatar, tab_data = st.tabs([
        "⚡ LLM Provider",
        "🧠 Spaced Repetition (SM-2)",
        "👩‍🏫 AI Teacher Persona",
        "💾 Storage & Data"
    ])

    # --- TAB 1: LLM PROVIDER ---
    with tab_llm:
        st.markdown("<h4 style='color: #F8FAFC;'>AI Model Configuration</h4>", unsafe_allow_html=True)
        st.caption("EduMentor uses a multi-provider abstraction layer. You can switch between cloud frontier models or run fully offline in Demo Mode.")

        provider = st.selectbox(
            "Active Provider",
            options=["demo", "anthropic", "openai", "gemini", "ollama"],
            index=["demo", "anthropic", "openai", "gemini", "ollama"].index(orch.llm_config.provider) if orch.llm_config.provider in ["demo", "anthropic", "openai", "gemini", "ollama"] else 0,
            format_func=lambda p: {
                "demo": "Demo Mode (Offline / Simulated - No API Key Required)",
                "anthropic": "Claude (Anthropic - claude-3-5-sonnet)",
                "openai": "OpenAI (GPT-4o / GPT-4o-mini)",
                "gemini": "Google Gemini (gemini-1.5-pro / flash)",
                "ollama": "Local Ollama (llama3 / mistral)"
            }.get(p, p)
        )

        orch.llm_config.provider = provider

        api_key = st.text_input(
            "API Key",
            value=orch.llm_config.api_key or "",
            type="password",
            help="Your API key is kept in-memory for the current session and never sent to external third-party telemetry."
        )
        orch.llm_config.api_key = api_key

        model_col, temp_col = st.columns(2)
        with model_col:
            model_name = st.text_input(
                "Model Identifier (Optional Override)",
                value=orch.llm_config.model_name or "",
                placeholder="e.g. claude-3-5-sonnet-20241022 or gpt-4o"
            )
            if model_name:
                orch.llm_config.model_name = model_name
        with temp_col:
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(orch.llm_config.temperature), step=0.05)
            orch.llm_config.temperature = temperature

        if st.button("Test LLM Connection", key="btn_test_conn"):
            with st.spinner("Testing provider handshake..."):
                ok, msg = test_llm_connection(orch.llm_config)
                if ok:
                    st.success(f"Connection Successful! Provider '{provider}' responded: {msg}")
                else:
                    st.error(f"Connection Failed: {msg}")

    # --- TAB 2: SM-2 SETTINGS ---
    with tab_sm2:
        st.markdown("<h4 style='color: #F8FAFC;'>SuperMemo-2 (SM-2) Parameters</h4>", unsafe_allow_html=True)
        st.caption("Customize the mathematical parameters of the spaced repetition interval calculations.")

        col_ef, col_min_ef = st.columns(2)
        with col_ef:
            st.number_input("Initial Ease Factor (EF)", min_value=1.3, max_value=3.5, value=2.5, step=0.1, key="sm2_ef")
        with col_min_ef:
            st.number_input("Minimum Ease Factor Floor", min_value=1.1, max_value=1.5, value=1.3, step=0.05, key="sm2_min_ef")

        st.markdown("""
        <div style="background: #0D1117; border: 1px solid #27303B; border-radius: 10px; padding: 14px 18px; margin-top: 14px; font-size: 0.85rem; color: #94A3B8;">
            <strong style="color: #25D8E8;">SM-2 Quality Rating Logic:</strong>
            <ul style="margin: 6px 0 0 16px;">
                <li><strong>5:</strong> Perfect recall without hesitation.</li>
                <li><strong>4:</strong> Correct response after brief hesitation.</li>
                <li><strong>3:</strong> Correct response with serious difficulty.</li>
                <li><strong>2 / 1 / 0:</strong> Incorrect response / complete blackout → Triggers <em>Adaptive Loopback Priority</em>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- TAB 3: AI TEACHER PERSONA & AVATAR SHOWCASE ---
    with tab_avatar:
        st.markdown("<h4 style='color: #F8FAFC;'>AI Teacher Persona & Avatar System</h4>", unsafe_allow_html=True)
        st.caption("EduMentor's teacher is designed to feel friendly, intelligent, calm, encouraging, slightly playful, and academic without being childish or robotic.")

        all_states = get_available_avatar_states()
        cur_state = getattr(orch, "teacher_state", "greeting")
        cur_idx = all_states.index(cur_state) if cur_state in all_states else 0

        # Live Interactive Avatar Controller
        ctl_c1, ctl_c2 = st.columns([1.2, 2.8])
        with ctl_c1:
            st.markdown("<div style='text-align: center; padding-top: 10px;'>", unsafe_allow_html=True)
            render_teacher_avatar(size=104, state=cur_state)
            st.markdown("</div>", unsafe_allow_html=True)
        with ctl_c2:
            st.markdown(f"**Current Avatar State:** <code style='color: #25D8E8; font-weight: 700;'>{cur_state}</code>", unsafe_allow_html=True)
            selected_state = st.selectbox(
                "Test State Reaction:",
                options=all_states,
                index=cur_idx,
                key="test_avatar_state_select"
            )
            if selected_state != cur_state:
                orch.teacher_state = selected_state
                st.rerun()

            st.markdown("""
            <div style="background: #090D14; border: 1px solid #1E293B; border-radius: 8px; padding: 12px 14px; font-size: 12.5px; color: #94A3B8; margin-top: 8px;">
                <span style="color: #25D8E8; font-weight: 600;">Tone Rule:</span> No robotic system messages like <em>“🤖 SYSTEM: Next concept...”</em>. Always introduce topics with warm academic phrasing: <em>“Alright, let's start with Process Scheduling. 😊 Take your time and study it from your notes.”</em>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<h5 style='color: #F8FAFC;'>Complete 11 Avatar States Gallery</h5>", unsafe_allow_html=True)

        # 11 States Gallery in a clean responsive grid
        cols = st.columns(4)
        for i, s in enumerate(all_states):
            col = cols[i % 4]
            with col:
                st.markdown(f"<div style='text-align: center; margin-bottom: 12px;'>", unsafe_allow_html=True)
                render_teacher_avatar(size=68, state=s)
                st.markdown(f"<span style='font-size: 11px; font-weight: 700; color: #CBD5E1;'>{s}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 4: DATA & STORAGE ---
    with tab_data:
        st.markdown("<h4 style='color: #F8FAFC;'>Active Workspace Storage</h4>", unsafe_allow_html=True)
        st.write(f"**Current Active Student Profile:** `{orch.student_name}`")
        st.write(f"**Loaded Module:** `{orch.curriculum_title or 'None'}`")
        st.write(f"**Concepts in Memory:** `{len(orch.concepts)}`")

        if st.button("Clear Active Workspace / Reset Session"):
            orch.initialize_home()
            render_banner("Session reset to initial empty state.", level="info")
            st.rerun()
