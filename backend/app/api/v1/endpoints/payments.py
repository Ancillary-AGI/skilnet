"""
Payment processing endpoints for EduVerse platform
Handles subscriptions, one-time purchases, and payment processing
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
import stripe
import paypalrestsdk
from datetime import datetime, timedelta
import logging
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan
from app.schemas.payments import (
    PaymentIntentCreate,
    PaymentIntentResponse,
    SubscriptionCreate,
    SubscriptionResponse,
    PaymentMethodCreate,
    PaymentMethodResponse,
    InvoiceResponse,
    RefundRequest,
    RefundResponse,
    WebhookEvent
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize payment processors
stripe.api_key = "your_stripe_secret_key"  # Should come from config
paypalrestsdk.configure({
    "mode": "sandbox",  # Should come from config
    "client_id": "your_paypal_client_id",
    "client_secret": "your_paypal_client_secret"
})

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a payment intent for one-time purchases
    """
    try:
        # Calculate total amount
        amount = await _calculate_payment_amount(payment_data.items, db)

        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=payment_data.currency,
            customer=current_user.stripe_customer_id,
            metadata={
                "user_id": str(current_user.id),
                "items": str(payment_data.items)
            }
        )

        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id,
            amount=amount,
            currency=payment_data.currency
        )

    except Exception as e:
        logger.error(f"Payment intent creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create payment intent"
        )

@router.post("/create-subscription", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a subscription for recurring payments
    """
    try:
        # Get subscription plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == subscription_data.plan_id
        ).first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )

        # Create or get Stripe customer
        customer_id = await _get_or_create_stripe_customer(current_user, db)

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                "price_data": {
                    "currency": plan.currency,
                    "product_data": {
                        "name": plan.name,
                        "description": plan.description,
                    },
                    "unit_amount": int(plan.price * 100),
                    "recurring": {
                        "interval": plan.interval,
                    },
                },
            }],
            metadata={
                "user_id": str(current_user.id),
                "plan_id": str(plan.id)
            }
        )

        # Save subscription to database
        db_subscription = Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            stripe_subscription_id=subscription.id,
            status=subscription.status,
            current_period_start=datetime.fromtimestamp(subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
            cancel_at_period_end=subscription.cancel_at_period_end
        )

        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)

        return SubscriptionResponse.from_orm(db_subscription)

    except Exception as e:
        logger.error(f"Subscription creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create subscription"
        )

@router.post("/payment-methods", response_model=PaymentMethodResponse)
async def add_payment_method(
    payment_method_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a payment method for the user
    """
    try:
        customer_id = await _get_or_create_stripe_customer(current_user, db)

        # Attach payment method to customer
        payment_method = stripe.PaymentMethod.attach(
            payment_method_data.payment_method_id,
            customer=customer_id,
        )

        # Set as default if requested
        if payment_method_data.set_as_default:
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method.id,
                },
            )

        return PaymentMethodResponse(
            id=payment_method.id,
            type=payment_method.type,
            last4=payment_method.card.last4 if payment_method.card else None,
            brand=payment_method.card.brand if payment_method.card else None,
            is_default=payment_method_data.set_as_default
        )

    except Exception as e:
        logger.error(f"Payment method addition failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add payment method"
        )

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's active subscriptions
    """
    subscriptions = db.query(Subscription).filter(
        and_(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "trialing"])
        )
    ).all()

    return [SubscriptionResponse.from_orm(sub) for sub in subscriptions]

@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a user's subscription
    """
    subscription = db.query(Subscription).filter(
        and_(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user.id
        )
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    try:
        # Cancel in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Update in database
        subscription.cancel_at_period_end = True
        db.commit()

        return {"message": "Subscription will be cancelled at the end of the billing period"}

    except Exception as e:
        logger.error(f"Subscription cancellation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel subscription"
        )

@router.post("/webhook")
async def stripe_webhook(
    webhook_data: WebhookEvent,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks for payment events
    """
    try:
        # Verify webhook signature (implement in production)
        event = webhook_data

        # Handle different event types
        if event.type == "customer.subscription.updated":
            await _handle_subscription_updated(event.data, db)
        elif event.type == "customer.subscription.deleted":
            await _handle_subscription_cancelled(event.data, db)
        elif event.type == "invoice.payment_succeeded":
            await _handle_payment_succeeded(event.data, db)
        elif event.type == "invoice.payment_failed":
            await _handle_payment_failed(event.data, db)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )

@router.post("/refund", response_model=RefundResponse)
async def create_refund(
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a refund for a payment
    """
    try:
        # Verify payment belongs to user (implement proper validation)
        refund = stripe.Refund.create(
            payment_intent=refund_data.payment_intent_id,
            amount=int(refund_data.amount * 100) if refund_data.amount else None,
            reason=refund_data.reason
        )

        return RefundResponse(
            id=refund.id,
            amount=refund.amount / 100,  # Convert from cents
            currency=refund.currency,
            status=refund.status
        )

    except Exception as e:
        logger.error(f"Refund creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create refund"
        )

@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_user_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's billing history
    """
    try:
        customer_id = current_user.stripe_customer_id
        if not customer_id:
            return []

        invoices = stripe.Invoice.list(customer=customer_id)

        return [
            InvoiceResponse(
                id=invoice.id,
                amount_due=invoice.amount_due / 100,
                amount_paid=invoice.amount_paid / 100,
                currency=invoice.currency,
                status=invoice.status,
                created=datetime.fromtimestamp(invoice.created),
                invoice_pdf=invoice.invoice_pdf
            )
            for invoice in invoices.data
        ]

    except Exception as e:
        logger.error(f"Invoice retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve invoices"
        )

# Helper functions
async def _calculate_payment_amount(items: List[Dict[str, Any]], db: Session) -> Decimal:
    """Calculate total payment amount"""
    total = Decimal('0.00')

    for item in items:
        item_type = item.get("type")
        item_id = item.get("id")

        if item_type == "course":
            # Get course price from database
            # Implementation depends on your course model
            pass
        elif item_type == "premium_feature":
            # Get feature price
            pass

    return total

async def _get_or_create_stripe_customer(user: User, db: Session) -> str:
    """Get or create Stripe customer"""
    if user.stripe_customer_id:
        return user.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email,
        name=f"{user.first_name} {user.last_name}",
        metadata={"user_id": str(user.id)}
    )

    user.stripe_customer_id = customer.id
    db.commit()

    return customer.id

async def _handle_subscription_updated(data: Dict[str, Any], db: Session):
    """Handle subscription updated webhook"""
    subscription_id = data.get("id")
    status = data.get("status")

    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()

    if subscription:
        subscription.status = status
        subscription.current_period_start = datetime.fromtimestamp(data["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(data["current_period_end"])
        subscription.cancel_at_period_end = data.get("cancel_at_period_end", False)
        db.commit()

async def _handle_subscription_cancelled(data: Dict[str, Any], db: Session):
    """Handle subscription cancelled webhook"""
    subscription_id = data.get("id")

    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()

    if subscription:
        subscription.status = "cancelled"
        db.commit()

async def _handle_payment_succeeded(data: Dict[str, Any], db: Session):
    """Handle successful payment webhook"""
    # Update payment status, grant access, etc.
    pass

async def _handle_payment_failed(data: Dict[str, Any], db: Session):
    """Handle failed payment webhook"""
    # Handle failed payment, notify user, etc.
    pass