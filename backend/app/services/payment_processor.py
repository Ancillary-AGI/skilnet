"""
Payment processor service for EduVerse platform
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.subscription import Payment, PaymentStatus

class PaymentProcessor:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_payment(self, payment: Payment) -> Payment:
        """Save payment record"""
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def update_payment_status(self, external_payment_id: str, status: PaymentStatus) -> bool:
        """Update payment status"""
        result = await self.db.execute(
            select(Payment).where(Payment.external_payment_id == external_payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = status
            await self.db.commit()
            return True
        return False
    
    async def update_payment(self, payment: Payment) -> Payment:
        """Update payment"""
        await self.db.commit()
        await self.db.refresh(payment)
        return payment