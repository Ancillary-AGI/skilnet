"""
Payment Processor Service for EduVerse

Handles payment processing using Stripe for course purchases and subscriptions
"""

import stripe
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from app.core.config import settings
from app.core.logging import get_logger, log_performance


class PaymentProcessor:
    """Stripe payment processing service"""

    def __init__(self):
        self.logger = get_logger("payment_processor")
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        else:
            self.logger.warning("Stripe secret key not configured")

    @log_performance
    async def create_payment_intent(
        self,
        amount: int,  # Amount in cents
        currency: str = "usd",
        course_id: str = None,
        user_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a Stripe payment intent for course purchase"""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency,
                "payment_method_types": ["card"],
                "metadata": {
                    "course_id": course_id,
                    "user_id": user_id,
                    **(metadata or {})
                }
            }

            intent = stripe.PaymentIntent.create(**intent_data)

            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe payment intent creation failed: {e}")
            raise Exception(f"Payment processing failed: {str(e)}")

    @log_performance
    async def create_subscription(
        self,
        customer_email: str,
        price_id: str,
        user_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a Stripe subscription for premium access"""
        try:
            # Create or retrieve customer
            customer = self._get_or_create_customer(customer_email, user_id)

            subscription_data = {
                "customer": customer.id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"],
                "metadata": {
                    "user_id": user_id,
                    **(metadata or {})
                }
            }

            subscription = stripe.Subscription.create(**subscription_data)

            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe subscription creation failed: {e}")
            raise Exception(f"Subscription creation failed: {str(e)}")

    @log_performance
    async def process_refund(
        self,
        payment_intent_id: str,
        amount: int = None,  # Amount in cents, None for full refund
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """Process a refund for a payment"""
        try:
            refund_data = {
                "payment_intent": payment_intent_id,
                "reason": reason
            }

            if amount:
                refund_data["amount"] = amount

            refund = stripe.Refund.create(**refund_data)

            return {
                "refund_id": refund.id,
                "amount": refund.amount,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe refund failed: {e}")
            raise Exception(f"Refund processing failed: {str(e)}")

    @log_performance
    async def create_customer_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> str:
        """Create a customer portal session for subscription management"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )

            return session.url

        except stripe.error.StripeError as e:
            self.logger.error(f"Customer portal session creation failed: {e}")
            raise Exception(f"Portal session creation failed: {str(e)}")

    @log_performance
    async def get_payment_methods(
        self,
        customer_id: str
    ) -> List[Dict[str, Any]]:
        """Get customer's saved payment methods"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )

            return [{
                "id": pm.id,
                "type": pm.type,
                "card": {
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year
                } if pm.card else None
            } for pm in payment_methods.data]

        except stripe.error.StripeError as e:
            self.logger.error(f"Failed to get payment methods: {e}")
            return []

    @log_performance
    async def create_setup_intent(
        self,
        customer_id: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a setup intent for saving payment methods"""
        try:
            intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
                metadata=metadata or {}
            )

            return {
                "setup_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Setup intent creation failed: {e}")
            raise Exception(f"Setup intent creation failed: {str(e)}")

    @log_performance
    async def handle_webhook_event(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )

            # Process different event types
            event_data = {
                "event_id": event.id,
                "event_type": event.type,
                "data": event.data.object
            }

            # Handle specific events
            if event.type == "payment_intent.succeeded":
                await self._handle_payment_success(event.data.object)
            elif event.type == "payment_intent.payment_failed":
                await self._handle_payment_failure(event.data.object)
            elif event.type == "customer.subscription.created":
                await self._handle_subscription_created(event.data.object)
            elif event.type == "customer.subscription.updated":
                await self._handle_subscription_updated(event.data.object)
            elif event.type == "customer.subscription.deleted":
                await self._handle_subscription_cancelled(event.data.object)

            return event_data

        except stripe.error.SignatureVerificationError as e:
            self.logger.error(f"Webhook signature verification failed: {e}")
            raise Exception("Invalid webhook signature")
        except Exception as e:
            self.logger.error(f"Webhook processing failed: {e}")
            raise Exception(f"Webhook processing failed: {str(e)}")

    def _get_or_create_customer(self, email: str, user_id: str = None) -> stripe.Customer:
        """Get existing customer or create new one"""
        try:
            # Try to find existing customer
            customers = stripe.Customer.list(email=email, limit=1)
            if customers.data:
                return customers.data[0]

            # Create new customer
            customer_data = {
                "email": email,
                "metadata": {}
            }

            if user_id:
                customer_data["metadata"]["user_id"] = user_id

            return stripe.Customer.create(**customer_data)

        except stripe.error.StripeError as e:
            self.logger.error(f"Customer creation/retrieval failed: {e}")
            raise

    async def _handle_payment_success(self, payment_intent: Dict[str, Any]):
        """Handle successful payment"""
        self.logger.info(f"Payment succeeded: {payment_intent.get('id')}")
        # TODO: Update database with payment success
        # TODO: Grant course access to user
        # TODO: Send confirmation email

    async def _handle_payment_failure(self, payment_intent: Dict[str, Any]):
        """Handle failed payment"""
        self.logger.warning(f"Payment failed: {payment_intent.get('id')}")
        # TODO: Log payment failure
        # TODO: Notify user of failure

    async def _handle_subscription_created(self, subscription: Dict[str, Any]):
        """Handle subscription creation"""
        self.logger.info(f"Subscription created: {subscription.get('id')}")
        # TODO: Update user subscription status
        # TODO: Grant premium access

    async def _handle_subscription_updated(self, subscription: Dict[str, Any]):
        """Handle subscription updates"""
        self.logger.info(f"Subscription updated: {subscription.get('id')}")
        # TODO: Update subscription details in database

    async def _handle_subscription_cancelled(self, subscription: Dict[str, Any]):
        """Handle subscription cancellation"""
        self.logger.info(f"Subscription cancelled: {subscription.get('id')}")
        # TODO: Update user subscription status
        # TODO: Revoke premium access if needed

    @log_performance
    async def get_subscription_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans"""
        try:
            # This would typically fetch from your database or Stripe products
            # For now, return sample plans
            return [
                {
                    "id": "premium_monthly",
                    "name": "Premium Monthly",
                    "price": 2999,  # $29.99
                    "currency": "usd",
                    "interval": "month",
                    "features": [
                        "Unlimited course access",
                        "Download course materials",
                        "Certificate of completion",
                        "Priority support"
                    ]
                },
                {
                    "id": "premium_yearly",
                    "name": "Premium Yearly",
                    "price": 29999,  # $299.99
                    "currency": "usd",
                    "interval": "year",
                    "features": [
                        "All monthly features",
                        "Save 17% annually",
                        "Early access to new courses",
                        "Exclusive webinars"
                    ]
                }
            ]

        except Exception as e:
            self.logger.error(f"Failed to get subscription plans: {e}")
            return []

    @log_performance
    async def calculate_pricing(
        self,
        course_price: float,
        currency: str = "usd",
        apply_discount: bool = False,
        discount_percent: int = 0
    ) -> Dict[str, Any]:
        """Calculate pricing with taxes and discounts"""
        try:
            base_price = course_price
            discount_amount = 0
            tax_amount = 0

            if apply_discount and discount_percent > 0:
                discount_amount = base_price * (discount_percent / 100)
                base_price -= discount_amount

            # Calculate tax (simplified - in production, use tax service)
            if currency == "usd":
                tax_rate = 0.08  # 8% tax
                tax_amount = base_price * tax_rate

            total = base_price + tax_amount

            return {
                "original_price": course_price,
                "discount_amount": discount_amount,
                "discounted_price": base_price,
                "tax_amount": tax_amount,
                "total": total,
                "currency": currency,
                "tax_rate": tax_rate if currency == "usd" else 0
            }

        except Exception as e:
            self.logger.error(f"Pricing calculation failed: {e}")
            return {
                "original_price": course_price,
                "discount_amount": 0,
                "discounted_price": course_price,
                "tax_amount": 0,
                "total": course_price,
                "currency": currency,
                "tax_rate": 0
            }


# Global instance
payment_processor = PaymentProcessor()
