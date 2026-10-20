"""
Database layer for EduMentor using SQLite.
Stores documents, extracted concepts, dependencies, SM-2 cards, and recall logs.
"""

import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "edumentor.db")


@contextmanager
def get_connection(db_path: str = DEFAULT_DB_PATH):
    """Get a SQLite database connection with row factory enabled and automatic close."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize database tables and indexes for Phase 33 Database Model."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                studying TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)

        # 2. documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                subject_id TEXT,
                module_id TEXT,
                filename TEXT,
                raw_text TEXT NOT NULL,
                file_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. document_chunks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                module_id TEXT,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );
        """)

        # 4. subjects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)

        # 5. concepts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concepts (
                id TEXT PRIMARY KEY,
                document_id INTEGER,
                subject_id TEXT,
                curriculum_id TEXT,
                title TEXT NOT NULL,
                summary TEXT,
                canonical_explanation TEXT NOT NULL,
                key_points TEXT NOT NULL, -- JSON list of strings
                prompt_question TEXT NOT NULL,
                tier INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );
        """)

        # 6. concept_dependencies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concept_dependencies (
                prerequisite_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (prerequisite_id, concept_id),
                FOREIGN KEY (prerequisite_id) REFERENCES concepts(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # 7. study_sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                subject_id TEXT,
                subject_title TEXT NOT NULL,
                current_concept_id TEXT,
                current_concept_title TEXT,
                finished_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                state TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                session_data_json TEXT,
                started_at TEXT NOT NULL DEFAULT (datetime('now')),
                ended_at TEXT,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 8. study_path_items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_path_items (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                sequence_order INTEGER NOT NULL,
                status TEXT DEFAULT 'upcoming',
                score REAL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # 9. recall_questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recall_questions (
                id TEXT PRIMARY KEY,
                concept_id TEXT NOT NULL,
                document_id TEXT,
                subject_id TEXT,
                question_text TEXT NOT NULL,
                question_type TEXT DEFAULT 'open_ended',
                sample_solution TEXT,
                explanation TEXT,
                grounding_chunk_ids_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # 10. recall_attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recall_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                concept_id TEXT NOT NULL,
                question_id TEXT,
                question TEXT,
                answer TEXT,
                student_response TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                judge_score REAL NOT NULL,
                composite_score REAL,
                final_score REAL NOT NULL,
                quality_q INTEGER NOT NULL,
                verdict TEXT,
                feedback_json TEXT NOT NULL,
                strengths_json TEXT,
                missing_json TEXT,
                misconceptions_json TEXT,
                actionable_tip TEXT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # 11. mastery_states
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mastery_states (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                mastery_level TEXT NOT NULL,
                mastery_percent REAL DEFAULT 0.0,
                consecutive_correct INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                is_mastered INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE (user_id, concept_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # 12. spaced_repetition_states
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spaced_repetition_states (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                repetition_n INTEGER DEFAULT 0,
                easiness_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 0,
                next_due_date TEXT NOT NULL,
                last_reviewed_at TEXT,
                consecutive_correct INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE (user_id, concept_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # 13. notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                concept_id TEXT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 14. conversation_messages (Phase 34: Conversation Database)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT NOT NULL,
                concept_id TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                metadata TEXT,
                session_id TEXT,
                content TEXT,
                metadata_json TEXT,
                expression_state TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE SET NULL
            );
        """)

        # 15. learning_events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT,
                concept_id TEXT,
                event_type TEXT NOT NULL,
                payload_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Backwards compatibility tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                prerequisite_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                PRIMARY KEY (prerequisite_id, concept_id),
                FOREIGN KEY (prerequisite_id) REFERENCES concepts(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sm2_cards (
                concept_id TEXT PRIMARY KEY,
                repetition_n INTEGER DEFAULT 0,
                easiness_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 0,
                next_due_date DATE NOT NULL,
                last_reviewed_at TIMESTAMP,
                total_reviews INTEGER DEFAULT 0,
                consecutive_correct INTEGER DEFAULT 0,
                last_quality_score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );
        """)

        # Safe column migrations for pre-existing tables
        for tbl, col, ctype in [
            ("users", "studying", "TEXT"),
            ("documents", "subject_id", "TEXT"),
            ("documents", "module_id", "TEXT"),
            ("documents", "filename", "TEXT"),
            ("documents", "title", "TEXT"),
            ("concepts", "subject_id", "TEXT"),
            ("concepts", "curriculum_id", "TEXT"),
            ("concepts", "document_id", "TEXT"),
            ("concepts", "tier", "INTEGER DEFAULT 0"),
            ("concepts", "prompt_question", "TEXT"),
            ("conversation_messages", "conversation_id", "TEXT"),
            ("conversation_messages", "message", "TEXT"),
            ("conversation_messages", "concept_id", "TEXT"),
            ("conversation_messages", "metadata", "TEXT")
        ]:
            try:
                cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {ctype}")
                conn.commit()
            except Exception:
                pass

        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_concepts_doc ON concepts(document_id);",
            "CREATE INDEX IF NOT EXISTS idx_sm2_due ON sm2_cards(next_due_date, status);",
            "CREATE INDEX IF NOT EXISTS idx_attempts_concept ON recall_attempts(concept_id);",
            "CREATE INDEX IF NOT EXISTS idx_concept_deps ON concept_dependencies(prerequisite_id, concept_id);",
            "CREATE INDEX IF NOT EXISTS idx_sr_states ON spaced_repetition_states(next_due_date, status);",
            "CREATE INDEX IF NOT EXISTS idx_study_sessions ON study_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_learning_events ON learning_events(user_id, event_type);",
            "CREATE INDEX IF NOT EXISTS idx_conv_messages_conv ON conversation_messages(conversation_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_conv_messages_concept ON conversation_messages(concept_id);",
            "CREATE INDEX IF NOT EXISTS idx_conv_messages_type ON conversation_messages(message_type);"
        ]:
            try:
                cursor.execute(idx_sql)
                conn.commit()
            except Exception:
                pass



def save_document(
    title: str,
    raw_text: str,
    file_type: str = "text",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Insert a document and return its auto-generated ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (title, raw_text, file_type) VALUES (?, ?, ?)",
            (title, raw_text, file_type)
        )
        conn.commit()
        return cursor.lastrowid


def save_concepts_and_dependencies(
    document_id: Optional[int],
    concepts: List[Dict[str, Any]],
    dependencies: List[Tuple[str, str]],
    db_path: str = DEFAULT_DB_PATH
) -> None:
    """
    Save a batch of extracted concepts, their dependency edges, and initialize SM-2 cards.
    Each concept dict must have: id, title, summary, canonical_explanation, key_points (list), prompt_question.
    """
    today_str = date.today().isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        for c in concepts:
            key_points_json = json.dumps(c.get("key_points", []))
            cursor.execute("""
                INSERT OR REPLACE INTO concepts 
                (id, document_id, title, summary, canonical_explanation, key_points, prompt_question)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"],
                document_id,
                c["title"],
                c.get("summary", ""),
                c["canonical_explanation"],
                key_points_json,
                c.get("prompt_question", f"Explain {c['title']} in your own words, covering core principles.")
            ))

            # Initialize SM-2 card if not existing
            cursor.execute("""
                INSERT OR IGNORE INTO sm2_cards 
                (concept_id, repetition_n, easiness_factor, interval_days, next_due_date, status)
                VALUES (?, 0, 2.5, 0, ?, 'new')
            """, (c["id"], today_str))

        for prereq_id, concept_id in dependencies:
            if prereq_id != concept_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO dependencies (prerequisite_id, concept_id)
                    VALUES (?, ?)
                """, (prereq_id, concept_id))

        conn.commit()


def get_all_documents(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all ingested documents."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, d.title, d.file_type, d.created_at,
                   COUNT(c.id) AS concept_count
            FROM documents d
            LEFT JOIN concepts c ON d.id = c.document_id
            GROUP BY d.id
            ORDER BY d.id DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_all_concepts(
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Fetch concepts with associated SM-2 scheduling metadata."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT c.*, s.repetition_n, s.easiness_factor, s.interval_days,
                   s.next_due_date, s.last_reviewed_at, s.total_reviews,
                   s.consecutive_correct, s.last_quality_score, s.status AS sm2_status
            FROM concepts c
            LEFT JOIN sm2_cards s ON c.id = s.concept_id
        """
        params = []
        if document_id is not None:
            query += " WHERE c.document_id = ?"
            params.append(document_id)
        
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            item = dict(row)
            item["key_points"] = json.loads(item["key_points"]) if item["key_points"] else []
            results.append(item)
        return results


def get_concept(concept_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve a single concept with its SM-2 status and prerequisites."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, s.repetition_n, s.easiness_factor, s.interval_days,
                   s.next_due_date, s.last_reviewed_at, s.total_reviews,
                   s.consecutive_correct, s.last_quality_score, s.status AS sm2_status
            FROM concepts c
            LEFT JOIN sm2_cards s ON c.id = s.concept_id
            WHERE c.id = ?
        """, (concept_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        item = dict(row)
        item["key_points"] = json.loads(item["key_points"]) if item["key_points"] else []

        # Get prerequisites
        cursor.execute("""
            SELECT prerequisite_id FROM dependencies WHERE concept_id = ?
        """, (concept_id,))
        item["prerequisites"] = [r["prerequisite_id"] for r in cursor.fetchall()]

        # Get dependents
        cursor.execute("""
            SELECT concept_id FROM dependencies WHERE prerequisite_id = ?
        """, (concept_id,))
        item["dependents"] = [r["concept_id"] for r in cursor.fetchall()]

        return item


def get_dependencies(
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> List[Tuple[str, str]]:
    """Fetch prerequisite dependency edges."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if document_id is not None:
            cursor.execute("""
                SELECT d.prerequisite_id, d.concept_id
                FROM dependencies d
                JOIN concepts c ON d.concept_id = c.id
                WHERE c.document_id = ?
            """, (document_id,))
        else:
            cursor.execute("SELECT prerequisite_id, concept_id FROM dependencies")
        return [(row["prerequisite_id"], row["concept_id"]) for row in cursor.fetchall()]


def get_sm2_card(concept_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve SM-2 card record for a concept."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sm2_cards WHERE concept_id = ?", (concept_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_sm2_card(
    concept_id: str,
    repetition_n: int,
    easiness_factor: float,
    interval_days: int,
    next_due_date: str,
    last_quality_score: int,
    status: str,
    consecutive_correct: int,
    db_path: str = DEFAULT_DB_PATH
) -> None:
    """Update SM-2 spaced repetition state."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sm2_cards
            SET repetition_n = ?,
                easiness_factor = ?,
                interval_days = ?,
                next_due_date = ?,
                last_reviewed_at = CURRENT_TIMESTAMP,
                total_reviews = total_reviews + 1,
                consecutive_correct = ?,
                last_quality_score = ?,
                status = ?
            WHERE concept_id = ?
        """, (
            repetition_n,
            easiness_factor,
            interval_days,
            next_due_date,
            consecutive_correct,
            last_quality_score,
            status,
            concept_id
        ))
        conn.commit()


def record_recall_attempt(
    concept_id: str,
    student_response: str,
    similarity_score: float,
    judge_score: float,
    final_score: float,
    quality_q: int,
    feedback: Dict[str, Any],
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Save student active recall submission and evaluation metrics."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recall_attempts 
            (concept_id, student_response, similarity_score, judge_score, final_score, quality_q, feedback_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            concept_id,
            student_response,
            similarity_score,
            judge_score,
            final_score,
            quality_q,
            json.dumps(feedback)
        ))
        conn.commit()
        return cursor.lastrowid


def get_recall_history(
    concept_id: Optional[str] = None,
    limit: int = 50,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """Retrieve recall history log."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT r.*, c.title AS concept_title
            FROM recall_attempts r
            JOIN concepts c ON r.concept_id = c.id
        """
        params = []
        if concept_id:
            query += " WHERE r.concept_id = ?"
            params.append(concept_id)
        query += " ORDER BY r.attempted_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            item = dict(row)
            item["feedback"] = json.loads(item["feedback_json"]) if item["feedback_json"] else {}
            results.append(item)
        return results


def get_due_and_weak_concepts(
    target_date: Optional[str] = None,
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """
    Get concepts that are due for revision or flagged as weak.
    Prioritizes:
    1. Weak concepts (last_quality_score < 3 or status == 'weak')
    2. Overdue concepts (next_due_date <= target_date)
    3. New unstudied concepts
    """
    if target_date is None:
        target_date = date.today().isoformat()

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT c.*, s.repetition_n, s.easiness_factor, s.interval_days,
                   s.next_due_date, s.last_reviewed_at, s.total_reviews,
                   s.consecutive_correct, s.last_quality_score, s.status AS sm2_status,
                   CASE 
                     WHEN s.status = 'weak' OR s.last_quality_score < 3 AND s.total_reviews > 0 THEN 1
                     WHEN s.next_due_date <= ? THEN 2
                     WHEN s.total_reviews = 0 THEN 3
                     ELSE 4
                   END AS priority_rank
            FROM concepts c
            JOIN sm2_cards s ON c.id = s.concept_id
        """
        params = [target_date]
        if document_id is not None:
            query += " WHERE c.document_id = ?"
            params.append(document_id)

        query += """
            ORDER BY priority_rank ASC, s.next_due_date ASC, s.last_quality_score ASC
        """
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            item = dict(row)
            item["key_points"] = json.loads(item["key_points"]) if item["key_points"] else []
            results.append(item)
        return results


def reset_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """Clear all data and reinitialize schema."""
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db(db_path)


def add_custom_concept(
    title: str,
    canonical_explanation: str,
    key_points: List[str],
    prompt_question: Optional[str] = None,
    summary: Optional[str] = None,
    concept_id: Optional[str] = None,
    document_id: Optional[int] = None,
    prerequisites: Optional[List[str]] = None,
    db_path: str = DEFAULT_DB_PATH
) -> str:
    """Create a new custom concept, associated SM-2 card, and dependencies."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if not concept_id:
            base_slug = re.sub(r"[^a-zA-Z0-9_]+", "_", title.lower()).strip("_") or "concept"
            cid = base_slug
            idx = 1
            while True:
                cursor.execute("SELECT 1 FROM concepts WHERE id = ?", (cid,))
                if not cursor.fetchone():
                    break
                cid = f"{base_slug}_{idx}"
                idx += 1
        else:
            cid = concept_id

        if not prompt_question:
            prompt_question = f"Explain the core mechanisms of {title} in your own words."
        if not summary:
            summary = canonical_explanation[:120] + ("..." if len(canonical_explanation) > 120 else "")

        cursor.execute("""
            INSERT INTO concepts (id, document_id, title, summary, canonical_explanation, key_points, prompt_question)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cid,
            document_id,
            title,
            summary,
            canonical_explanation,
            json.dumps(key_points),
            prompt_question
        ))

        today_str = date.today().isoformat()
        cursor.execute("""
            INSERT OR IGNORE INTO sm2_cards (concept_id, repetition_n, easiness_factor, interval_days, next_due_date, status)
            VALUES (?, 0, 2.5, 0, ?, 'new')
        """, (cid, today_str))

        if prerequisites:
            for prereq in prerequisites:
                if prereq and prereq != cid:
                    cursor.execute("""
                        INSERT OR IGNORE INTO dependencies (prerequisite_id, concept_id)
                        VALUES (?, ?)
                    """, (prereq, cid))

        conn.commit()
        return cid


def update_concept(
    concept_id: str,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    canonical_explanation: Optional[str] = None,
    key_points: Optional[List[str]] = None,
    prompt_question: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> bool:
    """Update editable fields of an existing concept."""
    fields = []
    params = []
    if title is not None:
        fields.append("title = ?")
        params.append(title)
    if summary is not None:
        fields.append("summary = ?")
        params.append(summary)
    if canonical_explanation is not None:
        fields.append("canonical_explanation = ?")
        params.append(canonical_explanation)
    if key_points is not None:
        fields.append("key_points = ?")
        params.append(json.dumps(key_points))
    if prompt_question is not None:
        fields.append("prompt_question = ?")
        params.append(prompt_question)

    if not fields:
        return False

    params.append(concept_id)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE concepts SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        return cursor.rowcount > 0


def delete_concept(concept_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Delete a concept and clean up associated records."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dependencies WHERE prerequisite_id = ? OR concept_id = ?", (concept_id, concept_id))
        cursor.execute("DELETE FROM sm2_cards WHERE concept_id = ?", (concept_id,))
        cursor.execute("DELETE FROM recall_attempts WHERE concept_id = ?", (concept_id,))
        cursor.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))
        conn.commit()
        return cursor.rowcount > 0


def add_dependency(prerequisite_id: str, concept_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Add a prerequisite dependency link between two concepts."""
    if prerequisite_id == concept_id:
        return False
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO dependencies (prerequisite_id, concept_id)
            VALUES (?, ?)
        """, (prerequisite_id, concept_id))
        conn.commit()
        return cursor.rowcount > 0


def remove_dependency(prerequisite_id: str, concept_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Remove a prerequisite dependency link between two concepts."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM dependencies WHERE prerequisite_id = ? AND concept_id = ?
        """, (prerequisite_id, concept_id))
        conn.commit()
        return cursor.rowcount > 0


def export_curriculum_dict(
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Export a curriculum document or all concepts as an interoperable JSON-serializable dictionary."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        doc_title = "EduMentor Exported Curriculum"
        doc_desc = "Exported curriculum deck from EduMentor Adaptive Mastery System"
        if document_id is not None:
            cursor.execute("SELECT title, raw_text FROM documents WHERE id = ?", (document_id,))
            drow = cursor.fetchone()
            if drow:
                doc_title = drow["title"]
                doc_desc = drow["raw_text"][:250]

        concepts = get_all_concepts(document_id=document_id, db_path=db_path)
        deps = get_dependencies(document_id=document_id, db_path=db_path)

        exportable_concepts = []
        for c in concepts:
            exportable_concepts.append({
                "id": c["id"],
                "title": c["title"],
                "summary": c.get("summary", ""),
                "canonical_explanation": c["canonical_explanation"],
                "key_points": c.get("key_points", []),
                "prompt_question": c.get("prompt_question", ""),
                "sm2": {
                    "repetition_n": c.get("repetition_n", 0),
                    "easiness_factor": c.get("easiness_factor", 2.5),
                    "interval_days": c.get("interval_days", 0),
                    "next_due_date": c.get("next_due_date", ""),
                    "status": c.get("sm2_status", "new")
                }
            })

        return {
            "title": doc_title,
            "description": doc_desc,
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "concepts": exportable_concepts,
            "dependencies": deps
        }


def export_curriculum_json(
    document_id: Optional[int] = None,
    indent: int = 2,
    db_path: str = DEFAULT_DB_PATH
) -> str:
    """Export curriculum formatted as indented JSON string."""
    return json.dumps(export_curriculum_dict(document_id=document_id, db_path=db_path), indent=indent)


def import_curriculum_dict(
    data: Dict[str, Any],
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[int, int]:
    """Import a curriculum dictionary, restoring concepts, prerequisites, and SM-2 metadata."""
    title = data.get("title", "Imported Curriculum")
    desc = data.get("description", "Imported via JSON Deck")
    concepts_raw = data.get("concepts", [])
    dependencies_raw = data.get("dependencies", [])

    doc_id = save_document(title=title, raw_text=desc, file_type="json_deck", db_path=db_path)

    cleaned_concepts = []
    for c in concepts_raw:
        cleaned_concepts.append({
            "id": c["id"],
            "title": c["title"],
            "summary": c.get("summary", ""),
            "canonical_explanation": c["canonical_explanation"],
            "key_points": c.get("key_points", []),
            "prompt_question": c.get("prompt_question", f"Explain {c['title']} in your own words.")
        })

    deps = [(d[0], d[1]) for d in dependencies_raw if len(d) >= 2]

    save_concepts_and_dependencies(
        document_id=doc_id,
        concepts=cleaned_concepts,
        dependencies=deps,
        db_path=db_path
    )

    # If any SM-2 metadata was included in export, restore it
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for c in concepts_raw:
            if "sm2" in c and isinstance(c["sm2"], dict):
                sm = c["sm2"]
                cursor.execute("""
                    UPDATE sm2_cards
                    SET repetition_n = ?,
                        easiness_factor = ?,
                        interval_days = ?,
                        next_due_date = ?,
                        status = ?
                    WHERE concept_id = ?
                """, (
                    sm.get("repetition_n", 0),
                    sm.get("easiness_factor", 2.5),
                    sm.get("interval_days", 0),
                    sm.get("next_due_date", date.today().isoformat()),
                    sm.get("status", "new"),
                    c["id"]
                ))
        conn.commit()

    return doc_id, len(cleaned_concepts)


def advance_sm2_simulation_days(
    days: int,
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Time-travel simulation: advance time by `days` by shifting next_due_date backwards by `days`.
    This brings cards scheduled in the future into 'due today' or overdue status.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if document_id is not None:
            cursor.execute("""
                SELECT s.concept_id, s.next_due_date
                FROM sm2_cards s
                JOIN concepts c ON s.concept_id = c.id
                WHERE c.document_id = ?
            """, (document_id,))
        else:
            cursor.execute("SELECT concept_id, next_due_date FROM sm2_cards")

        cards = cursor.fetchall()
        count = 0
        for row in cards:
            cid = row["concept_id"]
            due_str = row["next_due_date"]
            try:
                cur_date = datetime.strptime(due_str, "%Y-%m-%d").date()
                new_date = cur_date - timedelta(days=days)
                cursor.execute(
                    "UPDATE sm2_cards SET next_due_date = ? WHERE concept_id = ?",
                    (new_date.isoformat(), cid)
                )
                count += 1
            except Exception:
                continue

        conn.commit()
        return count


def reset_sm2_dates(
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Reset SM-2 due dates: new cards become due today, reviewed cards recomputed from interval."""
    today = date.today()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if document_id is not None:
            cursor.execute("""
                SELECT s.concept_id, s.total_reviews, s.interval_days
                FROM sm2_cards s
                JOIN concepts c ON s.concept_id = c.id
                WHERE c.document_id = ?
            """, (document_id,))
        else:
            cursor.execute("SELECT concept_id, total_reviews, interval_days FROM sm2_cards")

        cards = cursor.fetchall()
        count = 0
        for row in cards:
            cid = row["concept_id"]
            if row["total_reviews"] == 0:
                new_date = today
            else:
                new_date = today + timedelta(days=row["interval_days"])
            cursor.execute(
                "UPDATE sm2_cards SET next_due_date = ? WHERE concept_id = ?",
                (new_date.isoformat(), cid)
            )
            count += 1
        conn.commit()
        return count


def get_sm2_due_forecast(
    document_id: Optional[int] = None,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, int]:
    """
    Returns breakdown of cards due across temporal horizons:
    - overdue: due date < today
    - today: due date == today
    - 1_to_3_days: today < due date <= today + 3
    - 4_to_7_days: today + 3 < due date <= today + 7
    - 8_to_14_days: today + 7 < due date <= today + 14
    - 15_plus_days: due date > today + 14
    """
    today = date.today()
    forecast = {
        "overdue": 0,
        "today": 0,
        "1_to_3_days": 0,
        "4_to_7_days": 0,
        "8_to_14_days": 0,
        "15_plus_days": 0,
        "total": 0,
    }
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if document_id is not None:
            cursor.execute("""
                SELECT s.next_due_date, s.status
                FROM sm2_cards s
                JOIN concepts c ON s.concept_id = c.id
                WHERE c.document_id = ?
            """, (document_id,))
        else:
            cursor.execute("SELECT next_due_date, status FROM sm2_cards")

        rows = cursor.fetchall()
        for row in rows:
            due_str = row["next_due_date"]
            forecast["total"] += 1
            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
                delta_days = (due_date - today).days
                if delta_days < 0:
                    forecast["overdue"] += 1
                elif delta_days == 0:
                    forecast["today"] += 1
                elif delta_days <= 3:
                    forecast["1_to_3_days"] += 1
                elif delta_days <= 7:
                    forecast["4_to_7_days"] += 1
                elif delta_days <= 14:
                    forecast["8_to_14_days"] += 1
                else:
                    forecast["15_plus_days"] += 1
            except Exception:
                forecast["today"] += 1

    return forecast

