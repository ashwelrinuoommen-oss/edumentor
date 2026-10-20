"""
Concept Study Card & Progress Bar UI Component.
"""

import streamlit as st
from typing import Dict, Any, Optional
from edumentor.utils.text_utils import clean_html_for_markdown


def render_concept_card(concept: Dict[str, Any]):
    """Render inline concept intuition and core principles card."""
    tier = concept.get("tier", 0)
    tier_label = "Tier 0: Foundational" if tier == 0 else ("Tier 1: Intermediate" if tier == 1 else "Tier 2: Advanced")
    principles = "".join(f"<li>{p}</li>" for p in (concept.get("key_points") or concept.get("principles", [])))

    card_html = f"""
    <div style="background:#0D1117; border:1px solid #27303B; border-radius:14px; padding:18px 20px; margin:12px 0 16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <span style="font-size:16px; font-weight:700; color:#F5F7FA;">{concept.get('title', 'Concept')}</span>
        <span style="font-size:11px; font-weight:700; padding:2px 8px; border-radius:9999px; background:rgba(37,216,232,0.12); color:#25D8E8; border:1px solid rgba(37,216,232,0.3);">{tier_label}</span>
      </div>
      <div style="background:#161B22; border-left:3px solid #25D8E8; padding:10px 14px; border-radius:0 8px 8px 0; color:#9AA4B2; font-size:13.5px; margin-bottom:12px;">
        {concept.get('summary', '')}
      </div>
      <strong style="color:#F5F7FA; font-size:13px;">Core Principles:</strong>
      <ul style="margin-left:18px; color:#CCD6E0; font-size:13px; line-height:1.6;">
        {principles}
      </ul>
    </div>
    """
    st.markdown(clean_html_for_markdown(card_html), unsafe_allow_html=True)


def render_concept_progress(concept_title: str, current_step: int, total_steps: int, status: str = "In Progress"):
    """Render progress indicator across the prerequisite path."""
    pct = int((current_step / total_steps) * 100) if total_steps > 0 else 0
    progress_html = f"""
    <div style="background: #0D1117; border: 1px solid #27303B; border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 14px; color: #F5F7FA;">{concept_title}</span>
            <span style="font-size: 12px; color: #25D8E8; font-weight: 600;">Step {current_step} of {total_steps} ({pct}%)</span>
        </div>
        <div style="background: #161B22; border-radius: 9999px; height: 6px; width: 100%; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #25D8E8 0%, #8B5CF6 100%); width: {pct}%; height: 100%; border-radius: 9999px;"></div>
        </div>
        <div style="font-size: 11.5px; color: #64748B; margin-top: 6px;">{status}</div>
    </div>
    """
    st.markdown(clean_html_for_markdown(progress_html), unsafe_allow_html=True)
