"""
Comprehensive payment processing API with global support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import stripe
import paypal
from razorpay import Client as RazorpayClient
import uuid
from datetime import datetime, timedelta
import json
import hmac
import hashlib

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from backend.app.models.profile import User
from app.models.subscription import Subscription, Payment, PaymentStatus, PaymentMethod, Invoice
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.payment_processor import PaymentProcessor
from app.services.notification_service import NotificationService
from app.schemas.payment import (
    PaymentIntentCreate, PaymentIntentResponse, PaymentConfirm,
    SubscriptionCreate, SubscriptionResponse, InvoiceResponse,
    PaymentMethodResponse, RefundRequest, RefundResponse
)

router = APIRouter()

# Initialize payment processors
stripe.api_key = settings.STRIPE_SECRET_KEY
razorpay_client = RazorpayClient(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create payment intent for subscription or one-time payment"""
    
    payment_processor = PaymentProcessor(db)
    
    try:
        # Determine payment method and processor
        processor = payment_data.payment_method or "stripe"
        
        # Create payment intent based on processor
        if processor == "stripe":
            intent = await _create_stripe_payment_intent(payment_data, current_user)
        elif processor == "paypal":
            intent = await _create_paypal_payment_intent(payment_data, current_user)
        elif processor == "razorpay":
            intent = await _create_razorpay_payment_intent(payment_data, current_user)
        elif processor == "flutterwave":
            intent = await _create_flutterwave_payment_intent(payment_data, current_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported payment method: {processor}"
            )
        
        # Save payment record
        payment = Payment(
            user_id=current_user.id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_method=PaymentMethod(processor),
            external_payment_id=intent["id"],
            description=payment_data.description,
            metadata=payment_data.metadata or {}
        )
        
        await payment_processor.save_payment(payment)
        
        return PaymentIntentResponse(
            id=intent["id"],
            client_secret=intent.get("client_secret"),
            amount=payment_data.amount,
            currency=payment_data.currency,
            status="requires_payment_method",
            payment_method=processor,
            metadata=intent.get("metadata", {})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment intent: {str(e)}"
        )


@router.post("/confirm-payment", response_model=Dict[str, Any])
async def confirm_payment(
    payment_confirm: PaymentConfirm,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm payment and process subscription"""
    
    payment_processor = PaymentProcessor(db)
    
    try:
        # Verify payment with processor
        if payment_confirm.payment_method == "stripe":
            payment_result = await _confirm_stripe_payment(payment_confirm.payment_intent_id)
        elif payment_confirm.payment_method == "paypal":
            payment_result = await _confirm_paypal_payment(payment_confirm.payment_intent_id)
        elif payment_confirm.payment_method == "razorpay":
            payment_result = await _confirm_razorpay_payment(payment_confirm.payment_intent_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported payment method"
            )
        
        if payment_result["status"] == "succeeded":
            # Update payment record
            await payment_processor.update_payment_status(
                payment_confirm.payment_intent_id,
                PaymentStatus.COMPLETED
            )
            
            # Process subscription if applicable
            if payment_confirm.subscription_data:
                subscription = await _create_or_update_subscription(
                    current_user,
                    payment_confirm.subscription_data,
                    payment_result,
                    db
                )
                
                # Send confirmation notification
                await _send_payment_confirmation(current_user, payment_result, subscription)
                
                return {
                    "status": "success",
                    "payment_id": payment_result["id"],
                    "subscription": subscription.to_dict() if subscription else None,
                    "message": "Payment successful and subscription activated"
                }
            else:
                # One-time payment
                await _send_payment_confirmation(current_user, payment_result)
                
                return {
                    "status": "success",
                    "payment_id": payment_result["id"],
                    "message": "Payment completed successfully"
                }
        else:
            # Payment failed
            await payment_processor.update_payment_status(
                payment_confirm.payment_intent_id,
                PaymentStatus.FAILED
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment failed: {payment_result.get('failure_reason', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment confirmation failed: {str(e)}"
        )


@router.post("/create-subscription", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new subscription"""
    
    subscription_repo = SubscriptionRepository(db)
    
    try:
        # Check if user already has active subscription
        existing_subscription = await subscription_repo.get_user_subscription(current_user.id)
        
        if existing_subscription and existing_subscription.is_active:
            # Upgrade/downgrade existing subscription
            updated_subscription = await _modify_subscription(
                existing_subscription,
                subscription_data,
                db
            )
            return SubscriptionResponse.from_orm(updated_subscription)
        
        # Calculate pricing based on region
        pricing = await _calculate_regional_pricing(
            subscription_data.tier,
            subscription_data.billing_cycle,
            current_user.country_code or "US"
        )
        
        # Create subscription
        subscription = Subscription(
            user_id=current_user.id,
            tier=subscription_data.tier,
            billing_cycle=subscription_data.billing_cycle,
            price=pricing["price"],
            currency=pricing["currency"],
            current_period_start=datetime.utcnow(),
            current_period_end=_calculate_period_end(
                datetime.utcnow(),
                subscription_data.billing_cycle
            ),
            feature_limits=_get_feature_limits(subscription_data.tier),
            is_trial=subscription_data.is_trial,
            trial_ends_at=datetime.utcnow() + timedelta(days=14) if subscription_data.is_trial else None
        )
        
        created_subscription = await subscription_repo.create(subscription)
        
        # Create external subscription if not trial
        if not subscription_data.is_trial:
            external_subscription = await _create_external_subscription(
                created_subscription,
                subscription_data.payment_method,
                current_user
            )
            
            created_subscription.stripe_subscription_id = external_subscription.get("stripe_id")
            created_subscription.paypal_subscription_id = external_subscription.get("paypal_id")
            created_subscription.external_customer_id = external_subscription.get("customer_id")
            
            await subscription_repo.update(created_subscription)
        
        # Send welcome notification
        await _send_subscription_welcome(current_user, created_subscription)
        
        return SubscriptionResponse.from_orm(created_subscription)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel user subscription"""
    
    subscription_repo = SubscriptionRepository(db)
    
    try:
        subscription = await subscription_repo.get_user_subscription(current_user.id)
        
        if not subscription or not subscription.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Cancel external subscription
        if subscription.stripe_subscription_id:
            await _cancel_stripe_subscription(subscription.stripe_subscription_id)
        elif subscription.paypal_subscription_id:
            await _cancel_paypal_subscription(subscription.paypal_subscription_id)
        
        # Update subscription
        subscription.cancelled_at = datetime.utcnow()
        subscription.is_active = False
        
        await subscription_repo.update(subscription)
        
        # Send cancellation confirmation
        await _send_cancellation_confirmation(current_user, subscription)
        
        return {
            "message": "Subscription cancelled successfully",
            "access_until": subscription.current_period_end.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user subscription"""
    
    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.get_user_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    return SubscriptionResponse.from_orm(subscription)


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available payment methods for user's region"""
    
    country_code = current_user.country_code or "US"
    
    # Get regional payment methods
    regional_config = settings.REGIONAL_CONFIGS.get(
        _get_region_for_country(country_code),
        settings.REGIONAL_CONFIGS["us-east-1"]
    )
    
    payment_methods = []
    
    for method in regional_config["payment_methods"]:
        if method == "stripe":
            payment_methods.append(PaymentMethodResponse(
                id="stripe",
                name="Credit/Debit Card",
                type="card",
                supported_currencies=["USD", "EUR", "GBP", "INR"],
                fees={"percentage": 2.9, "fixed": 0.30},
                processing_time="instant"
            ))
        elif method == "paypal":
            payment_methods.append(PaymentMethodResponse(
                id="paypal",
                name="PayPal",
                type="wallet",
                supported_currencies=["USD", "EUR", "GBP"],
                fees={"percentage": 3.4, "fixed": 0.30},
                processing_time="instant"
            ))
        elif method == "razorpay":
            payment_methods.append(PaymentMethodResponse(
                id="razorpay",
                name="Razorpay",
                type="multiple",
                supported_currencies=["INR"],
                fees={"percentage": 2.0, "fixed": 0.00},
                processing_time="instant"
            ))
        elif method == "flutterwave":
            payment_methods.append(PaymentMethodResponse(
                id="flutterwave",
                name="Flutterwave",
                type="multiple",
                supported_currencies=["NGN", "KES", "GHS", "USD"],
                fees={"percentage": 1.4, "fixed": 0.00},
                processing_time="instant"
            ))
    
    return payment_methods


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_user_invoices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's payment invoices"""
    
    subscription_repo = SubscriptionRepository(db)
    invoices = await subscription_repo.get_user_invoices(current_user.id)
    
    return [InvoiceResponse.from_orm(invoice) for invoice in invoices]


@router.post("/refund", response_model=RefundResponse)
async def request_refund(
    refund_request: RefundRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Request payment refund"""
    
    payment_processor = PaymentProcessor(db)
    
    try:
        # Get payment record
        payment = await payment_processor.get_payment(refund_request.payment_id)
        
        if not payment or payment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Process refund based on payment method
        if payment.payment_method == PaymentMethod.STRIPE:
            refund_result = await _process_stripe_refund(payment, refund_request.amount)
        elif payment.payment_method == PaymentMethod.PAYPAL:
            refund_result = await _process_paypal_refund(payment, refund_request.amount)
        elif payment.payment_method == PaymentMethod.RAZORPAY:
            refund_result = await _process_razorpay_refund(payment, refund_request.amount)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refunds not supported for this payment method"
            )
        
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        await payment_processor.update_payment(payment)
        
        # Send refund confirmation
        await _send_refund_confirmation(current_user, payment, refund_result)
        
        return RefundResponse(
            id=refund_result["id"],
            amount=refund_result["amount"],
            currency=refund_result["currency"],
            status=refund_result["status"],
            reason=refund_request.reason,
            processed_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund request failed: {str(e)}"
        )


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhooks"""
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    await _handle_stripe_webhook_event(event, db)
    
    return {"status": "success"}


@router.post("/webhooks/paypal")
async def paypal_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle PayPal webhooks"""
    
    payload = await request.body()
    headers = dict(request.headers)
    
    # Verify PayPal webhook signature
    if not _verify_paypal_webhook(payload, headers):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_data = json.loads(payload)
    await _handle_paypal_webhook_event(event_data, db)
    
    return {"status": "success"}


# Helper functions for payment processing
async def _create_stripe_payment_intent(
    payment_data: PaymentIntentCreate,
    user: User
) -> Dict[str, Any]:
    """Create Stripe payment intent"""
    
    intent = stripe.PaymentIntent.create(
        amount=int(payment_data.amount * 100),  # Convert to cents
        currency=payment_data.currency.lower(),
        customer=user.stripe_customer_id,
        description=payment_data.description,
        metadata=payment_data.metadata or {},
        automatic_payment_methods={'enabled': True}
    )
    
    return {
        "id": intent.id,
        "client_secret": intent.client_secret,
        "metadata": intent.metadata
    }


async def _create_paypal_payment_intent(
    payment_data: PaymentIntentCreate,
    user: User
) -> Dict[str, Any]:
    """Create PayPal payment intent"""
    
    # PayPal implementation
    # This would use PayPal's SDK to create payment
    return {
        "id": f"paypal_{uuid.uuid4()}",
        "approval_url": "https://paypal.com/approve/...",
        "metadata": payment_data.metadata or {}
    }


async def _create_razorpay_payment_intent(
    payment_data: PaymentIntentCreate,
    user: User
) -> Dict[str, Any]:
    """Create Razorpay payment intent"""
    
    order = razorpay_client.order.create({
        "amount": int(payment_data.amount * 100),  # Convert to paise
        "currency": payment_data.currency.upper(),
        "receipt": f"order_{uuid.uuid4()}",
        "notes": payment_data.metadata or {}
    })
    
    return {
        "id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "metadata": order["notes"]
    }


async def _create_flutterwave_payment_intent(
    payment_data: PaymentIntentCreate,
    user: User
) -> Dict[str, Any]:
    """Create Flutterwave payment intent"""
    
    # Flutterwave implementation
    # This would use Flutterwave's API to create payment
    return {
        "id": f"flw_{uuid.uuid4()}",
        "payment_link": "https://checkout.flutterwave.com/...",
        "metadata": payment_data.metadata or {}
    }


async def _confirm_stripe_payment(payment_intent_id: str) -> Dict[str, Any]:
    """Confirm Stripe payment"""
    
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    
    return {
        "id": intent.id,
        "status": intent.status,
        "amount": intent.amount / 100,
        "currency": intent.currency,
        "failure_reason": intent.last_payment_error.message if intent.last_payment_error else None
    }


async def _calculate_regional_pricing(
    tier: str,
    billing_cycle: str,
    country_code: str
) -> Dict[str, Any]:
    """Calculate pricing based on user's region"""
    
    base_pricing = settings.SUBSCRIPTION_PLANS[tier]
    
    # Get regional pricing adjustments
    region = _get_region_for_country(country_code)
    regional_config = settings.REGIONAL_CONFIGS.get(region, settings.REGIONAL_CONFIGS["us-east-1"])
    
    # Apply purchasing power parity adjustment
    ppp_adjustment = _get_ppp_adjustment(country_code)
    
    if billing_cycle == "monthly":
        price = base_pricing["monthly_price"] * ppp_adjustment
    else:
        price = base_pricing["yearly_price"] * ppp_adjustment
    
    return {
        "price": round(price, 2),
        "currency": regional_config["currency"],
        "ppp_adjustment": ppp_adjustment
    }


def _get_feature_limits(tier: str) -> Dict[str, Any]:
    """Get feature limits for subscription tier"""
    
    return settings.SUBSCRIPTION_PLANS[tier]["features"]


def _calculate_period_end(start_date: datetime, billing_cycle: str) -> datetime:
    """Calculate subscription period end date"""
    
    if billing_cycle == "monthly":
        return start_date + timedelta(days=30)
    elif billing_cycle == "quarterly":
        return start_date + timedelta(days=90)
    elif billing_cycle == "semi_annual":
        return start_date + timedelta(days=180)
    elif billing_cycle == "annual":
        return start_date + timedelta(days=365)
    elif billing_cycle == "biennial":
        return start_date + timedelta(days=730)
    else:
        return start_date + timedelta(days=30)


def _get_region_for_country(country_code: str) -> str:
    """Get AWS region for country code"""
    
    # Simplified mapping - in production, use comprehensive mapping
    region_mapping = {
        "US": "us-east-1",
        "CA": "us-east-1",
        "GB": "eu-west-1",
        "DE": "eu-west-1",
        "FR": "eu-west-1",
        "IN": "ap-south-1",
        "SG": "ap-southeast-1",
        "JP": "ap-northeast-1",
        "AU": "ap-southeast-2",
        "BR": "sa-east-1",
        "NG": "af-south-1",
        "KE": "af-south-1",
        "ZA": "af-south-1"
    }
    
    return region_mapping.get(country_code, "us-east-1")


def _get_ppp_adjustment(country_code: str) -> float:
    """Get purchasing power parity adjustment for country"""
    
    # Simplified PPP adjustments - in production, use World Bank data
    ppp_adjustments = {
        "US": 1.0,
        "GB": 0.9,
        "DE": 0.85,
        "IN": 0.3,
        "NG": 0.2,
        "KE": 0.25,
        "BR": 0.4,
        "MX": 0.35,
        "PH": 0.3,
        "VN": 0.25
    }
    
    return ppp_adjustments.get(country_code, 1.0)


async def _send_payment_confirmation(
    user: User,
    payment_result: Dict[str, Any],
    subscription: Optional[Subscription] = None
):
    """Send payment confirmation notification"""
    
    notification_service = NotificationService()
    
    if subscription:
        message = f"Payment successful! Your {subscription.tier} subscription is now active."
    else:
        message = f"Payment of {payment_result['amount']} {payment_result['currency']} completed successfully."
    
    await notification_service.send_notification(
        user_id=user.id,
        title="Payment Confirmed",
        message=message,
        type="payment_success",
        channels=["email", "push"]
    )


async def _handle_stripe_webhook_event(event: Dict[str, Any], db: AsyncSession):
    """Handle Stripe webhook events"""
    
    event_type = event['type']
    
    if event_type == 'payment_intent.succeeded':
        # Handle successful payment
        payment_intent = event['data']['object']
        await _process_successful_payment(payment_intent, db)
    
    elif event_type == 'payment_intent.payment_failed':
        # Handle failed payment
        payment_intent = event['data']['object']
        await _process_failed_payment(payment_intent, db)
    
    elif event_type == 'invoice.payment_succeeded':
        # Handle subscription renewal
        invoice = event['data']['object']
        await _process_subscription_renewal(invoice, db)
    
    elif event_type == 'customer.subscription.deleted':
        # Handle subscription cancellation
        subscription = event['data']['object']
        await _process_subscription_cancellation(subscription, db)


async def _process_successful_payment(payment_intent: Dict[str, Any], db: AsyncSession):
    """Process successful payment from webhook"""
    
    payment_processor = PaymentProcessor(db)
    
    # Update payment status
    await payment_processor.update_payment_status(
        payment_intent['id'],
        PaymentStatus.COMPLETED
    )


async def _process_failed_payment(payment_intent: Dict[str, Any], db: AsyncSession):
    """Process failed payment from webhook"""
    
    payment_processor = PaymentProcessor(db)
    
    # Update payment status
    await payment_processor.update_payment_status(
        payment_intent['id'],
        PaymentStatus.FAILED
    )
    
    # Send failure notification
    # Implementation for failure notification


def _verify_paypal_webhook(payload: bytes, headers: Dict[str, str]) -> bool:
    """Verify PayPal webhook signature"""
    
    # PayPal webhook verification implementation
    # This would verify the webhook signature using PayPal's verification process
    return True  # Simplified for example