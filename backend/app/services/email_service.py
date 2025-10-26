"""
Email service for EduVerse platform
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import aiosmtplib
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path

from app.core.config import settings
from app.models.user import User

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.app_url = settings.APP_URL
        
        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email using SMTP"""
        if not self.smtp_host:
            print(f"Email would be sent to {to_email}: {subject}")
            return True  # Mock success for development
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_username
            message["To"] = to_email
            
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
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment['filename']}"
                    )
                    message.attach(part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=True,
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user"""
        template = self.jinja_env.get_template("welcome.html")
        
        html_content = template.render(
            user_name=user.display_name,
            app_url=self.app_url,
            verification_url=f"{self.app_url}/verify-email?token=verification_token_here"
        )
        
        return await self.send_email(
            to_email=user.email,
            subject="Welcome to EduVerse! 🎓",
            html_content=html_content
        )
    
    async def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email"""
        template = self.jinja_env.get_template("password_reset.html")
        
        reset_url = f"{self.app_url}/reset-password?token={reset_token}"
        
        html_content = template.render(
            user_name=user.display_name,
            reset_url=reset_url,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject="Reset Your EduVerse Password",
            html_content=html_content
        )
    
    async def send_email_verification(self, user: User, verification_token: str) -> bool:
        """Send email verification"""
        template = self.jinja_env.get_template("email_verification.html")
        
        verification_url = f"{self.app_url}/verify-email?token={verification_token}"
        
        html_content = template.render(
            user_name=user.display_name,
            verification_url=verification_url,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject="Verify Your EduVerse Email",
            html_content=html_content
        )
    
    async def send_course_enrollment_confirmation(
        self,
        user: User,
        course_title: str,
        course_url: str
    ) -> bool:
        """Send course enrollment confirmation"""
        template = self.jinja_env.get_template("course_enrollment.html")
        
        html_content = template.render(
            user_name=user.display_name,
            course_title=course_title,
            course_url=course_url,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject=f"You're enrolled in {course_title}! 🎉",
            html_content=html_content
        )
    
    async def send_certificate_earned(
        self,
        user: User,
        course_title: str,
        certificate_url: str
    ) -> bool:
        """Send certificate earned notification"""
        template = self.jinja_env.get_template("certificate_earned.html")
        
        html_content = template.render(
            user_name=user.display_name,
            course_title=course_title,
            certificate_url=certificate_url,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject=f"🏆 Congratulations! You've earned a certificate",
            html_content=html_content
        )
    
    async def send_subscription_confirmation(
        self,
        user: User,
        subscription_tier: str,
        amount: float,
        currency: str
    ) -> bool:
        """Send subscription confirmation"""
        template = self.jinja_env.get_template("subscription_confirmation.html")
        
        html_content = template.render(
            user_name=user.display_name,
            subscription_tier=subscription_tier,
            amount=amount,
            currency=currency,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Welcome to EduVerse {subscription_tier}! 🚀",
            html_content=html_content
        )
    
    async def send_learning_streak_milestone(
        self,
        user: User,
        streak_days: int
    ) -> bool:
        """Send learning streak milestone notification"""
        template = self.jinja_env.get_template("streak_milestone.html")
        
        html_content = template.render(
            user_name=user.display_name,
            streak_days=streak_days,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject=f"🔥 Amazing! {streak_days}-day learning streak!",
            html_content=html_content
        )
    
    async def send_weekly_progress_report(
        self,
        user: User,
        progress_data: Dict[str, Any]
    ) -> bool:
        """Send weekly progress report"""
        template = self.jinja_env.get_template("weekly_progress.html")
        
        html_content = template.render(
            user_name=user.display_name,
            progress_data=progress_data,
            app_url=self.app_url
        )
        
        return await self.send_email(
            to_email=user.email,
            subject="📊 Your Weekly Learning Progress",
            html_content=html_content
        )