# EduMentor — Adaptive Concept Recall Mastery

> **"Your notes. Your recall. Your mastery."**  
> An AI study companion workspace designed to transform passive note-taking into active recall mastery.

---

## ⚡ Product Philosophy

EduMentor is **not a conventional Learning Management System (LMS)**. There are no cluttered, multi-tab admin dashboards for manually selecting concepts, questions, or revision schedules.

The **chat workspace is the product**. 

The student enters a focused, personal AI workspace:
1. **Talk / Upload:** Say *"I want to study Operating Systems"* or drop lecture notes (PDF/Markdown).
2. **Analyze:** EduMentor silently parses notes, extracts atomic concepts, constructs a prerequisite Directed Acyclic Graph (DAG), and resolves cycles.
3. **Study:** The AI teacher introduces the first concept intuition and core principles.
4. **Recall:** Prompts an active retrieval question requiring memory generation.
5. **Evaluate:** Evaluates answers using a **Two-Pillar Hybrid Engine** (Sentence Vector Cosine Similarity + LLM-as-Judge Rubric).
6. **Adaptive Schedule:** Computes SuperMemo SM-2 spaced repetition intervals. Any weak topic ($q < 3$) automatically loops back into the immediate study queue.
7. **Master:** Advance sequentially through topological depth tiers until complete mastery is achieved.

$$\text{Talk} \longrightarrow \text{Upload} \longrightarrow \text{Study} \longrightarrow \text{Recall} \longrightarrow \text{Feedback} \longrightarrow \text{Continue} \longrightarrow \text{Revisit} \longrightarrow \text{Master}$$

---

## 🎭 The Two-Layer Architecture: Complexity Belongs Behind the Interface

The defining architectural principle of EduMentor is strict separation between **The Human Experience (What the Student Sees)** and **The Scientific Machinery (What the System Executes)**:

```
┌──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┐
│        WHAT THE STUDENT SEES                 │               WHAT THE SYSTEM IS ACTUALLY DOING                         │
│       (Calm Conversational Layer)            │                  (Behind-the-Scenes Pipeline)                           │
├──────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤
│                  👩🏻                          │                                                                         │
│              AI TEACHER                      │                                                                         │
│  "Welcome back, Ashwel."                     │  Session hydration from SQLite & active module resolution               │
│  "What do you want to study?"                │                                                                         │
│                      ↓                       │                                                                         │
│              [ Upload Notes ]                │  PDF Ingestion: pdfplumber text parsing & chunking                      │
│                      ↓                       │  LLM Concept Extraction → Prerequisite Dependency Graph                 │
│  "I've gone through your notes."             │  NetworkX Cycle Resolution → Topological Sort → Study Path Depth Tiers  │
│  "Let's start with Processes."               │                                                                         │
│                      ↓                       │                                                                         │
│  "Let me know when you're ready."            │  Conversation State Machine: Transition to WAITING_FOR_RECALL            │
│  [ I'm Ready ]                               │                                                                         │
│                      ↓                       │                                                                         │
│  "Here's something I want you to explain..." │  Targeted Recall Question Generation modulated by note chunks           │
│                      ↓                       │                                                                         │
│               Student answers                │  Intake & semantic input validation                                     │
│                      ↓                       │  Two-Pillar Hybrid Evaluation:                                          │
│  "You're very close!"                        │    • sentence-transformers cosine similarity (40%)                       │
│  (Empathetic expression & hint)              │    • LLM-as-Judge rubric & misconception flags (60%)                     │
│                      ↓                       │  Mastery Engine: SuperMemo SM-2 interval & EF calculation                │
│  "Let's move on."                            │  SQLite Attempt persistence → Notification scheduler & Resurfacing      │
└──────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────┘
```

> **"The complexity belongs behind the interface."**  
> That is the key idea that makes EduMentor feel like a real product rather than an AI technology demo.

---

## 📋 Master Development Order (Strict 23-Phase Roadmap)

All subsystems and components follow this strict implementation and verification order:

| Phase | Milestone | Subsystem / Focus | Core Verification Test |
| :---: | :--- | :--- | :--- |
| **01** | **Authentication** | Salted SHA-256 user auth, profile switcher, scoped student state | [`tests/test_authentication.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_authentication.py) |
| **02** | **Main conversational workspace** | Focused 1-on-1 AI chat workspace, input card, teacher message thread | [`tests/test_workspace_phase2.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_workspace_phase2.py) |
| **03** | **PDF/TXT ingestion** | `pdfplumber` text extraction, file type/size validation, note chunking | [`tests/test_upload_phase3.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_upload_phase3.py) |
| **04** | **Concept extraction** | Atomic concept extraction, summary, key terms, definitions from chunked notes | [`tests/test_study_path_phase4.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_study_path_phase4.py) |
| **05** | **Dependency graph + study path** | `NetworkX` Directed Acyclic Graph, cycle breaking, topological depth tiers | [`tests/test_phase22_concept_dependency_engine.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase22_concept_dependency_engine.py) |
| **06** | **AI teacher conversation** | Empathetic conversational AI teacher, progressive explanations, intuition | [`tests/test_phase25_teacher_message_engine.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase25_teacher_message_engine.py) |
| **07** | **Recall question generation** | Active retrieval questions requiring generative memory recall | [`tests/test_study_and_question_gen_phase6_7.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_study_and_question_gen_phase6_7.py) |
| **08** | **Typed/PDF answer submission** | Chat composer response intake, PDF answer file submission, validation | [`tests/test_phase28_chat_composer_design.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase28_chat_composer_design.py) |
| **09** | **Semantic evaluation** | `sentence-transformers` vector cosine similarity ($S_{\text{sem}}$) | [`tests/test_hybrid_evaluation_phase9.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_hybrid_evaluation_phase9.py) |
| **10** | **LLM judge** | LLM-as-Judge rubric ($S_{\text{judge}}$), key concepts, misconception flags | [`tests/test_hybrid_evaluation_phase9.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_hybrid_evaluation_phase9.py) |
| **11** | **Hybrid evaluation** | Composite scoring ($S_{\text{comp}} = 0.40 \cdot S_{\text{sem}} + 0.60 \cdot S_{\text{judge}}$) and quality grade ($q \in [0, 5]$) | [`tests/test_hybrid_evaluation_phase9.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_hybrid_evaluation_phase9.py) |
| **12** | **Mastery engine** | Concept retention scores, topological depth-tier progression, mastery radar | [`tests/test_mastery_engine_phase10.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_mastery_engine_phase10.py) |
| **13** | **SM-2** | SuperMemo SM-2 interval scheduler ($I(1)=1, I(2)=6, I(n)=I(n-1)\cdot EF$) | [`tests/test_sm2.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_sm2.py) |
| **14** | **Automatic resurfacing** | Immediate adaptive loopback for weak concepts ($q < 3$) into study queue | [`tests/test_phase15_automatic_resurfacing.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase15_automatic_resurfacing.py) |
| **15** | **Notifications** | Notification center, study reminders, browser notification permissions | [`tests/test_phase16_notification_system.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase16_notification_system.py) |
| **16** | **History** | SQLite session history persistence, attempt logging, session reconstruction | [`tests/test_phase34_conversation_database.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase34_conversation_database.py) |
| **17** | **Progress** | Lightweight progress view, retention curve, depth-tier indicators | [`tests/test_phase19_progress_page.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase19_progress_page.py) |
| **18** | **Avatar system** | Empathetic animated avatar (5 emotional states), expression mapper | [`tests/test_avatar_personality_phase5.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_avatar_personality_phase5.py) |
| **19** | **Premium UI polish** | Curated 7-color palette, Geist/Inter typography, glass surfaces, subtle glow | [`tests/test_phase44_visual_quality_standard.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase44_visual_quality_standard.py) |
| **20** | **Accessibility** | Skip link, ARIA live announcer, 44×44px touch targets, `:focus-visible` | [`tests/test_phase32_accessibility.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase32_accessibility.py) |
| **21** | **Testing** | 45 automated unit & integration test suites across full codebase | [`tests/`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/) |
| **22** | **Performance + security** | Offscreen animation pausing, asset caching, input sanitization, IDOR guards | [`tests/test_phase35_security_and_privacy.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase35_security_and_privacy.py) |
| **23** | **Complete end-to-end validation** | 28-milestone full student journey validation from signup to mastery | [`tests/test_phase40_complete_journey.py`](file:///c:/Users/ASHWEL%20RINU%20OOMMEN/Downloads/Edumentor%20final/tests/test_phase40_complete_journey.py) |

---

## 🏛️ Recommended Architecture

EduMentor follows a clean, modular, and decoupled architecture:

```
edumentor/
│
├── app.py                      # Target Streamlit app router & multi-page coordinator
│
├── pages/                      # Modular UI views
│   ├── home.py                 # Primary conversational AI study companion workspace
│   ├── login.py                # Student authentication & quick profile switcher
│   ├── signup.py               # New student onboarding
│   ├── history.py              # Recall logs, retention analytics, and due revisions
│   └── settings.py             # LLM provider settings, API keys, SM-2 params
│
├── components/                 # Reusable UI widgets
│   ├── teacher_avatar.py       # Glowing personal AI teacher avatar
│   ├── chat_message.py         # Conversational chat bubbles
│   ├── upload_zone.py          # PDF / Markdown lecture notes uploader
│   ├── study_path.py           # Responsive SVG DAG Knowledge Graph visualizer
│   ├── concept_progress.py     # Concept cards & path progress indicators
│   ├── mastery_meter.py        # Comprehensive retention radar & mastery gauge
│   ├── recall_feedback.py      # Glassmorphic diagnostic rubric & score breakdown
│   └── notification.py         # Adaptive loopback alert banners & toasts
│
├── ai/                         # Machine learning & LLM interfaces
│   ├── llm_client.py           # Multi-provider abstraction (Claude, GPT, Gemini, Ollama, Demo)
│   ├── concept_extractor.py    # Extracts key concepts & atomic definitions
│   ├── dependency_extractor.py # Resolves prerequisite relationships
│   ├── question_generator.py   # Formulates targeted recall questions
│   ├── answer_evaluator.py     # Hybrid scoring & diagnostic engine
│   ├── feedback_generator.py   # Socratic scaffolding hints & coaching feedback
│   └── embeddings.py           # Sentence-transformers vector embeddings
│
├── services/                   # Application domain services
│   ├── ingestion_service.py    # PDF and lecture notes parsing pipeline
│   ├── study_path_service.py   # NetworkX topological DAG sequencing
│   ├── recall_service.py       # Active recall session coordinator
│   ├── mastery_service.py      # Retention analytics & mastery aggregation
│   ├── spaced_repetition_service.py # SuperMemo SM-2 interval scheduler
│   ├── notification_service.py # Due revision detection & alert dispatch
│   └── history_service.py      # Longitudinal recall logging & attempts retrieval
│
├── database/                   # Persistence layer
│   ├── models.py               # Domain dataclasses (User, Concept, Attempt, SM2Card)
│   ├── database.py             # SQLite WAL-mode schema manager
│   └── repository.py           # Data access repository layer
│
├── utils/                      # Helper utilities
│   ├── pdf_utils.py            # pdfplumber text extraction
│   ├── text_utils.py           # String normalization & chunking
│   ├── validators.py           # Quality and schema validators
│   └── security.py             # Salted SHA-256 password hashing
│
├── assets/                     # Visual brand assets
│   ├── teacher_avatar/         # SVG teacher avatars
│   └── illustrations/          # Graph & study path SVG vector diagrams
│
├── tests/                      # Automated test suites (34 tests passing)
│
├── .env                        # Local environment variables
├── .env.example                # Environment configuration template
├── requirements.txt            # Project dependencies
└── README.md                   # System documentation
```

---

## 🔬 Core Scientific Engines

### 1. Prerequisite Graph & Topological Sorting (`NetworkX`)
- Concepts form a **Directed Acyclic Graph (DAG)** where directed edges $(u, v)$ denote that concept $u$ is a prerequisite for concept $v$.
- Cycles are detected and broken via feedback arc set minimization to guarantee a strict topological order.
- Concepts are categorized into **Depth Tiers**:
  - **Tier 0:** Foundational primitives (no incoming edges in DAG).
  - **Tier 1:** Core mechanisms.
  - **Tier 2:** Advanced architectural patterns.

### 2. Hybrid Two-Pillar Evaluation Engine
Student recall responses are evaluated across two complementary dimensions:
1. **Semantic Vector Cosine Similarity ($S_{\text{sem}}$):** Encoded via `sentence-transformers/all-MiniLM-L6-v2` (with TF-IDF vectorizer fallback).
2. **LLM-as-Judge Rubric ($S_{\text{judge}}$):** Evaluates key concept coverage, factual fidelity, and flags misconceptions.
3. **Composite Score:**
   $$S_{\text{comp}} = 0.40 \cdot S_{\text{sem}} + 0.60 \cdot S_{\text{judge}}$$
4. **Quality Grade ($q \in [0, 5]$):**
   - $q = 5$: Perfect recall ($S_{\text{comp}} \ge 85\%$).
   - $q = 4$: Good recall ($70\% \le S_{\text{comp}} < 85\%$).
   - $q = 3$: Passable recall with serious effort ($55\% \le S_{\text{comp}} < 70\%$).
   - $q < 3$: Below mastery threshold $\rightarrow$ **Triggers immediate adaptive loopback**.

### 3. SuperMemo-2 (SM-2) Spaced Repetition
- Calculates optimal review intervals:
  $$I(1) = 1, \quad I(2) = 6, \quad I(n) = I(n-1) \cdot EF$$
  $$EF' = EF + (0.1 - (5 - q) \cdot (0.08 + (5 - q) \cdot 0.02))$$
- Minimum Easiness Factor floor: $EF \ge 1.30$.
- If $q < 3$, repetitions reset to $0$, interval resets to $1$ day, and the topic is placed in the high-priority review queue.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*Note: By default, EduMentor runs out-of-the-box in **Demo Mode** without requiring any external cloud API keys.*

### 3. Run EduMentor
You can launch either the Streamlit app or the FastAPI server:

**Launch Streamlit (Primary Experience):**
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

**Launch FastAPI Backend Server:**
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```
API documentation is available at `http://localhost:8000/docs`.

---

## 🧪 Running Automated Tests

Run the complete automated test suite (34 unit & integration tests):
```bash
python -m unittest discover tests -v
python -m unittest discover edumentor/tests -v
```

---

## 🎨 Theme & Styling

EduMentor overrides default Streamlit chrome with a custom high-contrast dark palette:
- **Canvas:** `#050608` with radial cyan/violet glow
- **Cards & Bubbles:** `#0D1117` with subtle `#27303B` borders
- **Accent Glow:** `#25D8E8` (Cyber Cyan) and `#8B5CF6` (Hyper Violet)
- **Typography:** Outfit (Headings) & Inter (Body) via Google Fonts

---

## 🎯 Phase 42 — MVP Scope Boundaries & Deferred Features

EduMentor follows a strict negative scope specification to preserve deep focus, calm aesthetics, and adherence to the core learning loop: **Concept → Recall → Mastery**.

### ✅ Active MVP Scope
- **Chat Workspace:** Focused 1-on-1 AI companion for notes, active recall, and Socratic guidance.
- **Note Ingestion:** PDF and Markdown lecture material parsing into atomic concepts.
- **Prerequisite DAG:** Topological sequencing, depth-tier analysis, and cycle resolution.
- **Active Recall Generator:** Context-grounded generative retrieval prompts.
- **Two-Pillar Hybrid Evaluation:** Semantic Cosine Similarity (40%) + LLM-as-Judge Rubric (60%).
- **SuperMemo SM-2 Spaced Repetition:** Automatic review scheduling and weak-concept resurfacing.
- **Teacher Avatar:** Expressive lightweight SVG avatar (5 emotional states) with zero heavy video stream overhead.
- **Product Events Telemetry:** Full student journey conversion tracking.

### ⏳ Deferred Post-MVP Features (Phase 42 Backlog)
The following 9 features are intentionally **kept out of the MVP**:
1. **Voice input:** Preserves text-based deliberate thought formulation without audio noise.
2. **Handwritten OCR:** Focuses on clean digital PDF & Markdown notes.
3. **Math solving:** Prioritizes conceptual understanding over symbolic solvers.
4. **Programming/code evaluation:** Evaluates mental models and architectural tradeoffs rather than running sandboxed unit tests.
5. **Live video teacher:** Keeps interface responsive and calm using dynamic SVG expressions rather than high-latency video streams.
6. **Multiplayer learning:** Safeguards intimate, distraction-free 1-on-1 study sessions.
7. **Social features:** Eliminates social feed clutter, peer comparison anxiety, and vanity metrics.
8. **Complex gamification:** Adheres to the design doc rule: keep the interface calm and spacious rather than gamified (no loot boxes, coins, or XP grind).
9. **Leaderboards:** Focuses on self-referenced mastery against one's own forgetting curve rather than competitive rankings.

These features can come in post-MVP releases.

---

## ✨ Phase 44 — Final Visual Quality Standard

EduMentor meets the visual quality standard of a high-end AI SaaS product: a **"calm, intelligent learning system"** rather than an AI technology demo or student project.

### 💎 What is Prioritized:
- **Spacing:** Generous breathing room, standardized container widths (1140px landing, 860px workspace), balanced vertical rhythm.
- **Typography:** Antialiased font smoothing (`-webkit-font-smoothing: antialiased`), OpenType legibility features, Geist Sans and Inter typography hierarchy with balanced letter-spacing.
- **Micro-interactions:** Tactile cubic-bezier hover transitions (`translateY(-1.5px)`), gentle press states, and dark-offset keyboard focus rings.
- **Animation:** Restrained, purposeful transitions respecting `prefers-reduced-motion` and pausing when out of view.
- **Depth:** Multi-layered elevation shadows, high-clarity frosted glass surfaces (`backdrop-filter: blur(20px)`), and 1px inner highlight rims (`inset 0 1px 0 rgba(255, 255, 255, 0.06)`).
- **Soft Borders:** Harmonious radius tokens (8px, 14px, 20px, 9999px) with low-contrast borders.
- **Subtle Glow:** Quiet luminescence (cyan `#25D8E8` & violet `#8B5CF6`) without blinding neon halos.
- **Clean Icons:** Consistent 1.75px–2px stroke weights optically aligned with text labels.
- **Consistent Alignment:** Centered content column, optical vertical alignment, and structured data hierarchy.

### 🚫 What is Strictly Avoided:
- **Excessive Gradients:** Strictly sticks to the curated 7-color palette; no rainbow or chaotic gradients.
- **Huge Glowing Text:** No multi-layered glowing text-shadow halos on headlines.
- **Card Clutter:** Clean, grouped layout hierarchy avoiding card fatigue.
- **Rainbow Colors:** Disciplined dual-accent (cyan/violet) color harmony.
- **Overly Animated UI:** No bouncing or distracting movement; animations pause when idle.
- **Gaming Aesthetics:** No arcade coins, XP grind bars, or flashing popups.
- **Generic Robot Imagery:** Empathetic teacher avatar with five emotional expressions and clean geometric brand glyphs.

