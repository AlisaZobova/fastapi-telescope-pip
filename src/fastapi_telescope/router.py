from fastapi import APIRouter
from starlette import status

from .app.log_http_request import router as requests_router
from .app.log_db_queries import router as query_router
from .app.dashboard import router as dashboard_router


router = APIRouter(
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'message': 'Unauthorized',
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'message': 'Something went wrong',
        },
    },
    prefix='/api/telescope',
)


router.include_router(requests_router, tags=['Telescope Requests'], prefix='/http-requests')
router.include_router(query_router, tags=['Telescope DB Queries'], prefix='/db-queries')
router.include_router(dashboard_router, tags=['Telescope Dashboard'], prefix='/dashboard')


__all__ = ['router']