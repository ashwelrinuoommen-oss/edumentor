"""
Tests for Phase 34 — Conversation Database.

Verifies:
1. Conversation database table structure:
   - conversation_id
   - user_id
   - role
   - message
   - message_type
   - concept_id
   - created_at
   - metadata
2. Supported Roles:
   - user
   - assistant
   - system
3. Supported Message Types:
   - greeting
   - upload
   - analysis
   - study_instruction
   - question
   - answer
   - evaluation
   - feedback
   - revision
   - mastery
4. Session reconstruction to reconstruct pedagogical learning sessions for history screen.
5. User conversations grouping for history list.
6. HistoryService session reconstruction and conversation retrieval.
7. Orchestrator conversation logging across learning workflow.
8. FastAPI history endpoints (/api/history and /api/history/sessions/{conversation_id}).
"""

import os
import json
import tempfile
import unittest
from fastapi.testclient import TestClient

from edumentor.database.database import init_db, get_db_connection
from edumentor.database.repository import EduMentorRepository
from edumentor.database.models import ConversationMessage, VALID_CONVERSATION_ROLES, VALID_MESSAGE_TYPES
from edumentor.services.history_service import HistoryService
from edumentor.orchestrator import EduMentorOrchestrator
from server import app


class TestPhase34ConversationDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.repo = EduMentorRepository(db_path=self.db_path)
        self.repo.get_or_create_user(username="Ashwel", email="ashwel@edumentor.ai")
        # Seed test concepts to satisfy foreign key constraints
        self.repo.save_concept(
            concept_id="concept_cpu_scheduling",
            title="CPU Scheduling",
            summary="CPU Scheduling concept",
            canonical_explanation="CPU Scheduling explanation",
            key_points=["point 1", "point 2"]
        )
        self.repo.save_concept(
            concept_id="concept_os_paging",
            title="Paging",
            summary="Paging concept",
            canonical_explanation="Paging explanation",
            key_points=["point 1", "point 2"]
        )
        self.repo.save_concept(
            concept_id="concept_c1",
            title="Concept 1",
            summary="Concept 1",
            canonical_explanation="Explanation 1",
            key_points=["p1"]
        )

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_01_schema_has_all_required_columns(self):
        """Verify conversation_messages table contains all Phase 34 required fields."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(conversation_messages)")
        columns = {row["name"] for row in cur.fetchall()}
        conn.close()

        required_columns = {
            "conversation_id",
            "user_id",
            "role",
            "message",
            "message_type",
            "concept_id",
            "created_at",
            "metadata"
        }
        for col in required_columns:
            self.assertIn(col, columns, f"Column '{col}' must exist in conversation_messages")

    def test_02_all_roles_supported(self):
        """Verify user, assistant, system roles are stored and validated."""
        self.assertEqual(VALID_CONVERSATION_ROLES, {"user", "assistant", "system"})

        for role in ["user", "assistant", "system"]:
            msg = self.repo.save_conversation_message(
                conversation_id="conv_roles_test",
                user_id="user_ashwel",
                role=role,
                message=f"Hello from {role}",
                message_type="greeting"
            )
            self.assertEqual(msg.role, role)
            self.assertEqual(msg.message, f"Hello from {role}")

        # Invalid role should raise ValueError
        with self.assertRaises(ValueError):
            self.repo.save_conversation_message(
                conversation_id="conv_roles_test",
                user_id="user_ashwel",
                role="invalid_role",
                message="Will fail",
                message_type="greeting"
            )

    def test_03_all_ten_message_types_supported(self):
        """Verify all 10 required message types are supported and persisted correctly."""
        required_types = [
            "greeting",
            "upload",
            "analysis",
            "study_instruction",
            "question",
            "answer",
            "evaluation",
            "feedback",
            "revision",
            "mastery"
        ]

        for m_type in required_types:
            self.assertIn(m_type, VALID_MESSAGE_TYPES)
            msg = self.repo.save_conversation_message(
                conversation_id="conv_types_test",
                user_id="user_ashwel",
                role="assistant" if m_type != "answer" and m_type != "upload" else "user",
                message=f"Test message for type {m_type}",
                message_type=m_type,
                concept_id="concept_cpu_scheduling",
                metadata={"type_key": m_type}
            )
            self.assertEqual(msg.message_type, m_type)
            self.assertEqual(msg.concept_id, "concept_cpu_scheduling")
            self.assertEqual(msg.metadata.get("type_key"), m_type)

        # Retrieve and verify count
        retrieved = self.repo.get_conversation_messages(conversation_id="conv_types_test")
        self.assertEqual(len(retrieved), len(required_types))
        types_found = [m.message_type for m in retrieved]
        self.assertEqual(types_found, required_types)

    def test_04_session_reconstruction(self):
        """Verify session reconstruction recreates turns, recall exchanges, and milestones."""
        conv_id = "conv_recon_101"
        cid = "concept_os_paging"

        # Simulate complete pedagogical interaction sequence:
        # 1. greeting
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Welcome back, Ashwel! Ready for Virtual Memory?", message_type="greeting"
        )
        # 2. upload
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="user",
            message="Uploaded Operating Systems Module 3 notes", message_type="upload"
        )
        # 3. analysis
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Analyzed 4 concepts in your notes.", message_type="analysis"
        )
        # 4. study_instruction
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Let's study Paging and Page Tables.", message_type="study_instruction", concept_id=cid
        )
        # 5. question
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="What is the role of a page table in virtual memory?", message_type="question", concept_id=cid
        )
        # 6. answer
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="user",
            message="It maps virtual page numbers to physical frame numbers.", message_type="answer", concept_id=cid
        )
        # 7. evaluation
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Accurate! Composite score: 92/100", message_type="evaluation", concept_id=cid,
            metadata={"composite_score": 92, "verdict": "STRONG"}
        )
        # 8. feedback
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Excellent explanation of virtual address translation.", message_type="feedback", concept_id=cid
        )
        # 9. revision
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Revision scheduled in 3 days via SM-2.", message_type="revision", concept_id=cid
        )
        # 10. mastery
        self.repo.save_conversation_message(
            conversation_id=conv_id, user_id="user_ashwel", role="assistant",
            message="Congratulations! Concept Paging Mastered.", message_type="mastery", concept_id=cid
        )

        reconstructed = self.repo.reconstruct_session(conversation_id=conv_id)

        self.assertTrue(reconstructed["found"])
        self.assertEqual(reconstructed["conversation_id"], conv_id)
        self.assertEqual(reconstructed["user_id"], "user_ashwel")
        self.assertEqual(reconstructed["total_messages"], 10)
        self.assertIn(cid, reconstructed["concepts_covered"])

        # Chronological turns
        self.assertEqual(len(reconstructed["turns"]), 10)
        self.assertEqual(reconstructed["turns"][0]["message_type"], "greeting")
        self.assertEqual(reconstructed["turns"][4]["message_type"], "question")
        self.assertEqual(reconstructed["turns"][5]["message_type"], "answer")
        self.assertEqual(reconstructed["turns"][9]["message_type"], "mastery")

        # Recall exchanges
        self.assertEqual(len(reconstructed["recall_exchanges"]), 1)
        exchange = reconstructed["recall_exchanges"][0]
        self.assertEqual(exchange["concept_id"], cid)
        self.assertIn("role of a page table", exchange["question"])
        self.assertIn("maps virtual page numbers", exchange["answer"])
        self.assertEqual(exchange["score"], 92)
        self.assertEqual(exchange["verdict"], "STRONG")
        self.assertIn("Excellent explanation", exchange["feedback"])

        # Mastery milestones
        self.assertEqual(len(reconstructed["mastery_milestones"]), 1)
        self.assertEqual(reconstructed["mastery_milestones"][0]["concept_id"], cid)

        # Revisions triggered
        self.assertEqual(len(reconstructed["revisions_triggered"]), 1)
        self.assertEqual(reconstructed["revisions_triggered"][0]["concept_id"], cid)

    def test_05_get_user_conversations_aggregation(self):
        """Verify grouping of distinct conversation sessions for a student."""
        # Create messages in two different sessions
        self.repo.save_conversation_message(
            conversation_id="conv_session_A", user_id="user_ashwel", role="assistant",
            message="Session A Greeting", message_type="greeting"
        )
        self.repo.save_conversation_message(
            conversation_id="conv_session_A", user_id="user_ashwel", role="user",
            message="Session A Response", message_type="answer", concept_id="concept_c1"
        )

        self.repo.save_conversation_message(
            conversation_id="conv_session_B", user_id="user_ashwel", role="assistant",
            message="Session B Introduction", message_type="greeting"
        )

        conversations = self.repo.get_user_conversations(user_id="user_ashwel")
        self.assertGreaterEqual(len(conversations), 2)
        conv_ids = [c["conversation_id"] for c in conversations]
        self.assertIn("conv_session_A", conv_ids)
        self.assertIn("conv_session_B", conv_ids)

        conv_a = next(c for c in conversations if c["conversation_id"] == "conv_session_A")
        self.assertEqual(conv_a["message_count"], 2)
        self.assertEqual(conv_a["concepts_count"], 1)

    def test_06_history_service_reconstruction(self):
        """Verify HistoryService reconstructs sessions and returns conversation lists."""
        history_svc = HistoryService(repository=self.repo)

        self.repo.save_conversation_message(
            conversation_id="conv_svc_test", user_id="user_ashwel", role="assistant",
            message="Welcome to EduMentor History Service", message_type="greeting"
        )

        sessions = history_svc.get_user_conversations(user_id="user_ashwel")
        self.assertTrue(any(s["conversation_id"] == "conv_svc_test" for s in sessions))

        recon = history_svc.reconstruct_session(conversation_id="conv_svc_test")
        self.assertTrue(recon["found"])
        self.assertEqual(len(recon["turns"]), 1)

    def test_07_orchestrator_logs_conversation_messages(self):
        """Verify EduMentorOrchestrator writes conversation messages during workflows."""
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)
        self.assertTrue(hasattr(orch, "conversation_id"))
        self.assertTrue(orch.conversation_id.startswith("conv_"))

        # Trigger chat input
        chat_res = orch.handle_user_chat("Explain process states in OS")
        self.assertIn("chat_history", chat_res)

        # Verify messages logged into database
        msgs = self.repo.get_conversation_messages(conversation_id=orch.conversation_id)
        self.assertGreaterEqual(len(msgs), 2)
        roles = [m.role for m in msgs]
        self.assertIn("user", roles)
        self.assertIn("assistant", roles)

    def test_08_fastapi_history_endpoints(self):
        """Verify GET /api/history and GET /api/history/sessions/{id} endpoints."""
        client = TestClient(app)

        # GET /api/history
        res = client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("conversations", data)

        # Seed a session in database and query /api/history/sessions/{id}
        import uuid
        test_conv = f"conv_endpoint_test_{uuid.uuid4().hex[:8]}"
        from server import repo as server_repo
        # Seed concept if not exists to satisfy foreign key
        try:
            server_repo.save_concept(
                concept_id="concept_threads_test",
                title="Threads Test",
                summary="Threads concept",
                canonical_explanation="Threads explanation",
                key_points=["point 1"]
            )
        except Exception:
            pass

        server_repo.save_conversation_message(
            conversation_id=test_conv,
            user_id="user_ashwel",
            role="assistant",
            message="Endpoint reconstruction test message",
            message_type="study_instruction",
            concept_id="concept_threads_test"
        )

        res_session = client.get(f"/api/history/sessions/{test_conv}")
        self.assertEqual(res_session.status_code, 200)
        session_data = res_session.json()
        self.assertEqual(session_data["status"], "ok")
        self.assertEqual(session_data["session"]["conversation_id"], test_conv)
        self.assertEqual(len(session_data["session"]["turns"]), 1)
        self.assertEqual(session_data["session"]["turns"][0]["message_type"], "study_instruction")


if __name__ == "__main__":
    unittest.main()
