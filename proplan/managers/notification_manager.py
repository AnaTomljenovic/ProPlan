import os, asyncio, smtplib
from email.message import EmailMessage

class NotificationManager:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "").strip()
        self.port = int(os.getenv("SMTP_PORT", "0") or 0)
        self.user = os.getenv("SMTP_USER", "").strip()
        self.password = os.getenv("SMTP_PASSWORD", "").strip()
        self.use_tls = os.getenv("SMTP_TLS", "false").lower() in ("1", "true", "yes")
        self.mail_from = os.getenv("MAIL_FROM", "proplan@example.com")

    async def send_email(self, to: str, subject: str, body: str) -> None:
        if not self.host or not self.port:
            print(f"[email:skip] to={to} subject={subject!r}")
            return
        try:
            await asyncio.to_thread(self._send_sync, to, subject, body)
            print(f"[email:ok] to={to} subject={subject!r}")
        except Exception as e:
            print(f"[email:err] to={to} {e}")

    def _send_sync(self, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self.mail_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            smtp.ehlo()
            if self.use_tls:
                smtp.starttls()
                smtp.ehlo()

            # Only attempt AUTH if creds provided AND server supports AUTH
            supports_auth = "auth" in (smtp.esmtp_features or {})
            if self.user and self.password and supports_auth:
                smtp.login(self.user, self.password)

            smtp.send_message(msg)
