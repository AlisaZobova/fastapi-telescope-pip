from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from telescope.models import LogHttpRequest
from telescope.app.log_http_request.schema import LogHttpRequestBase
from main.shared.di.database import get_async_session
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate


router = APIRouter()

@router.get("", response_model=Page[LogHttpRequestBase])
async def get_http_requests(
    db: AsyncSession = Depends(get_async_session),
    params: Params = Depends()
):
    return await paginate(db, select(LogHttpRequest).order_by(LogHttpRequest.created_at.desc()))

@router.get("/{http_request_id}", response_model=LogHttpRequestBase)
async def get_http_request_detail(http_request_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(LogHttpRequest).where(LogHttpRequest.id == http_request_id))
    http_request = result.scalar()
    
    if not http_request:
        raise HTTPException(status_code=404, detail="HTTP request log not found")
    
    return http_request

@router.get("/{id}/db-queries")
async def get_async_session_queries_for_http_request(id: int, db: AsyncSession = Depends(get_async_session)):
    http_request = (
        await db.execute(
            select(LogHttpRequest)
            .options(joinedload(LogHttpRequest.db_queries))
            .where(LogHttpRequest.id == id)
        )
    ).scalars().first()
    
    if not http_request:
        raise HTTPException(status_code=404, detail="HTTP request log not found")
    
    return http_request.db_queries
