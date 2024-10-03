from typing import Generic, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.models import CharityProject, User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, obj_id: int, session: AsyncSession
    ) -> Optional[ModelType]:
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )

        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession) -> list[ModelType]:
        db_all_projects = await session.execute(select(self.model))
        return db_all_projects.scalars().all()

    async def create(
        self,
        session: AsyncSession,
        obj_data: CreateSchemaType,
        user: Optional[User] = None,
        commit_in_db: bool = True,
    ) -> ModelType:
        obj_in_data = obj_data.dict(exclude_none=True)
        if user is not None:
            obj_in_data['user_id'] = user.id
        obj_in_data['invested_amount'] = 0
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if commit_in_db:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, db_obj, obj_in
    ) -> CharityProject:
        obj_data = jsonable_encoder(db_obj)
        update_obj_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_obj_data:
                setattr(db_obj, field, update_obj_data[field])

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(self, session: AsyncSession, db_obj) -> CharityProject:
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_all_not_fully_invested_objects(
        self, session: AsyncSession
    ) -> list[ModelType]:
        return (
            (
                await session.execute(
                    select(self.model).where(
                        self.model.fully_invested == false()
                    )
                )
            )
            .scalars()
            .all()
        )
