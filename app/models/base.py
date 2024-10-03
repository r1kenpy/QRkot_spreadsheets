from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base


class AbstractModelForInvest(Base):
    __abstract__ = True
    __table_args__ = (
        CheckConstraint('full_amount >= 0'),
        CheckConstraint('0 <= invested_amount <= full_amount'),
    )

    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    def __repr__(self):
        return (
            f'{self.invested_amount=}; '
            f'{self.full_amount=}; '
            f'{self.fully_invested=}; '
            f'{self.create_date=}; '
            f'{self.close_date=}.'
        )
