"""
EduMentor Home Page (Phase 2).
The Main Conversational Workspace.
- Dark cinematic space, centered typography
- Floating large composer with integrated drag-and-drop notes upload
- Dynamic contextual greeting based on student history:
  * "What do you think we should study today?" (New user)
  * "Want to continue where you left off?" (Existing session / recently studied)
  * "Ready to revise something today?" (Pending revision / weak concepts)
- Unified upload and conversation interaction
"""

import streamlit as st
from datetime import date
from typing import Optional, Dict, Any, List

from edumentor.components.teacher_avatar import render_teacher_avatar, TeacherAvatar
from edumentor.components.teacher_message import render_teacher_message, TeacherMessage, render_status_notice
from edumentor.components.chat_message import render_chat_bubble
from edumentor.components.upload_zone import (
    render_floating_composer,
    render_composer_processing_card,
    get_composer_css,
    DEFAULT_COMPOSER_PLACEHOLDER
)
from edumentor.components.study_path import render_compact_study_path
from edumentor.components.concept_progress import render_concept_progress
from edumentor.components.mastery_meter import render_mastery_meter
from edumentor.components.recall_feedback import render_recall_feedback
from edumentor.components.notification import render_loopback_alert, render_banner
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.database.repository import EduMentorRepository
from edumentor.utils.text_utils import clean_html_for_markdown


def get_contextual_welcome(student_name: str, orch: EduMentorOrchestrator, repo: Optional[EduMentorRepository] = None) -> Dict[str, Any]:
    """
    Determines the appropriate contextual greeting dynamically based on:
    - New user
    - Existing study session
    - Pending revision
    - Weak concepts
    - Recently studied topics
    """
    repo = repo or EduMentorRepository(db_path=getattr(orch, "db_path", None))
    user_id = f"user_{student_name.lower().replace(' ', '_')}"
    today_iso = date.today().isoformat()

    # 1. Check for pending revisions or weak concepts (SM-2 status = 'weak' or next_due_date <= today)
    due_or_weak = repo.get_due_or_weak_concepts(user_id=user_id, today_iso=today_iso)
    if due_or_weak:
        weak_item = due_or_weak[0]
        topic_title = weak_item.get("title") or weak_item.get("concept_id", "Scheduled Topic")
        return {
            "mode": "REVISE",
            "welcome_title": f"Welcome back, {student_name} 👋",
            "headline": "Ready to revise something today?",
            "subtext": f"You have spaced repetition reviews due for retention: <strong>{topic_title}</strong>.",
            "placeholder": f"Ask about {topic_title}, or tell me what you want to study...",
            "target_concept": weak_item.get("concept_id"),
            "target_title": topic_title,
            "badge": "Pending Revision"
        }

    # 2. Check for existing active study session
    if orch.curriculum_title and orch.concepts and orch.current_concept_id:
        active_concept = orch.concepts.get(orch.current_concept_id, {}).get("title", "current topic")
        return {
            "mode": "CONTINUE",
            "welcome_title": f"Welcome back, {student_name} 👋",
            "headline": "Want to continue where you left off?",
            "subtext": f"Active module: <strong>{orch.curriculum_title}</strong> (Concept: <em>{active_concept}</em>).",
            "placeholder": f"Continue with {active_concept}, or tell me what you'd like to study...",
            "target_title": orch.curriculum_title,
            "badge": "In Progress"
        }

    # 3. Check for recently studied topics in history
    recent_attempts = repo.get_recent_attempts(user_id=user_id, limit=3)
    if recent_attempts:
        recent_topic = recent_attempts[0].get("concept_title") or "your last module"
        return {
            "mode": "CONTINUE",
            "welcome_title": f"Welcome back, {student_name} 👋",
            "headline": "Want to continue where you left off?",
            "subtext": f"Pick up where you left off in <strong>{recent_topic}</strong>, or start a new subject.",
            "placeholder": f"Continue {recent_topic}, or type a new topic...",
            "target_title": recent_topic,
            "badge": "Recent Activity"
        }

    # 4. New user default
    return {
        "mode": "NEW",
        "welcome_title": f"Welcome, {student_name}!",
        "headline": "What do you think we should study today?",
        "subtext": "Type any topic or upload your lecture notes to construct your prerequisite study path.",
        "placeholder": "What would you like to study today? (e.g. 'I want to study Operating Systems')",
        "badge": "AI Study Companion"
    }


def render_home_page(orch: EduMentorOrchestrator):
    """
    Renders the primary conversational workspace for EduMentor (Phase 2).
    """
    student_name = orch.student_name or "Ashwel"
    is_home = (orch.state == "HOME" and (not orch.curriculum_title or len(orch.chat_history) <= 1))

    # Top Overview Metrics if an active module is loaded
    if orch.curriculum_title and orch.concepts:
        mastered_cnt = sum(1 for c in orch.concepts.values() if c.get("mastered", False))
        total_cnt = len(orch.concepts)
        avg_score = (sum(c.get("last_score", 0.0) for c in orch.concepts.values()) / total_cnt) if total_cnt > 0 else 0.0

        top_c1, top_c2 = st.columns([2.5, 1.5])
        with top_c1:
            step_idx = getattr(orch, "current_step_index", getattr(orch, "current_concept_index", 0))
            render_concept_progress(
                concept_title=orch.curriculum_title,
                current_step=step_idx + 1,
                total_steps=total_cnt,
                status=f"Active Concept: {orch.concepts.get(orch.current_concept_id, {}).get('title', 'Overview')}"
            )
        with top_c2:
            render_mastery_meter(mastery_pct=avg_score, mastered_count=mastered_cnt, total_count=total_cnt)

    # -------------------------------------------------------------------------
    # 1. EMPTY / WELCOME STAGE (WHEN STUDENT HAS NOT STARTED A SESSION)
    # -------------------------------------------------------------------------
    if is_home:
        # Determine dynamic contextual prompt
        ctx = get_contextual_welcome(student_name, orch)

        # 3D AI Study Mentor Avatar with dynamic emotion state (Centered & Prominent)
        teacher_state = getattr(orch, "teacher_state", "greeting")
        render_teacher_avatar(size=140, state=teacher_state)

        # Centered typography: Dynamic contextual greeting
        welcome_title = ctx.get("welcome_title", f"Welcome back, {student_name} 👋")
        welcome_html = f"""<div style="text-align:center;margin-top:4px;margin-bottom:24px;">
<div style="display:inline-flex;align-items:center;gap:8px;background:rgba(37,216,232,0.08);border:1px solid rgba(37,216,232,0.25);border-radius:30px;padding:4px 16px;margin-bottom:12px;">
<span style="font-size:11px;font-weight:700;color:#25D8E8;letter-spacing:0.08em;text-transform:uppercase;">Learn • Recall • Master</span>
</div>
<div style="font-family:'Newsreader',Georgia,serif;font-size:35px;font-weight:700;color:#FFFFFF;letter-spacing:-0.4px;margin-bottom:6px;">
{welcome_title}
</div>
<div style="font-size:19px;font-weight:600;color:#E2E8F0;margin-bottom:8px;">
{ctx['headline']}
</div>
<div style="font-size:14.5px;color:#94A3B8;max-width:580px;margin:0 auto;line-height:1.55;">
{ctx['subtext']}
</div>
</div>"""
        st.markdown(welcome_html, unsafe_allow_html=True)


        # Contextual Action Banner if revision is due
        if ctx["mode"] == "REVISE" and ctx.get("target_concept"):
            rev_c1, rev_c2 = st.columns([3, 1])
            with rev_c1:
                render_banner(f"Spaced repetition revision due: {ctx.get('target_title')}", level="warning", icon="↺")
            with rev_c2:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button(f"Revise Now →", key="btn_quick_revise", use_container_width=True):
                    orch.state = "RECALL"
                    orch.current_concept_id = ctx.get("target_concept")
                    st.rerun()

        # ---------------------------------------------------------------------
        # PHASE 28: CHAT COMPOSER DESIGN (FLOATING ROUNDED CONTAINER)
        # ╭──────────────────────────────────────────────╮
        # │                                              │
        # │  Ask EduMentor anything about your learning  │
        # │                                              │
        # │                                              │
        # │  ＋ Upload notes                     ↑       │
        # ╰──────────────────────────────────────────────╯
        # ---------------------------------------------------------------------
        st.markdown(clean_html_for_markdown(get_composer_css()), unsafe_allow_html=True)

        composer_placeholder = ctx.get("placeholder") or DEFAULT_COMPOSER_PLACEHOLDER

        # Placeholder for dynamic transformation into processing state
        composer_slot = st.empty()

        with composer_slot.container():
            st.markdown("""
            <div class="floating-composer">
            """, unsafe_allow_html=True)

            # Floating Composer Text Input
            composer_text = st.text_area(
                label="Ask EduMentor anything about your learning",
                placeholder=composer_placeholder,
                height=95,
                key="floating_composer_input",
                label_visibility="collapsed"
            )

            # Bottom row of composer: ＋ Upload notes on left, ↑ on right
            b_col_upload, b_col_send = st.columns([3, 1])

            with b_col_upload:
                uploaded_files = st.file_uploader(
                    "＋ Upload notes",
                    type=["pdf", "txt", "md"],
                    accept_multiple_files=True,
                    key="floating_composer_files",
                    label_visibility="visible",
                    help="Drop PDF lecture slides, textbook chapters, or markdown notes."
                )

            with b_col_send:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                send_triggered = st.button("↑", key="composer_send_btn", use_container_width=True, help="Send message or process notes")

            # File attachment indicator chips if selected
            if uploaded_files:
                import html as py_html
                chips_html = "".join(
                    f"<span style='display:inline-flex;align-items:center;gap:6px;background:rgba(37,216,232,0.12);border:1px solid rgba(37,216,232,0.3);border-radius:14px;padding:3px 12px;font-size:12px;color:#25D8E8;margin-right:6px;margin-bottom:6px;'>📄 {py_html.escape(f.name)}</span>"
                    for f in uploaded_files
                )
                st.markdown(f"<div style='margin-top: 10px;'>{chips_html}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # Handle Composer Submission (Unified typing and file upload)
        if send_triggered:
            handled = False
            # 1. Process files if uploaded with honest step progression
            if uploaded_files:
                first_name = uploaded_files[0].name

                # Step 1: Reading your notes
                composer_slot.markdown(
                    render_composer_processing_card(
                        filename=first_name,
                        progress_pct=20,
                        status_text="Reading your notes..."
                    ),
                    unsafe_allow_html=True
                )

                combined_text = ""
                for uf in uploaded_files:
                    file_bytes = uf.read()
                    if uf.name.lower().endswith(".pdf"):
                        # Step 2: Identifying major topics & chunking
                        composer_slot.markdown(
                            render_composer_processing_card(
                                filename=first_name,
                                progress_pct=45,
                                status_text="Identifying major topics & extracting hierarchy..."
                            ),
                            unsafe_allow_html=True
                        )
                        orch.ingest_pdf(file_bytes, filename=uf.name)
                        handled = True
                    else:
                        text = file_bytes.decode("utf-8", errors="replace")
                        combined_text += f"\n\n--- Module: {uf.name} ---\n\n" + text

                if combined_text and not handled:
                    composer_slot.markdown(
                        render_composer_processing_card(
                            filename=first_name,
                            progress_pct=50,
                            status_text="Breaking topics into subtopics..."
                        ),
                        unsafe_allow_html=True
                    )
                    orch.ingest_notes_text(combined_text, title=first_name)
                    handled = True

                # Step 5: Preparing study path
                composer_slot.markdown(
                    render_composer_processing_card(
                        filename=first_name,
                        progress_pct=100,
                        status_text="Preparing your study path..."
                    ),
                    unsafe_allow_html=True
                )

            # 2. Process typed text if provided
            elif composer_text.strip():
                orch.handle_user_chat(composer_text.strip())
                handled = True

            if handled:
                # Automatically transform into the learning conversation
                st.rerun()

        # Quick Jump / Recently Studied Topic Cards
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin: 28px 0 12px 0;">
            <span style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B;">
                Recently Studied / Instant Curricula
            </span>
            <span style="font-size: 11px; color: #475569;">Instant concept graph generation</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⚡ Operating Systems\n\nScheduling & Virtual Memory", use_container_width=True, key="quick_os"):
                orch.load_sample_module("Operating Systems")
                st.rerun()
        with col2:
            if st.button("🧠 Machine Learning\n\nGradients & Regularization", use_container_width=True, key="quick_ml"):
                orch.load_sample_module("Machine Learning")
                st.rerun()
        with col3:
            if st.button("🏗️ System Design\n\nScale & Consensus", use_container_width=True, key="quick_sys"):
                orch.load_sample_module("System Design")
                st.rerun()
        with col4:
            if st.button("🌳 Data Structures\n\nTrees, Graphs & DP", use_container_width=True, key="quick_dsa"):
                orch.load_sample_module("Data Structures")
                st.rerun()

    # -------------------------------------------------------------------------
    # 2. CONVERSATIONAL WORKSPACE (STUDY / RECALL / FEEDBACK)
    # -------------------------------------------------------------------------
    else:
        # Subtle HUD Header in Conversational Mode
        concept_title = orch.concepts.get(orch.current_concept_id, {}).get("title", orch.curriculum_title or "Study Session")
        hud_html = f"""
        <div style="
            display: flex; align-items: center; justify-content: space-between;
            background: #0D1117; border: 1px solid #27303B; border-radius: 12px;
            padding: 10px 16px; margin-bottom: 16px;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #25D8E8; box-shadow: 0 0 8px #25D8E8;"></span>
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #25D8E8;">Active Module</span>
                <span style="font-size: 13.5px; font-weight: 600; color: #FFFFFF;">• {concept_title}</span>
            </div>
            <div style="font-size: 11.5px; color: #94A3B8;">
                EduMentor AI Teacher Online
            </div>
        </div>
        """
        st.markdown(clean_html_for_markdown(hud_html), unsafe_allow_html=True)

        for idx, msg in enumerate(orch.chat_history):
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            is_latest_assistant = (role == "assistant" and idx == len(orch.chat_history) - 1)

            if role == "assistant":
                expression = msg.get("expression_state") or getattr(orch, "teacher_state", "greeting")
                if getattr(orch, "is_major_message", lambda m: True)(msg):
                    render_teacher_message(
                        text=content,
                        expression=expression,
                        concept_title=orch.concepts.get(orch.current_concept_id, {}).get("title") if is_latest_assistant and orch.current_concept_id else None,
                        avatar_size=56
                    )
                else:
                    render_status_notice(text=content)
            else:
                render_chat_bubble(role="user", content=content, student_initial=student_name[0] if student_name else "A")

            if is_latest_assistant:
                # A. Studying state concept card
                if orch.state == "STUDYING" and orch.current_concept_id and orch.current_concept_id in orch.concepts:
                    # Phase 4: Display compact study-path visualization automatically
                    if orch.topological_order:
                        render_compact_study_path(
                            topological_order=orch.topological_order,
                            concepts=orch.concepts,
                            current_concept_id=orch.current_concept_id
                        )

                    c = orch.concepts[orch.current_concept_id]
                    tier = c.get("tier", 0)
                    tier_label = "Tier 0: Foundational" if tier == 0 else ("Tier 1: Intermediate" if tier == 1 else "Tier 2: Advanced")

                    major_topic = c.get("major_topic")
                    major_eyebrow = f"<div style='font-size: 11px; font-weight: 700; color: #25D8E8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;'>📂 {major_topic}</div>" if major_topic and major_topic.lower() != c['title'].lower() else ""

                    page_num = c.get("source_page")
                    page_badge = f"<span style='font-size: 11px; color: #94A3B8; background: rgba(255,255,255,0.04); padding: 2px 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);'>📄 Page {page_num}</span>" if page_num else ""

                    named_methods = c.get("named_types_or_methods") or []
                    named_html = ""
                    if named_methods:
                        chips_list = "".join(f"<span style='background: rgba(37,216,232,0.12); border: 1px solid rgba(37,216,232,0.3); border-radius: 4px; padding: 2px 7px; font-size: 11px; color: #7DD3FC; font-weight: 500; margin-right: 6px; display: inline-block; margin-bottom: 4px;'>{m}</span>" for m in named_methods)
                        named_html = f"<div style='margin-bottom: 10px;'><span style='font-size: 11.5px; color: #94A3B8; margin-right: 6px;'>Key Methods & Types:</span>{chips_list}</div>"

                    defs_list = c.get("definitions") or []
                    defs_html = ""
                    if defs_list:
                        defs_inner = "".join(f"<div style='margin-bottom: 4px;'>📖 <em>{d}</em></div>" for d in defs_list)
                        defs_html = f"<div style='background: rgba(139, 92, 246, 0.09); border-left: 3px solid #8B5CF6; padding: 8px 12px; border-radius: 0 6px 6px 0; margin-bottom: 12px; font-size: 12.5px; color: #E2E8F0;'>{defs_inner}</div>"

                    principles_list = c.get("key_points") or c.get("principles", [])
                    principles_html = "".join(f"<li style='margin-bottom: 4px;'>{p}</li>" for p in principles_list)

                    card_html = f"""
                    <div style="
                        background: #0D1117;
                        border: 1px solid #27303B;
                        border-radius: 14px;
                        padding: 18px 20px;
                        margin: 14px 0;
                        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
                    ">
                        {major_eyebrow}
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 16px; font-weight: 700; color: #F8FAFC;">{c['title']}</span>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                {page_badge}
                                <span style="
                                    font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 20px;
                                    background: rgba(37, 216, 232, 0.12); color: #25D8E8; border: 1px solid rgba(37, 216, 232, 0.3);
                                ">{tier_label}</span>
                            </div>
                        </div>
                        <div style="
                            font-size: 13.5px; color: #94A3B8; background: #161B22; border-left: 3px solid #25D8E8;
                            padding: 10px 14px; border-radius: 0 8px 8px 0; margin-bottom: 12px; line-height: 1.5;
                        ">
                            {c.get('summary', '')}
                        </div>
                        {defs_html}
                        {named_html}
                        <strong style="font-size: 13px; color: #CBD5E1;">Key Intuitions to Master:</strong>
                        <ul style="margin: 8px 0 12px 20px; font-size: 13px; color: #E2E8F0; line-height: 1.6;">
                            {principles_html}
                        </ul>
                    </div>
                    """
                    st.markdown(clean_html_for_markdown(card_html), unsafe_allow_html=True)

                    if st.button("I'm Ready to Recall →", key="btn_ready_recall", use_container_width=True):
                        orch.trigger_ready_for_recall()
                        st.rerun()

                # B. Feedback & Diagnostic rubric state
                elif orch.state == "FEEDBACK" and orch.last_evaluation and orch.current_concept_id in orch.concepts:
                    if orch.topological_order:
                        render_compact_study_path(
                            topological_order=orch.topological_order,
                            concepts=orch.concepts,
                            current_concept_id=orch.current_concept_id
                        )

                    ev = orch.last_evaluation
                    c = orch.concepts[orch.current_concept_id]
                    quality = ev.get("quality_q", 0)

                    if quality < 3:
                        render_loopback_alert(
                            concept_name=c.get("title", "Topic"),
                            quality_score=quality,
                            tip=ev.get("actionable_tip", "")
                        )

                    render_recall_feedback(
                        eval_result={
                            "score": ev.get("composite_score", 0) / 100.0,
                            "quality_score": quality,
                            "verdict": ev.get("verdict", "Evaluated"),
                            "semantic_similarity": ev.get("semantic_similarity_score", 0) / 100.0,
                            "llm_score": ev.get("judge_score", 0) / 100.0,
                            "strengths": ev.get("strengths", []),
                            "missing_points": ev.get("missing_concepts", []),
                            "actionable_tip": ev.get("actionable_tip", ""),
                            "summary": ""
                        },
                        sm2_data={
                            "interval_days": c.get("interval_days", 1),
                            "ease_factor": c.get("easiness_factor", 2.5),
                            "repetitions": c.get("repetitions", 1)
                        }
                    )

                    if st.button("Continue to Next Concept →", key="btn_continue_next", use_container_width=True):
                        orch.advance_next_step()
                        st.rerun()

        # Option 2: Upload answer file during recall phase
        if orch.state == "WAITING_RECALL":
            with st.expander("📎 Option 2: Upload Handwritten / Typed Answer (PDF or TXT)", expanded=False):
                ans_file = st.file_uploader(
                    "Upload answer document",
                    type=["pdf", "txt"],
                    key=f"recall_ans_uploader_{orch.current_concept_id}",
                    help="EduMentor parses and evaluates your answer using the hybrid evaluation engine."
                )
                if ans_file is not None and st.button("Submit Answer File →", key=f"btn_submit_ans_{orch.current_concept_id}"):
                    content = ans_file.read()
                    if ans_file.name.lower().endswith(".pdf"):
                        from edumentor.extractor import extract_text_from_pdf
                        _, text = extract_text_from_pdf(content)
                    else:
                        text = content.decode("utf-8", errors="replace")
                    orch.submit_recall_response(text if text.strip() else "Uploaded blank answer file.")
                    st.rerun()

        # Dynamic placeholder for conversational composer
        if orch.state == "WAITING_RECALL":
            c_title = orch.concepts.get(orch.current_concept_id, {}).get("title", "this concept")
            c_placeholder = f"Write what you remember about {c_title} from memory..."
        elif orch.state == "STUDYING":
            c_placeholder = "Tell me when you're ready... (or ask any question about this concept)"
        else:
            c_placeholder = "Explain from memory, ask a question, or continue..."

        # Phase 24: Conversation Memory & Session Context Inspector
        with st.expander("🧠 Session Context & Memory (Phase 24)", expanded=False):
            mem_summary = orch.memory.get_summary()
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown(f"**Current Subject**: `{mem_summary['current_subject'].get('title') or 'None'}`")
                st.markdown(f"**Current Module**: `{mem_summary['current_module'].get('title') or 'None'}`")
                st.markdown(f"**Current Concept**: `{mem_summary['current_concept'].get('title') or 'None'}`")
                st.markdown(f"**Current Mastery**: `{mem_summary['current_mastery'].get('concept_level', 'Learning')} ({mem_summary['current_mastery'].get('concept_score', 0):.0f}%)`")
            with s_col2:
                st.markdown(f"**Next Review**: `{mem_summary['next_review'].get('next_review_date') or 'Not scheduled'}`")
                st.markdown(f"**Previous Concepts Studied**: `{len(mem_summary['previous_concepts'])}`")
                st.markdown(f"**Previous Answers Recorded**: `{len(mem_summary['previous_answers'])}`")
                st.markdown(f"**Previous Evaluations/Feedback**: `{len(mem_summary['previous_feedback'])}`")

        chat_prompt = st.chat_input(c_placeholder)
        if chat_prompt:
            orch.handle_user_chat(chat_prompt)
            st.rerun()
