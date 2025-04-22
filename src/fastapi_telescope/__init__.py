import os

from fastapi import APIRouter
from starlette import status

from .app.log_http_request import router as requests_router
from .app.log_db_queries import router as query_router
from .app.dashboard import router as dashboard_router
from .middleware import TelescopeMiddleware


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

# create constant with full path to components
TELESCOPE_COMPONENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "app/dashboard/templates/components")

__all__ = ['router', 'TELESCOPE_COMPONENTS_DIR', 'TelescopeMiddleware']