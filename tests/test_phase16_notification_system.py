"""
Unit & Integration Tests for Phase 16: Notification System.

Validates:
1. Exact notification wording:
     🔔 EduMentor
     Time to revisit Process Scheduling.
     You were close last time — let's see if you've got it now.
2. In-app notification delivery, unread counter, and mark-as-read lifecycle.
3. Browser Web Notifications API payload generation (title, body, icon, tag).
4. Extensible pluggable email provider architecture (MockEmailProvider and SMTPEmailProvider).
5. Orchestrator state payload synchronization.
6. REST API endpoints in server.py.
"""

import unittest
from edumentor.services.notification_service import (
    NotificationService,
    MockEmailProvider,
    SMTPEmailProvider
)
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.samples import SAMPLE_CURRICULA
from starlette.testclient import TestClient
from server import app


class TestPhase16NotificationSystem(unittest.TestCase):

    def setUp(self):
        self.service = NotificationService()
        self.orchestrator = EduMentorOrchestrator(student_name="Ashwel")
        self.orchestrator.load_sample_module("Operating Systems")

    def test_exact_notification_wording(self):
        """
        Verify exact notification text format matching user prompt:
          🔔 EduMentor
          Time to revisit Process Scheduling.
          You were close last time — let's see if you've got it now.
        """
        notif = self.service.create_revisit_notification(
            student_name="Ashwel",
            concept_title="Process Scheduling",
            concept_id="os_process_scheduling",
            reason="close"
        )

        self.assertEqual(notif["title"], "🔔 EduMentor")
        self.assertEqual(notif["heading"], "Time to revisit Process Scheduling.")
        self.assertEqual(notif["body"], "You were close last time — let's see if you've got it now.")
        self.assertEqual(notif["concept_id"], "os_process_scheduling")
        self.assertEqual(notif["status"], "unread")
        self.assertIn("in_app", notif["channels"])
        self.assertIn("browser", notif["channels"])
        self.assertIn("email", notif["channels"])

    def test_in_app_notification_lifecycle_and_unread_count(self):
        """
        Verify unread badge counter, listing, and mark as read.
        """
        self.assertEqual(self.service.get_unread_count(), 0)

        n1 = self.service.create_revisit_notification("Ashwel", "Process Scheduling", "os_process_scheduling")
        n2 = self.service.create_revisit_notification("Ashwel", "Virtual Memory", "os_virtual_memory")

        self.assertEqual(self.service.get_unread_count(), 2)
        all_notifs = self.service.get_notifications()
        self.assertEqual(len(all_notifs), 2)

        # Mark single as read
        marked = self.service.mark_as_read(n1["id"])
        self.assertEqual(marked, 1)
        self.assertEqual(self.service.get_unread_count(), 1)

        # Mark all as read
        self.service.mark_as_read(None)
        self.assertEqual(self.service.get_unread_count(), 0)

    def test_browser_notification_payload_formatting(self):
        """
        Verify browser Web Notifications API payload structure.
        """
        notif = self.service.create_revisit_notification(
            student_name="Ashwel",
            concept_title="Process Scheduling",
            concept_id="os_process_scheduling"
        )

        browser_payload = self.service.get_browser_notification_payload(notif["id"])
        self.assertIsNotNone(browser_payload)
        self.assertIn("🔔 EduMentor: Time to revisit Process Scheduling.", browser_payload["title"])
        self.assertEqual(browser_payload["options"]["body"], "You were close last time — let's see if you've got it now.")
        self.assertEqual(browser_payload["options"]["icon"], "/assets/teacher_avatar/teacher_encouraging.png")
        self.assertEqual(browser_payload["options"]["tag"], "edumentor-os_process_scheduling")
        self.assertEqual(browser_payload["options"]["data"]["concept_id"], "os_process_scheduling")

    def test_pluggable_email_provider_architecture(self):
        """
        Verify that MockEmailProvider records sent emails without external SMTP servers,
        and SMTPEmailProvider architecture is ready for future production credentials.
        """
        mock_provider = MockEmailProvider()
        svc = NotificationService(email_provider=mock_provider)

        notif = svc.create_revisit_notification(
            student_name="Ashwel",
            concept_title="Process Scheduling",
            concept_id="os_process_scheduling"
        )

        # Dispatch via mock email provider
        res = svc.dispatch_email_notification(notif["id"], recipient_email="ashwel@example.com")
        self.assertTrue(res["delivered"])
        self.assertEqual(len(mock_provider.sent_emails), 1)
        
        sent = mock_provider.sent_emails[0]
        self.assertEqual(sent["to"], "ashwel@example.com")
        self.assertIn("Time to revisit Process Scheduling", sent["subject"])
        self.assertIn("You were close last time", sent["body"])
        self.assertIn("Give it another try", sent["html_body"])

        # Test SMTPEmailProvider graceful fallback when unconfigured
        smtp_provider = SMTPEmailProvider(username=None, password=None)
        smtp_res = smtp_provider.send_email(
            to_email="ashwel@example.com",
            subject="Test",
            body="Test body"
        )
        self.assertEqual(smtp_res["status"], "simulated")
        self.assertFalse(smtp_res["delivered"])
        self.assertIn("Pluggable architecture ready", smtp_res["reason"])

    def test_orchestrator_integration_and_state_payload(self):
        """
        Verify that EduMentorOrchestrator tracks notifications and bundles them in session state.
        """
        payload_initial = self.orchestrator.get_state_payload()
        self.assertIn("notifications", payload_initial)
        self.assertIn("unread_notifications_count", payload_initial)

        # Trigger automatic resurfacing for Process Scheduling
        resurface_payload = self.orchestrator.trigger_automatic_resurfacing("os_process_scheduling")
        self.assertGreaterEqual(resurface_payload["unread_notifications_count"], 1)
        
        notifs = resurface_payload["notifications"]
        self.assertTrue(any(n["concept_id"] == "os_process_scheduling" for n in notifs))
        matched = next(n for n in notifs if n["concept_id"] == "os_process_scheduling")
        self.assertEqual(matched["heading"], "Time to revisit Process Scheduling.")
        self.assertEqual(matched["body"], "You were close last time — let's see if you've got it now.")

    def test_fastapi_server_notification_endpoints(self):
        """
        Verify all notification REST endpoints in server.py.
        """
        client = TestClient(app)

        # 1. GET /api/notifications
        r = client.get("/api/notifications")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("notifications", data)
        self.assertIn("unread_count", data)

        # 2. POST /api/notifications/generate
        r_gen = client.post("/api/notifications/generate", json={"concept_id": "os_process_scheduling"})
        self.assertEqual(r_gen.status_code, 200)
        gen_data = r_gen.json()
        self.assertEqual(gen_data["status"], "ok")
        notif = gen_data["notification"]
        self.assertEqual(notif["title"], "🔔 EduMentor")
        self.assertIn("Process Scheduling", notif["heading"])

        # 3. POST /api/notifications/read
        r_read = client.post("/api/notifications/read", json={"notification_id": notif["id"]})
        self.assertEqual(r_read.status_code, 200)
        self.assertEqual(r_read.json()["status"], "ok")

        # 4. POST /api/notifications/dispatch-email
        r_email = client.post("/api/notifications/dispatch-email", json={
            "notification_id": notif["id"],
            "recipient_email": "test@example.com"
        })
        self.assertEqual(r_email.status_code, 200)
        self.assertTrue(r_email.json().get("delivered", False))

        # 5. GET and POST /api/notifications/settings
        r_set = client.post("/api/notifications/settings", json={
            "browser_enabled": True,
            "email_enabled": True,
            "recipient_email": "student@domain.com"
        })
        self.assertEqual(r_set.status_code, 200)
        settings = r_set.json()
        self.assertTrue(settings["browser_enabled"])
        self.assertTrue(settings["email_enabled"])
        self.assertEqual(settings["recipient_email"], "student@domain.com")


if __name__ == "__main__":
    unittest.main()
