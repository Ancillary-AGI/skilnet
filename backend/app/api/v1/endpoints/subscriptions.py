"""
Subscription management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.subscription import Subscription, SubscriptionTier, BillingCycle
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    SubscriptionResponse,
    SubscriptionCreate,
    SubscriptionUpdate
)
from app.core.security import get_current_user

router = APIRouter()

# Available subscription plans (could be moved to database later)
SUBSCRIPTION_PLANS = [
    {
        "id": "free",
        "name": "Free",
        "description": "Perfect for getting started",
        "tier": "free",
        "price": 0.0,
        "currency": "USD",
        "billing_cycle": "monthly",
        "features": [
            "Basic course access",
            "Community features",
            "Mobile app access",
            "Email support"
        ],
        "max_devices": 1,
        "storage_gb": 1,
        "includes_ai": False,
        "includes_vr": False,
        "is_popular": False,
    },
    {
        "id": "premium_monthly",
        "name": "Premium",
        "description": "Full access to all features",
        "tier": "premium",
        "price": 19.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "features": [
            "All courses and content",
            "AI tutor access",
            "VR/AR experiences",
            "Offline downloads",
            "Priority support",
            "Advanced analytics",
            "Certificate generation"
        ],
        "max_devices": 3,
        "storage_gb": 10,
        "includes_ai": True,
        "includes_vr": True,
        "is_popular": True,
    },
    {
        "id": "premium_yearly",
        "name": "Premium Yearly",
        "description": "Best value with yearly billing",
        "tier": "premium",
        "price": 199.99,
        "currency": "USD",
        "billing_cycle": "annual",
        "features": [
            "All courses and content",
            "AI tutor access",
            "VR/AR experiences",
            "Offline downloads",
            "Priority support",
            "Advanced analytics",
            "Certificate generation",
            "2 months free!"
        ],
        "max_devices": 5,
        "storage_gb": 25,
        "includes_ai": True,
        "includes_vr": True,
        "is_popular": False,
    },
]

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans():
    """Get all available subscription plans"""
    return [SubscriptionPlanResponse(**plan) for plan in SUBSCRIPTION_PLANS]

@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(plan_id: str):
    """Get a specific subscription plan"""
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return SubscriptionPlanResponse(**plan)

@router.get("/", response_model=SubscriptionResponse)
async def get_user_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).first()

    if not subscription:
        # Return free tier for users without active subscription
        free_plan = next(p for p in SUBSCRIPTION_PLANS if p["id"] == "free")
        return SubscriptionResponse(
            id="free",
            plan=SubscriptionPlanResponse(**free_plan),
            is_active=False,
            features=free_plan["features"],
            current_period_start=datetime.utcnow(),
            current_period_end=None,
        )

    plan = next((p for p in SUBSCRIPTION_PLANS if p["tier"] == subscription.tier.value), None)
    if not plan:
        plan = next(p for p in SUBSCRIPTION_PLANS if p["id"] == "free")

    return SubscriptionResponse(
        id=subscription.id,
        plan=SubscriptionPlanResponse(**plan),
        is_active=subscription.is_active,
        features=plan["features"],
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        trial_ends_at=subscription.trial_ends_at,
        cancelled_at=subscription.cancelled_at,
    )

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subscription for the user"""
    # Check if user already has an active subscription
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already has an active subscription"
        )

    # Get plan details
    plan = next((p for p in SUBSCRIPTION_PLANS if p["id"] == subscription.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Calculate period dates
    now = datetime.utcnow()
    if plan["billing_cycle"] == "monthly":
        period_end = now.replace(month=now.month + 1)
    elif plan["billing_cycle"] == "annual":
        period_end = now.replace(year=now.year + 1)
    else:
        period_end = now.replace(month=now.month + 1)  # Default to monthly

    db_subscription = Subscription(
        user_id=current_user.id,
        tier=SubscriptionTier(plan["tier"]),
        billing_cycle=BillingCycle(plan["billing_cycle"]),
        price=plan["price"],
        currency=plan["currency"],
        is_active=True,
        current_period_start=now,
        current_period_end=period_end,
        feature_limits={},  # Could be populated based on plan
    )

    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)

    return SubscriptionResponse(
        id=db_subscription.id,
        plan=SubscriptionPlanResponse(**plan),
        is_active=True,
        features=plan["features"],
        current_period_start=db_subscription.current_period_start,
        current_period_end=db_subscription.current_period_end,
    )

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    update: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update fields
    if update.is_active is not None:
        subscription.is_active = update.is_active
        if not update.is_active:
            subscription.cancelled_at = datetime.utcnow()

    subscription.updated_at = datetime.utcnow()
    db.commit()

    # Get plan details
    plan = next((p for p in SUBSCRIPTION_PLANS if p["tier"] == subscription.tier.value), None)
    if not plan:
        plan = next(p for p in SUBSCRIPTION_PLANS if p["id"] == "free")

    return SubscriptionResponse(
        id=subscription.id,
        plan=SubscriptionPlanResponse(**plan),
        is_active=subscription.is_active,
        features=plan["features"],
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        trial_ends_at=subscription.trial_ends_at,
        cancelled_at=subscription.cancelled_at,
    )

@router.delete("/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.is_active = False
    subscription.cancelled_at = datetime.utcnow()
    db.commit()

    return {"message": "Subscription cancelled successfully"}
