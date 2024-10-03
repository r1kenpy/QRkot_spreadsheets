from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.services.google_api import (spreadsheets_create,
                                     spreadsheets_update_value)

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service),
) -> dict[str, str]:
    """Только для суперюзеров."""
    projects = await project_crud.get_projects_by_completion_rate(session)
    spreadsheetId = await spreadsheets_create(wrapper_services)
    await spreadsheets_update_value(spreadsheetId, projects, wrapper_services)
    return {
        'messages': (
            f'Отчет успешно сформирован и доступен по ссылке: '
            f'https://docs.google.com/spreadsheets/d/{spreadsheetId}'
        )
    }
