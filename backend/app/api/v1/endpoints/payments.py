"""
Payments endpoints for EduVerse platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json

from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("payments")

@router.get("/subscription-plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    try:
        plans = [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "billing_period": "monthly",
                "description": "Perfect for getting started with basic learning",
                "features": [
                    "Access to free courses",
                    "Basic progress tracking",
                    "Community forums",
                    "Mobile app access",
                    "Standard video quality"
                ],
                "limitations": [
                    "Limited course selection",
                    "No certificates",
                    "No offline downloads",
                    "Basic support only"
                ],
                "max_courses": 5,
                "storage_gb": 1,
                "is_popular": False
            },
            {
                "id": "premium",
                "name": "Premium",
                "price": 19.99,
                "currency": "USD",
                "billing_period": "monthly",
                "description": "Unlock your full learning potential",
                "features": [
                    "Access to all courses",
                    "Certificates of completion",
                    "Offline downloads",
                    "HD video quality",
                    "Advanced analytics",
                    "Priority support",
                    "VR/AR content access",
                    "AI-powered recommendations"
                ],
                "limitations": [],
                "max_courses": "unlimited",
                "storage_gb": 50,
                "is_popular": True,
                "discount_annual": 0.20  # 20% off annual billing
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 39.99,
                "currency": "USD",
                "billing_period": "monthly",
                "description": "For serious learners and professionals",
                "features": [
                    "Everything in Premium",
                    "Live AI tutoring sessions",
                    "1-on-1 instructor sessions",
                    "Custom learning paths",
                    "Advanced VR experiences",
                    "Blockchain certificates",
                    "API access",
                    "White-label options",
                    "Team collaboration tools"
                ],
                "limitations": [],
                "max_courses": "unlimited",
                "storage_gb": 200,
                "is_popular": False,
                "discount_annual": 0.25  # 25% off annual billing
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": "custom",
                "currency": "USD",
                "billing_period": "annual",
                "description": "Tailored solutions for organizations",
                "features": [
                    "Everything in Pro",
                    "Custom branding",
                    "Advanced analytics dashboard",
                    "SSO integration",
                    "Dedicated account manager",
                    "Custom content creation",
                    "Bulk user management",
                    "Advanced reporting",
                    "SLA guarantees"
                ],
                "limitations": [],
                "max_courses": "unlimited",
                "storage_gb": "unlimited",
                "is_popular": False,
                "min_users": 100
            }
        ]
        
        return {"plans": plans}
        
    except Exception as e:
        logger.error(f"Failed to get subscription plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription plans"
        )

@router.get("/current-subscription")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's current subscription details"""
    try:
        # Mock subscription data - replace with real database queries
        subscription = {
            "user_id": current_user.id,
            "plan_id": "premium" if current_user.is_premium else "free",
            "plan_name": "Premium" if current_user.is_premium else "Free",
            "status": "active",
            "billing_period": "monthly",
            "price": 19.99 if current_user.is_premium else 0,
            "currency": "USD",
            "started_at": "2024-01-01T00:00:00Z",
            "current_period_start": "2024-01-15T00:00:00Z",
            "current_period_end": "2024-02-15T00:00:00Z",
            "auto_renew": True,
            "payment_method": {
                "type": "card",
                "last_four": "4242",
                "brand": "visa",
                "expires": "12/25"
            } if current_user.is_premium else None,
            "usage": {
                "courses_accessed": 8,
                "storage_used_gb": 2.5,
                "downloads_this_month": 15,
                "ai_sessions_used": 5
            },
            "next_billing_date": "2024-02-15T00:00:00Z" if current_user.is_premium else None,
            "next_billing_amount": 19.99 if current_user.is_premium else None
        }
        
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to get current subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription details"
        )

@router.post("/create-checkout-session")
async def create_checkout_session(
    checkout_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create payment checkout session"""
    try:
        plan_id = checkout_data.get("plan_id")
        billing_period = checkout_data.get("billing_period", "monthly")
        
        if not plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan ID is required"
            )
        
        # Mock checkout session - in production, integrate with Stripe/PayPal
        checkout_session = {
            "session_id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "plan_id": plan_id,
            "billing_period": billing_period,
            "amount": calculate_plan_price(plan_id, billing_period),
            "currency": "USD",
            "checkout_url": f"https://checkout.eduverse.com/session/{uuid.uuid4()}",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "success_url": "https://eduverse.com/payment/success",
            "cancel_url": "https://eduverse.com/payment/cancel",
            "metadata": {
                "user_id": current_user.id,
                "plan_id": plan_id,
                "billing_period": billing_period
            }
        }
        
        # Store session in database for verification
        logger.info(f"Checkout session created: {checkout_session['session_id']}")
        
        return checkout_session
        
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.post("/webhook")
async def payment_webhook(
    webhook_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle payment provider webhooks"""
    try:
        event_type = webhook_data.get("type")
        
        if event_type == "payment.succeeded":
            await handle_payment_success(webhook_data, db)
        elif event_type == "payment.failed":
            await handle_payment_failure(webhook_data, db)
        elif event_type == "subscription.cancelled":
            await handle_subscription_cancellation(webhook_data, db)
        elif event_type == "subscription.renewed":
            await handle_subscription_renewal(webhook_data, db)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

@router.get("/payment-history")
async def get_payment_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's payment history"""
    try:
        # Mock payment history - replace with real database queries
        payments = [
            {
                "id": "pay_001",
                "amount": 19.99,
                "currency": "USD",
                "status": "succeeded",
                "description": "Premium Monthly Subscription",
                "created_at": "2024-01-15T10:30:00Z",
                "payment_method": "card_4242",
                "invoice_url": "/invoices/inv_001.pdf"
            },
            {
                "id": "pay_002",
                "amount": 19.99,
                "currency": "USD",
                "status": "succeeded",
                "description": "Premium Monthly Subscription",
                "created_at": "2023-12-15T10:30:00Z",
                "payment_method": "card_4242",
                "invoice_url": "/invoices/inv_002.pdf"
            }
        ]
        
        return {
            "payments": payments[offset:offset+limit],
            "total_count": len(payments),
            "has_more": offset + limit < len(payments)
        }
        
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )

@router.post("/cancel-subscription")
async def cancel_subscription(
    cancellation_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel user's subscription"""
    try:
        reason = cancellation_data.get("reason", "user_request")
        immediate = cancellation_data.get("immediate", False)
        
        # Mock cancellation - in production, call payment provider API
        cancellation = {
            "user_id": current_user.id,
            "cancelled_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "immediate": immediate,
            "effective_date": datetime.utcnow().isoformat() if immediate else "2024-02-15T00:00:00Z",
            "refund_amount": 0,  # Calculate based on policy
            "access_until": "2024-02-15T00:00:00Z" if not immediate else datetime.utcnow().isoformat()
        }
        
        # Update user subscription status
        if immediate:
            current_user.is_premium = False
            await db.commit()
        
        logger.info(f"Subscription cancelled for user {current_user.id}")
        
        return {
            "success": True,
            "cancellation": cancellation,
            "message": "Subscription cancelled successfully"
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/update-payment-method")
async def update_payment_method(
    payment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's payment method"""
    try:
        # Mock payment method update - in production, use Stripe/PayPal API
        payment_method = {
            "id": payment_data.get("payment_method_id"),
            "type": payment_data.get("type", "card"),
            "last_four": payment_data.get("last_four"),
            "brand": payment_data.get("brand"),
            "expires": payment_data.get("expires"),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Payment method updated for user {current_user.id}")
        
        return {
            "success": True,
            "payment_method": payment_method,
            "message": "Payment method updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update payment method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment method"
        )

@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's invoices"""
    try:
        # Mock invoices - replace with real data
        invoices = [
            {
                "id": "inv_001",
                "number": "INV-2024-001",
                "amount": 19.99,
                "currency": "USD",
                "status": "paid",
                "issued_date": "2024-01-15T00:00:00Z",
                "due_date": "2024-01-15T00:00:00Z",
                "paid_date": "2024-01-15T10:30:00Z",
                "description": "Premium Monthly Subscription - January 2024",
                "download_url": "/api/v1/payments/invoices/inv_001/download"
            }
        ]
        
        return {"invoices": invoices}
        
    except Exception as e:
        logger.error(f"Failed to get invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )

@router.get("/usage-analytics")
async def get_usage_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription usage analytics"""
    try:
        analytics = {
            "current_period": {
                "start_date": "2024-01-15T00:00:00Z",
                "end_date": "2024-02-15T00:00:00Z",
                "days_remaining": 15
            },
            "usage_stats": {
                "courses_accessed": 8,
                "total_study_hours": 45.5,
                "downloads_used": 15,
                "downloads_limit": 50,
                "storage_used_gb": 2.5,
                "storage_limit_gb": 50,
                "ai_sessions_used": 5,
                "ai_sessions_limit": 20
            },
            "feature_usage": {
                "vr_ar_content": 12,
                "live_sessions": 3,
                "certificates_earned": 2,
                "collaboration_sessions": 8
            },
            "cost_analysis": {
                "cost_per_hour": 0.44,  # $19.99 / 45.5 hours
                "value_score": 8.5,  # out of 10
                "compared_to_alternatives": "35% more cost-effective"
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get usage analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage analytics"
        )

# Helper functions

def calculate_plan_price(plan_id: str, billing_period: str) -> float:
    """Calculate plan price based on ID and billing period"""
    prices = {
        "free": 0,
        "premium": 19.99 if billing_period == "monthly" else 191.90,  # 20% annual discount
        "pro": 39.99 if billing_period == "monthly" else 359.91  # 25% annual discount
    }
    return prices.get(plan_id, 0)

async def handle_payment_success(webhook_data: Dict[str, Any], db: AsyncSession):
    """Handle successful payment webhook"""
    user_id = webhook_data.get("metadata", {}).get("user_id")
    plan_id = webhook_data.get("metadata", {}).get("plan_id")
    
    if user_id and plan_id:
        # Update user subscription status
        logger.info(f"Payment succeeded for user {user_id}, plan {plan_id}")

async def handle_payment_failure(webhook_data: Dict[str, Any], db: AsyncSession):
    """Handle failed payment webhook"""
    user_id = webhook_data.get("metadata", {}).get("user_id")
    logger.warning(f"Payment failed for user {user_id}")

async def handle_subscription_cancellation(webhook_data: Dict[str, Any], db: AsyncSession):
    """Handle subscription cancellation webhook"""
    user_id = webhook_data.get("metadata", {}).get("user_id")
    logger.info(f"Subscription cancelled for user {user_id}")

async def handle_subscription_renewal(webhook_data: Dict[str, Any], db: AsyncSession):
    """Handle subscription renewal webhook"""
    user_id = webhook_data.get("metadata", {}).get("user_id")
    logger.info(f"Subscription renewed for user {user_id}")