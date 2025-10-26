"""
Payment schemas for EduVerse platform
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class PaymentMethodType(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    RAZORPAY = "razorpay"
    FLUTTERWAVE = "flutterwave"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class SubscriptionTierType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class BillingCycleType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    BIENNIAL = "biennial"

class PaymentIntentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", max_length=3)
    description: Optional[str] = None
    payment_method: Optional[PaymentMethodType] = PaymentMethodType.STRIPE
    metadata: Optional[Dict[str, Any]] = None

class PaymentIntentResponse(BaseModel):
    id: str
    client_secret: Optional[str]
    amount: float
    currency: str
    status: str
    payment_method: PaymentMethodType
    metadata: Dict[str, Any]

class SubscriptionData(BaseModel):
    tier: SubscriptionTierType
    billing_cycle: BillingCycleType

class PaymentConfirm(BaseModel):
    payment_intent_id: str
    payment_method: PaymentMethodType
    subscription_data: Optional[SubscriptionData] = None

class SubscriptionCreate(BaseModel):
    tier: SubscriptionTierType
    billing_cycle: BillingCycleType
    payment_method: PaymentMethodType
    is_trial: bool = False

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    tier: SubscriptionTierType
    billing_cycle: BillingCycleType
    price: float
    currency: str
    is_active: bool
    is_trial: bool
    current_period_start: datetime
    current_period_end: datetime
    trial_ends_at: Optional[datetime]
    feature_limits: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentMethodResponse(BaseModel):
    id: str
    name: str
    type: str
    supported_currencies: List[str]
    fees: Dict[str, float]
    processing_time: str

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    amount: float
    currency: str
    tax_amount: float
    total_amount: float
    status: str
    issue_date: datetime
    due_date: Optional[datetime]
    paid_date: Optional[datetime]
    line_items: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None  # If None, refund full amount
    reason: str

class RefundResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    reason: str
    processed_at: datetime