"""
Subscription repository for EduVerse platform
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.subscription import Subscription, Payment, Invoice

class SubscriptionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, subscription: Subscription) -> Subscription:
        """Create new subscription"""
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription
    
    async def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's active subscription"""
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def update(self, subscription: Subscription) -> Subscription:
        """Update subscription"""
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription
    
    async def get_user_invoices(self, user_id: str) -> List[Invoice]:
        """Get user's invoices"""
        result = await self.db.execute(
            select(Invoice).where(Invoice.user_id == user_id)
        )
        return result.scalars().all()