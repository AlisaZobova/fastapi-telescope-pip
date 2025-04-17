from fastapi import APIRouter
from starlette import status

from telescope.app.log_http_request import router as requests_router
from telescope.app.log_db_queries import router as query_router


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

__all__ = ['router']