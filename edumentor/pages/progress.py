"""
EduMentor Progress Page — Phase 19.
Lightweight progress overview:
Not a massive analytics dashboard.
Shows YOUR LEARNING, 4 core metrics, recent subjects, and pedagogical insights.
"""

import streamlit as st
from edumentor.orchestrator import EduMentorOrchestrator


def render_progress_page(orch: EduMentorOrchestrator):
    """
    Renders the student's lightweight progress page.
    """
    summary = orch.get_progress_summary()

    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div style="font-family: 'Outfit', sans-serif; font-size: 11px; font-weight: 700; color: #25D8E8; letter-spacing: 0.08em; text-transform: uppercase;">
            Student Progress
        </div>
        <div style="font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.02em; margin-top: 4px;">
            {summary.get('title', 'YOUR LEARNING')}
        </div>
        <div style="font-size: 14px; color: #94A3B8; margin-top: 4px;">
            A focused, lightweight view of your conceptual retention and recent subject progress.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Core Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background: rgba(13,17,23,0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 11.5px; font-weight: 600; color: #94A3B8; text-transform: uppercase;">Overall Mastery</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 36px; font-weight: 800; color: #25D8E8; margin-top: 6px;">{summary.get('overall_mastery', 76)}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: rgba(13,17,23,0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 11.5px; font-weight: 600; color: #94A3B8; text-transform: uppercase;">Concepts Mastered</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 36px; font-weight: 800; color: #FFFFFF; margin-top: 6px;">{summary.get('concepts_mastered', 32)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: rgba(13,17,23,0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 11.5px; font-weight: 600; color: #94A3B8; text-transform: uppercase;">Needs Review</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 36px; font-weight: 800; color: #F59E0B; margin-top: 6px;">{summary.get('needs_review', 6)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: rgba(13,17,23,0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 11.5px; font-weight: 600; color: #94A3B8; text-transform: uppercase;">Learning Sessions</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 36px; font-weight: 800; color: #FFFFFF; margin-top: 6px;">{summary.get('learning_sessions', 14)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Recent Subjects
    st.markdown("""
    <div style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
        Recent subjects
    </div>
    """, unsafe_allow_html=True)

    recent_subjects = summary.get("recent_subjects", [])
    for sub in recent_subjects:
        sname = sub.get("subject", "")
        smast = sub.get("mastery", 0)
        st.markdown(f"""
        <div style="background: rgba(13,17,23,0.7); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 14.5px; margin-bottom: 6px;">
                <span style="color: #F8FAFC;">{sname}</span>
                <span style="color: #25D8E8; font-weight: 700;">{smast}%</span>
            </div>
            <div style="width: 100%; height: 7px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">
                <div style="width: {smast}%; height: 100%; background: linear-gradient(90deg, #25D8E8, #8B5CF6); border-radius: 9999px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Pedagogical Insights: Strongest Area & Needs More Attention
    c_strong, c_atten = st.columns(2)
    with c_strong:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 16px 18px;">
            <div style="font-weight: 700; color: #34D399; font-size: 14px; margin-bottom: 6px;">🌟 Your strongest area</div>
            <div style="font-size: 13px; color: #CBD5E1; line-height: 1.45;">{summary.get('strongest_area', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_atten:
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 10px; padding: 16px 18px;">
            <div style="font-weight: 700; color: #FBBF24; font-size: 14px; margin-bottom: 6px;">🎯 Needs more attention</div>
            <div style="font-size: 13px; color: #CBD5E1; line-height: 1.45;">{summary.get('needs_attention', '')}</div>
        </div>
        """, unsafe_allow_html=True)

