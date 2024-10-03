from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationBase(BaseModel):
    id: int
    create_date: datetime


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None

    class Config:
        extra = Extra.forbid


class DonationUser(DonationBase, DonationCreate):
    class Config:
        orm_mode = True


class DonationDB(DonationBase, DonationCreate):
    user_id: int
    invested_amount: int = 0
    fully_invested: bool
    close_date: Optional[datetime] = None

    class Config:
        orm_mode = True
