"""
Pydantic schemas for subscription management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    description: str
    tier: str
    price: float
    currency: str
    billing_cycle: str
    features: List[str]
    max_devices: int
    storage_gb: int
    includes_ai: bool
    includes_vr: bool
    is_popular: bool

class SubscriptionResponse(BaseModel):
    id: str
    plan: SubscriptionPlanResponse
    is_active: bool
    features: List[str]
    current_period_start: datetime
    current_period_end: Optional[datetime]
    trial_ends_at: Optional[datetime]
    cancelled_at: Optional[datetime]

class SubscriptionCreate(BaseModel):
    plan_id: str = Field(..., description="The ID of the subscription plan")

class SubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None
