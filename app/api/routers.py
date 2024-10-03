from fastapi import APIRouter

from app.api.endpoints import (donation_router, google_api_router,
                               project_router, user_router)

main_router = APIRouter()
main_router.include_router(
    project_router, tags=['projects'], prefix='/charity_project'
)
main_router.include_router(
    donation_router, tags=['donations'], prefix='/donation'
)
main_router.include_router(
    google_api_router, prefix='/google', tags=['Google']
)
main_router.include_router(user_router)
