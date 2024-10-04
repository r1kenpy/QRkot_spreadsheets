def create_rows_projects_for_table(projects) -> list[list[str]]:
    return [
        [
            project.name,
            str(project.close_date - project.create_date).split('.')[0],
            project.description,
        ]
        for project in projects
    ]
