from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationUser
from app.services.investing import investing

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    all_danations = await donation_crud.get_multi(session)
    return all_danations


@router.post(
    '/', response_model=DonationUser, response_model_exclude_none=True
)
async def create_donation(
    donation_obj: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation = await donation_crud.create(
        session=session, obj_data=donation_obj, user=user, commit_in_db=False
    )

    session.add_all(
        investing(
            donation,
            await project_crud.get_all_not_fully_invested_objects(
                session=session
            ),
        )
    )
    await session.commit()
    await session.refresh(donation)
    return donation


@router.get(
    '/my',
    response_model=list[DonationUser],
    response_model_exclude_none=True,
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    db_donations = await donation_crud.get_user_donations(
        session=session, user=user
    )
    return db_donations
