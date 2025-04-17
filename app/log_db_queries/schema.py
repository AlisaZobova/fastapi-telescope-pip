from datetime import datetime

from pydantic import BaseModel


class LogDBQueryBase(BaseModel):
    id: int
    log_http_request_id: int
    level: str
    db_query: str
    db_query_time: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
