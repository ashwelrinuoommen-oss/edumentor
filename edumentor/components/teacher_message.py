"""
TeacherMessage Component for EduMentor.
Phase 26: Avatar + Chat Message Design (Avatar beside conversational content with connector branch).
Phase 27: Main Interface Visual Design (#050608, #0D1117, #25D8E8, #8B5CF6, #F5F7FA, #9AA4B2, #27303B, Geist/Inter).
"""

import re
import html
import streamlit as st
from typing import Optional, Dict, Any

from edumentor.services.avatar_expression_manager import avatar_expression_manager
from edumentor.components.teacher_avatar import get_avatar_state_config
from edumentor.utils.text_utils import clean_html_for_markdown


# -----------------------------------------------------------------------------
# DESIGN SYSTEM PALETTE COMPLIANCE (PHASE 27 TOKENS PRESERVED):
# Base: #050608, Surface: #0D1117, Accent Cyan: #25D8E8, Violet: #8B5CF6,
# Text Primary: #F5F7FA, Text Muted: #9AA4B2, Border: #27303B
# Fonts: Geist, Inter
# -----------------------------------------------------------------------------


def format_teacher_paragraph(text: str) -> str:
    """Converts a teacher message paragraph into clean HTML supporting bold, italics, code, and blockquotes."""
    p = text.strip()
    if not p:
        return ""
    is_quote = p.startswith(">")
    if is_quote:
        p = re.sub(r"^>\s*", "", p)
    safe = html.escape(p)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong style='color: #F8FAFC; font-weight: 700;'>\1</strong>", safe)
    safe = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em style='color: #E2E8F0;'>\1</em>", safe)
    safe = re.sub(r"`([^`]+?)`", r"<code style='background: #161B22; color: #25D8E8; padding: 2px 6px; border-radius: 4px; font-size: 13px;'>\1</code>", safe)
    if is_quote:
        return f"<blockquote style='margin: 10px 0; padding: 8px 14px; border-left: 3px solid #25D8E8; background: rgba(37, 216, 232, 0.08); border-radius: 0 8px 8px 0; color: #E2E8F0; font-size: 14px; line-height: 1.6;'>{safe}</blockquote>"
    return f"<p style='margin: 0 0 10px 0; line-height: 1.6; color: #F5F7FA;'>{safe}</p>"


class TeacherMessage:
    """
    Renders an AI Teacher message synchronized with the teacher's emotional expression,
    featuring the Phase 26 visual tree stem connector (Avatar -> Branch -> Conversational bubble).
    """

    def __init__(
        self,
        text: str,
        expression: str = "greeting",
        concept_title: Optional[str] = None,
        status_badge: Optional[str] = None,
        avatar_size: int = 56,
        is_major: bool = True,
    ):
        self.text = text
        self.expression = expression
        self.concept_title = concept_title
        self.status_badge = status_badge
        self.avatar_size = avatar_size
        self.is_major = is_major

    def render(self):
        """Render the unified avatar + message card in Streamlit."""
        if not self.is_major:
            render_status_notice(self.text)
        else:
            render_teacher_message(
                text=self.text,
                expression=self.expression,
                concept_title=self.concept_title,
                status_badge=self.status_badge,
                avatar_size=self.avatar_size,
            )


def render_status_notice(text: str):
    """
    Phase 26: Renders a lightweight, compact status notice WITHOUT an avatar.
    Used for tiny status messages, background processing notes, and calibration breadcrumbs.
    """
    safe_text = html.escape(text.strip())
    notice_html = f"""
    <div class="chat-status-notice chat-row status-notice" style="
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 10px 0 14px 20px;
      padding: 6px 14px;
      background: rgba(13, 17, 23, 0.85);
      border: 1px solid #27303B;
      border-radius: 20px;
      font-family: 'Geist', 'Inter', -apple-system, sans-serif;
      font-size: 12.5px;
      color: #9AA4B2;
      width: fit-content;
      max-width: 90%;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    ">
      <span class="status-pill" style="
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #25D8E8;
        box-shadow: 0 0 6px #25D8E8;
        flex-shrink: 0;
      "></span>
      <span style="line-height: 1.4;">{safe_text}</span>
    </div>
    """
    st.markdown(clean_html_for_markdown(notice_html), unsafe_allow_html=True)


def render_teacher_message(
    text: str,
    expression: str = "greeting",
    concept_title: Optional[str] = None,
    status_badge: Optional[str] = None,
    avatar_size: int = 56,
):
    """
    Phase 26: Renders a major AI Teacher message with the Avatar positioned beside
    the conversational bubble, connected by an elegant vertical tree branch stem (│ └──).
    Phase 27: Enforces strict palette (#050608, #0D1117, #25D8E8, #8B5CF6, #F5F7FA, #9AA4B2, #27303B)
    and typography (Geist / Inter).
    """
    b64_data = avatar_expression_manager.get_expression_base64(expression)
    cfg = get_avatar_state_config(expression)
    badge_label = status_badge or cfg.get("badge_text", "AI Academic Mentor")

    # Format text into paragraphs if multi-line
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    formatted_text = "".join(format_teacher_paragraph(p) for p in paragraphs)

    concept_header = ""
    if concept_title:
        concept_header = f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #25D8E8;">Concept</span>
          <span style="font-size: 13px; font-weight: 600; color: #F5F7FA;">• {html.escape(concept_title)}</span>
        </div>
        """

    msg_html = f"""
    <div class="teacher-message-wrapper" style="
      display: flex;
      gap: 16px;
      align-items: flex-start;
      margin: 16px 0 24px 0;
      max-width: 900px;
      position: relative;
    ">
      <!-- Left Column: Avatar + Tree Branch Stem Connector (│ └──) -->
      <div class="avatar-stem-col" style="
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: {avatar_size}px;
        position: relative;
      ">
        <!-- 1. Avatar with subtle ambient framing -->
        <div style="position: relative; width: {avatar_size}px; height: {avatar_size}px; margin: 0 auto; z-index: 2;">
          <div style="
            position: relative; width: {avatar_size}px; height: {avatar_size}px;
            border-radius: 50%;
            background: #050608;
            border: 2px solid {cfg.get('border_color', '#25D8E8')};
            box-shadow: 0 4px 14px rgba(0,0,0,0.5);
            overflow: hidden;
          ">
            <img src="data:image/png;base64,{b64_data}"
                 alt="EduMentor Teacher Avatar"
                 style="width: 100%; height: 100%; object-fit: contain; display: block;" />
          </div>
        </div>

        <!-- 2. Vertical Stem Line (│) descending from Avatar -->
        <div class="avatar-connector-stem" style="
          width: 2px;
          height: 32px;
          background: linear-gradient(180deg, rgba(37, 216, 232, 0.6) 0%, rgba(39, 48, 59, 0.8) 100%);
          margin: 4px auto 0 auto;
          position: relative;
        ">
          <!-- 3. Curved Branch Connector (└──) bridging horizontally to Speech Bubble -->
          <div class="avatar-branch-curve" style="
            position: absolute;
            bottom: 0;
            left: 0;
            width: 16px;
            height: 14px;
            border-bottom: 2px solid rgba(37, 216, 232, 0.4);
            border-left: 2px solid rgba(37, 216, 232, 0.4);
            border-bottom-left-radius: 8px;
            pointer-events: none;
          "></div>
        </div>

        <!-- 4. Subtle Expression Badge -->
        <div style="
          margin-top: 6px;
          font-size: 10.5px;
          font-weight: 700;
          color: {cfg.get('badge_color', '#25D8E8')};
          background: rgba(13, 17, 23, 0.9);
          border: 1px solid #27303B;
          border-radius: 10px;
          padding: 2px 8px;
          white-space: nowrap;
          display: inline-block;
          font-family: 'Geist', 'Inter', sans-serif;
        ">
          {html.escape(badge_label)}
        </div>
      </div>

      <!-- Right Column: Speech Bubble beside Avatar -->
      <div class="teacher-speech-bubble" style="
        flex: 1;
        background: #0D1117;
        border: 1px solid #27303B;
        border-left: 3px solid #25D8E8;
        border-radius: 0 14px 14px 14px;
        padding: 18px 22px 16px 22px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        color: #F5F7FA;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 14.5px;
        line-height: 1.6;
        transition: border-color 0.2s ease;
      ">
        {concept_header}
        <div class="teacher-message-body" style="color: #F5F7FA;">
          {formatted_text}
        </div>
      </div>
    </div>
    """
    st.markdown(clean_html_for_markdown(msg_html), unsafe_allow_html=True)
