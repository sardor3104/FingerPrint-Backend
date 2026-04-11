import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from app.core.config import settings

FRONTEND_URL = "http://localhost:3000"

async def send_reset_password_email(email_to: str, token: str):
    logger.info(f"Sending reset password email to {email_to}")

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

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
        if settings.SMTP_HOST:
            # Clean App Password: remove all spaces (Google App Passwords are 16 chars without spaces)
            smtp_password = settings.SMTP_PASSWORD.replace(" ", "") if settings.SMTP_PASSWORD else ""

            is_starttls = settings.SMTP_PORT == 587
            is_tls = settings.SMTP_PORT == 465

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                use_tls=is_tls,
                start_tls=is_starttls,
                username=settings.SMTP_USER,
                password=smtp_password,
            )
            logger.info(f"✅ Password reset email sent successfully to {email_to}")
        else:
            logger.warning("SMTP not configured. Email NOT sent.")
            logger.info(f"[DEV] Reset link for {email_to}: {reset_link}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {email_to}: {e}")
        # Re-raise so the caller knows, but don't expose details to client
        raise
