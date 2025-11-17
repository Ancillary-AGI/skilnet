"""
Email service for EduVerse platform
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import aiofiles
import jinja2
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger, log_performance
from app.models.user import User


class EmailService:
    """Email service with template support and multiple providers"""
    
    def __init__(self):
        self.logger = get_logger("email_service")
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("app/templates/emails"),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    @log_performance
    async def send_welcome_email(self, user: User, db_session=None) -> bool:
        """Send welcome email to new user"""
        # Generate email verification token
        if db_session:
            from app.services.auth_service import AuthService
            auth_service = AuthService(db_session)
            verification_token = auth_service.create_email_verification_token(user.id)
        else:
            # Fallback for when no db session is provided
            verification_token = f"verify_{user.id}_{datetime.now().timestamp()}"

        verification_url = f"{settings.APP_URL}/verify-email?token={verification_token}"

        template = self.template_env.get_template("welcome.html")
        html_content = template.render(
            user_name=user.display_name,
            verification_url=verification_url,
            app_url=settings.APP_URL,
            current_year=datetime.now().year
        )

        return await self.send_email(
            to_email=user.email,
            subject="Welcome to EduVerse! 🎓",
            html_content=html_content,
            template_name="welcome"
        )
    
    @log_performance
    async def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
            
            template = self.template_env.get_template("password_reset.html")
            html_content = template.render(
                user_name=user.display_name,
                reset_url=reset_url,
                app_url=settings.APP_URL,
                current_year=datetime.now().year
            )
            
            return await self.send_email(
                to_email=user.email,
                subject="Reset Your EduVerse Password 🔐",
                html_content=html_content,
                template_name="password_reset"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send password reset email: {e}")
            return False
    
    @log_performance
    async def send_course_enrollment_email(self, user: User, course_title: str, course_url: str) -> bool:
        """Send course enrollment confirmation email"""
        try:
            template = self.template_env.get_template("course_enrollment.html")
            html_content = template.render(
                user_name=user.display_name,
                course_title=course_title,
                course_url=course_url,
                app_url=settings.APP_URL,
                current_year=datetime.now().year
            )
            
            return await self.send_email(
                to_email=user.email,
                subject=f"Welcome to {course_title}! 📚",
                html_content=html_content,
                template_name="course_enrollment"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send course enrollment email: {e}")
            return False
    
    @log_performance
    async def send_certificate_email(self, user: User, course_title: str, certificate_url: str) -> bool:
        """Send course completion certificate email"""
        try:
            template = self.template_env.get_template("certificate.html")
            html_content = template.render(
                user_name=user.display_name,
                course_title=course_title,
                certificate_url=certificate_url,
                app_url=settings.APP_URL,
                current_year=datetime.now().year
            )
            
            return await self.send_email(
                to_email=user.email,
                subject=f"🎉 Congratulations! You've completed {course_title}",
                html_content=html_content,
                template_name="certificate"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send certificate email: {e}")
            return False
    
    @log_performance
    async def send_streak_milestone_email(self, user: User, streak_days: int) -> bool:
        """Send learning streak milestone email"""
        try:
            template = self.template_env.get_template("streak_milestone.html")
            html_content = template.render(
                user_name=user.display_name,
                streak_days=streak_days,
                app_url=settings.APP_URL,
                current_year=datetime.now().year
            )
            
            return await self.send_email(
                to_email=user.email,
                subject=f"🔥 Amazing! {streak_days}-day learning streak!",
                html_content=html_content,
                template_name="streak_milestone"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send streak milestone email: {e}")
            return False
    
    @log_performance
    async def send_weekly_progress_email(self, user: User, progress_data: Dict[str, Any]) -> bool:
        """Send weekly learning progress summary email"""
        try:
            template = self.template_env.get_template("weekly_progress.html")
            html_content = template.render(
                user_name=user.display_name,
                progress_data=progress_data,
                app_url=settings.APP_URL,
                current_year=datetime.now().year
            )
            
            return await self.send_email(
                to_email=user.email,
                subject="📊 Your Weekly Learning Progress",
                html_content=html_content,
                template_name="weekly_progress"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send weekly progress email: {e}")
            return False
    
    @log_performance
    async def send_security_alert_email(self, user: User, alert_type: str, details: Dict[str, Any]) -> bool:
        """Send security alert email"""
        try:
            template = self.template_env.get_template("security_alert.html")
            html_content = template.render(
                user_name=user.display_name,
                alert_type=alert_type,
                details=details,
                app_url=settings.APP_URL,
                current_year=datetime.now().year
            )
            
            return await self.send_email(
                to_email=user.email,
                subject="🔒 Security Alert - EduVerse Account",
                html_content=html_content,
                template_name="security_alert",
                priority="high"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send security alert email: {e}")
            return False
    
    @log_performance
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        template_name: Optional[str] = None,
        priority: str = "normal",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email using configured SMTP server"""
        
        if not settings.SMTP_HOST:
            self.logger.warning("SMTP not configured, email not sent")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"EduVerse <{settings.SMTP_USERNAME}>"
            message["To"] = to_email
            
            # Set priority
            if priority == "high":
                message["X-Priority"] = "1"
                message["X-MSMail-Priority"] = "High"
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    await self._add_attachment(message, attachment)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            self.logger.info(f"Email sent successfully to {to_email} (template: {template_name})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """Add attachment to email message"""
        try:
            file_path = attachment["path"]
            filename = attachment.get("filename", Path(file_path).name)
            
            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()
            
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file_data)
            encoders.encode_base64(part)
            
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            
            message.attach(part)
            
        except Exception as e:
            self.logger.error(f"Failed to add attachment: {e}")
    
    @log_performance
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        batch_size: int = 50
    ) -> Dict[str, int]:
        """Send bulk email to multiple recipients"""
        results = {"sent": 0, "failed": 0}
        
        # Process in batches
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            for email in batch:
                success = await self.send_email(
                    to_email=email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
                
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
        
        self.logger.info(f"Bulk email completed: {results}")
        return results
    
    def validate_email_template(self, template_name: str) -> bool:
        """Validate that email template exists"""
        try:
            self.template_env.get_template(f"{template_name}.html")
            return True
        except jinja2.TemplateNotFound:
            return False
    
    async def preview_email_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Preview email template with given context"""
        try:
            template = self.template_env.get_template(f"{template_name}.html")
            return template.render(**context)
        except Exception as e:
            self.logger.error(f"Failed to preview template: {e}")
            return f"Error previewing template: {e}"


# Email template creation helper
async def create_email_templates():
    """Create default email templates if they don't exist"""
    templates_dir = Path("app/templates/emails")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Welcome email template
    welcome_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Welcome to EduVerse</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Welcome to EduVerse!</h1>
                <p>The future of learning is here</p>
            </div>
            <div class="content">
                <h2>Hello {{ user_name }}!</h2>
                <p>Welcome to EduVerse, the most advanced e-learning platform with VR/AR capabilities and AI-powered personalization.</p>
                
                <p>To get started, please verify your email address:</p>
                <a href="{{ verification_url }}" class="button">Verify Email Address</a>
                
                <h3>What's Next?</h3>
                <ul>
                    <li>🔍 Explore our course catalog</li>
                    <li>🎯 Set your learning goals</li>
                    <li>👥 Join study groups</li>
                    <li>🥽 Try VR/AR experiences</li>
                </ul>
                
                <p>If you have any questions, our support team is here to help!</p>
            </div>
            <div class="footer">
                <p>&copy; {{ current_year }} EduVerse. All rights reserved.</p>
                <p><a href="{{ app_url }}">Visit EduVerse</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Password reset template
    password_reset_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Reset Your Password</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #e74c3c; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .button { display: inline-block; background: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset</h1>
                <p>Reset your EduVerse password</p>
            </div>
            <div class="content">
                <h2>Hello {{ user_name }}!</h2>
                <p>We received a request to reset your EduVerse password.</p>
                
                <a href="{{ reset_url }}" class="button">Reset Password</a>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <ul>
                        <li>This link expires in 1 hour</li>
                        <li>If you didn't request this, please ignore this email</li>
                        <li>Never share this link with anyone</li>
                    </ul>
                </div>
                
                <p>If the button doesn't work, copy and paste this link:</p>
                <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 5px;">{{ reset_url }}</p>
            </div>
            <div class="footer">
                <p>&copy; {{ current_year }} EduVerse. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write templates
    async with aiofiles.open(templates_dir / "welcome.html", "w") as f:
        await f.write(welcome_template)
    
    async with aiofiles.open(templates_dir / "password_reset.html", "w") as f:
        await f.write(password_reset_template)