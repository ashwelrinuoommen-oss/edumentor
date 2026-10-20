"""
Notes upload zone and Phase 28 Chat Composer component.
Phase 28 — Chat Composer Design:
- Strongest UI element on the home canvas
- Floating rounded container (border-radius: 20px, #0D1117, #27303B)
- Default prompt: "Ask EduMentor anything about your learning"
- "＋ Upload notes" trigger
- "↑" Send button
- Dedicated upload processing state (📄 filename, "Processing your notes...", progress bar: 82%)
- Automatic transformation into the learning conversation
"""

import html
import streamlit as st
from typing import Optional, Tuple, List, Dict, Any

from edumentor.utils.text_utils import clean_html_for_markdown

DEFAULT_COMPOSER_PLACEHOLDER = "Ask EduMentor anything about your learning"


def get_composer_css() -> str:
    """Returns Phase 28 Floating Rounded Composer CSS styles."""
    return """
    <style>
    /* Phase 28: Floating Rounded Container */
    .floating-composer {
        background: #0D1117;
        border: 1px solid #27303B;
        border-radius: 20px;
        padding: 20px 22px 16px 22px;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.65), 0 0 1px 1px rgba(255, 255, 255, 0.05);
        margin: 16px 0 24px 0;
        transition: all 0.2s ease-in-out;
    }
    .floating-composer:hover, .floating-composer:focus-within {
        border-color: rgba(37, 216, 232, 0.55);
        box-shadow: 0 22px 52px rgba(0, 0, 0, 0.75), 0 0 28px rgba(37, 216, 232, 0.18);
    }
    .composer-processing-card {
        background: #0D1117;
        border: 1px solid #27303B;
        border-radius: 20px;
        padding: 22px 24px;
        margin: 16px 0 24px 0;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.65), 0 0 24px rgba(37, 216, 232, 0.15);
    }
    .composer-progress-track {
        background: #161B22;
        border-radius: 9999px;
        height: 8px;
        width: 100%;
        overflow: hidden;
    }
    .composer-progress-fill {
        background: linear-gradient(90deg, #25D8E8 0%, #8B5CF6 100%);
        height: 100%;
        border-radius: 9999px;
        transition: width 0.4s ease;
    }
    @keyframes pulseGlowDot {
        0%, 100% { opacity: 0.6; transform: scale(0.95); }
        50% { opacity: 1; transform: scale(1.15); }
    }
    .pulse-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #25D8E8;
        box-shadow: 0 0 8px #25D8E8;
        animation: pulseGlowDot 1.8s infinite ease-in-out;
    }
    </style>
    """


def render_composer_processing_card(
    filename: str,
    progress_pct: int = 82,
    status_text: str = "Processing your notes..."
) -> str:
    """
    Renders Phase 28 Document Upload Processing Card:
    ╭──────────────────────────────────────────────╮
    │ 📄 Operating Systems Module 1.pdf            │
    │                                              │
    │ Processing your notes...                    │
    │                                              │
    │ ████████████████████░░░ 82%                 │
    ╰──────────────────────────────────────────────╯
    """
    safe_name = html.escape(filename)
    safe_status = html.escape(status_text)
    pct = max(0, min(100, int(progress_pct)))

    card_html = f"""
    <div class="composer-processing-card" style="background: #0D1117; border: 1px solid #27303B; border-radius: 20px; padding: 22px 24px; margin: 16px 0 24px 0; box-shadow: 0 20px 48px rgba(0, 0, 0, 0.65), 0 0 24px rgba(37, 216, 232, 0.15);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">📄</span>
                <span style="font-weight: 700; font-size: 15px; color: #F5F7FA; letter-spacing: 0.02em;">{safe_name}</span>
            </div>
            <span style="font-size: 12.5px; font-weight: 700; color: #25D8E8; background: rgba(37, 216, 232, 0.12); padding: 3px 12px; border-radius: 14px; border: 1px solid rgba(37, 216, 232, 0.35);">{pct}%</span>
        </div>
        <div style="color: #9AA4B2; font-size: 13px; margin-bottom: 14px; display: flex; align-items: center; gap: 8px;">
            <span class="pulse-dot" style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #25D8E8; box-shadow: 0 0 8px #25D8E8;"></span>
            <span>{safe_status}</span>
        </div>
        <div class="composer-progress-track" style="background: #161B22; border-radius: 9999px; height: 8px; width: 100%; overflow: hidden;">
            <div class="composer-progress-fill" style="background: linear-gradient(90deg, #25D8E8 0%, #8B5CF6 100%); width: {pct}%; height: 100%; border-radius: 9999px;"></div>
        </div>
    </div>
    """
    return clean_html_for_markdown(card_html)


def render_upload_zone(label: str = "📎 Upload your study notes (PDF or Text)") -> Optional[Tuple[str, bytes]]:
    """Legacy single file uploader helper."""
    uploaded = st.file_uploader(label, type=["pdf", "txt", "md"], key="component_file_uploader")
    if uploaded is not None:
        content = uploaded.read()
        return uploaded.name, content
    return None


def render_floating_composer(
    prompt_placeholder: str = DEFAULT_COMPOSER_PLACEHOLDER,
    key_prefix: str = "home_composer"
) -> Tuple[str, List[Tuple[str, bytes]]]:
    """
    Renders the Phase 28 Floating Rounded Composer:
    ╭──────────────────────────────────────────────╮
    │                                              │
    │  Ask EduMentor anything about your learning  │
    │                                              │
    │                                              │
    │  ＋ Upload notes                     ↑        │
    ╰──────────────────────────────────────────────╯
    Returns (typed_text, list_of_uploaded_files)
    """
    st.markdown(clean_html_for_markdown(get_composer_css()), unsafe_allow_html=True)

    with st.container():
        # Large Input Text Area
        typed_text = st.text_area(
            label="Ask EduMentor anything about your learning",
            placeholder=prompt_placeholder,
            label_visibility="collapsed",
            key=f"{key_prefix}_text",
            height=95
        )

        # Action Bar Row inside composer
        act_c1, act_c2 = st.columns([3, 1])

        with act_c1:
            # File attachment uploader (PDF, TXT, MD, multiple files)
            uploaded_files = st.file_uploader(
                "＋ Upload notes",
                type=["pdf", "txt", "md"],
                accept_multiple_files=True,
                key=f"{key_prefix}_files",
                label_visibility="visible",
                help="EduMentor automatically parses lecture slides, textbook extracts, and markdown notes. Max 15MB per file."
            )
            # Phase 35: Explain Note Privacy Near Upload Flow
            st.markdown(
                """
                <div style="font-size: 11.5px; color: #9AA4B2; margin-top: 4px; display: flex; align-items: center; gap: 6px;">
                    <span style="color: #25D8E8;">🔒</span>
                    <span><strong>Note Privacy:</strong> Stored locally in your session (max 15MB). Never used to train public AI models.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with act_c2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            send_clicked = st.button("↑", key=f"{key_prefix}_btn_send", use_container_width=True, help="Send message or process notes")

        # Process attachments if present
        attachments: List[Tuple[str, bytes]] = []
        if uploaded_files:
            for uf in uploaded_files:
                attachments.append((uf.name, uf.read()))

        # If send clicked or user submitted, return inputs
        if send_clicked and (typed_text.strip() or attachments):
            return typed_text.strip(), attachments

    return "", []
