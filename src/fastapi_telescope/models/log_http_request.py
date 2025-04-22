from datetime import datetime
from typing import Optional, List

from pytz import UTC
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sqlalchemy import DateTime

from .base import Base


class LogHttpRequest(Base):
    __tablename__ = "log_http_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str]
    request_method: Mapped[str]
    request_url: Mapped[str]
    path_params: Mapped[str]
    query_params: Mapped[str]
    headers: Mapped[str]
    request_body: Mapped[str]
    status_code: Mapped[int]
    response_time: Mapped[float]
    response_body: Mapped[str]
    exception_message: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    stack_trace: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    user_id: Mapped[Optional[str]] = mapped_column(nullable=True, default=None) # TODO: need to use as FK, but separate module can't find users table
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    db_queries: Mapped[List['LogDBQuery']] = relationship("LogDBQuery", back_populates="log_http_request", passive_deletes=True)
