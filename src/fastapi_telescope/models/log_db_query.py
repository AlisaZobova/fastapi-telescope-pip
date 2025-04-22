from datetime import datetime
from typing import List

from pytz import UTC
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sqlalchemy import DateTime

from .base import Base


class LogDBQuery(Base):
    __tablename__ = "log_db_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    log_http_request_id: Mapped[int] = mapped_column(
        ForeignKey('log_http_requests.id'),
        index=True,
    )
    level: Mapped[str]
    db_query: Mapped[str]
    db_query_time: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    log_http_request: Mapped[List['LogHttpRequest']] = relationship("LogHttpRequest", back_populates="db_queries")