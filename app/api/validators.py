from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import project_crud

PROJECT_ALREADY_EXISTS = 'Такой проект уже существует'
NO_SUCH_PROJECT = 'Такого проекта не существует'
CANT_DELETE_PROJECT = (
    'Нельзя удалять закрытый проект или проект, '
    'в который уже были инвестированы средства.'
)
CANNOT_UPDATE_CLOSED_PROJECT = 'Нельзя обновить закрытый проект'
AMOUNT_CANNOT_BE_LESS_PAID = 'Сумма сбора не может быть меньше уже внесенной'


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    project = await project_crud.get_project_by_name(
        session=session, project_name=project_name
    )
    if project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_ALREADY_EXISTS,
        )


async def check_project_exists(project_id: int, session: AsyncSession) -> None:
    project = await project_crud.get(obj_id=project_id, session=session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=NO_SUCH_PROJECT,
        )


async def check_investment_or_closed_project(
    project_id: int,
    session: AsyncSession,
) -> None:
    project = await project_crud.get(obj_id=project_id, session=session)
    if project.invested_amount > 0 or project.close_date is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=CANT_DELETE_PROJECT,
        )


async def check_project_closed(project_id: int, session: AsyncSession) -> None:
    project = await project_crud.get(obj_id=project_id, session=session)
    if project.close_date is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=CANNOT_UPDATE_CLOSED_PROJECT,
        )


async def check_investment_sum(
    project_id: int, session: AsyncSession, obj_data
) -> None:
    project = await project_crud.get(obj_id=project_id, session=session)
    if project.invested_amount > obj_data:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=AMOUNT_CANNOT_BE_LESS_PAID,
        )
