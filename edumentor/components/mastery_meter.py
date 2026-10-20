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
    meter_html = f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
      <div style="flex:1; background:#161B22; height:8px; border-radius:4px; overflow:hidden;">
        <div style="width:{mastery_percent}%; background:linear-gradient(90deg, #25D8E8, #8B5CF6); height:100%;"></div>
      </div>
      <span style="font-size:12px; font-weight:700; color:#25D8E8;">{mastery_percent}% ({mastered_count}/{total_count} Mastered)</span>
    </div>
    """
    st.markdown(clean_html_for_markdown(meter_html), unsafe_allow_html=True)

