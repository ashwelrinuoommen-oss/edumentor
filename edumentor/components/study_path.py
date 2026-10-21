"""
Knowledge Graph / Study Path DAG visualizer and Compact Learning Path component.
"""

import html
import streamlit as st
from typing import Dict, List, Any, Optional
from edumentor.utils.text_utils import clean_html_for_markdown


def render_study_path_dag(graph_obj):
    """Render responsive SVG Knowledge Graph."""
    if graph_obj and hasattr(graph_obj, "generate_html_graph"):
        st.markdown(graph_obj.generate_html_graph(), unsafe_allow_html=True)
    else:
        st.info("Study path will appear once your module notes are analyzed.")


def render_compact_study_path(
    topological_order: List[str],
    concepts: Dict[str, Dict[str, Any]],
    current_concept_id: Optional[str] = None
):
    """
    Renders the compact conversational study-path visualization specified in Phase 4:
    YOUR LEARNING PATH
    01  Operating System Basics       ✓ Ready
    02  Processes                     → Next
    03  Process Scheduling
    04  Threads
    05  CPU Scheduling Algorithms
    06  Deadlocks
    07  Memory Management
    """
    if not topological_order or not concepts:
        return

    curr_idx = -1
    if current_concept_id and current_concept_id in topological_order:
        curr_idx = topological_order.index(current_concept_id)

    items_html = []
    for idx, cid in enumerate(topological_order):
        c = concepts.get(cid, {})
        title = c.get("title", cid)
        num_str = f"{idx + 1:02d}"

        is_current = (cid == current_concept_id)
        lvl = c.get("mastery_level")
        m_score = c.get("mastery_score")
        score_text = f" • {m_score}%" if m_score is not None and m_score > 0 else ""

        is_mastered = (lvl == "Mastered") or c.get("is_mastered", False) or (c.get("sm2_status") == "mastered" and c.get("last_quality_score", 0) >= 4)
        is_proficient = (lvl == "Proficient") or (c.get("last_quality_score", 0) >= 3 and not is_mastered and c.get("total_reviews", 0) > 0)
        is_practicing = (lvl == "Practicing")
        is_weak = (c.get("last_quality_score", 0) < 3 and c.get("total_reviews", 0) > 0) or lvl == "Learning" and c.get("total_reviews", 0) > 0

        if is_mastered:
            status_badge = f"""
            <span style="
                color: #10B981; font-weight: 700; font-size: 11.5px;
                background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3);
                padding: 2px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;
            ">★ Mastered{score_text}</span>
            """
            row_style = "color: #E2E8F0; font-weight: 600;"
            num_style = "color: #10B981; font-weight: 700;"
            bg_style = "background: rgba(16, 185, 129, 0.04); border-left: 3px solid #10B981; padding-left: 10px;"
        elif is_current:
            status_badge = """
            <span style="
                color: #25D8E8; font-weight: 700; font-size: 11.5px;
                background: rgba(37, 216, 232, 0.15); border: 1px solid rgba(37, 216, 232, 0.4);
                padding: 2px 10px; border-radius: 9999px;
                display: inline-flex; align-items: center; gap: 4px;
            ">→ Next</span>
            """
            row_style = "color: #FFFFFF; font-weight: 700;"
            num_style = "color: #25D8E8; font-weight: 800;"
            bg_style = "background: rgba(37, 216, 232, 0.06); border-left: 3px solid #25D8E8; padding-left: 10px;"
        elif is_proficient:
            status_badge = f"""
            <span style="
                color: #25D8E8; font-weight: 600; font-size: 11.5px;
                background: rgba(37, 216, 232, 0.10); border: 1px solid rgba(37, 216, 232, 0.25);
                padding: 2px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;
            ">✓ Proficient{score_text}</span>
            """
            row_style = "color: #94A3B8; font-weight: 500;"
            num_style = "color: #25D8E8; font-weight: 700;"
            bg_style = "background: rgba(255, 255, 255, 0.01);"
        elif is_practicing:
            status_badge = f"""
            <span style="
                color: #F59E0B; font-weight: 600; font-size: 11.5px;
                background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3);
                padding: 2px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;
            ">⚡ Practicing{score_text}</span>
            """
            row_style = "color: #CBD5E1; font-weight: 500;"
            num_style = "color: #F59E0B; font-weight: 600;"
            bg_style = "background: rgba(245, 158, 11, 0.03);"
        elif is_weak:
            status_badge = f"""
            <span style="
                color: #F87171; font-weight: 600; font-size: 11.5px;
                background: rgba(248, 113, 113, 0.12); border: 1px solid rgba(248, 113, 113, 0.3);
                padding: 2px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;
            ">🌱 Needs Review</span>
            """
            row_style = "color: #CBD5E1; font-weight: 500;"
            num_style = "color: #F87171; font-weight: 600;"
            bg_style = "background: rgba(248, 113, 113, 0.03); border-left: 3px solid #F87171; padding-left: 10px;"
        elif idx < curr_idx:
            status_badge = """
            <span style="
                color: #10B981; font-weight: 700; font-size: 11.5px;
                background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3);
                padding: 2px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;
            ">✓ Ready</span>
            """
            row_style = "color: #94A3B8; font-weight: 500;"
            num_style = "color: #10B981; font-weight: 700;"
            bg_style = "background: rgba(255, 255, 255, 0.01);"
        else:
            status_badge = """
            <span style="color: #475569; font-size: 11.5px;">Upcoming</span>
            """
            row_style = "color: #64748B; font-weight: 400;"
            num_style = "color: #475569; font-weight: 600;"
            bg_style = "background: transparent;"

        meta_html = ""
        named_methods = c.get("named_types_or_methods") or []
        page_num = c.get("source_page")
        major = c.get("major_topic")

        chips = []
        if major and major.lower() != title.lower():
            chips.append(f"<span style='font-size: 10px; color: #25D8E8; text-transform: uppercase; letter-spacing: 0.04em;'>{html.escape(major)}</span>")
        for m in named_methods[:3]:
            chips.append(f"<span style='background: rgba(37, 216, 232, 0.1); border: 1px solid rgba(37, 216, 232, 0.25); border-radius: 3px; padding: 1px 5px; font-size: 10px; color: #25D8E8;'>{html.escape(m)}</span>")
        if page_num:
            chips.append(f"<span style='font-size: 10px; color: #64748B;'>p. {page_num}</span>")

        if chips:
            meta_html = f"<div style='display: flex; align-items: center; gap: 5px; margin-top: 2px; flex-wrap: wrap;'>{''.join(chips)}</div>"

        items_html.append(f"""
        <div style="
            display: flex; align-items: center; justify-content: space-between;
            padding: 8px 12px; margin-bottom: 4px; border-radius: 8px;
            {bg_style}
            transition: all 0.15s ease;
        ">
            <div style="display: flex; align-items: center; gap: 14px;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 12.5px; {num_style} width: 22px;">
                    {num_str}
                </span>
                <div>
                    <span style="font-size: 13.5px; {row_style}">
                        {html.escape(title)}
                    </span>
                    {meta_html}
                </div>
            </div>
            <div>
                {status_badge}
            </div>
        </div>
        """)

    card_html = f"""
    <div style="
        background: #0D1117;
        border: 1px solid #27303B;
        border-radius: 14px;
        padding: 16px 18px 14px 18px;
        margin: 14px 0 18px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
            <div style="font-family: 'Outfit', sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.1em; color: #25D8E8; text-transform: uppercase;">
                YOUR LEARNING PATH
            </div>
            <div style="font-size: 11px; color: #64748B;">
                Concept → Recall → Mastery progression
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 2px;">
            {''.join(items_html)}
        </div>
    </div>
    """
    st.markdown(clean_html_for_markdown(card_html), unsafe_allow_html=True)
