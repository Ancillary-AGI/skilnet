"""
Payment-related Pydantic schemas for EduVerse API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal


class PaymentItem(BaseModel):
    """Item in a payment"""
    type: str = Field(..., description="Type of item (course, premium_feature, etc.)")
    id: str = Field(..., description="ID of the item")
    quantity: int = Field(default=1, description="Quantity of the item")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class PaymentIntentCreate(BaseModel):
    """Request to create a payment intent"""
    items: List[PaymentItem] = Field(..., description="Items to purchase")
    currency: str = Field(default="usd", description="Payment currency")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class PaymentIntentResponse(BaseModel):
    """Response containing payment intent details"""
    client_secret: str = Field(..., description="Stripe client secret")
    payment_intent_id: str = Field(..., description="Payment intent ID")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency")


class SubscriptionCreate(BaseModel):
    """Request to create a subscription"""
    plan_id: str = Field(..., description="Subscription plan ID")
    payment_method_id: Optional[str] = Field(default=None, description="Payment method ID")
    trial_period_days: Optional[int] = Field(default=None, description="Trial period in days")


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: str
    user_id: str
    plan_id: str
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentMethodCreate(BaseModel):
    """Request to add a payment method"""
    payment_method_id: str = Field(..., description="Stripe payment method ID")
    set_as_default: bool = Field(default=True, description="Set as default payment method")


class PaymentMethodResponse(BaseModel):
    """Payment method response"""
    id: str
    type: str
    last4: Optional[str]
    brand: Optional[str]
    is_default: bool


class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: str
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    status: str
    created: datetime
    invoice_pdf: Optional[str]


class RefundRequest(BaseModel):
    """Refund request"""
    payment_intent_id: str = Field(..., description="Payment intent to refund")
    amount: Optional[Decimal] = Field(default=None, description="Amount to refund (full refund if not specified)")
    reason: Optional[str] = Field(default=None, description="Reason for refund")


class RefundResponse(BaseModel):
    """Refund response"""
    id: str
    amount: Decimal
    currency: str
    status: str


class WebhookEvent(BaseModel):
    """Stripe webhook event"""
    id: str
    type: str
    data: Dict[str, Any]
    created: datetime


class SubscriptionPlanCreate(BaseModel):
    """Create subscription plan"""
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    price: Decimal = Field(..., description="Monthly price")
    currency: str = Field(default="usd", description="Currency")
    interval: str = Field(default="month", description="Billing interval")
    features: List[str] = Field(default_factory=list, description="Plan features")
    max_users: Optional[int] = Field(default=None, description="Maximum users (for team plans)")
    is_active: bool = Field(default=True, description="Plan is active")


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan response"""
    id: str
    name: str
    description: str
    price: Decimal
    currency: str
    interval: str
    features: List[str]
    max_users: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentHistoryResponse(BaseModel):
    """Payment history response"""
    id: str
    amount: Decimal
    currency: str
    status: str
    description: str
    created_at: datetime
    invoice_url: Optional[str]


class CouponCreate(BaseModel):
    """Create discount coupon"""
    code: str = Field(..., description="Coupon code")
    description: str = Field(..., description="Coupon description")
    discount_type: str = Field(..., description="Type: percent or fixed")
    discount_value: Decimal = Field(..., description="Discount value")
    max_uses: Optional[int] = Field(default=None, description="Maximum uses")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration date")
    applicable_plans: List[str] = Field(default_factory=list, description="Applicable plan IDs")


class CouponResponse(BaseModel):
    """Coupon response"""
    id: str
    code: str
    description: str
    discount_type: str
    discount_value: Decimal
    max_uses: Optional[int]
    used_count: int
    expires_at: Optional[datetime]
    applicable_plans: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BillingAddress(BaseModel):
    """Billing address"""
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str


class TaxInfo(BaseModel):
    """Tax information"""
    tax_id: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None


class InvoiceCreate(BaseModel):
    """Create invoice"""
    customer_id: str
    items: List[PaymentItem]
    billing_address: Optional[BillingAddress] = None
    tax_info: Optional[TaxInfo] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class PaymentAnalytics(BaseModel):
    """Payment analytics"""
    total_revenue: Decimal
    monthly_recurring_revenue: Decimal
    active_subscriptions: int
    churn_rate: Decimal
    average_revenue_per_user: Decimal
    payment_success_rate: Decimal
    top_plans: List[Dict[str, Any]]
    revenue_by_month: List[Dict[str, Any]]