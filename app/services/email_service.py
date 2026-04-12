import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from app.core.config import settings
from urllib.parse import urlencode
FRONTEND_URL = "http://localhost:3000"

async def send_reset_password_email(email_to: str, token: str):
    logger.info(f"Sending reset password email to {email_to}")

    reset_link = f"{FRONTEND_URL}/reset-password?{urlencode({'token': token})}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #1e40af, #06b6d4); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🔐 Password Reset</h1>
            <p style="color: rgba(255,255,255,0.8); margin-top: 8px;">Secure Fingerprint Attendance System</p>
        </div>
        <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb;">
            <p style="color: #374151; font-size: 16px;">We received a request to reset your password.</p>
            <p style="color: #374151;">Click the button below to reset your password. This link will expire in <strong>30 minutes</strong>.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}"
                   style="background: #1e40af; color: white; padding: 14px 32px; border-radius: 8px;
                          text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block;">
                    Reset My Password
                </a>
            </div>
            <p style="color: #6b7280; font-size: 12px;">
                If you did not request a password reset, please ignore this email.<br>
                This link will expire in 30 minutes for your security.
            </p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #9ca3af; font-size: 11px; text-align: center;">
                Secure Fingerprint Attendance &amp; Access Control System
            </p>
        </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = email_to
    msg["Subject"] = "🔐 Password Reset Request - Fingerprint Attendance System"
    msg.attach(MIMEText(html_body, "html"))

    try:
        smtp_host = settings.SMTP_HOST
        smtp_port = settings.SMTP_PORT or 587
        smtp_user = settings.SMTP_USER
        smtp_password = (settings.SMTP_PASSWORD or "").replace(" ", "")

        logger.info(f"📧 SMTP Config: host={smtp_host}, port={smtp_port}, user={smtp_user}")

        if not smtp_host or not smtp_user or not smtp_password:
            logger.warning("⚠️ SMTP not fully configured. Email NOT sent.")
            logger.info(f"[DEV] Reset link for {email_to}: {reset_link}")
            return

        # aiosmtplib: use_tls and start_tls are MUTUALLY EXCLUSIVE
        # Port 465 = SSL/TLS (use_tls=True, start_tls=False)
        # Port 587 = STARTTLS (use_tls=False, start_tls=True)
        use_tls = (smtp_port == 465)
        start_tls = (smtp_port in (587, 25))

        logger.info(f"📧 Connecting: use_tls={use_tls}, start_tls={start_tls}")

        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=use_tls,
            start_tls=start_tls,
        )
        logger.info(f"✅ Password reset email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {email_to}: {type(e).__name__}: {e}")
        logger.info(f"[FALLBACK] Reset link for {email_to}: {reset_link}")
        # Don't re-raise: return gracefully so the user gets the generic response
        # and the reset link is logged for debugging

