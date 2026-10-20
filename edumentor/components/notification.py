"""
Notification UI Component.
Displays toasts, inline banners, and adaptive loopback alerts for EduMentor.
"""

import html
import streamlit as st
from typing import Optional
from edumentor.utils.text_utils import clean_html_for_markdown


def render_loopback_alert(concept_name: str, quality_score: int, tip: Optional[str] = None):
    """
    Renders an adaptive loopback notification when a concept recall score falls below mastery threshold.
    """
    alert_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.06) 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 12px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        display: flex;
        align-items: flex-start;
        gap: 14px;
    ">
        <div style="
            background: rgba(239, 68, 68, 0.2);
            color: #EF4444;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            flex-shrink: 0;
        ">↺</div>
        <div>
            <div style="font-weight: 700; color: #F87171; font-size: 0.92rem;">
                Adaptive Loopback: "{html.escape(concept_name)}" queued for reinforcement
            </div>
            <div style="font-size: 0.84rem; color: #CBD5E1; margin-top: 4px; line-height: 1.4;">
                Recall score was {quality_score}/5. SM-2 reset repetition interval to 1 day. 
                EduMentor will prompt you with a targeted variation to seal this concept.
            </div>
            {f'<div style="margin-top: 6px; font-size: 0.8rem; color: #94A3B8;"><em>Hint: {html.escape(tip)}</em></div>' if tip else ''}
        </div>
    </div>
    """
    st.markdown(clean_html_for_markdown(alert_html), unsafe_allow_html=True)


def render_banner(message: str, level: str = "info", icon: Optional[str] = None):
    """
    Render a stylized banner (info, success, warning, error).
    """
    colors = {
        "info": {"bg": "rgba(37, 216, 232, 0.1)", "border": "rgba(37, 216, 232, 0.3)", "text": "#25D8E8", "def_icon": "ℹ"},
        "success": {"bg": "rgba(16, 185, 129, 0.1)", "border": "rgba(16, 185, 129, 0.3)", "text": "#10B981", "def_icon": "✓"},
        "warning": {"bg": "rgba(245, 158, 11, 0.1)", "border": "rgba(245, 158, 11, 0.3)", "text": "#F59E0B", "def_icon": "⚠"},
        "error": {"bg": "rgba(239, 68, 68, 0.1)", "border": "rgba(239, 68, 68, 0.3)", "text": "#EF4444", "def_icon": "✕"},
    }
    cfg = colors.get(level, colors["info"])
    display_icon = icon or cfg["def_icon"]

    banner_html = f"""
    <div style="
        background: {cfg['bg']};
        border: 1px solid {cfg['border']};
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #E2E8F0;
        font-size: 0.88rem;
    ">
        <span style="color: {cfg['text']}; font-weight: 800; font-size: 1.1rem;">{display_icon}</span>
        <span>{html.escape(message)}</span>
    </div>
    """
    st.markdown(clean_html_for_markdown(banner_html), unsafe_allow_html=True)
