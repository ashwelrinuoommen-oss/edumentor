"""
Chat Message UI Component for EduMentor.
Phase 27: Main Interface Visual Design (#050608, #0D1117, #25D8E8, #8B5CF6, #F5F7FA, #9AA4B2, #27303B).
"""

import html
import re
import streamlit as st
from typing import Optional
from edumentor.utils.text_utils import clean_html_for_markdown


def render_chat_bubble(
    role: str,
    content: str,
    student_initial: str = "A",
    expression: Optional[str] = None,
    concept_title: Optional[str] = None
):
    """Render formatted chat message bubble with academic design tokens."""
    if role == "assistant":
        from edumentor.components.teacher_message import render_teacher_message
        render_teacher_message(
            text=content,
            expression=expression or "greeting",
            concept_title=concept_title,
            avatar_size=56
        )
        return

    # Student message rendering with subtle cyan/violet gradient badge
    safe_content = html.escape(content.strip())
    safe_content = re.sub(r"\*\*(.+?)\*\*", r"<strong style='color:#FFFFFF;'>\1</strong>", safe_content)
    safe_content = re.sub(r"`([^`]+?)`", r"<code style='background:rgba(255,255,255,0.08); padding:1px 5px; border-radius:4px;'>\1</code>", safe_content)
    safe_content = safe_content.replace("\n", "<br/>")

    initial = (student_initial or "A").upper()[:1]

    user_bubble_html = f"""
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; gap: 12px; margin: 16px 0;">
        <div style="max-width: 78%; background: rgba(37, 216, 232, 0.07); border: 1px solid rgba(37, 216, 232, 0.22); border-radius: 14px 14px 2px 14px; padding: 12px 18px; color: #F5F7FA; font-size: 14px; line-height: 1.6; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);">
            {safe_content}
        </div>
        <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #8B5CF6 0%, #25D8E8 100%); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: #050608; flex-shrink: 0; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.4);">
            {initial}
        </div>
    </div>
    """
    st.markdown(clean_html_for_markdown(user_bubble_html), unsafe_allow_html=True)
