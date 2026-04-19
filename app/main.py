from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.task_routes import router as task_router
from app.core.config import settings
from app.core.database import check_db_connection, init_db
from app.services.task_service import TaskConflictError, TaskDependencyNotFoundError, TaskNotFoundError

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Keep database initialization in the application lifespan so tests and local runs
    # share the same startup behavior.
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)
app.mount("/assets", StaticFiles(directory=str(STATIC_DIR)), name="assets")


def error_response(
    *,
    http_status: int,
    error: str,
    message: str,
    details: list[dict] | None = None,
) -> JSONResponse:
    # Centralizing error payload construction keeps API failures consistent across
    # validation, business-rule, and unexpected runtime errors.
    payload: dict[str, object] = {
        "error": error,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    return JSONResponse(status_code=http_status, content=jsonable_encoder(payload))


@app.exception_handler(TaskNotFoundError)
async def task_not_found_exception_handler(_: Request, exc: TaskNotFoundError) -> JSONResponse:
    return error_response(
        http_status=status.HTTP_404_NOT_FOUND,
        error="not_found",
        message=str(exc),
    )


@app.exception_handler(TaskDependencyNotFoundError)
async def task_dependency_not_found_exception_handler(
    _: Request,
    exc: TaskDependencyNotFoundError,
) -> JSONResponse:
    return error_response(
        http_status=status.HTTP_404_NOT_FOUND,
        error="dependency_not_found",
        message=str(exc),
    )


@app.exception_handler(TaskConflictError)
async def task_conflict_exception_handler(_: Request, exc: TaskConflictError) -> JSONResponse:
    return error_response(
        http_status=status.HTTP_409_CONFLICT,
        error="conflict",
        message=str(exc),
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        http_status=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error="validation_error",
        message="Request validation failed.",
        details=exc.errors(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    error_code_map = {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_409_CONFLICT: "conflict",
    }
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return error_response(
        http_status=exc.status_code,
        error=error_code_map.get(exc.status_code, "http_error"),
        message=message,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return error_response(
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="internal_server_error",
        message="An unexpected error occurred.",
    )


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "database": check_db_connection(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(task_router)
