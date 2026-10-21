"""
Mastery meter progress component.
"""

import streamlit as st
from typing import Optional
from edumentor.utils.text_utils import clean_html_for_markdown


def render_mastery_meter(mastery_percent: int = 0, mastered_count: int = 0, total_count: int = 0, mastery_pct: Optional[float] = None):
    """Render compact mastery progress bar and badge."""
    if mastery_pct is not None:
        mastery_percent = int(mastery_pct * 100) if mastery_pct <= 1.0 else int(mastery_pct)
    mastery_percent = max(0, min(100, mastery_percent))
    meter_html = f"""
    <div style="background: rgba(13, 17, 23, 0.7); border: 1px solid #27303B; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
      <div style="flex: 1; background: #161B22; height: 8px; border-radius: 9999px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
        <div style="width: {mastery_percent}%; background: linear-gradient(90deg, #25D8E8, #8B5CF6); height: 100%; border-radius: 9999px; transition: width 0.4s ease;"></div>
      </div>
      <span style="font-size: 12.5px; font-weight: 700; color: #25D8E8; white-space: nowrap; font-family: 'Inter', sans-serif;">
        {mastery_percent}% ({mastered_count}/{total_count} Mastered)
      </span>
    </div>
    """
    st.markdown(clean_html_for_markdown(meter_html), unsafe_allow_html=True)

