"""Email notification integration."""

import os
import smtplib
from email.message import EmailMessage
from typing import Optional, List


def notify_email(
    subject: str,
    body: str,
    to: Optional[str] = None,
    from_addr: Optional[str] = None,
    smtp_host: Optional[str] = None,
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
) -> bool:
    """
    Send email notification.

    Args:
        subject: Email subject
        body: Email body
        to: Recipient email (uses EMAIL_TO env var if not provided)
        from_addr: Sender email (uses EMAIL_FROM env var if not provided)
        smtp_host: SMTP server (uses SMTP_HOST env var if not provided)
        smtp_port: SMTP port (default: 587)
        smtp_user: SMTP username (uses SMTP_USER env var if not provided)
        smtp_pass: SMTP password (uses SMTP_PASS env var if not provided)

    Returns:
        True if successful, False otherwise
    """
    # Load from environment if not provided
    to = to or os.environ.get("EMAIL_TO")
    from_addr = from_addr or os.environ.get("EMAIL_FROM")
    smtp_host = smtp_host or os.environ.get("SMTP_HOST")
    smtp_user = smtp_user or os.environ.get("SMTP_USER")
    smtp_pass = smtp_pass or os.environ.get("SMTP_PASS")

    # Validate required fields
    if not all([to, from_addr, smtp_host, smtp_user, smtp_pass]):
        print("Warning: Email not fully configured, skipping email notification")
        print(f"Missing: {[k for k, v in {
            'EMAIL_TO': to,
            'EMAIL_FROM': from_addr,
            'SMTP_HOST': smtp_host,
            'SMTP_USER': smtp_user,
            'SMTP_PASS': smtp_pass
        }.items() if not v]}")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to
        msg.set_content(body)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return True

    except Exception as e:
        print(f"Email notification failed: {e}")
        return False


def notify_email_html(
    subject: str,
    html_body: str,
    to: Optional[str] = None,
    from_addr: Optional[str] = None,
) -> bool:
    """
    Send HTML email notification.

    Args:
        subject: Email subject
        html_body: HTML email body
        to: Recipient email
        from_addr: Sender email

    Returns:
        True if successful, False otherwise
    """
    to = to or os.environ.get("EMAIL_TO")
    from_addr = from_addr or os.environ.get("EMAIL_FROM")
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")

    if not all([to, from_addr, smtp_host, smtp_user, smtp_pass]):
        print("Warning: Email not fully configured")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to
        msg.set_content("This email requires HTML support")
        msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(smtp_host, 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return True

    except Exception as e:
        print(f"HTML email notification failed: {e}")
        return False
