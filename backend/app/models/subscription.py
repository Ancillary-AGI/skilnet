from .base_model import BaseModel
from ..core.database import Field
from enum import Enum
import uuid

class SubscriptionTier(str, Enum):
    FREE = "free"
    EXPLORER = "explorer"
    SCHOLAR = "scholar"
    GENIUS = "genius"
    UNLIMITED = "unlimited"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    BIENNIAL = "biennial"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    RAZORPAY = "razorpay"
    FLUTTERWAVE = "flutterwave"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CRYPTO = "crypto"

class Subscription(BaseModel):
    _table_name = "subscriptions"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'tier': Field('TEXT', default=SubscriptionTier.FREE),
        'billing_cycle': Field('TEXT', default=BillingCycle.MONTHLY),
        'price': Field('REAL', default=0.0),
        'currency': Field('TEXT', default='USD'),
        'is_active': Field('BOOLEAN', default=True),
        'is_trial': Field('BOOLEAN', default=False),
        'trial_ends_at': Field('TIMESTAMP'),
        'current_period_start': Field('TIMESTAMP'),
        'current_period_end': Field('TIMESTAMP'),
        'cancelled_at': Field('TIMESTAMP'),
        'stripe_subscription_id': Field('TEXT'),
        'paypal_subscription_id': Field('TEXT'),
        'external_customer_id': Field('TEXT'),
        'feature_limits': Field('JSON', default={}),
        'usage_stats': Field('JSON'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class Payment(BaseModel):
    _table_name = "payments"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'subscription_id': Field('TEXT', index=True),
        'user_id': Field('TEXT', nullable=False, index=True),
        'amount': Field('REAL', nullable=False),
        'currency': Field('TEXT', default='USD'),
        'status': Field('TEXT', default=PaymentStatus.PENDING),
        'payment_method': Field('TEXT', nullable=False),
        'external_payment_id': Field('TEXT'),
        'external_customer_id': Field('TEXT'),
        'payment_intent_id': Field('TEXT'),
        'description': Field('TEXT'),
        'metadata': Field('JSON', default={}),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'processed_at': Field('TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class UsageRecord(BaseModel):
    _table_name = "usage_records"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'subscription_id': Field('TEXT', nullable=False, index=True),
        'user_id': Field('TEXT', nullable=False, index=True),
        'feature': Field('TEXT', nullable=False),
        'usage_count': Field('INTEGER', default=0),
        'usage_date': Field('TIMESTAMP', nullable=False),
        'metadata': Field('JSON', default={}),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class PromoCode(BaseModel):
    _table_name = "promo_codes"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'code': Field('TEXT', unique=True, nullable=False, index=True),
        'discount_type': Field('TEXT', nullable=False),  # percentage, fixed
        'discount_value': Field('REAL', nullable=False),
        'max_discount_amount': Field('REAL'),
        'is_active': Field('BOOLEAN', default=True),
        'valid_from': Field('TIMESTAMP', nullable=False),
        'valid_until': Field('TIMESTAMP', nullable=False),
        'max_uses': Field('INTEGER'),
        'max_uses_per_user': Field('INTEGER', default=1),
        'current_uses': Field('INTEGER', default=0),
        'applicable_tiers': Field('JSON', default=[]),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class Invoice(BaseModel):
    _table_name = "invoices"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'subscription_id': Field('TEXT', index=True),
        'invoice_number': Field('TEXT', unique=True, nullable=False),
        'amount': Field('REAL', nullable=False),
        'currency': Field('TEXT', default='USD'),
        'tax_amount': Field('REAL', default=0.0),
        'total_amount': Field('REAL', nullable=False),
        'status': Field('TEXT', default="draft"),  # draft, sent, paid, overdue
        'issue_date': Field('TIMESTAMP', nullable=False),
        'due_date': Field('TIMESTAMP', nullable=False),
        'paid_date': Field('TIMESTAMP'),
        'external_invoice_id': Field('TEXT'),
        'line_items': Field('JSON', default=[]),
        'billing_address': Field('JSON', default={}),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class RegionalPricing(BaseModel):
    _table_name = "regional_pricing"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'country_code': Field('TEXT', nullable=False),  # ISO country code
        'currency': Field('TEXT', nullable=False),
        'region_name': Field('TEXT', nullable=False),
        'tier': Field('TEXT', nullable=False),
        'monthly_price': Field('REAL', nullable=False),
        'annual_price': Field('REAL', nullable=False),
        'ppp_adjustment': Field('REAL', default=1.0),  # Purchasing power parity
        'is_active': Field('BOOLEAN', default=True),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class SubscriptionAnalytics(BaseModel):
    _table_name = "subscription_analytics"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'date': Field('TIMESTAMP', nullable=False),
        'period_type': Field('TEXT', nullable=False),  # daily, weekly, monthly
        'new_subscriptions': Field('INTEGER', default=0),
        'cancelled_subscriptions': Field('INTEGER', default=0),
        'upgraded_subscriptions': Field('INTEGER', default=0),
        'downgraded_subscriptions': Field('INTEGER', default=0),
        'mrr': Field('REAL', default=0.0),  # Monthly Recurring Revenue
        'arr': Field('REAL', default=0.0),  # Annual Recurring Revenue
        'churn_rate': Field('REAL', default=0.0),
        'tier_breakdown': Field('JSON', default={}),
        'regional_breakdown': Field('JSON', default={}),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }