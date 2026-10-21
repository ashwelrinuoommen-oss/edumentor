"""
SQLite Database connection and schema manager for EduMentor.
Phase 33 Database Model implementation.
"""

import sqlite3
import os
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "edumentor.db")


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Return a thread-safe sqlite3 connection with Row factory."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize SQLite database tables and indexes for Phase 33 Database Model."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    -- 1. users
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        studying TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- 2. documents
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        subject_id TEXT,
        module_id TEXT,
        filename TEXT NOT NULL,
        title TEXT,
        raw_text TEXT NOT NULL,
        file_type TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- 3. document_chunks
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

    -- 4. subjects
    CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- 5. concepts
    CREATE TABLE IF NOT EXISTS concepts (
        id TEXT PRIMARY KEY,
        subject_id TEXT,
        curriculum_id TEXT,
        document_id TEXT,
        title TEXT NOT NULL,
        summary TEXT,
        canonical_explanation TEXT,
        key_points_json TEXT,
        prompt_question TEXT,
        tier INTEGER DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- 6. concept_dependencies
    CREATE TABLE IF NOT EXISTS concept_dependencies (
        prerequisite_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (prerequisite_id, concept_id),
        FOREIGN KEY (prerequisite_id) REFERENCES concepts(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    -- 7. study_sessions
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

    -- 8. study_path_items
    CREATE TABLE IF NOT EXISTS study_path_items (
        id TEXT PRIMARY KEY,
        session_id TEXT,
        user_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        sequence_order INTEGER NOT NULL,
        status TEXT DEFAULT 'upcoming', -- 'mastered', 'current', 'proficient', 'review', 'upcoming'
        score REAL,
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    -- 9. recall_questions
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

    -- 10. recall_attempts
    CREATE TABLE IF NOT EXISTS recall_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        question_id TEXT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        similarity_score REAL,
        judge_score REAL,
        composite_score REAL NOT NULL,
        quality_q INTEGER NOT NULL,
        verdict TEXT NOT NULL,
        strengths_json TEXT,
        missing_json TEXT,
        misconceptions_json TEXT,
        actionable_tip TEXT,
        attempted_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    -- 11. mastery_states
    CREATE TABLE IF NOT EXISTS mastery_states (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        mastery_level TEXT NOT NULL, -- 'New', 'Developing', 'Partial', 'Strong', 'Mastered'
        mastery_percent REAL DEFAULT 0.0,
        consecutive_correct INTEGER DEFAULT 0,
        total_attempts INTEGER DEFAULT 0,
        is_mastered INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE (user_id, concept_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    -- 12. spaced_repetition_states
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
        status TEXT DEFAULT 'new', -- 'new', 'learning', 'reviewing', 'mastered', 'weak'
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE (user_id, concept_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    -- 13. notifications
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

    -- 14. conversation_messages (Phase 34: Conversation Database)
    CREATE TABLE IF NOT EXISTS conversation_messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL, -- 'user', 'assistant', 'system'
        message TEXT NOT NULL,
        message_type TEXT NOT NULL, -- 'greeting', 'upload', 'analysis', 'study_instruction', 'question', 'answer', 'evaluation', 'feedback', 'revision', 'mastery'
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

    -- 15. learning_events
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

    -- =========================================================================
    -- BACKWARDS COMPATIBILITY TABLES FOR EXISTING CODE & PHASES
    -- =========================================================================
    CREATE TABLE IF NOT EXISTS curricula (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS dependencies (
        prerequisite_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        PRIMARY KEY (prerequisite_id, concept_id),
        FOREIGN KEY (prerequisite_id) REFERENCES concepts(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS sm2_cards (
        user_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        repetition_n INTEGER DEFAULT 0,
        easiness_factor REAL DEFAULT 2.5,
        interval_days INTEGER DEFAULT 0,
        next_due_date TEXT NOT NULL,
        consecutive_correct INTEGER DEFAULT 0,
        status TEXT DEFAULT 'new',
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, concept_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS learning_sessions (
        user_id TEXT PRIMARY KEY,
        subject TEXT NOT NULL,
        current_concept_id TEXT,
        current_concept_title TEXT,
        finished_count INTEGER DEFAULT 0,
        total_count INTEGER DEFAULT 0,
        state TEXT NOT NULL,
        session_data_json TEXT,
        is_active INTEGER DEFAULT 1,
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS subject_progress (
        user_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        mastery INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, subject),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS modules (
        id TEXT PRIMARY KEY,
        subject_id TEXT NOT NULL,
        module_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        document_id TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS source_chunks (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        module_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_text TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS question_groundings (
        question_id TEXT PRIMARY KEY,
        subject_id TEXT NOT NULL,
        module_id TEXT NOT NULL,
        document_id TEXT NOT NULL,
        concept_id TEXT NOT NULL,
        source_chunk_ids_json TEXT NOT NULL,
        question_text TEXT NOT NULL,
        explanation TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- =========================================================================
    -- SYNC TRIGGERS FOR COMPLETE INTEROPERABILITY
    -- =========================================================================
    CREATE TRIGGER IF NOT EXISTS trg_sync_concept_deps_insert AFTER INSERT ON dependencies
    BEGIN
        INSERT OR IGNORE INTO concept_dependencies (prerequisite_id, concept_id, created_at)
        VALUES (new.prerequisite_id, new.concept_id, datetime('now'));
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_concept_deps_reverse AFTER INSERT ON concept_dependencies
    BEGIN
        INSERT OR IGNORE INTO dependencies (prerequisite_id, concept_id)
        VALUES (new.prerequisite_id, new.concept_id);
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_sm2_insert AFTER INSERT ON sm2_cards
    BEGIN
        INSERT OR REPLACE INTO spaced_repetition_states
        (id, user_id, concept_id, repetition_n, easiness_factor, interval_days, next_due_date, consecutive_correct, status, updated_at)
        VALUES (
            new.user_id || '_' || new.concept_id,
            new.user_id,
            new.concept_id,
            new.repetition_n,
            new.easiness_factor,
            new.interval_days,
            new.next_due_date,
            new.consecutive_correct,
            new.status,
            new.updated_at
        );
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_sm2_update AFTER UPDATE ON sm2_cards
    BEGIN
        INSERT OR REPLACE INTO spaced_repetition_states
        (id, user_id, concept_id, repetition_n, easiness_factor, interval_days, next_due_date, consecutive_correct, status, updated_at)
        VALUES (
            new.user_id || '_' || new.concept_id,
            new.user_id,
            new.concept_id,
            new.repetition_n,
            new.easiness_factor,
            new.interval_days,
            new.next_due_date,
            new.consecutive_correct,
            new.status,
            new.updated_at
        );
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_chunks_insert AFTER INSERT ON source_chunks
    BEGIN
        INSERT OR IGNORE INTO document_chunks
        (id, document_id, module_id, chunk_index, chunk_text, created_at)
        VALUES (new.id, new.document_id, new.module_id, new.chunk_index, new.chunk_text, datetime('now'));
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_chunks_reverse AFTER INSERT ON document_chunks
    BEGIN
        INSERT OR IGNORE INTO source_chunks
        (id, document_id, module_id, chunk_index, chunk_text)
        VALUES (new.id, new.document_id, coalesce(new.module_id, 'm1'), new.chunk_index, new.chunk_text);
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_curricula_insert AFTER INSERT ON curricula
    BEGIN
        INSERT OR IGNORE INTO subjects (id, title, description, created_at)
        VALUES (new.id, new.title, new.description, new.created_at);
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_subjects_reverse AFTER INSERT ON subjects
    BEGIN
        INSERT OR IGNORE INTO curricula (id, title, description, created_at)
        VALUES (new.id, new.title, new.description, new.created_at);
    END;

    CREATE TRIGGER IF NOT EXISTS trg_sync_sessions_insert AFTER INSERT ON learning_sessions
    BEGIN
        INSERT OR REPLACE INTO study_sessions
        (id, user_id, subject_title, current_concept_id, current_concept_title, finished_count, total_count, state, is_active, session_data_json, started_at, updated_at)
        VALUES (
            'session_' || new.user_id,
            new.user_id,
            new.subject,
            new.current_concept_id,
            new.current_concept_title,
            new.finished_count,
            new.total_count,
            new.state,
            new.is_active,
            new.session_data_json,
            datetime('now'),
            new.updated_at
        );
    END;

    -- =========================================================================
    -- INDEXES FOR PERFORMANCE
    -- =========================================================================
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc ON document_chunks(document_id);
    CREATE INDEX IF NOT EXISTS idx_concept_deps_prereq ON concept_dependencies(prerequisite_id);
    CREATE INDEX IF NOT EXISTS idx_concept_deps_concept ON concept_dependencies(concept_id);
    CREATE INDEX IF NOT EXISTS idx_study_sessions_user ON study_sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_path_items_session ON study_path_items(session_id);
    CREATE INDEX IF NOT EXISTS idx_recall_questions_concept ON recall_questions(concept_id);
    CREATE INDEX IF NOT EXISTS idx_recall_attempts_user_concept ON recall_attempts(user_id, concept_id);
    CREATE INDEX IF NOT EXISTS idx_mastery_user_concept ON mastery_states(user_id, concept_id);
    CREATE INDEX IF NOT EXISTS idx_sr_states_due ON spaced_repetition_states(next_due_date, status);
    CREATE INDEX IF NOT EXISTS idx_notifs_user ON notifications(user_id, is_read);
    CREATE INDEX IF NOT EXISTS idx_conv_messages_user ON conversation_messages(user_id, created_at);
    CREATE INDEX IF NOT EXISTS idx_learning_events_user ON learning_events(user_id, event_type);
    """)

    conn.commit()

    # Gracefully add missing columns to pre-existing tables if they were created in earlier phases
    for tbl, col, ctype in [
        ("users", "studying", "TEXT"),
        ("documents", "user_id", "TEXT"),
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

    # Safe index creation for migrated columns
    for idx_sql in [
        "CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_docs_subject ON documents(subject_id);",
        "CREATE INDEX IF NOT EXISTS idx_concepts_subject ON concepts(subject_id);",
        "CREATE INDEX IF NOT EXISTS idx_conv_messages_conv ON conversation_messages(conversation_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_conv_messages_concept ON conversation_messages(concept_id);",
        "CREATE INDEX IF NOT EXISTS idx_conv_messages_type ON conversation_messages(message_type);"
    ]:
        try:
            cursor.execute(idx_sql)
            conn.commit()
        except Exception:
            pass

    conn.close()
