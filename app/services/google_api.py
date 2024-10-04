from datetime import datetime

from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.config import settings
from app.services.utils import create_rows_projects_for_table

FORMAT = '%Y/%m/%d %H:%M:%S'

ROW_COUNT = 100
COLUMN_COUNT = 3

TABLE_HEADER = [
    ['Отчет от', 'now_date_time'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]
SPREADSHEET_BODY = dict(
    properties=dict(
        title='Отчёт по длительности сбора средств на {now_date_time}',
        locale='ru_RU',
    ),
    sheets=[
        dict(
            properties=dict(
                sheetType='GRID',
                sheetId=0,
                title='Лист1',
                gridProperties=dict(
                    rowCount=ROW_COUNT,
                    columnCount=COLUMN_COUNT,
                ),
            )
        )
    ],
)

MORE_ROWS_ERROR = (
    'Попытка записать в табилцу {len_table_values} строк. '
    'Таблица может вместить не больше {ROW_COUNT} строк'
)
MORE_COLUMNS_ERROR = (
    'Попытка записать в табилцу {len_table_column} колонок. '
    'Таблица может вместить не больше {COLUMN_COUNT} колонок'
)


async def spreadsheets_create(
    wrapper_services: Aiogoogle, body_table=SPREADSHEET_BODY
) -> tuple[str, str]:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    copy_body_table = body_table.copy()
    copy_body_table['properties']['title'] = copy_body_table['properties'][
        'title'
    ].format(now_date_time=now_date_time)
    spreadsheet_body = copy_body_table

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )

    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
    spreadsheet_id: str, wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id, json=permissions_body, fields='id'
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str, projects: list, wrapper_services: Aiogoogle
) -> None:
    rows = create_rows_projects_for_table(projects)
    service = await wrapper_services.discover('sheets', 'v4')
    table_header = TABLE_HEADER.copy()
    table_header[0][1] = datetime.now().strftime(FORMAT)
    table_values = [
        *[*table_header],
        *[list(map(str, row)) for row in rows],
    ]
    if len(table_values) > ROW_COUNT:
        raise HTTPException(
            status_code=400,
            detail=MORE_ROWS_ERROR.format(
                ROW_COUNT=ROW_COUNT, len_table_values=len(table_values)
            ),
        )
    for row in table_values:
        if len(row) > 3:
            raise HTTPException(
                status_code=400,
                detail=MORE_COLUMNS_ERROR.format(
                    len_table_column=len(row), COLUMN_COUNT=COLUMN_COUNT
                ),
            )
    update_body = {'majorDimension': 'ROWS', 'values': table_values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{ROW_COUNT}C{COLUMN_COUNT}',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
