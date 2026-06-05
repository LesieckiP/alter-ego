"""Email notification service for lead capture and unknown question logging."""
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


class Notifier:
    """Sends email alerts triggered by tool calls from the chat agent."""

    def __init__(self) -> None:
        self.login = os.environ.get("ALERT_FROM_EMAIL", "").strip()
        self.password = os.environ.get("EMAIL_PASSWORD", "").strip()
        self.to_email = os.environ.get("ALERT_TO_EMAIL", "").strip()

        missing = [
            name
            for name, value in [
                ("ALERT_FROM_EMAIL", self.login),
                ("EMAIL_PASSWORD", self.password),
                ("ALERT_TO_EMAIL", self.to_email),
            ]
            if not value
        ]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def send_alert(self, subject: str, body: str) -> None:
        """Send an email alert via SMTP SSL."""
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.login
        msg["To"] = self.to_email
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.mail.ovh.net", 465, timeout=20) as smtp:
            smtp.login(self.login, self.password)
            smtp.send_message(msg)
        print(f"Email sent to {self.to_email} with subject: {subject}", flush=True)

    def record_user_details(
        self, email: str, name: str = "Name not provided", notes: str = "Not provided"
    ) -> dict[str, str]:
        """Record a visitor's contact details and forward via email."""
        subject = "New user interaction with AI alter-ego"
        body = f"User details:\nName: {name}\nEmail: {email}\nNotes: {notes}"
        self.send_alert(subject, body)
        return {"recorded": "ok"}

    def record_unknown_question(self, question: str) -> dict[str, str]:
        """Log a question the agent could not answer and forward via email."""
        subject = "AI alter-ego received an unknown question"
        body = f"The following question was not understood by the AI alter-ego:\n\n{question}"
        self.send_alert(subject, body)
        return {"recorded": "ok"}
