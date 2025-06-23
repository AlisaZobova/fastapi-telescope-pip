from fastapi_telescope.db import get_async_sessionmaker, get_async_engine
from starlette.datastructures import UploadFile
from .models import LogHttpRequest, LogDBQuery
from datetime import datetime, date
import time
import json
from fastapi import FastAPI, Request, Response
from sqlalchemy import event
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import traceback
from contextvars import ContextVar
from typing import Optional
from uuid import uuid4

# Create a context variable to store the request ID
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

engine = get_async_engine()
sessionmaker = get_async_sessionmaker(engine)



class TelescopeMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: FastAPI,
    ):
        super().__init__(app)
        self.db_session_maker = sessionmaker
        self._request_queries = {}
        # Set up SQL logging once during middleware initialization
        self._setup_sql_logging()

    def _setup_sql_logging(self):
        """Set up SQLAlchemy event listeners for query logging"""
        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if LogDBQuery.__tablename__ in statement.lower() or LogHttpRequest.__tablename__ in statement.lower():
                return
            
            conn.info.setdefault("query_start_time", {})
            conn.info["query_start_time"][cursor] = time.time()
            # ... rest of the handler ...

        @event.listens_for(engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if LogDBQuery.__tablename__ in statement.lower() or LogHttpRequest.__tablename__ in statement.lower():
                return
            
            total_time = round(time.time() - conn.info["query_start_time"][cursor], 5)
            request_id = request_id_context.get()
            
            if request_id and request_id in self._request_queries:  # Add check for request_id in self._request_queries
                compiled_query = compile_query(statement, parameters)
                self.add_query(
                    request_id=request_id,
                    query_info={
                        "query": compiled_query,
                        "execution_time": total_time,
                        "level": "INFO"
                    }
                )
                
        @event.listens_for(engine.sync_engine, "handle_error")
        def handle_error(context):
            if LogDBQuery.__tablename__ in context.statement.lower() or LogHttpRequest.__tablename__ in context.statement.lower():
                return
            
            request_id = request_id_context.get()
            if request_id and request_id in self._request_queries:
                compiled_query = compile_query(context.statement, context.parameters)
                self.add_query(
                    request_id=request_id,
                    query_info={
                        "query": compiled_query,
                        "execution_time": 0,
                        "level": "ERROR"
                    }
                )

    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
    ) -> Response:

        if 'telescope' in request.url.path:
            return await call_next(request)

        # Generate unique ID for this request
        request_id = str(uuid4())

        # Store the request ID in the context variable
        token = request_id_context.set(request_id)

        # Initialize request queries storage
        self._request_queries[request_id] = []

        start_time = time.time()

        response: Optional[Response] = None
        exception_info = None

        body = await self._get_request_body(request)
        
        response_body = None
        request.state.user_id = None

        try:
            response = await call_next(request)
            response_body = await self._get_response_body(response)

        except Exception as e:
            exception_info = {
                "message": str(e),
                "stack_trace": "".join(traceback.format_exception(type(e), e, e.__traceback__))
            }
            raise e
        finally:
            response_time = round(time.time() - start_time, 5)
                        
            await self._store_log_entry(
                request=request,
                response=response,
                response_time=response_time,
                request_body=body,
                response_body=response_body if response_body else "",
                exception_info=exception_info,
                request_id=request_id,
                user_id=request.state.user_id
            )

            # Clean up stored queries
            self._request_queries.pop(request_id, None)
            
            # Clean up context
            request_id_context.reset(token)

        return Response(content=response_body, status_code=response.status_code, headers=dict(response.headers))

    def add_query(self, request_id: str, query_info: dict):
        """Add a query to the current request's query list"""
        if request_id in self._request_queries:
            self._request_queries[request_id].append(query_info)

    async def _get_request_body(self, request: Request) -> str:
        """Get the request body as a string, handling all data types gracefully"""
        body = await request.body()
        if not body:
            return ""

        content_type = request.headers.get('content-type', '').lower()

        if 'multipart/form-data' in content_type or 'application/x-www-form-urlencoded' in content_type:
            form_data = dict(await request.form())
            data = {}
            
            for key, value in form_data.items():                
                if isinstance(value, UploadFile):                    
                    data[key] = {
                        "filename": value.filename,
                        "content_type": value.content_type,
                        "size": value.size
                    }
                else:
                    data[key] = value

            return json.dumps(data)

        try:
            return body.decode('utf-8')
        except UnicodeDecodeError:
            # Fall through to binary handling
            return f"<Binary data: {len(body)} bytes, Content-Type: {content_type}>"


    async def _get_response_body(self, response: Optional[Response]) -> str:
        if not response:
            return ""

        body = b""
        
        async for chunk in response.body_iterator:
            body += chunk

        # Reconstruct response with the body
        response.body = body

        if not body:
            return ""

        content_type = response.headers.get('content-type', '').lower()

        try:
            return body.decode('utf-8')
        except UnicodeDecodeError:
            # Fall through to binary handling
            return f"<Binary data: {len(body)} bytes, Content-Type: {content_type}>"

    async def _store_log_entry(
            self,
            request: Request,
            response: Optional[Response],
            response_time: float,
            request_body: str,
            response_body: str,
            exception_info: Optional[dict],
            request_id: str,
            user_id: Optional[str] = None
    ):
        """Store the request log and associated queries in the database"""
        async with self.db_session_maker() as session:
            try:
                # Create HTTP request log entry
                log_request = LogHttpRequest(
                    level="INFO" if not exception_info else "ERROR",
                    request_method=request.method,
                    request_url=str(request.url),
                    path_params=json.dumps(request.path_params),
                    query_params=json.dumps(dict(request.query_params)),
                    headers=json.dumps(dict(request.headers)),
                    request_body=request_body,
                    status_code=response.status_code if response else 500,
                    response_time=response_time,
                    response_body=response_body,
                    exception_message=exception_info["message"] if exception_info else None,
                    stack_trace=exception_info["stack_trace"] if exception_info else None,
                    user_id=user_id
                )

                session.add(log_request)
                await session.flush()  # To get the log_request.id

                db_queries = []
            
                # Create DB query log entries
                for query_info in self._request_queries.get(request_id, []):
                    db_queries.append(LogDBQuery(
                        log_http_request_id=log_request.id,
                        level=query_info["level"],
                        db_query=query_info["query"],
                        db_query_time=query_info["execution_time"],
                    ))
                    
                session.add_all(db_queries)

                await session.commit()
            except Exception as e:
                await session.rollback()
                # Log the error somewhere (e.g., console, file, etc.)
                print(f"Error storing request log: {str(e)}")


def compile_query(statement: str, parameters: tuple) -> str:
    """
    Compile SQL query by replacing PostgreSQL positional parameters ($1, $2, etc.)
    with their actual values, removing type casts
    """
    if not parameters:
        return statement

    # First, strip type casts from the statement (e.g., ::VARCHAR, ::INTEGER)
    statement = statement.replace("::VARCHAR", "").replace("::INTEGER", "").replace("::FLOAT", "")
    statement = statement.replace("::TIMESTAMP WITHOUT TIME ZONE", "")
    statement = statement.replace("::BOOLEAN", "").replace("::TEXT", "")

    # Create a mapping of parameter positions to values
    param_mapping = {}
    for i, value in enumerate(parameters, start=1):
        if value is None:
            param_mapping[f"${i}"] = "NULL"
        elif isinstance(value, (int, float)):
            param_mapping[f"${i}"] = str(value)
        elif isinstance(value, (datetime, date)):
            param_mapping[f"${i}"] = f"'{value}'"
        elif isinstance(value, bool):
            param_mapping[f"${i}"] = 'TRUE' if value else 'FALSE'
        elif isinstance(value, (list, tuple)):
            param_mapping[f"${i}"] = f"({', '.join(repr(v) for v in value)})"
        else:
            # Handle strings and other types, escape single quotes
            value_str = str(value).replace("'", "''")
            param_mapping[f"${i}"] = f"'{value_str}'"

    # Sort parameters by length in reverse order to avoid partial replacements
    sorted_params = sorted(param_mapping.keys(), key=len, reverse=True)

    # Replace each parameter placeholder with its value
    result = statement
    for param in sorted_params:
        if param in param_mapping:
            result = result.replace(param, param_mapping[param])

    return result

# Optional: Create a dependency to access the request ID
async def get_request_id():
    return request_id_context.get()
