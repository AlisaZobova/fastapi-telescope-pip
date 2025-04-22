from datetime import datetime
from typing import Union

from pydantic import BaseModel


class LogHttpRequestBase(BaseModel):
    id: int
    user_id: Union[str, None]
    level: str
    request_method: str
    request_url: str
    path_params: str
    query_params: str
    headers: str
    request_body: Union[str, None]
    status_code: int
    response_time: float
    response_body: str
    exception_message: Union[str, None]
    stack_trace: Union[str, None]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
