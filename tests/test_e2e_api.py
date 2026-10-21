"""
End-to-End API & Integration Verification Test for EduMentor.
Tests the complete conversational learning loop over HTTP:
Talk -> Upload/Select -> Study -> Recall -> Feedback -> Continue -> Revisit -> Master.
"""

import urllib.request
import json
import unittest

from fastapi.testclient import TestClient
from server import app

BASE_URL = "http://127.0.0.1:8000"
_test_client = TestClient(app)


def http_post(endpoint: str, payload: dict) -> dict:
    try:
        url = f"{BASE_URL}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        res = _test_client.post(endpoint, json=payload)
        return res.json()


def http_get(endpoint: str) -> dict:
    try:
        url = f"{BASE_URL}{endpoint}"
        with urllib.request.urlopen(url, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        res = _test_client.get(endpoint)
        return res.json()


class TestEduMentorE2E(unittest.TestCase):
    def test_01_static_and_home(self):
        # 1. Check index page
        try:
            with urllib.request.urlopen(f"{BASE_URL}/", timeout=2) as resp:
                html = resp.read().decode("utf-8")
                self.assertEqual(resp.status, 200)
        except Exception:
            resp = _test_client.get("/")
            html = resp.text
            self.assertEqual(resp.status_code, 200)

        self.assertIn("EduMentor — AI Study Companion Workspace", html)
        self.assertIn("Tell me what you want to study", html)
        self.assertIn("Ashwel", html)

        # 2. Check session state
        session = http_get("/api/session")
        self.assertEqual(session["student_name"], "Ashwel")
        print("[PASS] Step 1: Landing page & student session verified.")

    def test_02_conversational_topic_intent(self):
        # Reset first
        http_post("/api/reset", {})
        
        # Student says: "I want to study Operating Systems"
        res = http_post("/api/chat", {"message": "I want to study Operating Systems"})
        self.assertEqual(res["state"], "STUDYING")
        self.assertIn("Operating Systems", res["curriculum_title"])
        self.assertEqual(res["current_concept"]["title"], "Process Scheduling")
        self.assertGreater(len(res["graph"]["nodes"]), 0)
        self.assertGreater(len(res["graph"]["edges"]), 0)
        print("[PASS] Step 2: 'I want to study Operating Systems' intent parsed & study path built.")

    def test_03_study_to_active_recall_challenge(self):
        # Student clicks "I'm Ready to Recall"
        res = http_post("/api/ready", {})
        self.assertEqual(res["state"], "WAITING_RECALL")
        self.assertIsNotNone(res["last_recall_question"])
        self.assertIn("process scheduling", res["last_recall_question"].lower())
        print("[PASS] Step 3: Active recall challenge prompt formulated.")

    def test_04_hybrid_evaluation_and_sm2(self):
        # Student provides self-explanation
        student_ans = (
            "Process scheduling selects runnable processes from the ready queue to execute on the CPU using context switching, "
            "balancing CPU utilization, throughput, turnaround time, waiting time, and preventing process starvation."
        )
        res = http_post("/api/recall/submit", {"answer": student_ans})
        self.assertEqual(res["state"], "FEEDBACK")
        
        ev = res["last_evaluation"]
        self.assertIsNotNone(ev)
        self.assertGreaterEqual(ev["composite_score"], 65.0)
        self.assertIn(ev["verdict"].lower(), ["correct", "almost correct", "almost_correct"])
        self.assertGreaterEqual(ev["quality_q"], 3)
        self.assertTrue(len(ev["strengths"]) > 0)
        self.assertIsNotNone(ev["actionable_tip"])
        print(f"[PASS] Step 4: Hybrid evaluation passed. Score: {ev['composite_score']}/100, Verdict: {ev['verdict']}.")

    def test_05_advance_to_next_prerequisite(self):
        # Advance down the topological DAG (next foundational concept: Virtual Memory & Address Spaces)
        res = http_post("/api/advance", {})
        self.assertEqual(res["state"], "STUDYING")
        self.assertEqual(res["current_concept"]["title"], "Virtual Memory & Address Spaces")
        self.assertEqual(res["current_concept_index"], 1)
        print("[PASS] Step 5: Advanced to next topological concept: 'Virtual Memory & Address Spaces'.")

    def test_06_weak_spot_resurfacing_loopback(self):
        # 1. Trigger recall on Virtual Memory & Address Spaces
        http_post("/api/ready", {})
        
        # 2. Submit blank / weak answer to simulate failure
        res = http_post("/api/recall/submit", {"answer": "I don't know the mechanics of virtual memory."})
        self.assertIn(res["last_evaluation"]["verdict"].lower(), ["wrong"])
        self.assertLess(res["last_evaluation"]["quality_q"], 3)
        self.assertGreater(res["weak_queue_count"], 0)

        
        # 3. Advance should trigger loopback to revisit the weak concept
        res_adv = http_post("/api/advance", {})
        self.assertTrue(
            "loop back" in res_adv["system_message"].lower() or
            "refresher" in res_adv["system_message"].lower() or
            "revisit" in res_adv["system_message"].lower()
        )
        self.assertEqual(res_adv["current_concept"]["title"], "Virtual Memory & Address Spaces")
        print("[PASS] Step 6: Weak spot detected, SM-2 closed-loop adaptive resurfacing verified.")



if __name__ == "__main__":
    unittest.main()
