"""
Email service for the ERP.

Behavior:
- If SMTP_HOST is configured (see .env.example), sends real email via smtplib.
- If SMTP_HOST is empty ("dev mode"), the email is NOT sent anywhere — instead
  it's logged to the console and written as an .html file under
  backend/uploads/dev_emails/, so the full password-reset flow (including the
  actual reset link) is inspectable and testable without real mail credentials.

This means the password reset feature is 100% functional end-to-end in any
environment; only the final "does it land in an inbox" step depends on
configuring real SMTP credentials.
"""

import logging
import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from app.config import settings

logger = logging.getLogger("shaheen_erp.email")
logging.basicConfig(level=logging.INFO)

DEV_EMAIL_DIR = Path(settings.UPLOAD_DIR) / "dev_emails"


def send_email(to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """
    Returns True if the email was sent (or successfully logged in dev mode).
    Never raises — a failed email should not crash the calling request; the
    caller (e.g. forgot-password) already returns a generic success message
    regardless, to avoid leaking which emails exist.
    """
    if not settings.SMTP_HOST:
        return _log_dev_email(to_email, subject, html_body)

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg.set_content(text_body or _strip_html(html_body))
        msg.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls(context=context)
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        # Fall back to dev logging so the content isn't lost even if SMTP fails
        _log_dev_email(to_email, subject, html_body, note=f"[SMTP SEND FAILED: {e}]")
        return False


def _log_dev_email(to_email: str, subject: str, html_body: str, note: str = "") -> bool:
    DEV_EMAIL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    safe_email = to_email.replace("@", "_at_").replace(".", "_")
    filepath = DEV_EMAIL_DIR / f"{timestamp}__{safe_email}.html"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"<!-- To: {to_email} | Subject: {subject} {note} -->\n{html_body}")

    logger.info(
        f"[DEV MODE — no SMTP configured] Email to {to_email} ('{subject}') "
        f"logged to {filepath}. Configure SMTP_HOST in .env to send real email."
    )
    return True


def _strip_html(html: str) -> str:
    import re
    return re.sub("<[^<]+?>", "", html)


def send_password_reset_email(to_email: str, full_name: str, reset_token: str) -> bool:
    reset_link = f"{settings.FRONTEND_BASE_URL}/templates/auth/reset-password.html?token={reset_token}"
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color:#1D3E6E;">Password Reset Request</h2>
      <p>Hello {full_name},</p>
      <p>We received a request to reset your password for your Shaheen Model
      Girls High School ERP account. Click the button below to choose a new
      password. This link expires in 1 hour.</p>
      <p style="margin: 24px 0;">
        <a href="{reset_link}" style="background:#C7962C; color:#17213A; padding:12px 24px;
           text-decoration:none; border-radius:8px; font-weight:600;">Reset My Password</a>
      </p>
      <p style="color:#666; font-size:13px;">If you didn't request this, you can safely ignore
      this email — your password will remain unchanged.</p>
      <p style="color:#999; font-size:12px;">Link not working? Copy and paste this URL:<br>{reset_link}</p>
    </div>
    """
    return send_email(to_email, "Reset Your Password — Shaheen Model Girls High School", html_body)
