from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User
from app.schemas.donation import DonationCreate, DonationDB


class CRUDDonation(CRUDBase[Donation, DonationCreate, DonationDB]):

    async def get_user_donations(
        self, session: AsyncSession, user: User
    ) -> list[DonationDB]:
        obj_in_db = await session.execute(
            select(self.model).where(self.model.user_id == user.id)
        )
        return obj_in_db.scalars().all()


donation_crud = CRUDDonation(Donation)
