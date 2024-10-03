from typing import Optional

from sqlalchemy import extract, false, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import ProjectCreate, ProjectDB


class CRUDProject(CRUDBase[CharityProject, ProjectCreate, ProjectDB]):

    async def get_project_by_name(
        self, session: AsyncSession, project_name
    ) -> Optional[CharityProject]:
        project_id = await session.execute(
            select(self.model.id).where(self.model.name == project_name)
        )
        project_id = project_id.scalars().first()
        return project_id

    async def get_all_projects_for_invest(self, session: AsyncSession):
        projects_for_invest = await session.execute(
            select(self.model).where(self.model.fully_invested == false())
        )
        return projects_for_invest.scalars().all()

    async def get_projects_by_completion_rate(self, session: AsyncSession):

        projects = await session.execute(
            select(self.model)
            .options(
                load_only(
                    self.model.name,
                    self.model.description,
                    self.model.create_date,
                    self.model.close_date,
                )
            )
            .where(self.model.fully_invested == true())
            .order_by(
                extract('epoch', self.model.close_date) -
                extract('epoch', self.model.create_date)
            ),
        )
        return projects.scalars().all()


project_crud = CRUDProject(CharityProject)
