from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

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
    'Нельзя записать в табилцу {len_table_values} строк. Максимум {max_rows}.'
)
MORE_COLUMNS_ERROR = (
    'Нельзя записать в табилцу {len_table_column} колонок. '
    'Максимум {max_columns}.'
)


async def spreadsheets_create(
    wrapper_services: Aiogoogle, body_table=SPREADSHEET_BODY
) -> tuple[str, str]:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = deepcopy(body_table)
    spreadsheet_body['properties']['title'] = spreadsheet_body['properties'][
        'title'
    ].format(now_date_time=now_date_time)

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
    table_header = deepcopy(TABLE_HEADER)
    table_header[0][1] = datetime.now().strftime(FORMAT)
    table_values = [
        *[*table_header],
        *[list(map(str, row)) for row in rows],
    ]
    len_rows_table = len(table_values)
    max_len_table_column = max(map(len, table_values))
    if len_rows_table > ROW_COUNT:
        raise ValueError(
            MORE_ROWS_ERROR.format(
                len_table_values=len_rows_table, max_rows=ROW_COUNT
            ),
        )
    if max_len_table_column > COLUMN_COUNT:
        raise ValueError(
            MORE_COLUMNS_ERROR.format(
                len_table_column=max_len_table_column,
                max_columns=COLUMN_COUNT,
            ),
        )
    update_body = {'majorDimension': 'ROWS', 'values': table_values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{len_rows_table}C{max_len_table_column}',
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )
