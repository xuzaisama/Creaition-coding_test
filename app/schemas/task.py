from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.models.task import Task, TaskPriority, TaskStatus


class TaskSortBy(str, Enum):
    CREATED_AT = "created_at"
    PRIORITY = "priority"
    STATUS = "status"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Title cannot be empty.")
        return normalized

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized_tags: list[str] = []
        for item in value:
            tag = item.strip()
            if not tag:
                continue
            if tag in seen:
                continue
            seen.add(tag)
            normalized_tags.append(tag)
        return normalized_tags


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Title cannot be empty.")
        return normalized

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        seen: set[str] = set()
        normalized_tags: list[str] = []
        for item in value:
            tag = item.strip()
            if not tag:
                continue
            if tag in seen:
                continue
            seen.add(tag)
            normalized_tags.append(tag)
        return normalized_tags


class TaskRead(BaseModel):
    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    tags: list[str]


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    page_size: int


class TaskDependencyLinkResponse(BaseModel):
    task_id: str
    dependency_id: str
    message: str


class TaskDependencyTreeNode(BaseModel):
    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    tags: list[str]
    dependencies: list["TaskDependencyTreeNode"] = Field(default_factory=list)


def task_to_read(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
        updated_at=task.updated_at,
        tags=[tag.tag for tag in task.tags],
    )


def task_to_dependency_tree_node(
    task: Task,
    dependencies: list[TaskDependencyTreeNode] | None = None,
) -> TaskDependencyTreeNode:
    return TaskDependencyTreeNode(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        tags=[tag.tag for tag in task.tags],
        dependencies=dependencies or [],
    )


TaskDependencyTreeNode.model_rebuild()
