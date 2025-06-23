# FAST API TELESCOPE

This is a FastAPI middleware with UI dashboard for monitoring and debugging your FastAPI applications. It provides a set of tools to help you visualize and analyze the performance of your API endpoints, including request/response times, error rates, and more.

## Requirements
- FastAPI
- PostgreSQL
- SQLAlchemy

## Setup

1. Install the package using pip.
2. Create main.py file with a FastAPI application, include the middleware and mount components like this:
```python
from dotenv import load_dotenv

load_dotenv()

from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_telescope import TelescopeMiddleware
from fastapi_telescope import TELESCOPE_COMPONENTS_DIR
from fastapi_pagination import add_pagination
from .router import router

app = FastAPI()

app.add_middleware(TelescopeMiddleware)  # add telescope middleware

app.include_router(router) # optionally add admin auth dependency here

add_pagination(app)  # add pagination to your app

app.mount("/components", StaticFiles(directory=TELESCOPE_COMPONENTS_DIR),
          name="components")  # mount Vue components directory


@app.exception_handler(Exception)  # global exception handler, you can add your own
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'message': 'An unexpected error occurred'},
    )


if __name__ == '__main__':
    uvicorn.run(
        'main.cmd.main:app', host='0.0.0.0', port=8000, reload=True
    )  # use for debugging
```
3. Create router.py file and include the Telescope router and optionally add the authenticated user ID in requests using custom dependency like this:
```python
from starlette.requests import Request
from fastapi import APIRouter, Depends
from fastapi_telescope import router as telescope_router

async def get_user_id(
    request: Request,
) -> str:
    user_id = '111' # this is just an example, you can get user id from your auth system
    request.state.user_id = user_id # this user_id will be used in logs
    return user_id

router = APIRouter(dependencies=[Depends(get_user_id)])
router.include_router(telescope_router)

__all__ = ['router']
```
4. Add creds (DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME) to POSTGRES db, SITE_URL (f.e. http://localhost:8000) and API_PREFIX (f.e. '/api') to your .env file.
5. To allow middleware use hooks to intercept database calls and log them, use the session maker from the package to create an asynchronous session:
```python
from fastapi_telescope.db import get_async_sessionmaker
from typing import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

async def get_async_session(
    sessionmaker: Callable[..., AsyncSession] = Depends(get_async_sessionmaker),
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session
```
6. Add migration with such methods to your migrations folder and run it (or you can use raw sql query for your db).
```python
def upgrade():
    op.create_table('log_http_requests',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('level', sa.String(), nullable=False),
                    sa.Column('request_method', sa.String(), nullable=False),
                    sa.Column('request_url', sa.String(), nullable=False),
                    sa.Column('path_params', sa.String(), nullable=False),
                    sa.Column('query_params', sa.String(), nullable=False),
                    sa.Column('headers', sa.String(), nullable=False),
                    sa.Column('request_body', sa.String(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.Column('response_time', sa.Float(), nullable=False),
                    sa.Column('response_body', sa.String(), nullable=False),
                    sa.Column('exception_message', sa.String(), nullable=True),
                    sa.Column('stack_trace', sa.String(), nullable=True),
                    sa.Column('user_id', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('log_db_queries',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('log_http_request_id', sa.Integer(), nullable=False),
                    sa.Column('level', sa.String(), nullable=False),
                    sa.Column('db_query', sa.String(), nullable=False),
                    sa.Column('db_query_time', sa.Float(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['log_http_request_id'], ['log_http_requests.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_log_db_queries_log_http_request_id'), 'log_db_queries', ['log_http_request_id'],
                    unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_log_db_queries_log_http_request_id'), table_name='log_db_queries')
    op.drop_table('log_db_queries')
    op.drop_table('log_http_requests')
```
7. Run your FastAPI app and open docs page http://localhost:8000/docs.
8. Open your browser and go to `<SITE_URL><API_PREFIX>/telescope/dashboard` to see the dashboard. It should look like this:<br><br>
![Dashboard](https://github.com/AlisaZobova/fastapi-telescope-pip/blob/master/dashboard.png?raw=true)
