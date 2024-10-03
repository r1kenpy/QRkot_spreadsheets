from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import AbstractModelForInvest


class Donation(AbstractModelForInvest):
    user_id = Column(
        Integer, ForeignKey('user.id', name='fk_donation_user_id_user')
    )
    comment = Column(Text, nullable=True)

    def __repr__(self):
        return f'{self.user_id=} {self.comment=} {super().__repr__()}'
