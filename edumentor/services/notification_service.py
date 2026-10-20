"""
Notification and background reminder service for spaced repetition reviews.
Phase 16 — Notification System:
- In-app notifications (Always implemented)
- Browser notifications (Web Notifications API integration)
- Extensible Email notification architecture (Ready for future email integration)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid
from abc import ABC, abstractmethod


class BaseEmailProvider(ABC):
    """Abstract interface for pluggable email notification delivery."""

    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatch email to recipient."""
        pass


class MockEmailProvider(BaseEmailProvider):
    """
    Default MVP in-memory email provider for testing and local development.
    Requires no external credentials or network connectivity.
    """

    def __init__(self):
        self.sent_emails: List[Dict[str, Any]] = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        record = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "status": "delivered",
            "provider": "mock",
            "timestamp": datetime.now().isoformat()
        }
        self.sent_emails.append(record)
        return {"status": "ok", "delivered": True, "provider": "mock", "record": record}


class SMTPEmailProvider(BaseEmailProvider):
    """
    Production-ready SMTP email provider for future email integration.
    Configured via environment variables or settings.
    """

    def __init__(
        self,
        host: str = "smtp.example.com",
        port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: str = "edumentor@example.com",
        use_tls: bool = True
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        # If credentials are not configured, log and return simulated delivery
        if not self.username or not self.password:
            return {
                "status": "simulated",
                "delivered": False,
                "reason": "SMTP credentials unconfigured. Pluggable architecture ready.",
                "to": to_email,
                "subject": subject
            }
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, [to_email], msg.as_string())

            return {"status": "ok", "delivered": True, "provider": "smtp"}
        except Exception as e:
            return {"status": "error", "delivered": False, "error": str(e)}


class NotificationService:
    """
    Core Notification System managing in-app, browser, and email reminder pipelines.
    """

    def __init__(self, email_provider: Optional[BaseEmailProvider] = None):
        self.notifications: List[Dict[str, Any]] = []
        self.email_provider: BaseEmailProvider = email_provider or MockEmailProvider()
        self.browser_enabled: bool = True
        self.email_enabled: bool = False
        self.recipient_email: Optional[str] = None

    # -------------------------------------------------------------------------
    # Legacy / Backwards-Compatible Class Method
    # -------------------------------------------------------------------------
    @staticmethod
    def check_due_notifications(
        concepts: Dict[str, Dict[str, Any]],
        today_iso: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Maintains backwards compatibility with modular services test suite."""
        today = today_iso or date.today().isoformat()
        alerts = []
        for cid, c in concepts.items():
            due = c.get("next_due_date", today)
            status = c.get("sm2_status", "new")
            if (status == "weak" or due <= today) and c.get("total_reviews", 0) > 0:
                alerts.append({
                    "concept_id": cid,
                    "title": f"Review Due: {c.get('title', cid)}",
                    "message": "This concept is scheduled for active recall reinforcement today.",
                    "status": status
                })
        return alerts

    # -------------------------------------------------------------------------
    # Phase 16: Dynamic Revisit Notification Generator
    # -------------------------------------------------------------------------
    def create_revisit_notification(
        self,
        student_name: str,
        concept_title: str,
        concept_id: str,
        reason: str = "close"
    ) -> Dict[str, Any]:
        """
        Creates a notification conforming to Phase 16 specifications:
        🔔 EduMentor
        Time to revisit Process Scheduling.
        You were close last time — let's see if you've got it now.
        """
        notif_id = str(uuid.uuid4())
        title = "🔔 EduMentor"
        heading = f"Time to revisit {concept_title}."
        
        if reason == "close":
            body = "You were close last time — let's see if you've got it now."
        elif reason == "weak":
            body = "You had a bit of trouble last time — let's solidify this foundational concept."
        else:
            body = "You were close last time — let's see if you've got it now."

        notif = {
            "id": notif_id,
            "title": title,
            "heading": heading,
            "body": body,
            "concept_id": concept_id,
            "concept_title": concept_title,
            "student_name": student_name,
            "status": "unread",
            "channels": ["in_app", "browser", "email"],
            "created_at": datetime.now().isoformat(),
            "action_label": "Recall Now →",
            "action_url": f"/?recall={concept_id}"
        }
        
        # Avoid exact duplicate unread notifications for the same concept
        existing = [n for n in self.notifications if n["concept_id"] == concept_id and n["status"] == "unread"]
        if not existing:
            self.notifications.insert(0, notif)
            try:
                from edumentor.events import event_tracker, ProductEvent
                event_tracker.track(
                    ProductEvent.NOTIFICATION_SENT,
                    user_id=f"user_{student_name.lower().replace(' ', '_')}",
                    concept_id=concept_id,
                    properties={"heading": heading, "channel": "in_app", "reason": reason}
                )
            except Exception:
                pass
            return notif
        return existing[0]

    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve stored notifications, optionally filtering by unread."""
        if unread_only:
            return [n for n in self.notifications if n["status"] == "unread"]
        return list(self.notifications)

    def get_unread_count(self) -> int:
        """Return the current number of unread notifications."""
        return sum(1 for n in self.notifications if n["status"] == "unread")

    def mark_as_read(self, notification_id: Optional[str] = None) -> int:
        """
        Mark a specific notification as read, or mark all notifications as read if id is None.
        Returns count of notifications updated.
        """
        count = 0
        for n in self.notifications:
            if notification_id is None or n["id"] == notification_id:
                if n["status"] == "unread":
                    n["status"] = "read"
                    count += 1
        if count > 0 or notification_id is not None:
            try:
                from edumentor.events import event_tracker, ProductEvent
                event_tracker.track(
                    ProductEvent.NOTIFICATION_OPENED,
                    properties={"notification_id": notification_id, "count": count}
                )
            except Exception:
                pass
        return count

    def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss/remove a notification by id."""
        initial_len = len(self.notifications)
        self.notifications = [n for n in self.notifications if n["id"] != notification_id]
        return len(self.notifications) < initial_len

    def get_browser_notification_payload(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Format browser Web Notifications API payload for native display.
        """
        match = next((n for n in self.notifications if n["id"] == notification_id), None)
        if not match:
            return None

        return {
            "title": f"🔔 EduMentor: {match['heading']}",
            "options": {
                "body": match["body"],
                "icon": "/assets/teacher_avatar/teacher_encouraging.png",
                "badge": "/assets/teacher_avatar/teacher_greeting.png",
                "tag": f"edumentor-{match['concept_id']}",
                "requireInteraction": False,
                "data": {
                    "concept_id": match["concept_id"],
                    "url": match["action_url"]
                }
            }
        }

    def dispatch_email_notification(
        self,
        notification_id: str,
        recipient_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches notification via the pluggable email provider.
        """
        target_email = recipient_email or self.recipient_email
        if not target_email:
            return {"status": "error", "delivered": False, "reason": "No recipient email configured."}

        match = next((n for n in self.notifications if n["id"] == notification_id), None)
        if not match:
            return {"status": "error", "delivered": False, "reason": "Notification not found."}

        subject = f"🔔 EduMentor: {match['heading']}"
        text_body = (
            f"Hello {match['student_name']},\n\n"
            f"{match['heading']}\n\n"
            f"{match['body']}\n\n"
            f"Ready to recall? Click here to test your recall without checking your notes:\n"
            f"{match['action_url']}\n\n"
            f"— Your EduMentor AI Study Companion"
        )
        html_body = f"""
        <div style="font-family: Arial, sans-serif; background-color: #050608; color: #F1F5F9; padding: 24px; border-radius: 12px; border: 1px solid #27303B;">
          <h2 style="color: #25D8E8; margin-top: 0;">🔔 EduMentor</h2>
          <h3 style="color: #FFFFFF;">{match['heading']}</h3>
          <p style="color: #94A3B8; font-size: 15px; line-height: 1.5;">{match['body']}</p>
          <div style="margin: 20px 0;">
            <a href="{match['action_url']}" style="background: linear-gradient(135deg, #25D8E8 0%, #00B4D8 100%); color: #080D14; font-weight: bold; text-decoration: none; padding: 10px 20px; border-radius: 8px; display: inline-block;">Give it another try &rarr;</a>
          </div>
          <p style="color: #64748B; font-size: 12px;">Adaptive Spaced Repetition Notification — EduMentor</p>
        </div>
        """

        res = self.email_provider.send_email(
            to_email=target_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )
        try:
            from edumentor.events import event_tracker, ProductEvent
            event_tracker.track(
                ProductEvent.NOTIFICATION_SENT,
                user_id=f"user_{match['student_name'].lower().replace(' ', '_')}",
                concept_id=match.get('concept_id'),
                properties={"channel": "email", "recipient": target_email, "heading": match['heading']}
            )
        except Exception:
            pass
        return res

    def update_settings(
        self,
        browser_enabled: Optional[bool] = None,
        email_enabled: Optional[bool] = None,
        recipient_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update notification delivery preferences."""
        if browser_enabled is not None:
            self.browser_enabled = browser_enabled
        if email_enabled is not None:
            self.email_enabled = email_enabled
        if recipient_email is not None:
            self.recipient_email = recipient_email.strip()
        return self.get_settings()

    def get_settings(self) -> Dict[str, Any]:
        """Retrieve active notification settings."""
        return {
            "browser_enabled": self.browser_enabled,
            "email_enabled": self.email_enabled,
            "recipient_email": self.recipient_email,
            "provider_type": getattr(self.email_provider, "__class__", {}).__name__
        }

    def clear_all(self):
        """Clear all stored notifications."""
        self.notifications.clear()
