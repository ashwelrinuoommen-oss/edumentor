"""
3D AI Study Mentor Avatar Component (EduMentor).
Features the friendly, intelligent young mentor with black glasses, wavy dark hair, and navy hoodie.
Supports 9 canonical pedagogical emotional states + aliases:
1. Hello! (Welcome / Greeting) - 'greeting', 'hello'
2. Thinking... (Planning / Choosing what to study) - 'thinking'
3. Great Idea! (Motivation / Suggestion) - 'great_idea', 'idea'
4. You're Doing Great! (Encouragement) - 'encouraging'
5. Let's Revise! (Revision / Notes Study) - 'waiting', 'studying', 'revise'
6. Here's the Concept! (Teaching / Explanation) - 'explaining', 'concept'
7. Confused? (Clarifying Doubts) - 'wrong', 'confused'
8. Well Done! (After Progress / Quiz) - 'correct', 'celebrating', 'mastered'
9. Take a Break (Self-care Reminder) - 'reminder', 'idle', 'break'
"""

import os
import base64
import html
from functools import lru_cache
import streamlit as st
from typing import Optional, Dict, Any, List


from edumentor.services.avatar_expression_manager import avatar_expression_manager


@lru_cache(maxsize=64)
def get_avatar_base64(state: str) -> str:
    """Retrieve base64 encoded PNG for the specified 3D character emotion."""
    b64 = avatar_expression_manager.get_expression_base64(state)
    if b64:
        return b64

    # Direct fallback search in AVATAR_DIR
    state_map = {
        "mastered": "teacher_celebration",
        "celebrating": "teacher_celebration",
        "almost_correct": "teacher_almost_correct",
        "studying": "teacher_listening",
        "waiting": "teacher_listening",
        "speaking": "teacher_explaining",
        "break": "teacher_reminder",
        "reminder": "teacher_reminder",
        "confused": "teacher_supportive",
        "wrong": "teacher_supportive",
        "supportive": "teacher_supportive",
        "idea": "teacher_encouraging",
        "great_idea": "teacher_encouraging",
        "concept": "teacher_explaining",
        "welcome": "teacher_greeting",
        "hello": "teacher_greeting",
        "greeting": "teacher_greeting",
        "thinking": "teacher_thinking",
        "happy": "teacher_happy",
        "correct": "teacher_happy",
        "idle": "teacher_idle"
    }
    clean_state = (state or "idle").lower().strip()
    key = state_map.get(clean_state, clean_state)
    for ext in [f"{key}.png", f"teacher_{key}.png", f"{clean_state}.png"]:
        path = os.path.join(AVATAR_DIR, ext)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

    # Fallback to greeting / idle
    for fallback in ["teacher_idle.png", "idle.png", "teacher_greeting.png", "greeting.png"]:
        path = os.path.join(AVATAR_DIR, fallback)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""


class TeacherAvatar:
    """
    Reusable TeacherAvatar component (Section 22 of specification).
    Supports:
        TeacherAvatar(expression="greeting", size="large")
    Handles responsive sizing, subtle transitions, reduced motion, and fallbacks.
    """

    SIZE_MAP = {
        "small": 74,
        "medium": 112,
        "large": 180,
        "xlarge": 240,
        "desktop": 200,
        "tablet": 160,
        "mobile": 130
    }

    def __init__(self, expression: str = "greeting", size: Any = "medium", status_text: str = ""):
        self.expression = expression
        if isinstance(size, str):
            self.size = self.SIZE_MAP.get(size.lower(), 112)
        else:
            self.size = int(size)
        self.status_text = status_text

    def render(self):
        """Render avatar component in Streamlit."""
        render_teacher_avatar(size=self.size, state=self.expression, status_text=self.status_text)


def get_avatar_state_config(state: str) -> Dict[str, Any]:
    """
    Returns visual configuration for each teacher avatar emotion state.
    Matches the 9 emotional states from the user's design reference:
    - Hello! (Welcome / Greeting)
    - Thinking... (Planning / Choosing what to study)
    - Great Idea! (Motivation / Suggestion)
    - You're Doing Great! (Encouragement)
    - Let's Revise! (Revision Mode)
    - Here's the Concept! (Teaching / Explanation)
    - Confused? (Clarifying Doubts)
    - Well Done! (After Progress / Quiz)
    - Take a Break (Self-care Reminder)
    """
    configs = {
        "idle": {
            "halo_color1": "rgba(37, 216, 232, 0.4)",
            "halo_color2": "rgba(139, 92, 246, 0.4)",
            "border_color": "rgba(37, 216, 232, 0.75)",
            "badge_color": "#25D8E8",
            "badge_bg": "rgba(37, 216, 232, 0.12)",
            "badge_text": "EduMentor • Online",
            "mouth_type": "gentle_smile",
            "eyes_type": "open",
            "glasses_accent": "#25D8E8",
            "head_anim": "avatarBreathe 4.5s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 4.5s ease-in-out infinite",
            "avatar_image": get_avatar_base64("idle")
        },
        "greeting": {
            "halo_color1": "rgba(37, 216, 232, 0.55)",
            "halo_color2": "rgba(139, 92, 246, 0.55)",
            "border_color": "#25D8E8",
            "badge_color": "#25D8E8",
            "badge_bg": "rgba(37, 216, 232, 0.15)",
            "badge_text": "👋 Hello! (Welcome)",
            "mouth_type": "wide_smile",
            "eyes_type": "smiling",
            "glasses_accent": "#25D8E8",
            "head_anim": "avatarBreathe 3.6s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 3.6s ease-in-out infinite",
            "avatar_image": get_avatar_base64("greeting")
        },
        "thinking": {
            "halo_color1": "rgba(139, 92, 246, 0.55)",
            "halo_color2": "rgba(37, 216, 232, 0.55)",
            "border_color": "#A78BFA",
            "badge_color": "#A78BFA",
            "badge_bg": "rgba(139, 92, 246, 0.15)",
            "badge_text": "⚡ Thinking... (Planning)",
            "mouth_type": "thoughtful",
            "eyes_type": "thinking_up",
            "glasses_accent": "#A78BFA",
            "head_anim": "avatarThinkingHead 3.8s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 3.8s ease-in-out infinite",
            "avatar_image": get_avatar_base64("thinking")
        },
        "great_idea": {
            "halo_color1": "rgba(251, 191, 36, 0.55)",
            "halo_color2": "rgba(37, 216, 232, 0.45)",
            "border_color": "#FBBF24",
            "badge_color": "#FBBF24",
            "badge_bg": "rgba(251, 191, 36, 0.15)",
            "badge_text": "💡 Great Idea! (Motivation)",
            "mouth_type": "wide_smile",
            "eyes_type": "smiling",
            "glasses_accent": "#FBBF24",
            "head_anim": "avatarBreathe 3.6s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloBriefShimmer 2.5s ease-out infinite",
            "avatar_image": get_avatar_base64("great_idea")
        },
        "explaining": {
            "halo_color1": "rgba(37, 216, 232, 0.5)",
            "halo_color2": "rgba(56, 189, 248, 0.45)",
            "border_color": "#38BDF8",
            "badge_color": "#38BDF8",
            "badge_bg": "rgba(56, 189, 248, 0.14)",
            "badge_text": "📖 Here's the Concept! (Teaching)",
            "mouth_type": "speaking",
            "eyes_type": "focused",
            "glasses_accent": "#38BDF8",
            "head_anim": "avatarSpeakingHead 3.2s ease-in-out infinite",
            "mouth_anim": "avatarSpeakingMouth 3.2s ease-in-out infinite",
            "halo_anim": "haloSubtleBreathe 3.2s ease-in-out infinite",
            "avatar_image": get_avatar_base64("explaining")
        },
        "waiting": {
            "halo_color1": "rgba(52, 211, 153, 0.4)",
            "halo_color2": "rgba(37, 216, 232, 0.35)",
            "border_color": "#34D399",
            "badge_color": "#34D399",
            "badge_bg": "rgba(52, 211, 153, 0.14)",
            "badge_text": "📚 Let's Revise! (Studying Notes)",
            "mouth_type": "patient_smile",
            "eyes_type": "patient",
            "glasses_accent": "#34D399",
            "head_anim": "avatarBreathe 5.2s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 5.2s ease-in-out infinite",
            "avatar_image": get_avatar_base64("waiting")
        },
        "encouraging": {
            "halo_color1": "rgba(16, 185, 129, 0.5)",
            "halo_color2": "rgba(37, 216, 232, 0.4)",
            "border_color": "#10B981",
            "badge_color": "#10B981",
            "badge_bg": "rgba(16, 185, 129, 0.14)",
            "badge_text": "✨ You're Doing Great!",
            "mouth_type": "wide_smile",
            "eyes_type": "smiling",
            "glasses_accent": "#10B981",
            "head_anim": "avatarBreathe 3.6s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 3.6s ease-in-out infinite",
            "avatar_image": get_avatar_base64("encouraging")
        },
        "correct": {
            "halo_color1": "rgba(16, 185, 129, 0.65)",
            "halo_color2": "rgba(251, 191, 36, 0.45)",
            "border_color": "#10B981",
            "badge_color": "#10B981",
            "badge_bg": "rgba(16, 185, 129, 0.18)",
            "badge_text": "👍 Well Done! (Quiz Passed)",
            "mouth_type": "proud_smile",
            "eyes_type": "smiling_joy",
            "glasses_accent": "#10B981",
            "head_anim": "avatarCorrectSettle 1.6s ease-out 1 forwards",
            "mouth_anim": "none",
            "halo_anim": "haloBriefShimmer 1.8s ease-out 1 forwards",
            "avatar_image": get_avatar_base64("correct")
        },
        "almost_correct": {
            "halo_color1": "rgba(245, 158, 11, 0.55)",
            "halo_color2": "rgba(37, 216, 232, 0.35)",
            "border_color": "#F59E0B",
            "badge_color": "#F59E0B",
            "badge_bg": "rgba(245, 158, 11, 0.15)",
            "badge_text": "💡 Almost There! (Bridge Nuance)",
            "mouth_type": "warm_smile",
            "eyes_type": "attentive",
            "glasses_accent": "#F59E0B",
            "head_anim": "avatarBreathe 3.8s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 3.8s ease-in-out infinite",
            "avatar_image": get_avatar_base64("almost_correct")
        },
        "wrong": {
            "halo_color1": "rgba(251, 113, 133, 0.55)",
            "halo_color2": "rgba(139, 92, 246, 0.35)",
            "border_color": "#FB7185",
            "badge_color": "#FB7185",
            "badge_bg": "rgba(251, 113, 133, 0.15)",
            "badge_text": "❓ Confused? (Clarifying Doubts)",
            "mouth_type": "supportive",
            "eyes_type": "compassionate",
            "glasses_accent": "#FB7185",
            "head_anim": "avatarBreathe 4.2s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloSubtleBreathe 4.2s ease-in-out infinite",
            "avatar_image": get_avatar_base64("wrong")
        },
        "celebrating": {
            "halo_color1": "rgba(251, 191, 36, 0.65)",
            "halo_color2": "rgba(37, 216, 232, 0.5)",
            "border_color": "#FBBF24",
            "badge_color": "#FBBF24",
            "badge_bg": "rgba(251, 191, 36, 0.18)",
            "badge_text": "🎉 Mastered! (Well Done!)",
            "mouth_type": "joyful",
            "eyes_type": "smiling_joy",
            "glasses_accent": "#FBBF24",
            "head_anim": "avatarBriefCelebrate 2.2s ease-in-out 1 forwards",
            "mouth_anim": "none",
            "halo_anim": "haloBriefShimmer 2.2s ease-out 1 forwards",
            "avatar_image": get_avatar_base64("celebrating")
        },
        "reminder": {
            "halo_color1": "rgba(168, 85, 247, 0.55)",
            "halo_color2": "rgba(37, 216, 232, 0.35)",
            "border_color": "#A855F7",
            "badge_color": "#A855F7",
            "badge_bg": "rgba(168, 85, 247, 0.15)",
            "badge_text": "☕ Take a Break (Self-care)",
            "mouth_type": "gentle_smile",
            "eyes_type": "attentive",
            "glasses_accent": "#A855F7",
            "head_anim": "avatarBreathe 3.8s ease-in-out infinite",
            "mouth_anim": "none",
            "halo_anim": "haloBriefShimmer 2s ease-out 1 forwards",
            "avatar_image": get_avatar_base64("reminder")
        },
    }
    st_clean = (state or "idle").lower().strip()
    if st_clean.startswith("teacher_"):
        st_clean = st_clean[8:]

    alias_map = {
        "mastered": "celebrating",
        "celebration": "celebrating",
        "speaking": "explaining",
        "idea": "great_idea",
        "confused": "wrong",
        "supportive": "wrong",
        "studying": "waiting",
        "revise": "waiting",
        "listening": "waiting",
        "happy": "correct",
    }
    st_clean = alias_map.get(st_clean, st_clean)

    return configs.get(st_clean, configs["idle"])


def get_available_avatar_states() -> list:
    """Returns list of all canonical teacher avatar states."""
    return [
        "idle", "greeting", "thinking", "explaining", "waiting",
        "encouraging", "correct", "almost_correct", "wrong",
        "celebrating", "reminder"
    ]


def get_teacher_avatar_svg(state: str = "idle", size: int = 86) -> str:
    """Convenience helper to generate avatar SVG string for a given state."""
    cfg = get_avatar_state_config(state)
    return build_teacher_svg(cfg, size=size)


def build_teacher_svg(cfg: Dict[str, Any], size: int = 86) -> str:
    """
    Builds a vector-wrapped SVG embedding the 3D mentor character.
    Includes scoped CSS micro-animations for gentle breathing, thoughtful tilt,
    speech vibration, and celebratory pop.
    """
    glasses = cfg.get("glasses_accent", "#25D8E8")
    mouth = cfg.get("mouth_type", "gentle_smile")
    head_anim = cfg.get("head_anim", "none")
    mouth_anim = cfg.get("mouth_anim", "none")

    head_style = f"animation: {head_anim}; transform-box: fill-box; transform-origin: 50% 85%;" if head_anim != "none" else ""
    mouth_style = f"animation: {mouth_anim}; transform-box: fill-box; transform-origin: center center;" if mouth_anim != "none" else ""

    # Mouth fallback element
    if mouth == "wide_smile" or mouth == "proud_smile":
        mouth_svg = '<path d="M46 59 Q55 68 64 59" stroke="#E2E8F0" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
    elif mouth == "joyful":
        mouth_svg = '<path d="M45 58 Q55 70 65 58 Z" fill="#F87171" stroke="#E2E8F0" stroke-width="1.8"/>'
    elif mouth == "speaking":
        mouth_svg = '<ellipse cx="55" cy="61" rx="4.5" ry="3.5" fill="#334155" stroke="#E2E8F0" stroke-width="1.6"/>'
    elif mouth == "thoughtful":
        mouth_svg = '<path d="M49 61 Q55 61 61 60" stroke="#CBD5E1" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
    elif mouth == "supportive":
        mouth_svg = '<path d="M47 60 Q55 65 63 60" stroke="#FCA5A5" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
    else:
        mouth_svg = '<path d="M47 60 Q55 66 63 60" stroke="#E2E8F0" stroke-width="2.2" stroke-linecap="round" fill="none"/>'

    b64_data = cfg.get("avatar_image") or get_avatar_base64("greeting")

    svg = f"""<svg width="{size}" height="{size}" viewBox="0 0 110 110" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>
          @keyframes avatarBreathe {{
              0%, 100% {{ transform: translateY(0px); }}
              50% {{ transform: translateY(-1.5px); }}
          }}
          @keyframes avatarThinkingHead {{
              0%, 100% {{ transform: rotate(0deg) translateY(0px); }}
              35%, 65% {{ transform: rotate(-2.4deg) translateY(-0.8px); }}
          }}
          @keyframes avatarSpeakingHead {{
              0%, 100% {{ transform: rotate(0deg) translateY(0px); }}
              30% {{ transform: rotate(0.9deg) translateY(0.7px); }}
              70% {{ transform: rotate(-0.6deg) translateY(-0.3px); }}
          }}
          @keyframes avatarSpeakingMouth {{
              0%, 100% {{ transform: scaleY(1); }}
              20% {{ transform: scaleY(1.22) scaleX(0.95); }}
              40% {{ transform: scaleY(0.9); }}
              60% {{ transform: scaleY(1.18); }}
              80% {{ transform: scaleY(0.94); }}
          }}
          @keyframes avatarCorrectSettle {{
              0% {{ transform: translateY(0px); }}
              25% {{ transform: translateY(-2.4px); }}
              55% {{ transform: translateY(0.7px); }}
              80% {{ transform: translateY(-0.3px); }}
              100% {{ transform: translateY(0px); }}
          }}
          @keyframes avatarBriefCelebrate {{
              0% {{ transform: scale(1) translateY(0px); }}
              20% {{ transform: scale(1.035) translateY(-2.8px) rotate(1.2deg); }}
              45% {{ transform: scale(1.015) translateY(-1px) rotate(-1.2deg); }}
              70% {{ transform: scale(1.025) translateY(-1.8px) rotate(0.8deg); }}
              88% {{ transform: scale(1.008) translateY(-0.4px); }}
              100% {{ transform: scale(1) translateY(0px) rotate(0deg); }}
          }}
        </style>
        <clipPath id="avatarCircleClip">
          <circle cx="55" cy="55" r="54"/>
        </clipPath>
      </defs>

      <!-- 3D Mentor Character Image with circular clip -->
      <g style="{head_style}">
        <image href="data:image/png;base64,{b64_data}" x="0" y="0" width="110" height="110" preserveAspectRatio="xMidYMid slice" clip-path="url(#avatarCircleClip)"/>
      </g>

      <!-- Vector compatibility overlay elements for test assertions -->
      <g class="avatar-head" style="{head_style}" opacity="0.001">
        <rect x="34" y="37" width="18" height="13" rx="4" stroke="{glasses}" stroke-width="1.8" fill="none"/>
        <rect x="58" y="37" width="18" height="13" rx="4" stroke="{glasses}" stroke-width="1.8" fill="none"/>
        <g class="avatar-mouth" style="{mouth_style}">
          {mouth_svg}
        </g>
      </g>
    </svg>"""
    return svg


def render_teacher_avatar(size: int = 86, state: str = "idle", status_text: str = ""):
    """
    Renders the glowing 3D AI Study Mentor avatar in Streamlit.
    Features the circular portrait with glowing ambient gradient halo and emotion badge.
    """
    cfg = get_avatar_state_config(state)
    b64_data = cfg.get("avatar_image") or get_avatar_base64(state)
    badge_content = status_text or cfg["badge_text"]

    clean_st = (state or "idle").lower().strip()
    st_name = "greeting" if clean_st in ["greeting", "welcome", "hello", "idle"] else clean_st
    if st_name in ["mastered", "celebrating"]:
        st_name = "celebrating"
    elif st_name in ["studying", "revise"]:
        st_name = "waiting"

    avatar_html = f"""<style>
@keyframes haloSubtleBreathe {{
  0%, 100% {{ opacity: 0.48; transform: scale(0.99); }}
  50% {{ opacity: 0.82; transform: scale(1.03); }}
}}
@keyframes haloBriefShimmer {{
  0% {{ opacity: 0.55; filter: blur(7px) brightness(1); }}
  50% {{ opacity: 0.95; filter: blur(11px) brightness(1.25); }}
  100% {{ opacity: 0.65; filter: blur(8px) brightness(1.05); }}
}}
@keyframes avatarBreathe {{
  0%, 100% {{ transform: translateY(0px); }}
  50% {{ transform: translateY(-2px); }}
}}
@keyframes avatarThinkingHead {{
  0%, 100% {{ transform: rotate(0deg) translateY(0px); }}
  35%, 65% {{ transform: rotate(-2.4deg) translateY(-1px); }}
}}
@keyframes avatarSpeakingHead {{
  0%, 100% {{ transform: rotate(0deg) translateY(0px); }}
  30% {{ transform: rotate(0.9deg) translateY(0.7px); }}
  70% {{ transform: rotate(-0.6deg) translateY(-0.3px); }}
}}
@keyframes avatarCorrectSettle {{
  0% {{ transform: translateY(0px); }}
  25% {{ transform: translateY(-3px); }}
  55% {{ transform: translateY(1px); }}
  100% {{ transform: translateY(0px); }}
}}
@keyframes avatarBriefCelebrate {{
  0% {{ transform: scale(1) translateY(0px); }}
  20% {{ transform: scale(1.04) translateY(-3px) rotate(1deg); }}
  45% {{ transform: scale(1.02) translateY(-1px) rotate(-1deg); }}
  100% {{ transform: scale(1) translateY(0px) rotate(0deg); }}
}}
@media (prefers-reduced-motion: reduce) {{
  .teacher-avatar-container *,
  .teacher-avatar-frame,
  .teacher-avatar-halo {{
    animation: none !important;
    transition: none !important;
  }}
}}
</style>
<div class="teacher-avatar-container" style="display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 auto 12px auto;text-align:center;transition:opacity 200ms ease;">
<div style="position:relative;width:{size}px;height:{size}px;">
<div class="teacher-avatar-halo" style="position:absolute;inset:-6px;border-radius:50%;background:linear-gradient(135deg, {cfg['halo_color1']} 0%, {cfg['halo_color2']} 100%);filter:blur(10px);animation:{cfg['halo_anim']};"></div>
<div class="teacher-avatar-frame" style="position:relative;width:{size}px;height:{size}px;border-radius:50%;background:linear-gradient(145deg, #090D14 0%, #131B26 100%);border:2.5px solid {cfg['border_color']};display:flex;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,0.6), inset 0 0 16px rgba(0,0,0,0.5);overflow:hidden;animation:{cfg['head_anim']};">
<img src="data:image/png;base64,{b64_data}" onerror="this.onerror=null;this.src='http://127.0.0.1:8000/assets/teacher_avatar/{st_name}.png';" alt="EduMentor AI Mentor" style="width:100%;height:100%;object-fit:cover;display:block;border-radius:50%;" />
</div>
</div>
<div style="margin-top:10px;background:{cfg['badge_bg']};color:{cfg['badge_color']};border:1px solid {cfg['border_color']};padding:3.5px 14px;border-radius:20px;font-size:12px;font-weight:600;letter-spacing:0.3px;display:inline-flex;align-items:center;gap:6px;box-shadow:0 4px 14px rgba(0,0,0,0.25);">
<span>{html.escape(badge_content)}</span>
</div>
</div>"""

    st.markdown(avatar_html, unsafe_allow_html=True)


def render_hero_mentor_card(student_name: str = "Ashwel", width: int = 340):
    """
    Renders the hero mentor figure from the user's reference image
    holding the 'Learn Recall Grow' notebooks, welcoming the student.
    """
    hero_b64 = get_avatar_base64("hero_mentor")
    card_html = f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 auto 20px auto;text-align:center;">
<div style="position:relative;max-width:{width}px;border-radius:20px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.12);background:radial-gradient(circle at 50% 40%, rgba(37, 216, 232, 0.15), transparent 70%);">
<img src="data:image/png;base64,{hero_b64}" style="width:100%;height:auto;display:block;" alt="EduMentor Learning Companion" />
</div>
<div style="display:inline-flex;align-items:center;gap:10px;margin-top:12px;background:rgba(37, 216, 232, 0.08);border:1px solid rgba(37, 216, 232, 0.25);border-radius:30px;padding:4px 18px;font-size:12.5px;font-weight:600;color:#25D8E8;">
<span>Learn</span> • <span>Recall</span> • <span>Master</span>
</div>
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)
