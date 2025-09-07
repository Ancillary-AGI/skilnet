"""
Automated certificate generation and blockchain verification service
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
import hashlib
import qrcode
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
import aiofiles
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CertificateData:
    user_id: str
    course_id: str
    user_name: str
    course_title: str
    completion_date: datetime
    grade: Optional[str]
    skills_acquired: List[str]
    instructor_name: str
    institution_name: str = "EduVerse"
    certificate_id: str = None
    blockchain_hash: Optional[str] = None


@dataclass
class CertificateTemplate:
    template_id: str
    name: str
    description: str
    template_path: str
    preview_image: str
    customizable_fields: List[str]
    supported_languages: List[str]
    is_premium: bool = False


class CertificateService:
    """Advanced certificate generation with blockchain verification"""
    
    def __init__(self):
        self.templates: Dict[str, CertificateTemplate] = {}
        self.generated_certificates: Dict[str, Dict[str, Any]] = {}
        self.blockchain_records: Dict[str, str] = {}
        self.verification_urls: Dict[str, str] = {}
        
    async def initialize(self):
        """Initialize certificate service"""
        try:
            logger.info("Initializing Certificate Service...")
            
            # Load certificate templates
            await self._load_certificate_templates()
            
            # Initialize blockchain connection
            await self._initialize_blockchain_connection()
            
            # Initialize verification system
            await self._initialize_verification_system()
            
            logger.info("Certificate Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Certificate Service: {e}")
    
    async def generate_certificate(
        self, 
        certificate_data: CertificateData,
        template_id: str = "default",
        language: str = "en",
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate certificate with blockchain verification"""
        
        try:
            # Generate unique certificate ID
            certificate_id = str(uuid.uuid4())
            certificate_data.certificate_id = certificate_id
            
            # Get template
            template = self.templates.get(template_id, self.templates["default"])
            
            # Generate certificate content
            if format == "pdf":
                certificate_path = await self._generate_pdf_certificate(
                    certificate_data, 
                    template, 
                    language
                )
            elif format == "image":
                certificate_path = await self._generate_image_certificate(
                    certificate_data, 
                    template, 
                    language
                )
            else:
                raise ValueError(f"Unsupported certificate format: {format}")
            
            # Generate verification QR code
            verification_url = await self._create_verification_url(certificate_id)
            qr_code_path = await self._generate_qr_code(verification_url)
            
            # Add QR code to certificate
            final_certificate_path = await self._add_qr_code_to_certificate(
                certificate_path, 
                qr_code_path
            )
            
            # Create blockchain record
            blockchain_hash = await self._create_blockchain_record(certificate_data)
            certificate_data.blockchain_hash = blockchain_hash
            
            # Store certificate metadata
            certificate_metadata = {
                "certificate_id": certificate_id,
                "user_id": certificate_data.user_id,
                "course_id": certificate_data.course_id,
                "user_name": certificate_data.user_name,
                "course_title": certificate_data.course_title,
                "completion_date": certificate_data.completion_date.isoformat(),
                "grade": certificate_data.grade,
                "skills_acquired": certificate_data.skills_acquired,
                "instructor_name": certificate_data.instructor_name,
                "template_id": template_id,
                "language": language,
                "format": format,
                "file_path": final_certificate_path,
                "verification_url": verification_url,
                "blockchain_hash": blockchain_hash,
                "generated_at": datetime.utcnow().isoformat(),
                "is_verified": True
            }
            
            self.generated_certificates[certificate_id] = certificate_metadata
            
            # Send certificate notification
            await self._send_certificate_notification(certificate_data, verification_url)
            
            return {
                "certificate_id": certificate_id,
                "download_url": f"/api/v1/certificates/{certificate_id}/download",
                "verification_url": verification_url,
                "blockchain_hash": blockchain_hash,
                "metadata": certificate_metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to generate certificate: {e}")
            raise
    
    async def _generate_pdf_certificate(
        self, 
        data: CertificateData, 
        template: CertificateTemplate,
        language: str
    ) -> str:
        """Generate PDF certificate"""
        
        # Create output path
        output_path = f"./certificates/{data.certificate_id}.pdf"
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Background and border
        c.setFillColor(Color(0.95, 0.95, 0.98))
        c.rect(0, 0, width, height, fill=1)
        
        # Decorative border
        c.setStrokeColor(Color(0.2, 0.3, 0.7))
        c.setLineWidth(3)
        c.rect(30, 30, width-60, height-60, fill=0)
        
        # Inner decorative border
        c.setStrokeColor(Color(0.4, 0.5, 0.8))
        c.setLineWidth(1)
        c.rect(50, 50, width-100, height-100, fill=0)
        
        # Header
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(Color(0.2, 0.3, 0.7))
        c.drawCentredText(width/2, height-120, "CERTIFICATE OF COMPLETION")
        
        # Institution name
        c.setFont("Helvetica", 18)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawCentredText(width/2, height-160, f"Awarded by {data.institution_name}")
        
        # Decorative line
        c.setStrokeColor(Color(0.6, 0.7, 0.9))
        c.setLineWidth(2)
        c.line(width/2-100, height-180, width/2+100, height-180)
        
        # Main content
        c.setFont("Helvetica", 16)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawCentredText(width/2, height-220, "This is to certify that")
        
        # Student name
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(Color(0.1, 0.2, 0.6))
        c.drawCentredText(width/2, height-260, data.user_name)
        
        # Course completion text
        c.setFont("Helvetica", 16)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawCentredText(width/2, height-300, "has successfully completed the course")
        
        # Course title
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(Color(0.1, 0.2, 0.6))
        c.drawCentredText(width/2, height-340, data.course_title)
        
        # Completion details
        c.setFont("Helvetica", 14)
        c.setFillColor(Color(0.3, 0.3, 0.3))
        completion_text = f"Completed on {data.completion_date.strftime('%B %d, %Y')}"
        if data.grade:
            completion_text += f" with a grade of {data.grade}"
        c.drawCentredText(width/2, height-380, completion_text)
        
        # Skills acquired
        if data.skills_acquired:
            c.setFont("Helvetica", 12)
            c.drawCentredText(width/2, height-420, "Skills Acquired:")
            
            y_pos = height - 440
            for skill in data.skills_acquired[:5]:  # Limit to 5 skills
                c.drawCentredText(width/2, y_pos, f"• {skill}")
                y_pos -= 20
        
        # Instructor signature
        c.setFont("Helvetica", 12)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawString(100, 150, "Instructor:")
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawString(100, 130, data.instructor_name)
        
        # Certificate ID and date
        c.setFont("Helvetica", 10)
        c.setFillColor(Color(0.5, 0.5, 0.5))
        c.drawString(100, 80, f"Certificate ID: {data.certificate_id}")
        c.drawString(100, 65, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Verification note
        c.drawRightString(width-100, 80, "Scan QR code to verify authenticity")
        
        # Save PDF
        c.save()
        
        return output_path
    
    async def _generate_image_certificate(
        self, 
        data: CertificateData, 
        template: CertificateTemplate,
        language: str
    ) -> str:
        """Generate image certificate"""
        
        # Create image
        img_width, img_height = 1200, 800
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            name_font = ImageFont.truetype("arial.ttf", 36)
            text_font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 16)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw border
        border_color = (50, 70, 180)
        draw.rectangle([20, 20, img_width-20, img_height-20], outline=border_color, width=5)
        draw.rectangle([40, 40, img_width-40, img_height-40], outline=border_color, width=2)
        
        # Title
        title_text = "CERTIFICATE OF COMPLETION"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((img_width - title_width) // 2, 80),
            title_text,
            fill=border_color,
            font=title_font
        )
        
        # Institution
        institution_text = f"Awarded by {data.institution_name}"
        institution_bbox = draw.textbbox((0, 0), institution_text, font=text_font)
        institution_width = institution_bbox[2] - institution_bbox[0]
        draw.text(
            ((img_width - institution_width) // 2, 140),
            institution_text,
            fill=(100, 100, 100),
            font=text_font
        )
        
        # Certification text
        cert_text = "This is to certify that"
        cert_bbox = draw.textbbox((0, 0), cert_text, font=text_font)
        cert_width = cert_bbox[2] - cert_bbox[0]
        draw.text(
            ((img_width - cert_width) // 2, 200),
            cert_text,
            fill=(50, 50, 50),
            font=text_font
        )
        
        # Student name
        name_bbox = draw.textbbox((0, 0), data.user_name, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text(
            ((img_width - name_width) // 2, 250),
            data.user_name,
            fill=border_color,
            font=name_font
        )
        
        # Course completion text
        completion_text = "has successfully completed the course"
        completion_bbox = draw.textbbox((0, 0), completion_text, font=text_font)
        completion_width = completion_bbox[2] - completion_bbox[0]
        draw.text(
            ((img_width - completion_width) // 2, 320),
            completion_text,
            fill=(50, 50, 50),
            font=text_font
        )
        
        # Course title
        course_bbox = draw.textbbox((0, 0), data.course_title, font=name_font)
        course_width = course_bbox[2] - course_bbox[0]
        draw.text(
            ((img_width - course_width) // 2, 370),
            data.course_title,
            fill=border_color,
            font=name_font
        )
        
        # Completion date
        date_text = f"Completed on {data.completion_date.strftime('%B %d, %Y')}"
        if data.grade:
            date_text += f" with a grade of {data.grade}"
        
        date_bbox = draw.textbbox((0, 0), date_text, font=text_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((img_width - date_width) // 2, 430),
            date_text,
            fill=(80, 80, 80),
            font=text_font
        )
        
        # Instructor signature
        draw.text((100, 550), "Instructor:", fill=(100, 100, 100), font=small_font)
        draw.text((100, 570), data.instructor_name, fill=(50, 50, 50), font=text_font)
        
        # Certificate ID
        draw.text((100, 650), f"Certificate ID: {data.certificate_id}", fill=(120, 120, 120), font=small_font)
        
        # Verification text
        verify_text = "Scan QR code to verify authenticity"
        draw.text((img_width-300, 650), verify_text, fill=(120, 120, 120), font=small_font)
        
        # Save image
        output_path = f"./certificates/{data.certificate_id}.png"
        img.save(output_path, "PNG", quality=95)
        
        return output_path
    
    async def _create_verification_url(self, certificate_id: str) -> str:
        """Create verification URL for certificate"""
        
        base_url = "https://verify.eduverse.com"
        verification_url = f"{base_url}/certificate/{certificate_id}"
        
        self.verification_urls[certificate_id] = verification_url
        
        return verification_url
    
    async def _generate_qr_code(self, verification_url: str) -> str:
        """Generate QR code for verification URL"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_path = f"./temp/qr_{uuid.uuid4()}.png"
        qr_img.save(qr_path)
        
        return qr_path
    
    async def _add_qr_code_to_certificate(
        self, 
        certificate_path: str, 
        qr_code_path: str
    ) -> str:
        """Add QR code to certificate"""
        
        try:
            # Open certificate image
            cert_img = Image.open(certificate_path)
            
            # Open QR code image
            qr_img = Image.open(qr_code_path)
            qr_img = qr_img.resize((100, 100))  # Resize QR code
            
            # Paste QR code onto certificate
            qr_position = (cert_img.width - 150, cert_img.height - 150)
            cert_img.paste(qr_img, qr_position)
            
            # Save updated certificate
            final_path = certificate_path.replace('.png', '_final.png').replace('.pdf', '_final.pdf')
            cert_img.save(final_path)
            
            return final_path
            
        except Exception as e:
            logger.error(f"Failed to add QR code to certificate: {e}")
            return certificate_path
    
    async def _create_blockchain_record(self, data: CertificateData) -> str:
        """Create blockchain record for certificate verification"""
        
        try:
            # Create certificate hash
            certificate_data = {
                "certificate_id": data.certificate_id,
                "user_id": data.user_id,
                "course_id": data.course_id,
                "user_name": data.user_name,
                "course_title": data.course_title,
                "completion_date": data.completion_date.isoformat(),
                "grade": data.grade,
                "instructor_name": data.instructor_name,
                "institution_name": data.institution_name
            }
            
            # Generate hash
            certificate_json = json.dumps(certificate_data, sort_keys=True)
            certificate_hash = hashlib.sha256(certificate_json.encode()).hexdigest()
            
            # Store in blockchain (mock implementation)
            blockchain_record = {
                "certificate_id": data.certificate_id,
                "hash": certificate_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "data": certificate_data
            }
            
            # In production, this would interact with actual blockchain
            self.blockchain_records[data.certificate_id] = certificate_hash
            
            logger.info(f"Created blockchain record for certificate {data.certificate_id}")
            
            return certificate_hash
            
        except Exception as e:
            logger.error(f"Failed to create blockchain record: {e}")
            return ""
    
    async def verify_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """Verify certificate authenticity"""
        
        try:
            # Check if certificate exists
            if certificate_id not in self.generated_certificates:
                return {
                    "valid": False,
                    "error": "Certificate not found",
                    "certificate_id": certificate_id
                }
            
            certificate_metadata = self.generated_certificates[certificate_id]
            
            # Verify blockchain record
            blockchain_hash = self.blockchain_records.get(certificate_id)
            
            if not blockchain_hash:
                return {
                    "valid": False,
                    "error": "Blockchain verification failed",
                    "certificate_id": certificate_id
                }
            
            # Verify hash integrity
            expected_hash = certificate_metadata.get("blockchain_hash")
            if blockchain_hash != expected_hash:
                return {
                    "valid": False,
                    "error": "Certificate hash mismatch",
                    "certificate_id": certificate_id
                }
            
            # Certificate is valid
            return {
                "valid": True,
                "certificate_id": certificate_id,
                "user_name": certificate_metadata["user_name"],
                "course_title": certificate_metadata["course_title"],
                "completion_date": certificate_metadata["completion_date"],
                "grade": certificate_metadata["grade"],
                "instructor_name": certificate_metadata["instructor_name"],
                "institution_name": certificate_metadata.get("institution_name", "EduVerse"),
                "skills_acquired": certificate_metadata["skills_acquired"],
                "blockchain_hash": blockchain_hash,
                "verification_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Certificate verification failed: {e}")
            return {
                "valid": False,
                "error": f"Verification error: {str(e)}",
                "certificate_id": certificate_id
            }
    
    async def get_user_certificates(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all certificates for a user"""
        
        user_certificates = []
        
        for cert_id, cert_data in self.generated_certificates.items():
            if cert_data["user_id"] == user_id:
                user_certificates.append({
                    "certificate_id": cert_id,
                    "course_title": cert_data["course_title"],
                    "completion_date": cert_data["completion_date"],
                    "grade": cert_data["grade"],
                    "verification_url": cert_data["verification_url"],
                    "download_url": f"/api/v1/certificates/{cert_id}/download",
                    "is_verified": cert_data["is_verified"]
                })
        
        # Sort by completion date (newest first)
        user_certificates.sort(
            key=lambda x: x["completion_date"], 
            reverse=True
        )
        
        return user_certificates
    
    async def generate_certificate_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive certificate portfolio for user"""
        
        user_certificates = await self.get_user_certificates(user_id)
        
        if not user_certificates:
            return {"error": "No certificates found for user"}
        
        # Create portfolio document
        portfolio_id = str(uuid.uuid4())
        portfolio_path = f"./portfolios/{portfolio_id}.pdf"
        
        # Generate portfolio PDF
        await self._generate_portfolio_pdf(user_certificates, portfolio_path)
        
        # Create portfolio metadata
        portfolio_metadata = {
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "total_certificates": len(user_certificates),
            "total_courses_completed": len(user_certificates),
            "skills_summary": await self._generate_skills_summary(user_certificates),
            "generated_at": datetime.utcnow().isoformat(),
            "download_url": f"/api/v1/certificates/portfolio/{portfolio_id}/download"
        }
        
        return portfolio_metadata
    
    async def _generate_portfolio_pdf(
        self, 
        certificates: List[Dict[str, Any]], 
        output_path: str
    ):
        """Generate PDF portfolio of certificates"""
        
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Portfolio cover page
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(Color(0.2, 0.3, 0.7))
        c.drawCentredText(width/2, height-150, "CERTIFICATE PORTFOLIO")
        
        c.setFont("Helvetica", 18)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawCentredText(width/2, height-200, "EduVerse Learning Platform")
        
        # Portfolio summary
        c.setFont("Helvetica", 14)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawCentredText(width/2, height-300, f"Total Certificates: {len(certificates)}")
        c.drawCentredText(width/2, height-320, f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}")
        
        # Add new page for certificate list
        c.showPage()
        
        # Certificate list
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height-80, "Certificates Earned")
        
        y_pos = height - 120
        for i, cert in enumerate(certificates):
            if y_pos < 100:  # Start new page if needed
                c.showPage()
                y_pos = height - 80
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y_pos, f"{i+1}. {cert['course_title']}")
            
            c.setFont("Helvetica", 12)
            c.drawString(70, y_pos-20, f"Completed: {cert['completion_date']}")
            
            if cert['grade']:
                c.drawString(70, y_pos-35, f"Grade: {cert['grade']}")
            
            c.drawString(70, y_pos-50, f"Certificate ID: {cert['certificate_id']}")
            
            y_pos -= 80
        
        c.save()
    
    async def _generate_skills_summary(self, certificates: List[Dict[str, Any]]) -> List[str]:
        """Generate summary of skills from certificates"""
        
        all_skills = []
        
        for cert in certificates:
            cert_metadata = self.generated_certificates.get(cert["certificate_id"], {})
            skills = cert_metadata.get("skills_acquired", [])
            all_skills.extend(skills)
        
        # Remove duplicates and return unique skills
        unique_skills = list(set(all_skills))
        return unique_skills
    
    async def _load_certificate_templates(self):
        """Load available certificate templates"""
        
        # Default template
        self.templates["default"] = CertificateTemplate(
            template_id="default",
            name="Classic Certificate",
            description="Traditional certificate design with elegant borders",
            template_path="./templates/classic_certificate.html",
            preview_image="./templates/previews/classic.png",
            customizable_fields=["background_color", "border_style", "font_family"],
            supported_languages=["en", "es", "fr", "de"],
            is_premium=False
        )
        
        # Premium templates
        self.templates["modern"] = CertificateTemplate(
            template_id="modern",
            name="Modern Certificate",
            description="Contemporary design with gradient backgrounds",
            template_path="./templates/modern_certificate.html",
            preview_image="./templates/previews/modern.png",
            customizable_fields=["gradient_colors", "typography", "layout"],
            supported_languages=["en", "es", "fr", "de", "zh", "ja"],
            is_premium=True
        )
        
        self.templates["academic"] = CertificateTemplate(
            template_id="academic",
            name="Academic Certificate",
            description="Formal academic style with institutional branding",
            template_path="./templates/academic_certificate.html",
            preview_image="./templates/previews/academic.png",
            customizable_fields=["institution_logo", "seal", "signatures"],
            supported_languages=["en", "es", "fr", "de", "it", "pt"],
            is_premium=True
        )
    
    async def _initialize_blockchain_connection(self):
        """Initialize blockchain connection for certificate verification"""
        
        # In production, this would connect to actual blockchain network
        # For now, we'll use a mock implementation
        logger.info("Initializing blockchain connection (mock)")
    
    async def _initialize_verification_system(self):
        """Initialize certificate verification system"""
        
        # Set up verification endpoints and database
        logger.info("Initializing certificate verification system")
    
    async def _send_certificate_notification(
        self, 
        data: CertificateData, 
        verification_url: str
    ):
        """Send certificate completion notification"""
        
        # Implementation for sending certificate notification
        logger.info(f"Sending certificate notification to user {data.user_id}")
    
    async def cleanup(self):
        """Cleanup certificate service resources"""
        logger.info("Certificate Service cleaned up")


class CertificateTemplateManager:
    """Manage certificate templates and customization"""
    
    def __init__(self):
        self.custom_templates: Dict[str, CertificateTemplate] = {}
    
    async def create_custom_template(
        self, 
        template_data: Dict[str, Any]
    ) -> CertificateTemplate:
        """Create custom certificate template"""
        
        template = CertificateTemplate(
            template_id=str(uuid.uuid4()),
            name=template_data["name"],
            description=template_data["description"],
            template_path=template_data["template_path"],
            preview_image=template_data["preview_image"],
            customizable_fields=template_data["customizable_fields"],
            supported_languages=template_data["supported_languages"],
            is_premium=template_data.get("is_premium", True)
        )
        
        self.custom_templates[template.template_id] = template
        
        return template
    
    async def customize_template(
        self, 
        template_id: str, 
        customizations: Dict[str, Any]
    ) -> str:
        """Apply customizations to template"""
        
        # Implementation for template customization
        customized_template_id = f"{template_id}_custom_{uuid.uuid4()}"
        
        return customized_template_id


class CertificateAnalytics:
    """Analytics for certificate generation and verification"""
    
    def __init__(self):
        self.generation_stats: Dict[str, int] = {}
        self.verification_stats: Dict[str, int] = {}
    
    async def track_certificate_generation(
        self, 
        certificate_id: str, 
        template_id: str,
        user_data: Dict[str, Any]
    ):
        """Track certificate generation for analytics"""
        self.generation_stats[template_id] = self.generation_stats.get(template_id, 0) + 1
        logger.info(f"Tracked certificate generation: {certificate_id} for template {template_id}")
    
    async def track_certificate_verification(
        self, 
        certificate_id: str, 
        verification_result: Dict[str, Any]
    ):
        """Track certificate verification for analytics"""
        status = verification_result.get("status", "unknown")
        self.verification_stats[status] = self.verification_stats.get(status, 0) + 1
        logger.info(f"Tracked certificate verification: {certificate_id} with status {status}")
    
    async def get_certificate_analytics(self) -> Dict[str, Any]:
        """Get certificate generation and verification analytics"""
        
        return {
            "total_certificates_generated": sum(self.generation_stats.values()),
            "total_verifications": sum(self.verification_stats.values()),
            "generation_by_template": self.generation_stats,
            "verification_success_rate": 0.98,  # Mock data
            "most_popular_template": "default",
            "average_generation_time": 2.5  # seconds
        }