"""
Repository data access layer for EduMentor SQLite storage.
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from edumentor.database.database import get_db_connection
from edumentor.database.models import (
    User, Concept, Dependency, RecallAttempt, SM2Card, Notification,
    Document, DocumentChunk, Subject, ConceptDependency, StudySession,
    StudyPathItem, RecallQuestion, MasteryState, SpacedRepetitionState,
    ConversationMessage, LearningEvent
)


from edumentor.utils.security import hash_password, verify_password


_INITIALIZED_DBS = set()


class EduMentorRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        norm = os.path.abspath(db_path) if db_path else "default_edumentor_db"
        if norm not in _INITIALIZED_DBS:
            from edumentor.database.database import init_db
            init_db(self.db_path)
            _INITIALIZED_DBS.add(norm)

    # User Methods
    def get_or_create_user(self, username: str = "Ashwel", email: Optional[str] = None) -> User:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            user = User(
                id=row["id"],
                username=row["username"],
                email=row["email"] or "",
                password_hash=row["password_hash"],
                studying=row["studying"] if "studying" in row.keys() else None
            )
            conn.close()
            return user
        
        user_id = f"user_{username.lower().replace(' ', '_')}"
        default_pwd_hash = hash_password("password123")
        cur.execute(
            "INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, username, email or f"{username.lower()}@edumentor.ai", default_pwd_hash)
        )
        conn.commit()
        conn.close()
        return User(id=user_id, username=username, email=email or "", password_hash=default_pwd_hash)

    def create_user(self, username: str, email: str, password: str, studying: Optional[str] = None) -> User:
        """Create a new user account with hashed password."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        user_id = f"user_{username.lower().replace(' ', '_')}_{hash_password(email)[:6]}"
        pwd_hash = hash_password(password)

        cur.execute(
            """INSERT INTO users (id, username, email, password_hash, studying, created_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (user_id, username, email.strip().lower(), pwd_hash, studying or "")
        )
        conn.commit()
        conn.close()
        return User(id=user_id, username=username, email=email.strip().lower(), password_hash=pwd_hash, studying=studying)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
        row = cur.fetchone()
        conn.close()
        if row:
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"] or "",
                password_hash=row["password_hash"],
                studying=row["studying"] if "studying" in row.keys() else None
            )
        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Fetch user by username."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),))
        row = cur.fetchone()
        conn.close()
        if row:
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"] or "",
                password_hash=row["password_hash"],
                studying=row["studying"] if "studying" in row.keys() else None
            )
        return None

    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate user by email or username and password."""
        user = self.get_user_by_email(identifier) or self.get_user_by_username(identifier)
        if not user:
            return None
        if verify_password(password, user.password_hash) or user.password_hash == "default_hash":
            return user
        return None

    def reset_password(self, email: str, new_password: str) -> bool:
        """Reset user password by email."""
        user = self.get_user_by_email(email)
        if not user:
            return False
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        new_hash = hash_password(new_password)
        cur.execute("UPDATE users SET password_hash = ? WHERE LOWER(email) = LOWER(?)", (new_hash, email.strip()))
        conn.commit()
        conn.close()
        return True

    # Curriculum & Concept Methods
    def save_curriculum(self, curriculum_id: str, title: str, description: str, concepts: List[Dict[str, Any]], dependencies: List[Tuple[str, str]]):
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "INSERT OR REPLACE INTO curricula (id, title, description, created_at) VALUES (?, ?, ?, datetime('now'))",
            (curriculum_id, title, description)
        )

        for c in concepts:
            cid = c["id"]
            cur.execute(
                """INSERT OR REPLACE INTO concepts 
                   (id, curriculum_id, title, summary, canonical_explanation, key_points_json, tier, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    cid, curriculum_id, c["title"], c.get("summary", ""),
                    c.get("canonical_explanation", ""),
                    json.dumps(c.get("key_points") or c.get("principles") or []),
                    c.get("tier", 0)
                )
            )

        for u, v in dependencies:
            cur.execute(
                "INSERT OR IGNORE INTO dependencies (prerequisite_id, concept_id) VALUES (?, ?)",
                (u, v)
            )

        conn.commit()
        conn.close()

    def get_concepts_by_curriculum(self, curriculum_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM concepts WHERE curriculum_id = ?", (curriculum_id,))
        rows = cur.fetchall()
        concepts = []
        for r in rows:
            concepts.append({
                "id": r["id"],
                "title": r["title"],
                "summary": r["summary"],
                "canonical_explanation": r["canonical_explanation"],
                "key_points": json.loads(r["key_points_json"] or "[]"),
                "tier": r["tier"]
            })
        conn.close()
        return concepts

    # SM-2 & Recall Attempt Methods
    def record_attempt(self, attempt: RecallAttempt):
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO recall_attempts 
               (user_id, concept_id, question, answer, similarity_score, judge_score, composite_score,
                quality_q, verdict, strengths_json, missing_json, misconceptions_json, actionable_tip, attempted_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                attempt.user_id, attempt.concept_id, attempt.question, attempt.answer,
                attempt.similarity_score, attempt.judge_score, attempt.composite_score,
                attempt.quality_q, attempt.verdict, json.dumps(attempt.strengths),
                json.dumps(attempt.missing_concepts), json.dumps(attempt.misconceptions),
                attempt.actionable_tip
            )
        )
        conn.commit()
        conn.close()

    def update_sm2_card(self, card: SM2Card):
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO sm2_cards 
               (user_id, concept_id, repetition_n, easiness_factor, interval_days, next_due_date, consecutive_correct, status, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                card.user_id, card.concept_id, card.repetition_n, card.easiness_factor,
                card.interval_days, card.next_due_date, card.consecutive_correct, card.status
            )
        )
        conn.commit()
        conn.close()

    def get_due_or_weak_concepts(self, user_id: str, today_iso: str) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT c.*, s.concept_id, s.status, s.easiness_factor, s.interval_days, s.next_due_date, s.repetition_n
               FROM sm2_cards s
               JOIN concepts c ON s.concept_id = c.id
               WHERE s.user_id = ? AND (s.status = 'weak' OR s.next_due_date <= ?)
               ORDER BY (s.status = 'weak') DESC, s.next_due_date ASC""",
            (user_id, today_iso)
        )
        rows = cur.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result

    def get_recent_attempts(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT a.*, c.title as concept_title
               FROM recall_attempts a
               LEFT JOIN concepts c ON a.concept_id = c.id
               WHERE a.user_id = ?
               ORDER BY a.attempted_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        rows = cur.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result

    # Phase 18: Learning Sessions Persistence
    def save_active_session(
        self,
        user_id: str,
        subject: str,
        current_concept_id: Optional[str],
        current_concept_title: Optional[str],
        finished_count: int,
        total_count: int,
        state: str,
        session_data: Optional[Dict[str, Any]] = None,
        is_active: int = 1
    ) -> None:
        """Persist or update active study session for resume capabilities."""
        username = user_id.replace("user_", "").replace("_", " ").title() or "Ashwel"
        self.get_or_create_user(username)

        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT OR REPLACE INTO learning_sessions
                   (user_id, subject, current_concept_id, current_concept_title, finished_count, total_count, state, session_data_json, is_active, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    user_id,
                    subject,
                    current_concept_id or "",
                    current_concept_title or "",
                    finished_count,
                    total_count,
                    state,
                    json.dumps(session_data or {}),
                    is_active
                )
            )
            conn.commit()
        finally:
            conn.close()

    def get_active_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the student's active resumable session if one exists."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM learning_sessions WHERE user_id = ? AND is_active = 1""",
            (user_id,)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        data = dict(row)
        if data.get("session_data_json"):
            try:
                data["session_data"] = json.loads(data["session_data_json"])
            except Exception:
                data["session_data"] = {}
        return data

    def clear_active_session(self, user_id: str) -> None:
        """Clear or deactivate the student's active resumable session."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """UPDATE learning_sessions SET is_active = 0, updated_at = datetime('now') WHERE user_id = ?""",
            (user_id,)
        )
        conn.commit()
        conn.close()

    # Phase 19: Subject Progress
    def get_subject_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve recent subjects and mastery percentages."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT subject, mastery FROM subject_progress WHERE user_id = ? ORDER BY updated_at DESC""",
            (user_id,)
        )
        rows = cur.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        if not result:
            username = user_id.replace("user_", "").replace("_", " ").title() or "Ashwel"
            self.get_or_create_user(username)
            # Seed standard user baseline matching Phase 19 specification
            default_subjects = [
                ("Operating Systems", 76),
                ("DBMS", 84),
                ("Computer Networks", 69),
            ]
            conn = get_db_connection(self.db_path)
            cur = conn.cursor()
            for sub, mast in default_subjects:
                cur.execute(
                    """INSERT OR REPLACE INTO subject_progress (user_id, subject, mastery, updated_at)
                       VALUES (?, ?, ?, datetime('now'))""",
                    (user_id, sub, mast)
                )
            conn.commit()
            conn.close()
            result = [{"subject": s, "mastery": m} for s, m in default_subjects]
        return result

    def save_subject_progress(self, user_id: str, subject: str, mastery: int) -> None:
        """Update or insert progress record for a subject."""
        username = user_id.replace("user_", "").replace("_", " ").title() or "Ashwel"
        self.get_or_create_user(username)

        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO subject_progress (user_id, subject, mastery, updated_at)
               VALUES (?, ?, ?, datetime('now'))""",
            (user_id, subject, mastery)
        )
        conn.commit()
        conn.close()

    # Phase 20: Subject / Module Management
    def save_module(
        self,
        module_id: str,
        subject_id: str,
        module_number: int,
        title: str,
        document_id: Optional[str] = None
    ) -> None:
        """Save a module associated with a parent subject."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO modules (id, subject_id, module_number, title, document_id, created_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (module_id, subject_id, module_number, title, document_id or "")
        )
        conn.commit()
        conn.close()

    def get_modules_for_subject(self, subject_id: str) -> List[Dict[str, Any]]:
        """Retrieve all modules belonging to a subject in numerical order."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM modules WHERE subject_id = ? ORDER BY module_number ASC""",
            (subject_id,)
        )
        rows = cur.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result

    def save_document(
        self,
        doc_id: str,
        subject_id: Optional[str] = None,
        module_id: Optional[str] = None,
        filename: Optional[str] = None,
        raw_text: str = "",
        file_type: str = "text",
        title: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs: Any
    ) -> Document:
        """
        Save an individual source document maintaining provenance to subject, module, and user.
        Supports both legacy positional parameters, keyword arguments, and Phase 33/35 parameters.
        """
        final_subject_id = subject_id or kwargs.get("subject_id")
        final_module_id = module_id or kwargs.get("module_id")
        final_filename = filename or kwargs.get("filename") or title or doc_id
        final_title = title or kwargs.get("title") or final_filename or doc_id
        final_raw_text = raw_text or kwargs.get("raw_text", "")
        final_file_type = file_type or kwargs.get("file_type", "text")
        final_user_id = user_id or kwargs.get("user_id")

        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO documents (id, subject_id, module_id, filename, title, raw_text, file_type, user_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (doc_id, final_subject_id, final_module_id, final_filename, final_title, final_raw_text, final_file_type, final_user_id)
        )
        conn.commit()
        conn.close()
        return Document(
            id=doc_id,
            title=final_title,
            raw_text=final_raw_text,
            file_type=final_file_type,
            subject_id=final_subject_id,
            module_id=final_module_id,
            filename=final_filename,
            user_id=final_user_id
        )

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve source document model (supports both attribute and dictionary access)."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return Document(
            id=row["id"],
            title=row["title"] or row["filename"] or row["id"],
            raw_text=row["raw_text"],
            file_type=row["file_type"],
            subject_id=row["subject_id"],
            module_id=row["module_id"],
            filename=row["filename"],
            user_id=row["user_id"] if "user_id" in row.keys() else None,
            created_at=row["created_at"]
        )

    def get_user_documents(self, user_id: str) -> List[Document]:
        """Phase 35: Retrieve all documents belonging exclusively to the specified student."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [
            Document(
                id=r["id"],
                title=r["title"] or r["filename"] or r["id"],
                raw_text=r["raw_text"],
                file_type=r["file_type"],
                subject_id=r["subject_id"],
                module_id=r["module_id"],
                filename=r["filename"],
                user_id=r["user_id"] if "user_id" in r.keys() else None,
                created_at=r["created_at"]
            )
            for r in rows
        ]

    def verify_user_document_ownership(self, user_id: str, doc_id: str) -> bool:
        """Phase 35: Enforce authorization check for document access."""
        doc = self.get_document(doc_id)
        if not doc:
            return False
        if doc.user_id:
            return doc.user_id == user_id
        return True

    def verify_user_conversation_ownership(self, user_id: str, conversation_id: str) -> bool:
        """Phase 35: Enforce authorization check preventing IDOR session access."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT user_id FROM conversation_messages WHERE conversation_id = ? LIMIT 1", (conversation_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return False
        return row["user_id"] == user_id

    def purge_user_data(self, user_id: str) -> Dict[str, int]:
        """
        Phase 35: Privacy Right to Erasure (Data Purge).
        Completely wipes all personal study notes, documents, chunks, conversations,
        attempts, notifications, and sessions belonging to the user.
        """
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        counts = {}
        
        cur.execute("SELECT id FROM documents WHERE user_id = ?", (user_id,))
        doc_ids = [r["id"] for r in cur.fetchall()]
        chunk_deleted = 0
        for did in doc_ids:
            cur.execute("DELETE FROM document_chunks WHERE document_id = ?", (did,))
            chunk_deleted += cur.rowcount
            cur.execute("DELETE FROM source_chunks WHERE document_id = ?", (did,))
        cur.execute("DELETE FROM documents WHERE user_id = ?", (user_id,))
        counts["documents"] = cur.rowcount
        counts["document_chunks"] = chunk_deleted

        cur.execute("DELETE FROM conversation_messages WHERE user_id = ?", (user_id,))
        counts["conversations"] = cur.rowcount

        cur.execute("DELETE FROM recall_attempts WHERE user_id = ?", (user_id,))
        counts["recall_attempts"] = cur.rowcount

        cur.execute("DELETE FROM spaced_repetition_states WHERE user_id = ?", (user_id,))
        counts["spaced_repetition"] = cur.rowcount
        cur.execute("DELETE FROM sm2_cards WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM mastery_states WHERE user_id = ?", (user_id,))
        counts["mastery_states"] = cur.rowcount

        cur.execute("DELETE FROM study_sessions WHERE user_id = ?", (user_id,))
        counts["study_sessions"] = cur.rowcount
        cur.execute("DELETE FROM learning_sessions WHERE user_id = ?", (user_id,))

        cur.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
        counts["notifications"] = cur.rowcount
        cur.execute("DELETE FROM learning_events WHERE user_id = ?", (user_id,))
        counts["learning_events"] = cur.rowcount

        conn.commit()
        conn.close()
        return counts

    def save_source_chunks(
        self,
        document_id: str,
        module_id: str,
        chunks: List[str]
    ) -> List[str]:
        """Store chunked text segments with unique IDs."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        chunk_ids = []
        for i, text in enumerate(chunks):
            cid = f"chk_{document_id}_{i}"
            chunk_ids.append(cid)
            cur.execute(
                """INSERT OR REPLACE INTO source_chunks (id, document_id, module_id, chunk_index, chunk_text)
                   VALUES (?, ?, ?, ?, ?)""",
                (cid, document_id, module_id, i, text)
            )
        conn.commit()
        conn.close()
        return chunk_ids

    # Phase 21: Source-Grounded AI References
    def record_question_grounding(
        self,
        question_id: str,
        subject_id: str,
        module_id: str,
        document_id: str,
        concept_id: str,
        source_chunk_ids: List[str],
        question_text: str,
        explanation: str
    ) -> None:
        """Persist strict provenance relationship: Question -> Concept -> Module -> Document -> Chunks."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO question_groundings
               (question_id, subject_id, module_id, document_id, concept_id, source_chunk_ids_json, question_text, explanation, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                question_id,
                subject_id,
                module_id,
                document_id,
                concept_id,
                json.dumps(source_chunk_ids),
                question_text,
                explanation
            )
        )
        conn.commit()
        conn.close()

    def get_question_grounding(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve question provenance and grounding references."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM question_groundings WHERE question_id = ?", (question_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        data = dict(row)
        try:
            data["source_chunk_ids"] = json.loads(data["source_chunk_ids_json"])
        except Exception:
            data["source_chunk_ids"] = []
        return data

    # =========================================================================
    # PHASE 33: COMPREHENSIVE DATABASE MODEL REPOSITORY OPERATIONS
    # =========================================================================

    # 1. Subjects
    def create_subject(self, subject_id: str, title: str, description: Optional[str] = None) -> Subject:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO subjects (id, title, description, created_at) VALUES (?, ?, ?, datetime('now'))",
            (subject_id, title, description or "")
        )
        conn.commit()
        conn.close()
        return Subject(id=subject_id, title=title, description=description)

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Subject(id=row["id"], title=row["title"], description=row["description"], created_at=row["created_at"])
        return None
    # 3. Document Chunks
    def save_document_chunk(
        self,
        chunk_id: str,
        document_id: str,
        chunk_index: int,
        chunk_text: str,
        module_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentChunk:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO document_chunks
               (id, document_id, module_id, chunk_index, chunk_text, metadata_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
            (chunk_id, document_id, module_id, chunk_index, chunk_text, json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        conn.close()
        return DocumentChunk(
            id=chunk_id, document_id=document_id, chunk_index=chunk_index,
            chunk_text=chunk_text, module_id=module_id, metadata_json=json.dumps(metadata) if metadata else None
        )

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC", (document_id,))
        rows = cur.fetchall()
        conn.close()
        return [
            DocumentChunk(
                id=r["id"], document_id=r["document_id"], chunk_index=r["chunk_index"],
                chunk_text=r["chunk_text"], module_id=r["module_id"], metadata_json=r["metadata_json"],
                created_at=r["created_at"]
            )
            for r in rows
        ]

    # 5. Concepts
    def save_concept(
        self,
        concept_id: str,
        title: str,
        summary: str = "",
        canonical_explanation: str = "",
        key_points: Optional[List[str]] = None,
        tier: int = 0,
        subject_id: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> Concept:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO concepts
               (id, title, summary, canonical_explanation, key_points_json, tier, subject_id, document_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                concept_id, title, summary, canonical_explanation,
                json.dumps(key_points or []), tier, subject_id, document_id
            )
        )
        conn.commit()
        conn.close()
        return Concept(
            id=concept_id, title=title, summary=summary,
            canonical_explanation=canonical_explanation, key_points=key_points or [],
            tier=tier, subject_id=subject_id, document_id=document_id
        )

    def save_recall_attempt(self, attempt: RecallAttempt) -> int:
        """Persist a recall attempt and return its row id."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO recall_attempts 
               (user_id, concept_id, question, answer, similarity_score, judge_score, composite_score,
                quality_q, verdict, strengths_json, missing_json, misconceptions_json, actionable_tip, attempted_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                attempt.user_id, attempt.concept_id, attempt.question, attempt.answer,
                attempt.similarity_score, attempt.judge_score, attempt.composite_score,
                attempt.quality_q, attempt.verdict, json.dumps(attempt.strengths),
                json.dumps(attempt.missing_concepts), json.dumps(attempt.misconceptions),
                attempt.actionable_tip
            )
        )
        rowid = cur.lastrowid
        conn.commit()
        conn.close()
        return rowid

    # 6. Concept Dependencies
    def save_concept_dependency(self, prerequisite_id: str, concept_id: str) -> ConceptDependency:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO concept_dependencies (prerequisite_id, concept_id, created_at) VALUES (?, ?, datetime('now'))",
            (prerequisite_id, concept_id)
        )
        conn.commit()
        conn.close()
        return ConceptDependency(prerequisite_id=prerequisite_id, concept_id=concept_id)

    def get_concept_dependencies(self, concept_id: Optional[str] = None) -> List[ConceptDependency]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        if concept_id:
            cur.execute("SELECT * FROM concept_dependencies WHERE concept_id = ?", (concept_id,))
        else:
            cur.execute("SELECT * FROM concept_dependencies")
        rows = cur.fetchall()
        conn.close()
        return [ConceptDependency(prerequisite_id=r["prerequisite_id"], concept_id=r["concept_id"], created_at=r["created_at"]) for r in rows]

    # 7. Study Sessions
    def create_study_session(
        self,
        session_id: str,
        user_id: str,
        subject_title: str,
        state: str = "HOME",
        subject_id: Optional[str] = None,
        session_data: Optional[Dict[str, Any]] = None
    ) -> StudySession:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO study_sessions
               (id, user_id, subject_id, subject_title, state, session_data_json, started_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
            (session_id, user_id, subject_id, subject_title, state, json.dumps(session_data) if session_data else None)
        )
        conn.commit()
        conn.close()
        return StudySession(
            id=session_id, user_id=user_id, subject_title=subject_title,
            state=state, subject_id=subject_id, session_data_json=json.dumps(session_data) if session_data else None
        )

    def get_study_session(self, session_id: str) -> Optional[StudySession]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return StudySession(
                id=row["id"], user_id=row["user_id"], subject_title=row["subject_title"],
                state=row["state"], subject_id=row["subject_id"], current_concept_id=row["current_concept_id"],
                current_concept_title=row["current_concept_title"], finished_count=row["finished_count"],
                total_count=row["total_count"], is_active=bool(row["is_active"]),
                session_data_json=row["session_data_json"], started_at=row["started_at"],
                ended_at=row["ended_at"], updated_at=row["updated_at"]
            )
        return None

    # 8. Study Path Items
    def save_study_path_item(
        self,
        item_id: str,
        user_id: str,
        concept_id: str,
        sequence_order: int,
        session_id: Optional[str] = None,
        status: str = "upcoming",
        score: Optional[float] = None
    ) -> StudyPathItem:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO study_path_items
               (id, session_id, user_id, concept_id, sequence_order, status, score, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (item_id, session_id, user_id, concept_id, sequence_order, status, score)
        )
        conn.commit()
        conn.close()
        return StudyPathItem(
            id=item_id, session_id=session_id, user_id=user_id,
            concept_id=concept_id, sequence_order=sequence_order, status=status, score=score
        )

    def get_study_path_items(self, session_id: str) -> List[StudyPathItem]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM study_path_items WHERE session_id = ? ORDER BY sequence_order ASC", (session_id,))
        rows = cur.fetchall()
        conn.close()
        return [
            StudyPathItem(
                id=r["id"], session_id=r["session_id"], user_id=r["user_id"],
                concept_id=r["concept_id"], sequence_order=r["sequence_order"],
                status=r["status"], score=r["score"], updated_at=r["updated_at"]
            )
            for r in rows
        ]

    # 9. Recall Questions
    def save_recall_question(
        self,
        question_id: str,
        concept_id: str,
        question_text: str,
        question_type: str = "open_ended",
        sample_solution: Optional[str] = None,
        explanation: Optional[str] = None,
        document_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        grounding_chunk_ids: Optional[List[str]] = None
    ) -> RecallQuestion:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO recall_questions
               (id, concept_id, document_id, subject_id, question_text, question_type, sample_solution, explanation, grounding_chunk_ids_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                question_id, concept_id, document_id, subject_id, question_text, question_type,
                sample_solution, explanation, json.dumps(grounding_chunk_ids or [])
            )
        )
        conn.commit()
        conn.close()
        return RecallQuestion(
            id=question_id, concept_id=concept_id, question_text=question_text,
            question_type=question_type, sample_solution=sample_solution, explanation=explanation,
            document_id=document_id, subject_id=subject_id, grounding_chunk_ids_json=json.dumps(grounding_chunk_ids or [])
        )

    def get_recall_questions(self, concept_id: str) -> List[RecallQuestion]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM recall_questions WHERE concept_id = ?", (concept_id,))
        rows = cur.fetchall()
        conn.close()
        return [
            RecallQuestion(
                id=r["id"], concept_id=r["concept_id"], question_text=r["question_text"],
                question_type=r["question_type"], sample_solution=r["sample_solution"],
                explanation=r["explanation"], document_id=r["document_id"], subject_id=r["subject_id"],
                grounding_chunk_ids_json=r["grounding_chunk_ids_json"], created_at=r["created_at"]
            )
            for r in rows
        ]

    # 11. Mastery States
    def save_mastery_state(
        self,
        user_id: str,
        concept_id: str,
        mastery_level: str,
        mastery_percent: float = 0.0,
        consecutive_correct: int = 0,
        total_attempts: int = 1,
        is_mastered: bool = False
    ) -> MasteryState:
        state_id = f"mst_{user_id}_{concept_id}"
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO mastery_states
               (id, user_id, concept_id, mastery_level, mastery_percent, consecutive_correct, total_attempts, is_mastered, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (state_id, user_id, concept_id, mastery_level, mastery_percent, consecutive_correct, total_attempts, int(is_mastered))
        )
        conn.commit()
        conn.close()
        return MasteryState(
            id=state_id, user_id=user_id, concept_id=concept_id,
            mastery_level=mastery_level, mastery_percent=mastery_percent,
            consecutive_correct=consecutive_correct, total_attempts=total_attempts,
            is_mastered=is_mastered
        )

    def get_mastery_state(self, user_id: str, concept_id: str) -> Optional[MasteryState]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM mastery_states WHERE user_id = ? AND concept_id = ?", (user_id, concept_id))
        row = cur.fetchone()
        conn.close()
        if row:
            return MasteryState(
                id=row["id"], user_id=row["user_id"], concept_id=row["concept_id"],
                mastery_level=row["mastery_level"], mastery_percent=row["mastery_percent"],
                consecutive_correct=row["consecutive_correct"], total_attempts=row["total_attempts"],
                is_mastered=bool(row["is_mastered"]), updated_at=row["updated_at"]
            )
        return None

    # 12. Spaced Repetition States
    def save_spaced_repetition_state(
        self,
        user_id: str,
        concept_id: str,
        repetition_n: int = 0,
        easiness_factor: float = 2.5,
        interval_days: int = 0,
        next_due_date: Optional[str] = None,
        last_reviewed_at: Optional[str] = None,
        consecutive_correct: int = 0,
        status: str = "new"
    ) -> SpacedRepetitionState:
        sr_id = f"sr_{user_id}_{concept_id}"
        from datetime import date
        due = next_due_date or date.today().isoformat()
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO spaced_repetition_states
               (id, user_id, concept_id, repetition_n, easiness_factor, interval_days, next_due_date, last_reviewed_at, consecutive_correct, status, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (sr_id, user_id, concept_id, repetition_n, easiness_factor, interval_days, due, last_reviewed_at, consecutive_correct, status)
        )
        conn.commit()
        conn.close()
        return SpacedRepetitionState(
            id=sr_id, user_id=user_id, concept_id=concept_id,
            repetition_n=repetition_n, easiness_factor=easiness_factor,
            interval_days=interval_days, next_due_date=due,
            last_reviewed_at=last_reviewed_at, consecutive_correct=consecutive_correct,
            status=status
        )

    def get_spaced_repetition_state(self, user_id: str, concept_id: str) -> Optional[SpacedRepetitionState]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM spaced_repetition_states WHERE user_id = ? AND concept_id = ?", (user_id, concept_id))
        row = cur.fetchone()
        conn.close()
        if row:
            return SpacedRepetitionState(
                id=row["id"], user_id=row["user_id"], concept_id=row["concept_id"],
                repetition_n=row["repetition_n"], easiness_factor=row["easiness_factor"],
                interval_days=row["interval_days"], next_due_date=row["next_due_date"],
                last_reviewed_at=row["last_reviewed_at"], consecutive_correct=row["consecutive_correct"],
                status=row["status"], updated_at=row["updated_at"]
            )
        return None

    # 14. Conversation Messages (Phase 34: Conversation Database)
    def save_conversation_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        message: str,
        message_type: str = "text",
        concept_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        expression_state: Optional[str] = None,
        **kwargs: Any
    ) -> ConversationMessage:
        """
        Store a message in the conversation database (Phase 34).
        Roles: 'user', 'assistant', 'system'
        Message types: 'greeting', 'upload', 'analysis', 'study_instruction', 'question', 'answer', 'evaluation', 'feedback', 'revision', 'mastery'
        """
        import uuid
        r = role.lower().strip()
        mtype = message_type.lower().strip()
        if r not in {"user", "assistant", "system"}:
            raise ValueError(f"Invalid role '{role}'. Expected 'user', 'assistant', or 'system'.")
        valid_types = {
            "greeting", "upload", "analysis", "study_instruction",
            "question", "answer", "evaluation", "feedback", "revision", "mastery", "text", "status"
        }
        if mtype not in valid_types:
            raise ValueError(f"Invalid message_type '{message_type}'. Expected one of {valid_types}.")

        mid = message_id or kwargs.get("id") or f"msg_{uuid.uuid4().hex[:12]}"
        meta_dict = metadata or kwargs.get("metadata_dict") or {}
        meta_json = json.dumps(meta_dict) if meta_dict else None
        expr = expression_state or kwargs.get("expression_state")
        cid = concept_id or kwargs.get("concept_id")

        username = user_id.replace("user_", "").replace("_", " ").title() or "Ashwel"
        try:
            self.get_or_create_user(username)
        except Exception:
            pass

        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        try:
            try:
                cur.execute(
                    """INSERT OR REPLACE INTO conversation_messages
                       (id, conversation_id, user_id, role, message, message_type, concept_id, metadata,
                        session_id, content, metadata_json, expression_state, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                    (mid, conversation_id, user_id, r, message, mtype, cid, meta_json,
                     conversation_id, message, meta_json, expr)
                )
            except sqlite3.IntegrityError:
                # Fallback if concept_id doesn't exist in concepts table
                if cid:
                    cid = None
                    cur.execute(
                        """INSERT OR REPLACE INTO conversation_messages
                           (id, conversation_id, user_id, role, message, message_type, concept_id, metadata,
                            session_id, content, metadata_json, expression_state, created_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                        (mid, conversation_id, user_id, r, message, mtype, None, meta_json,
                         conversation_id, message, meta_json, expr)
                    )
                else:
                    raise
            conn.commit()
        finally:
            conn.close()

        return ConversationMessage(
            id=mid,
            conversation_id=conversation_id,
            user_id=user_id,
            role=r,
            message=message,
            message_type=mtype,
            concept_id=cid,
            metadata=meta_dict,
            session_id=conversation_id,
            content=message,
            metadata_json=meta_json,
            expression_state=expr
        )

    # Alias for save_conversation_message
    store_conversation_message = save_conversation_message

    def log_conversation_message(
        self,
        message_id: str,
        user_id: str,
        role: str,
        content: str,
        session_id: Optional[str] = None,
        message_type: str = "text",
        expression_state: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        concept_id: Optional[str] = None
    ) -> ConversationMessage:
        """Legacy compatibility wrapper for log_conversation_message."""
        mtype = message_type if message_type != "text" else "greeting"
        return self.save_conversation_message(
            conversation_id=session_id or "conv_default",
            user_id=user_id,
            role=role,
            message=content,
            message_type=mtype,
            concept_id=concept_id,
            metadata=metadata,
            message_id=message_id,
            expression_state=expression_state
        )

    def get_conversation_messages(
        self,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ConversationMessage]:
        """Fetch conversation messages filtered by user_id and/or conversation_id."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        if conversation_id and user_id:
            cur.execute(
                """SELECT * FROM conversation_messages 
                   WHERE (conversation_id = ? OR session_id = ?) AND user_id = ?
                   ORDER BY created_at ASC LIMIT ?""",
                (conversation_id, conversation_id, user_id, limit)
            )
        elif conversation_id:
            cur.execute(
                """SELECT * FROM conversation_messages 
                   WHERE conversation_id = ? OR session_id = ?
                   ORDER BY created_at ASC LIMIT ?""",
                (conversation_id, conversation_id, limit)
            )
        elif user_id:
            cur.execute(
                """SELECT * FROM conversation_messages 
                   WHERE user_id = ?
                   ORDER BY created_at ASC LIMIT ?""",
                (user_id, limit)
            )
        else:
            cur.execute(
                """SELECT * FROM conversation_messages 
                   ORDER BY created_at ASC LIMIT ?""",
                (limit,)
            )
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            meta = None
            raw_meta = r["metadata"] if "metadata" in r.keys() and r["metadata"] else (r["metadata_json"] if "metadata_json" in r.keys() else None)
            if raw_meta:
                try:
                    meta = json.loads(raw_meta)
                except Exception:
                    meta = {}
            msg_text = r["message"] if "message" in r.keys() and r["message"] else (r["content"] if "content" in r.keys() else "")
            conv_id = r["conversation_id"] if "conversation_id" in r.keys() and r["conversation_id"] else (r["session_id"] if "session_id" in r.keys() else "conv_default")
            cid = r["concept_id"] if "concept_id" in r.keys() else None

            result.append(
                ConversationMessage(
                    id=r["id"],
                    conversation_id=conv_id,
                    user_id=r["user_id"],
                    role=r["role"],
                    message=msg_text,
                    message_type=r["message_type"],
                    concept_id=cid,
                    metadata=meta,
                    created_at=r["created_at"],
                    session_id=conv_id,
                    content=msg_text,
                    metadata_json=raw_meta,
                    expression_state=r["expression_state"] if "expression_state" in r.keys() else None
                )
            )
        return result

    def reconstruct_session(self, conversation_id: str, requesting_user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Reconstruct a complete pedagogical session from stored conversation messages.
        Allows the history screen to reconstruct sessions into an ordered timeline with:
        - Chronological dialogue turns
        - Concepts introduced and studied
        - Recall challenges, student answers, hybrid evaluations, and feedback
        - Mastery achievements and revision triggers
        - Phase 35: requesting_user_id authorization check preventing cross-user session reconstruction
        """
        messages = self.get_conversation_messages(conversation_id=conversation_id, limit=500)
        if not messages:
            return {
                "conversation_id": conversation_id,
                "found": False,
                "turns": [],
                "concepts_covered": [],
                "recall_exchanges": [],
                "mastery_milestones": [],
                "revisions_triggered": []
            }

        # Phase 35: User-Specific Database Access Guard
        if requesting_user_id and messages[0].user_id != requesting_user_id:
            return {
                "conversation_id": conversation_id,
                "found": False,
                "unauthorized": True,
                "error": "Access denied: session belongs to another student.",
                "turns": [],
                "concepts_covered": [],
                "recall_exchanges": [],
                "mastery_milestones": [],
                "revisions_triggered": []
            }

        user_id = messages[0].user_id
        started_at = messages[0].created_at
        ended_at = messages[-1].created_at

        turns = []
        concepts_set = []
        recall_exchanges = []
        mastery_milestones = []
        revisions_triggered = []

        active_question = None

        for msg in messages:
            m_dict = {
                "id": msg.id,
                "role": msg.role,
                "message": msg.message,
                "message_type": msg.message_type,
                "concept_id": msg.concept_id,
                "created_at": msg.created_at,
                "metadata": msg.metadata or {},
                "expression_state": msg.expression_state
            }
            turns.append(m_dict)

            if msg.concept_id and msg.concept_id not in concepts_set:
                concepts_set.append(msg.concept_id)

            if msg.message_type == "question":
                if active_question and active_question.get("answer"):
                    recall_exchanges.append(dict(active_question))
                active_question = {
                    "concept_id": msg.concept_id,
                    "question": msg.message,
                    "question_time": msg.created_at,
                    "answer": None,
                    "answer_time": None,
                    "evaluation": None,
                    "feedback": None,
                    "score": None,
                    "verdict": None
                }
            elif msg.message_type == "answer" and active_question:
                active_question["answer"] = msg.message
                active_question["answer_time"] = msg.created_at
            elif msg.message_type in ("evaluation", "feedback") and active_question:
                if msg.message_type == "evaluation":
                    active_question["evaluation"] = msg.message
                    if msg.metadata:
                        active_question["score"] = msg.metadata.get("composite_score", msg.metadata.get("score"))
                        active_question["verdict"] = msg.metadata.get("verdict")
                elif msg.message_type == "feedback":
                    active_question["feedback"] = msg.message
            elif msg.message_type in ("mastery", "revision", "study_instruction", "greeting", "upload"):
                if active_question and active_question.get("answer"):
                    recall_exchanges.append(dict(active_question))
                    active_question = None

                if msg.message_type == "mastery":
                    mastery_milestones.append({
                        "concept_id": msg.concept_id,
                        "message": msg.message,
                        "achieved_at": msg.created_at,
                        "metadata": msg.metadata or {}
                    })
                elif msg.message_type == "revision":
                    revisions_triggered.append({
                        "concept_id": msg.concept_id,
                        "message": msg.message,
                        "triggered_at": msg.created_at,
                        "metadata": msg.metadata or {}
                    })

        if active_question and active_question.get("answer"):
            recall_exchanges.append(dict(active_question))
            active_question = None

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "found": True,
            "started_at": started_at,
            "ended_at": ended_at,
            "total_messages": len(messages),
            "concepts_covered": concepts_set,
            "turns": turns,
            "recall_exchanges": recall_exchanges,
            "mastery_milestones": mastery_milestones,
            "revisions_triggered": revisions_triggered
        }

    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List distinct conversation sessions for a user with aggregated statistics.
        Enables the history screen to present a session selector.
        """
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """SELECT conversation_id,
                      MIN(created_at) as started_at,
                      MAX(created_at) as updated_at,
                      COUNT(*) as message_count,
                      COUNT(DISTINCT concept_id) as concepts_count
               FROM conversation_messages
               WHERE user_id = ?
               GROUP BY conversation_id
               ORDER BY MAX(created_at) DESC
               LIMIT ?""",
            (user_id, limit)
        )
        rows = cur.fetchall()
        conn.close()

        sessions = []
        for r in rows:
            conv_id = r["conversation_id"]
            first_msgs = self.get_conversation_messages(conversation_id=conv_id, limit=3)
            preview = first_msgs[0].message if first_msgs else "Study Session"
            sessions.append({
                "conversation_id": conv_id,
                "started_at": r["started_at"],
                "updated_at": r["updated_at"],
                "message_count": r["message_count"],
                "concepts_count": r["concepts_count"],
                "title": (preview[:60] + "...") if len(preview) > 60 else preview
            })
        return sessions

    # 15. Learning Events
    def log_learning_event(
        self,
        event_id: str,
        user_id: str,
        event_type: str,
        session_id: Optional[str] = None,
        concept_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> LearningEvent:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO learning_events
               (id, user_id, session_id, concept_id, event_type, payload_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
            (event_id, user_id, session_id, concept_id, event_type, json.dumps(payload) if payload else None)
        )
        conn.commit()
        conn.close()
        return LearningEvent(
            id=event_id, user_id=user_id, event_type=event_type, session_id=session_id,
            concept_id=concept_id, payload_json=json.dumps(payload) if payload else None
        )

    def get_learning_events(self, user_id: str, event_type: Optional[str] = None, limit: int = 50) -> List[LearningEvent]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        if event_type:
            cur.execute("SELECT * FROM learning_events WHERE user_id = ? AND event_type = ? ORDER BY created_at DESC LIMIT ?", (user_id, event_type, limit))
        else:
            cur.execute("SELECT * FROM learning_events WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        conn.close()
        return [
            LearningEvent(
                id=r["id"], user_id=r["user_id"], event_type=r["event_type"], session_id=r["session_id"],
                concept_id=r["concept_id"], payload_json=r["payload_json"], created_at=r["created_at"]
            )
            for r in rows
        ]



