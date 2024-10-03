from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)


class ProjectDB(ProjectBase):
    full_amount: PositiveInt
    id: int
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: Optional[datetime] = datetime.now()
    close_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class ProjectCreate(ProjectBase):
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
    )
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[PositiveInt] = None

    class Config:
        extra = Extra.forbid
