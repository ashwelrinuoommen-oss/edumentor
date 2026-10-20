"""
EduMentor FastAPI Web Application Server.
Exposes REST APIs for the conversational AI teacher, note ingestion, active recall evaluation,
and serves the high-performance modern web client.
"""

import os
import io
import json
import asyncio
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.samples import SAMPLE_CURRICULA
from edumentor.llm import LLMConfig, test_llm_connection
from edumentor.database.repository import EduMentorRepository
from edumentor.events import event_tracker, ProductEvent
from edumentor.scope import (
    DEFERRED_MVP_FEATURES,
    MVP_CORE_FEATURES,
    is_feature_enabled,
    get_deferred_features,
    get_mvp_manifest
)
from edumentor.utils.security import (
    validate_uploaded_file,
    safe_temporary_file,
    mask_api_key,
    is_masked_key,
    sanitize_error_message,
    MAX_UPLOAD_SIZE_BYTES,
    MAX_UPLOAD_SIZE_MB,
    NOTE_PRIVACY_STATEMENT
)
from edumentor.utils.validators import (
    validate_chat_input,
    validate_student_name,
    validate_email,
    validate_password_strength,
    validate_subject_or_module_title,
    sanitize_input_string
)
from edumentor.utils.error_handler import (
    ERROR_PROCESSING_MSG,
    ERROR_UPLOAD_MSG,
    ERROR_LLM_MSG,
    EduMentorError,
    EduMentorProcessingError,
    EduMentorUploadError,
    EduMentorLLMError,
    resolve_friendly_error,
    is_upload_error,
    is_llm_error
)

app = FastAPI(title="EduMentor API", version="1.0.0")

# Global Controlled Error Handler (Phase 35 & Phase 36)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Intercept unhandled exceptions and return controlled, Phase 36 friendly error messages."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    friendly_msg = resolve_friendly_error(exc)
    status_code = 400 if is_upload_error(exc) else 500
    return JSONResponse(status_code=status_code, content={"status": "error", "detail": friendly_msg})

# Initialize database repository and seed default student profiles
repo = EduMentorRepository()
repo.get_or_create_user(username="Ashwel", email="ashwel@edumentor.ai")
repo.get_or_create_user(username="Maya", email="maya@edumentor.ai")
repo.get_or_create_user(username="Leo", email="leo@edumentor.ai")
event_tracker.set_repository(repo)

# Single session instance for current student
orchestrator = EduMentorOrchestrator(student_name="Ashwel")
orchestrator.initialize_home()

# Mount static folder
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)


class LoginRequest(BaseModel):
    identifier: str
    password: Optional[str] = ""


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    studying: Optional[str] = None


class DemoLoginRequest(BaseModel):
    username: str


class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str


class ChatRequest(BaseModel):
    message: str


class SampleSelectRequest(BaseModel):
    module: str


class RecallSubmitRequest(BaseModel):
    answer: str


class RecallConfidenceRequest(BaseModel):
    confidence: str
    concept_id: Optional[str] = None


class ResurfaceRequest(BaseModel):
    concept_id: Optional[str] = None


class NotificationReadRequest(BaseModel):
    notification_id: Optional[str] = None


class NotificationEmailRequest(BaseModel):
    notification_id: str
    recipient_email: Optional[str] = None


class NotificationSettingsRequest(BaseModel):
    browser_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    recipient_email: Optional[str] = None


class SettingsRequest(BaseModel):
    student_name: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


class TrackEventRequest(BaseModel):
    event_name: str
    user_id: Optional[str] = None
    concept_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


# -----------------------------------------------------------------------------
# AUTHENTICATION & STUDENT ONBOARDING (PHASE 1)
# -----------------------------------------------------------------------------
@app.post("/api/auth/login")
def login_endpoint(req: LoginRequest):
    """Authenticate student using email or username, with demo profile fallback."""
    user = repo.authenticate_user(req.identifier, req.password or "")
    if not user:
        clean = req.identifier.strip().lower()
        if clean in ["ashwel", "maya", "leo"]:
            name = req.identifier.strip().capitalize()
            user = repo.get_or_create_user(username=name, email=f"{clean}@edumentor.ai")
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    orchestrator.student_name = user.username
    orchestrator.initialize_home()
    try:
        event_tracker.track(
            ProductEvent.LOGIN,
            user_id=f"user_{user.username.lower()}",
            properties={"username": user.username, "email": user.email}
        )
    except Exception:
        pass
    return {
        "status": "ok",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "studying": user.studying
        },
        "session": orchestrator.get_state_payload()
    }


@app.post("/api/auth/demo")
def demo_login_endpoint(req: DemoLoginRequest):
    """Instant 1-click authentication for demo student profiles."""
    name = req.username.strip().capitalize()
    email = f"{name.lower()}@edumentor.ai"
    user = repo.get_or_create_user(username=name, email=email)
    orchestrator.student_name = user.username
    orchestrator.initialize_home()
    try:
        event_tracker.track(
            ProductEvent.LOGIN,
            user_id=f"user_{user.username.lower()}",
            properties={"username": user.username, "email": user.email, "demo": True}
        )
    except Exception:
        pass
    return {
        "status": "ok",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "studying": user.studying
        },
        "session": orchestrator.get_state_payload()
    }


@app.post("/api/auth/signup")
def signup_endpoint(req: SignupRequest):
    """Register a new student profile and initialize personalized workspace with Phase 35 input validation."""
    v_name_ok, v_name = validate_student_name(req.username)
    if not v_name_ok:
        raise HTTPException(status_code=400, detail=v_name)
    if not validate_email(req.email):
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    if not validate_password_strength(req.password):
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    
    existing = repo.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    user = repo.create_user(
        username=v_name,
        email=req.email.strip().lower(),
        password=req.password,
        studying=sanitize_input_string(req.studying or "")
    )
    orchestrator.student_name = user.username
    orchestrator.initialize_home()
    try:
        event_tracker.track(
            ProductEvent.SIGNUP,
            user_id=f"user_{user.username.lower()}",
            properties={"username": user.username, "email": user.email, "studying": user.studying}
        )
    except Exception:
        pass
    return {
        "status": "ok",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "studying": user.studying
        },
        "session": orchestrator.get_state_payload()
    }


@app.post("/api/auth/forgot-password")
def forgot_password_endpoint(req: ForgotPasswordRequest):
    """Reset password for an existing student profile with input validation."""
    if not validate_email(req.email):
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    if not validate_password_strength(req.new_password):
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    ok = repo.reset_password(req.email.strip().lower(), req.new_password)
    if not ok:
        raise HTTPException(status_code=404, detail="No account found with this email address.")
    return {"status": "ok", "message": "Password successfully reset."}


@app.post("/api/auth/logout")
def logout_endpoint():
    """Sign out student and return to authentication stage."""
    orchestrator.student_name = "Guest"
    orchestrator.initialize_home()
    return {"status": "ok"}


@app.get("/api/auth/user")
def get_current_user_endpoint():
    """Retrieve currently active student profile."""
    return {
        "student_name": orchestrator.student_name,
        "is_authenticated": orchestrator.student_name not in ["Guest", ""]
    }


@app.get("/api/session")
def get_session():
    """Retrieve full current state of the active study session."""
    return orchestrator.get_state_payload()


@app.get("/api/memory")
def get_conversation_memory():
    """Phase 24: Retrieve structured conversation memory and relevant session context."""
    return {
        "conversation_memory": orchestrator.memory.get_summary(),
        "session_context": orchestrator.memory.retrieve_relevant_context()
    }


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Conversational interaction endpoint with Phase 35 input validation & Phase 36 crash prevention."""
    if not req.message or not req.message.strip():
        return orchestrator.get_state_payload()
    valid, clean_or_err = validate_chat_input(req.message)
    if not valid:
        raise HTTPException(status_code=400, detail=clean_or_err)
    try:
        return orchestrator.handle_user_chat(clean_or_err)
    except Exception as exc:
        friendly = resolve_friendly_error(exc, context="chat")
        return orchestrator.get_state_payload(system_message=friendly)


@app.post("/api/select-sample")
def select_sample_endpoint(req: SampleSelectRequest):
    """Load a pre-curated curriculum module."""
    return orchestrator.load_sample_module(req.module)


@app.post("/api/upload")
async def upload_endpoint(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    title: Optional[str] = Form("Uploaded Notes")
):
    """Upload study notes (PDF or plain text) with Phase 35 validation & Phase 36 error handling."""
    if file:
        content = await file.read()
        filename = file.filename or "Notes.pdf"
        is_valid, safe_name, err = validate_uploaded_file(filename, content, max_size_bytes=MAX_UPLOAD_SIZE_BYTES)
        if not is_valid:
            status_code = 413 if "exceeds maximum" in err.lower() else 400
            raise HTTPException(status_code=status_code, detail=err)

        with safe_temporary_file(content, suffix=os.path.splitext(safe_name)[1]) as _:
            try:
                if safe_name.lower().endswith(".pdf"):
                    payload = await asyncio.to_thread(orchestrator.ingest_pdf, content, filename=safe_name)
                else:
                    text = content.decode("utf-8", errors="replace")
                    payload = await asyncio.to_thread(orchestrator.ingest_notes_text, text, title=safe_name)
                if isinstance(payload, dict):
                    payload["privacy_notice"] = NOTE_PRIVACY_STATEMENT
                try:
                    event_tracker.track(
                        ProductEvent.NOTE_UPLOADED,
                        user_id=f"user_{orchestrator.student_name.lower()}",
                        properties={"filename": safe_name, "size_bytes": len(content)}
                    )
                except Exception:
                    pass
                return payload
            except EduMentorUploadError as e:
                raise HTTPException(status_code=400, detail=str(e.friendly_message))
            except Exception:
                raise HTTPException(status_code=400, detail=ERROR_UPLOAD_MSG)

    elif raw_text:
        clean_text = sanitize_input_string(raw_text)
        if not clean_text:
            raise HTTPException(status_code=400, detail="Provided notes text is empty or invalid.")
        if len(clean_text.encode('utf-8')) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Pasted notes exceed the 15 MB size limit.")
        clean_title = sanitize_input_string(title or "Notes")
        payload = orchestrator.ingest_notes_text(clean_text, title=clean_title)
        if isinstance(payload, dict):
            payload["privacy_notice"] = NOTE_PRIVACY_STATEMENT
        try:
            event_tracker.track(
                ProductEvent.NOTE_UPLOADED,
                user_id=f"user_{orchestrator.student_name.lower()}",
                properties={"filename": clean_title, "size_bytes": len(clean_text)}
            )
        except Exception:
            pass
        return payload
    else:
        raise HTTPException(status_code=400, detail="No file or text provided")


# Phase 20: Subject / Module Management Endpoints
@app.post("/api/modules/upload")
async def upload_module_endpoint(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    subject_title: Optional[str] = Form("Operating Systems"),
    module_title: Optional[str] = Form("Module 1: Process Scheduling"),
    module_number: Optional[int] = Form(None),
    subject_id: Optional[str] = Form(None)
):
    """Phase 20 & 35: Upload and ingest module with file validation and safe temporary storage."""
    clean_subj = sanitize_input_string(subject_title or "Operating Systems")
    clean_mod = sanitize_input_string(module_title or "Module")

    if file:
        content = await file.read()
        filename = file.filename or "module.pdf"
        is_valid, safe_name, err = validate_uploaded_file(filename, content, max_size_bytes=MAX_UPLOAD_SIZE_BYTES)
        if not is_valid:
            status_code = 413 if "exceeds maximum" in err.lower() else 400
            raise HTTPException(status_code=status_code, detail=err)

        with safe_temporary_file(content, suffix=os.path.splitext(safe_name)[1]) as _:
            try:
                payload = await asyncio.to_thread(
                    orchestrator.add_module_to_subject,
                    subject_title=clean_subj,
                    module_title=clean_mod,
                    module_number=module_number,
                    text_or_bytes=content,
                    filename=safe_name,
                    subject_id=subject_id
                )
                if isinstance(payload, dict):
                    payload["privacy_notice"] = NOTE_PRIVACY_STATEMENT
                return payload
            except EduMentorUploadError as e:
                raise HTTPException(status_code=400, detail=str(e.friendly_message))
            except Exception:
                raise HTTPException(status_code=400, detail=ERROR_UPLOAD_MSG)

    elif raw_text:
        clean_text = sanitize_input_string(raw_text)
        if not clean_text:
            raise HTTPException(status_code=400, detail="Provided module text is empty.")
        if len(clean_text.encode('utf-8')) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Module text exceeds the 15 MB size limit.")
        payload = orchestrator.add_module_to_subject(
            subject_title=clean_subj,
            module_title=clean_mod,
            module_number=module_number,
            text_or_bytes=clean_text,
            filename=f"{clean_mod}.txt",
            subject_id=subject_id
        )
        if isinstance(payload, dict):
            payload["privacy_notice"] = NOTE_PRIVACY_STATEMENT
        return payload
    else:
        payload = orchestrator.add_module_to_subject(
            subject_title=clean_subj,
            module_title=clean_mod or "Module 1",
            module_number=module_number,
            text_or_bytes="",
            filename="module.pdf",
            subject_id=subject_id
        )
        if isinstance(payload, dict):
            payload["privacy_notice"] = NOTE_PRIVACY_STATEMENT
        return payload


@app.get("/api/modules")
def get_modules_endpoint(subject_id: Optional[str] = None):
    """Phase 20: Retrieve all modules belonging to the specified or active subject."""
    modules = orchestrator.get_subject_modules(subject_id=subject_id)
    return {
        "status": "ok",
        "subject_id": subject_id or orchestrator.subject_id,
        "curriculum_title": orchestrator.curriculum_title,
        "modules": modules
    }


# Phase 21: Source-Grounded AI Endpoint
@app.get("/api/recall/grounding")
def get_recall_grounding_endpoint(question_id: Optional[str] = None):
    """Phase 21: Retrieve strict source grounding reference for active or specified question."""
    if question_id:
        grounding = orchestrator.get_question_grounding(question_id)
    else:
        grounding = orchestrator.last_question_grounding
    
    if not grounding:
        return {"status": "empty", "message": "No question grounding available"}
    return {"status": "ok", "grounding": grounding}


@app.post("/api/ready")
def ready_endpoint():
    """Student indicates readiness for active recall challenge."""
    return orchestrator.trigger_ready_for_recall()


@app.post("/api/recall/submit")
def recall_submit_endpoint(req: RecallSubmitRequest):
    """Submit student recall response for hybrid evaluation."""
    return orchestrator.submit_recall_response(req.answer)


@app.post("/api/recall/upload-answer")
async def recall_upload_answer_endpoint(file: UploadFile = File(...)):
    """Allow student to upload their handwritten / typed answer as a PDF or text file."""
    content = await file.read()
    filename = file.filename or "answer.txt"
    if filename.lower().endswith(".pdf"):
        from edumentor.extractor import async_extract_text_from_pdf
        text = await async_extract_text_from_pdf(content)
    else:
        text = content.decode("utf-8", errors="replace")
    
    if not text.strip():
        text = "Uploaded blank answer file."
    
    try:
        event_tracker.track(
            ProductEvent.ANSWER_UPLOADED,
            user_id=f"user_{orchestrator.student_name.lower()}",
            concept_id=orchestrator.current_concept_id,
            properties={"filename": filename, "size_bytes": len(content)}
        )
    except Exception:
        pass

    return orchestrator.submit_recall_response(text)


@app.post("/api/recall/confidence")
def recall_confidence_endpoint(req: RecallConfidenceRequest):
    """Student rates their confidence for their recent recall response."""
    return orchestrator.record_student_confidence(req.confidence, concept_id=req.concept_id)


@app.post("/api/resurface/trigger")
def resurface_trigger_endpoint(req: Optional[ResurfaceRequest] = None):
    """Proactively trigger Phase 15 automatic resurfacing of weak or due topics."""
    cid = req.concept_id if req else None
    return orchestrator.trigger_automatic_resurfacing(concept_id=cid)


@app.post("/api/resurface/accept")
def resurface_accept_endpoint():
    """Student accepts proactive resurfacing prompt and starts active recall directly."""
    return orchestrator.trigger_ready_for_recall()


@app.post("/api/advance")
def advance_endpoint():
    """Advance to next concept or trigger adaptive loopback."""
    return orchestrator.advance_next_step()


@app.post("/api/reset")
def reset_endpoint():
    """Reset to home screen."""
    return orchestrator.initialize_home()


# Phase 18: Resume Learning Endpoints
@app.get("/api/resume-state")
def get_resume_state_endpoint():
    """Retrieve active resumable session status and formatted dialogue."""
    return orchestrator.get_resume_state()


@app.post("/api/resume/continue")
def resume_continue_endpoint():
    """Student clicks [ Continue ] to resume study session where they left off."""
    return orchestrator.resume_session()


@app.post("/api/resume/dismiss")
def resume_dismiss_endpoint():
    """Student clicks [ Start Something Else ] to clear active session and return home."""
    return orchestrator.dismiss_resume()


# Phase 19: Lightweight Progress Page Endpoint
@app.get("/api/progress")
def get_progress_endpoint():
    """Retrieve clean, lightweight progress metrics and recent subjects."""
    return orchestrator.get_progress_summary()


@app.get("/api/curricula")
def list_curricula_endpoint():
    """List available pre-curated benchmark curricula."""
    curricula = []
    for k, v in SAMPLE_CURRICULA.items():
        curricula.append({
            "key": k,
            "title": v.get("title", k),
            "description": v.get("description", ""),
            "concept_count": len(v.get("concepts", []))
        })
    return {"curricula": curricula}


# Phase 22: Concept Dependency Engine Endpoint
@app.get("/api/graph/dependencies")
def get_graph_dependencies_endpoint():
    """Retrieve NetworkX dependency graph metadata, topological sequence, and validation status."""
    g = orchestrator.graph.graph if orchestrator.graph else None
    return orchestrator.dependency_engine.get_graph_metadata(g)


# Phase 23: AI Conversation State Machine Endpoint
@app.get("/api/state")
def get_conversation_state_endpoint():
    """Retrieve active conversation state machine status, valid transitions, and history."""
    from edumentor.state_machine import ConversationState
    return {
        "state": str(orchestrator.state),
        "conversation_state": orchestrator.conversation_state.value,
        "legacy_state": str(orchestrator.state),
        "state_machine": orchestrator.state_machine.to_dict(),
        "valid_next_states": [s.value for s in orchestrator.state_machine.get_valid_next_states()],
        "can_advance": orchestrator.state_machine.can_transition(ConversationState.NEXT_CONCEPT),
        "can_recall": orchestrator.state_machine.can_transition(ConversationState.WAITING_FOR_RECALL),
    }


@app.get("/api/mastery")
@app.get("/api/session/mastery")
def get_mastery_endpoint():
    """Retrieve Phase 10 multidimensional mastery analytics."""
    from edumentor.services.mastery_service import MasteryService
    curriculum_mastery = MasteryService.calculate_curriculum_mastery(
        orchestrator.concepts,
        orchestrator.dependencies
    )
    return {
        "status": "ok",
        "student_name": orchestrator.student_name,
        "curriculum_title": orchestrator.curriculum_title,
        "mastery": curriculum_mastery
    }


@app.get("/api/graph")
def graph_endpoint():
    """Return nodes and edges for SVG DAG rendering."""
    if orchestrator.graph:
        return orchestrator.graph.to_dict()
    return {"nodes": [], "edges": []}


@app.get("/api/notifications")
def get_notifications_endpoint():
    """Retrieve in-app notifications, unread count, and channel settings."""
    return {
        "status": "ok",
        "notifications": orchestrator.notification_service.get_notifications(),
        "unread_count": orchestrator.notification_service.get_unread_count(),
        "settings": orchestrator.notification_service.get_settings()
    }


@app.post("/api/notifications/generate")
def generate_notification_endpoint(req: Optional[ResurfaceRequest] = None):
    """Proactively generate a revisit notification for a weak/due concept."""
    if not orchestrator.concepts:
        orchestrator.load_sample_module("Operating Systems")

    cid = req.concept_id if req else None
    if not cid:
        cid = orchestrator.check_resurfacing_candidate()
    if not cid and orchestrator.topological_order:
        cid = orchestrator.topological_order[0]
    
    if not cid or cid not in orchestrator.concepts:
        return {"status": "error", "message": "No suitable concept found"}

    c = orchestrator.concepts[cid]
    notif = orchestrator.notification_service.create_revisit_notification(
        student_name=orchestrator.student_name,
        concept_title=c.get("title", cid),
        concept_id=cid,
        reason="close"
    )
    browser_payload = orchestrator.notification_service.get_browser_notification_payload(notif["id"])
    return {
        "status": "ok",
        "notification": notif,
        "browser_payload": browser_payload
    }


@app.post("/api/notifications/read")
def read_notification_endpoint(req: Optional[NotificationReadRequest] = None):
    """Mark one or all notifications as read."""
    nid = req.notification_id if req else None
    count = orchestrator.notification_service.mark_as_read(nid)
    return {
        "status": "ok",
        "marked_read": count,
        "unread_count": orchestrator.notification_service.get_unread_count()
    }


@app.post("/api/notifications/dispatch-email")
def dispatch_email_endpoint(req: NotificationEmailRequest):
    """Dispatch email notification via pluggable email adapter."""
    res = orchestrator.notification_service.dispatch_email_notification(
        notification_id=req.notification_id,
        recipient_email=req.recipient_email
    )
    return res


@app.get("/api/notifications/settings")
def get_notification_settings_endpoint():
    """Retrieve notification channel settings."""
    return orchestrator.notification_service.get_settings()


@app.post("/api/notifications/settings")
def update_notification_settings_endpoint(req: NotificationSettingsRequest):
    """Update notification channel preferences."""
    return orchestrator.notification_service.update_settings(
        browser_enabled=req.browser_enabled,
        email_enabled=req.email_enabled,
        recipient_email=req.recipient_email
    )


@app.post("/api/settings")
def update_settings_endpoint(req: SettingsRequest):
    """Update student profile or LLM provider with API key protection (Phase 35)."""
    if req.student_name:
        v_ok, v_name = validate_student_name(req.student_name)
        if not v_ok:
            raise HTTPException(status_code=400, detail=v_name)
        orchestrator.student_name = v_name
    if req.provider:
        orchestrator.llm_config.provider = req.provider.lower()
    if req.api_key is not None:
        # Protect against overwriting valid keys with masked bullet representations
        cleaned_key = req.api_key.strip()
        if cleaned_key and not is_masked_key(cleaned_key):
            orchestrator.llm_config.api_key = cleaned_key
    if req.model:
        orchestrator.llm_config.model = req.model
    
    success, msg = test_llm_connection(orchestrator.llm_config)
    return {
        "status": "ok",
        "student_name": orchestrator.student_name,
        "provider": orchestrator.llm_config.provider,
        "model": orchestrator.llm_config.model,
        "api_key_configured": bool(orchestrator.llm_config.api_key),
        "api_key_masked": mask_api_key(orchestrator.llm_config.api_key),
        "connection_test": {"success": success, "message": msg}
    }


# Phase 34: Conversation Database & History Endpoints
@app.get("/api/history")
def get_history_endpoint():
    """Retrieve past study sessions and conversations for the history screen (user isolated)."""
    user_id = f"user_{orchestrator.student_name.lower().replace(' ', '_')}"
    conversations = repo.get_user_conversations(user_id=user_id, limit=30)
    current_reconstructed = None
    if hasattr(orchestrator, "conversation_id") and orchestrator.conversation_id:
        current_reconstructed = repo.reconstruct_session(orchestrator.conversation_id, requesting_user_id=user_id)
    return {
        "status": "ok",
        "student_name": orchestrator.student_name,
        "conversations": conversations,
        "active_conversation_id": getattr(orchestrator, "conversation_id", None),
        "current_session": current_reconstructed
    }


@app.get("/api/history/sessions/{conversation_id}")
def reconstruct_session_endpoint(conversation_id: str):
    """Reconstruct an entire study session with user ownership authorization (Phase 35)."""
    user_id = f"user_{orchestrator.student_name.lower().replace(' ', '_')}"
    session = repo.reconstruct_session(conversation_id, requesting_user_id=user_id)
    if session.get("unauthorized"):
        raise HTTPException(status_code=403, detail="Access denied: this study session belongs to another student.")
    if not session.get("found"):
        raise HTTPException(status_code=404, detail="Conversation session not found")
    return {
        "status": "ok",
        "session": session
    }


# Phase 35: Privacy & Data Protection Endpoints
@app.get("/api/privacy/policy")
def get_privacy_policy_endpoint():
    """Phase 35: Return student note privacy guarantees and file limits."""
    return {
        "status": "ok",
        "privacy_statement": NOTE_PRIVACY_STATEMENT,
        "max_upload_size_mb": MAX_UPLOAD_SIZE_MB,
        "local_storage_guarantee": True,
        "public_data_sharing": False,
        "allowed_formats": [".pdf", ".txt", ".md", ".markdown"],
        "user_data_isolation": True
    }


@app.post("/api/privacy/purge")
def purge_user_data_endpoint():
    """Phase 35: Privacy Right to Erasure — permanently delete student notes and study history."""
    user_id = f"user_{orchestrator.student_name.lower().replace(' ', '_')}"
    deleted_counts = repo.purge_user_data(user_id)
    orchestrator.initialize_home()
    return {
        "status": "ok",
        "message": "All personal study data, uploaded documents, and history have been permanently purged.",
        "purged_records": deleted_counts
    }


# =============================================================================
# PHASE 41: PRODUCT EVENTS TELEMETRY ENDPOINTS
# =============================================================================
@app.post("/api/events/track")
def track_event_endpoint(req: TrackEventRequest):
    """Phase 41: Ingest product telemetry events from web clients or external services."""
    uid = req.user_id or f"user_{orchestrator.student_name.lower()}"
    rec = event_tracker.track(
        event_name=req.event_name,
        user_id=uid,
        concept_id=req.concept_id,
        session_id=req.session_id,
        properties=req.properties
    )
    return {"status": "ok", "event": rec.to_dict()}


@app.get("/api/events")
def get_events_endpoint(
    event_name: Optional[str] = None,
    user_id: Optional[str] = None,
    concept_id: Optional[str] = None,
    limit: int = 100
):
    """Phase 41: Retrieve recorded product events with optional filters."""
    events = event_tracker.get_events(
        user_id=user_id,
        event_name=event_name,
        concept_id=concept_id,
        limit=limit
    )
    return {
        "status": "ok",
        "total": len(events),
        "events": [e.to_dict() for e in events]
    }


@app.get("/api/events/summary")
def get_events_summary_endpoint(user_id: Optional[str] = None):
    """Phase 41: Retrieve event counts and student learning funnel conversion statistics."""
    summary = event_tracker.get_funnel_summary(user_id=user_id)
    return {"status": "ok", "summary": summary}


# =============================================================================
# PHASE 42: MVP SCOPE BOUNDARIES & DEFERRED FEATURES GOVERNANCE
# =============================================================================
@app.get("/api/scope")
@app.get("/api/features")
def get_scope_manifest_endpoint():
    """Phase 42: Return MVP feature manifesto and list of features deferred post-MVP."""
    return {"status": "ok", "manifest": get_mvp_manifest()}


@app.get("/api/features/deferred")
def get_deferred_features_endpoint():
    """Phase 42: Retrieve the 9 features intentionally kept out of the MVP."""
    return {
        "status": "ok",
        "total_deferred": len(DEFERRED_MVP_FEATURES),
        "deferred_features": get_deferred_features()
    }


@app.get("/api/features/{feature_key}")
def get_feature_status_endpoint(feature_key: str):
    """Phase 42: Query feature enablement and status."""
    norm_key = feature_key.strip().lower().replace(" ", "_").replace("-", "_")
    if norm_key in DEFERRED_MVP_FEATURES:
        feat = DEFERRED_MVP_FEATURES[norm_key]
        return JSONResponse(
            status_code=501,
            content={
                "status": "deferred_post_mvp",
                "enabled": False,
                "feature": feat,
                "message": f"{feat['name']} is kept out of the MVP and scheduled for a post-MVP release."
            }
        )
    if is_feature_enabled(norm_key):
        return {"status": "active_mvp", "enabled": True, "feature_key": norm_key}
    raise HTTPException(status_code=404, detail=f"Feature '{feature_key}' not recognized.")


# Static and Root serving
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
assets_dir = os.path.join(STATIC_DIR, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "EduMentor backend running. Static assets building."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
