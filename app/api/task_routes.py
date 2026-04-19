from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.cache import task_cache
from app.core.database import get_db
from app.models.task import TaskPriority, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    SortOrder,
    TaskCreate,
    TaskDependencyLinkResponse,
    TaskDependencyTreeNode,
    TaskListResponse,
    TaskRead,
    TaskSortBy,
    TaskUpdate,
    task_to_read,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    repository = TaskRepository(db)
    return TaskService(repository)


def _task_detail_cache_key(task_id: str) -> str:
    return f"task:detail:{task_id}"


def _task_tree_cache_key(task_id: str) -> str:
    return f"task:tree:{task_id}"


def _task_search_cache_key(*, query: str, page: int, page_size: int) -> str:
    payload = {
        "query": query.strip(),
        "page": page,
        "page_size": page_size,
    }
    # Hashing the full parameter set keeps cache keys stable even when queries grow.
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"task:search:{digest}"


def _task_list_cache_key(
    *,
    page: int,
    page_size: int,
    status: TaskStatus | None,
    priority: TaskPriority | None,
    tags: list[str] | None,
    sort_by: TaskSortBy,
    order: SortOrder,
) -> str:
    payload = {
        "page": page,
        "page_size": page_size,
        "status": status.value if status is not None else None,
        "priority": priority.value if priority is not None else None,
        "tags": sorted(tag.strip() for tag in (tags or []) if tag.strip()),
        "sort_by": sort_by.value,
        "order": order.value,
    }
    # List responses depend on several filters, so the cache key is derived from a
    # normalized payload rather than from a raw query string.
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"task:list:{digest}"


def _invalidate_task_read_caches() -> None:
    # Any write can affect list, detail, search, and dependency tree responses.
    task_cache.invalidate_prefix("task:")


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskService = Depends(get_task_service)) -> TaskRead:
    task = service.create_task(payload)
    _invalidate_task_read_caches()
    return task_to_read(task)


@router.get("/search", response_model=TaskListResponse)
def search_tasks(
    response: Response,
    q: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    cache_key = _task_search_cache_key(query=q, page=page, page_size=page_size)
    cached_payload = task_cache.get(cache_key)
    if cached_payload is not None:
        response.headers["X-Cache"] = "HIT"
        return cached_payload

    tasks, total = service.search_tasks(query=q, page=page, page_size=page_size)
    payload = TaskListResponse(
        items=[task_to_read(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )
    serialized_payload = jsonable_encoder(payload)
    task_cache.set(cache_key, serialized_payload)
    response.headers["X-Cache"] = "MISS"
    return serialized_payload


@router.get("", response_model=TaskListResponse)
def list_tasks(
    response: Response,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: TaskStatus | None = Query(default=None),
    priority: TaskPriority | None = Query(default=None),
    tags: list[str] | None = Query(default=None),
    sort_by: TaskSortBy = Query(default=TaskSortBy.CREATED_AT),
    order: SortOrder = Query(default=SortOrder.DESC),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    cache_key = _task_list_cache_key(
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        tags=tags,
        sort_by=sort_by,
        order=order,
    )
    cached_payload = task_cache.get(cache_key)
    if cached_payload is not None:
        response.headers["X-Cache"] = "HIT"
        return cached_payload

    tasks, total = service.list_tasks(
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        tags=tags,
        sort_by=sort_by,
        order=order,
    )
    payload = TaskListResponse(
        items=[task_to_read(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )
    serialized_payload = jsonable_encoder(payload)
    task_cache.set(cache_key, serialized_payload)
    response.headers["X-Cache"] = "MISS"
    return serialized_payload


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, response: Response, service: TaskService = Depends(get_task_service)) -> TaskRead:
    cache_key = _task_detail_cache_key(task_id)
    cached_payload = task_cache.get(cache_key)
    if cached_payload is not None:
        response.headers["X-Cache"] = "HIT"
        return cached_payload

    task = service.get_task(task_id)
    payload = task_to_read(task)
    serialized_payload = jsonable_encoder(payload)
    task_cache.set(cache_key, serialized_payload)
    response.headers["X-Cache"] = "MISS"
    return serialized_payload


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    task = service.update_task(task_id, payload)
    _invalidate_task_read_caches()
    return task_to_read(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)) -> Response:
    service.delete_task(task_id)
    _invalidate_task_read_caches()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{task_id}/dependencies/{dependency_id}",
    response_model=TaskDependencyLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_dependency(
    task_id: str,
    dependency_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskDependencyLinkResponse:
    service.add_dependency(task_id, dependency_id)
    _invalidate_task_read_caches()

    return TaskDependencyLinkResponse(
        task_id=task_id,
        dependency_id=dependency_id,
        message="Dependency added successfully.",
    )


@router.delete("/{task_id}/dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_dependency(
    task_id: str,
    dependency_id: str,
    service: TaskService = Depends(get_task_service),
) -> Response:
    service.remove_dependency(task_id, dependency_id)
    _invalidate_task_read_caches()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{task_id}/dependencies/tree", response_model=TaskDependencyTreeNode)
def get_dependency_tree(
    task_id: str,
    response: Response,
    service: TaskService = Depends(get_task_service),
) -> TaskDependencyTreeNode:
    cache_key = _task_tree_cache_key(task_id)
    cached_payload = task_cache.get(cache_key)
    if cached_payload is not None:
        response.headers["X-Cache"] = "HIT"
        return cached_payload

    payload = service.get_dependency_tree(task_id)
    serialized_payload = jsonable_encoder(payload)
    task_cache.set(cache_key, serialized_payload)
    response.headers["X-Cache"] = "MISS"
    return serialized_payload
