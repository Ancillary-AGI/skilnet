"""
Subscription and payment models for EduVerse platform
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from enum import Enum as PyEnum
import uuid

class SubscriptionTier(PyEnum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class BillingCycle(PyEnum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    BIENNIAL = "biennial"

class PaymentStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(PyEnum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    RAZORPAY = "razorpay"
    FLUTTERWAVE = "flutterwave"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Subscription details
    tier = Column(Enum(SubscriptionTier), nullable=False)
    billing_cycle = Column(Enum(BillingCycle), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    
    # Dates
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_ends_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # External IDs
    stripe_subscription_id = Column(String)
    paypal_subscription_id = Column(String)
    external_customer_id = Column(String)
    
    # Features and limits
    feature_limits = Column(JSON)  # Dict of feature limits
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier={self.tier})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier.value,
            "billing_cycle": self.billing_cycle.value,
            "price": self.price,
            "currency": self.currency,
            "is_active": self.is_active,
            "is_trial": self.is_trial,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # External payment IDs
    external_payment_id = Column(String)  # Stripe payment intent ID, etc.
    external_transaction_id = Column(String)
    
    # Description and metadata
    description = Column(Text)
    metadata = Column(JSON)
    
    # Failure information
    failure_reason = Column(String)
    failure_code = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    payment_id = Column(String, ForeignKey("payments.id"))
    
    # Invoice details
    invoice_number = Column(String, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(String, default="draft")  # draft, sent, paid, overdue, cancelled
    
    # Dates
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    # Content
    line_items = Column(JSON)  # List of invoice line items
    notes = Column(Text)
    
    # External IDs
    external_invoice_id = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number})>"