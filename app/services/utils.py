def create_rows_projects_for_table(projects) -> list[list[str]]:
    rows = []

    for project in projects:
        rows.append(
            [
                project.name,
                project.description,
                str(project.close_date - project.create_date).split('.')[0],
            ]
        )
    return rows
