"""
EduMentor History Page.
Displays the student's longitudinal recall attempts, SM-2 retention logs, and scheduled revisions.
"""

import json
from datetime import date
import streamlit as st

from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.services.history_service import HistoryService
from edumentor.components.notification import render_banner


def render_history_page(orch: EduMentorOrchestrator):
    """
    Renders the history and retention tracking page.
    """
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 700; color: #FFFFFF;">
            Recall History & Spaced Retention
        </div>
        <div style="font-size: 14px; color: #94A3B8; margin-top: 4px;">
            Track your concept retention trajectory and inspect algorithmic SM-2 scheduling
        </div>
    </div>
    """, unsafe_allow_html=True)

    history_service = HistoryService()
    user_id = f"user_{orch.student_name.lower().replace(' ', '_')}"
    today_iso = date.today().isoformat()

    attempts = history_service.get_user_recall_attempts(user_id=user_id, limit=30)
    due_reviews = history_service.get_due_reviews(user_id=user_id, today_iso=today_iso)

    # Summary Metrics Row
    total_attempts = len(attempts)
    avg_score = (sum(a.get("composite_score", 0) for a in attempts) / total_attempts) if total_attempts > 0 else 0.0
    due_count = len(due_reviews)
    
    # In-memory curriculum status if active
    mastered_in_session = sum(1 for c in orch.concepts.values() if c.get("mastered", False)) if orch.concepts else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Total Recall Attempts", value=total_attempts)
    with m2:
        st.metric(label="Average Recall Score", value=f"{int(avg_score)}%")
    with m3:
        st.metric(label="Current Session Mastered", value=f"{mastered_in_session}/{len(orch.concepts)}")
    with m4:
        st.metric(label="Due for Spaced Revision", value=due_count)

    st.markdown("---")

    # Due for revision section
    if due_reviews:
        render_banner(f"{due_count} concept(s) due for spaced reinforcement based on the SM-2 algorithm.", level="warning")
        st.markdown("<h4 style='color: #F8FAFC;'>Scheduled Revisions</h4>", unsafe_allow_html=True)
        
        for item in due_reviews:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"""
                <div style="background: #0D1117; border: 1px solid #27303B; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;">
                    <div style="font-weight: 700; color: #25D8E8;">{item.get('title', item.get('concept_id'))}</div>
                    <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">
                        Due: {item.get('next_due_date')} | Interval: {item.get('interval_days')} day(s) | Status: {item.get('status', 'due')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                if st.button("Review Now →", key=f"rev_{item.get('concept_id')}"):
                    orch.state = "RECALL"
                    orch.current_concept_id = item.get("concept_id")
                    st.session_state["current_page"] = "home"
                    st.rerun()

    # Longitudinal Attempts Log
    st.markdown("<h4 style='color: #F8FAFC; margin-top: 20px;'>Recent Recall Submissions</h4>", unsafe_allow_html=True)

    if not attempts:
        st.markdown("""
        <div style="
            background: #0D1117; border: 1px dashed #27303B; border-radius: 12px;
            padding: 30px; text-align: center; color: #64748B; margin-top: 10px;
        ">
            No recall attempts recorded yet for profile <strong>{}</strong>.<br/>
            Head over to the <strong style="color: #25D8E8;">Home Workspace</strong> and start your first study topic!
        </div>
        """.format(orch.student_name), unsafe_allow_html=True)
    else:
        for a in attempts:
            verdict = a.get("verdict", "Evaluated")
            v_color = "#10B981" if "correct" in verdict.lower() and "almost" not in verdict.lower() else ("#F59E0B" if "almost" in verdict.lower() else "#EF4444")
            v_bg = "rgba(16, 185, 129, 0.12)" if v_color == "#10B981" else ("rgba(245, 158, 11, 0.12)" if v_color == "#F59E0B" else "rgba(239, 68, 68, 0.12)")

            st.markdown(f"""
            <div style="
                background: #0D1117;
                border: 1px solid #27303B;
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 12px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-weight: 700; font-size: 1.05rem; color: #F8FAFC;">
                            {a.get('concept_title') or a.get('concept_id')}
                        </span>
                        <span style="font-size: 0.8rem; color: #64748B; margin-left: 10px;">
                            {a.get('attempted_at', '')}
                        </span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="
                            background: {v_bg}; color: {v_color}; border: 1px solid {v_color};
                            padding: 2px 10px; border-radius: 16px; font-size: 0.78rem; font-weight: 700;
                        ">{verdict}</span>
                        <span style="font-size: 1.1rem; font-weight: 800; color: {v_color};">
                            {int(a.get('composite_score', 0))}%
                        </span>
                    </div>
                </div>

                <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;">
                    <strong>Q:</strong> {a.get('question')}
                </div>
                <div style="font-size: 0.85rem; color: #CBD5E1; background: #161B22; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
                    <strong>Your Response:</strong> {a.get('answer')}
                </div>

                {f'<div style="font-size: 0.82rem; color: #25D8E8;"><strong>Tip:</strong> {a.get("actionable_tip")}</div>' if a.get("actionable_tip") else ''}
            </div>
            """, unsafe_allow_html=True)
