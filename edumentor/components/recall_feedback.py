"""
Recall Feedback UI Component.
Renders rich diagnostic cards for student recall submissions:
- Blended score and verdict
- Cosine semantic similarity & LLM judge breakdown
- Key strengths and conceptual gaps
- Actionable study tip
- SM-2 spaced repetition interval calculation
"""

import html
import streamlit as st
from typing import Dict, Any, Optional
from edumentor.services.mastery_service import MasteryService
from edumentor.utils.text_utils import clean_html_for_markdown


def render_recall_feedback(
    eval_result: Dict[str, Any],
    sm2_data: Optional[Dict[str, Any]] = None,
    concept_title: str = "this concept",
    on_confidence_selected = None
):
    """
    Renders an aesthetic, glassmorphic feedback card strictly prioritizing:
      1. Understanding (Semantic state badge: '82% — Strong understanding')
      2. Feedback (Teacher insights, strengths, nuanced tips)
      3. Next Action (Metacognitive confidence check: 'How confident were you about that answer?')
    """
    if not eval_result:
        return

    raw_score = eval_result.get("score", eval_result.get("composite_score", 0.0))
    score_pct = int(raw_score * 100) if raw_score <= 1.0 else int(raw_score)
    quality = eval_result.get("quality_score", eval_result.get("quality_q", 0))
    verdict = eval_result.get("verdict", "Evaluated")
    strengths = eval_result.get("strengths", [])
    missing = eval_result.get("missing_points", eval_result.get("missing_concepts", []))
    tip = eval_result.get("actionable_tip", "")
    summary = eval_result.get("summary", "")

    # Phase 11 & 12: Resolve accessible semantic mastery indicator
    mastery_state = MasteryService.get_mastery_state(score_pct)
    indicator = MasteryService.get_mastery_indicator(mastery_state)
    semantic_score_text = f"{score_pct}% — {mastery_state}"

    strengths_html = "".join([f"<li style='margin-bottom: 4px;'>{html.escape(s)}</li>" for s in strengths]) if strengths else "<li>Solid core attempt</li>"
    missing_html = "".join([f"<li style='margin-bottom: 4px;'>{html.escape(m)}</li>" for m in missing]) if missing else "<li>None! Comprehensive answer</li>"

    # Phase 14 SM-2 Spaced Repetition diagnostic strip
    sm2_section = ""
    if sm2_data:
        interval = sm2_data.get("interval", sm2_data.get("interval_days", 1))
        ef = sm2_data.get("ease_factor", sm2_data.get("easiness_factor", 2.5))
        reps = sm2_data.get("repetition", sm2_data.get("repetition_n", sm2_data.get("repetitions", 1)))
        next_rev = sm2_data.get("next_review", sm2_data.get("next_due_date", "Tomorrow"))
        sm2_section = f"""
        <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08); display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.82rem; color: #94A3B8;">
            <div><span style="color: #64748B;">Next Review:</span> <strong style="color: #F8FAFC;">{next_rev} ({interval}d)</strong></div>
            <div><span style="color: #64748B;">Ease Factor:</span> <strong style="color: #F8FAFC;">{ef:.2f}</strong></div>
            <div><span style="color: #64748B;">Repetition:</span> <strong style="color: #F8FAFC;">#{reps}</strong></div>
        </div>
        """

    card_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(16, 22, 34, 0.95) 0%, rgba(20, 27, 43, 0.92) 100%);
        border: 1px solid {indicator['border']};
        border-radius: 14px;
        padding: 20px;
        margin: 16px 0 8px 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        color: #E2E8F0;
    ">
        <!-- 1. UNDERSTANDING: Prioritized Semantic Header (Never color alone) -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="
                    background: {indicator['bg']};
                    color: {indicator['color']};
                    border: 1px solid {indicator['border']};
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.82rem;
                    font-weight: 700;
                    letter-spacing: 0.03em;
                ">{indicator['icon']} {indicator['label']}</span>
                <span style="font-size: 0.85rem; color: #94A3B8;">{indicator['description']}</span>
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: {indicator['color']}; font-family: monospace;">
                {semantic_score_text}
            </div>
        </div>

        {f'<div style="font-size: 0.9rem; color: #CBD5E1; margin-bottom: 14px; line-height: 1.5;">{html.escape(summary)}</div>' if summary else ''}

        <!-- 2. FEEDBACK: Strengths & Attention Areas -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 12px;">
            <div style="background: rgba(16, 185, 129, 0.07); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 10px 14px;">
                <div style="font-size: 0.78rem; font-weight: 700; color: #34D399; text-transform: uppercase; margin-bottom: 6px;">✓ Strengths</div>
                <ul style="margin: 0; padding-left: 18px; font-size: 0.84rem; color: #E2E8F0;">
                    {strengths_html}
                </ul>
            </div>
            <div style="background: rgba(239, 68, 68, 0.07); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px;">
                <div style="font-size: 0.78rem; font-weight: 700; color: #F87171; text-transform: uppercase; margin-bottom: 6px;">! Needs Attention</div>
                <ul style="margin: 0; padding-left: 18px; font-size: 0.84rem; color: #E2E8F0;">
                    {missing_html}
                </ul>
            </div>
        </div>

        {f'''
        <div style="background: rgba(37, 216, 232, 0.08); border-left: 3px solid #25D8E8; padding: 10px 14px; border-radius: 0 8px 8px 0; margin-top: 10px;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #25D8E8; text-transform: uppercase; margin-bottom: 3px;">💡 Academic Mentor Coaching Tip</div>
            <div style="font-size: 0.86rem; color: #E2E8F0; line-height: 1.4;">{html.escape(tip)}</div>
        </div>
        ''' if tip else ''}

        {sm2_section}
    </div>
    """
    st.markdown(clean_html_for_markdown(card_html), unsafe_allow_html=True)

    # 3. NEXT ACTION: Phase 13 Confidence Calibration Buttons
    conf_prompt_html = """
    <div style="margin-top: 8px; margin-bottom: 6px; font-size: 0.85rem; font-weight: 600; color: #94A3B8;">
        How confident were you about that answer?
    </div>
    """
    st.markdown(clean_html_for_markdown(conf_prompt_html), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Not very confident", key=f"conf_not_{concept_title}"):
            if on_confidence_selected:
                on_confidence_selected("Not very confident")
    with col2:
        if st.button("Somewhat confident", key=f"conf_some_{concept_title}"):
            if on_confidence_selected:
                on_confidence_selected("Somewhat confident")
    with col3:
        if st.button("Very confident", key=f"conf_very_{concept_title}"):
            if on_confidence_selected:
                on_confidence_selected("Very confident")
