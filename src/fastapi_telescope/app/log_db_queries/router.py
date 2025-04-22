from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_telescope.db import get_async_session

from fastapi_telescope.models import LogDBQuery
from .schema import LogDBQueryBase

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate


router = APIRouter()

@router.get("", response_model=Page[LogDBQueryBase])
async def get_http_requests(
    db: AsyncSession = Depends(get_async_session),
    params: Params = Depends()
):
    return await paginate(db, select(LogDBQuery).order_by(LogDBQuery.created_at.desc()))


@router.get("/{db_query_id}", response_model=LogDBQueryBase)
async def get_async_session_query_detail(db_query_id: int, db: AsyncSession = Depends(get_async_session)):
    db_query = (await db.execute(select(LogDBQuery).where(LogDBQuery.id == db_query_id))).scalar()
    
    if not db_query:
        raise HTTPException(status_code=404, detail="DB query log not found")
    return db_query
