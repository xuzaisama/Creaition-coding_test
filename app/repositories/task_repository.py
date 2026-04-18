from __future__ import annotations

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.task import Task, TaskDependency, TaskPriority, TaskStatus, TaskTag
from app.schemas.task import SortOrder, TaskCreate, TaskSortBy, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: TaskCreate) -> Task:
        task = Task(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
        )
        task.tags = [TaskTag(tag=tag) for tag in payload.tags]

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        tags: list[str] | None = None,
        sort_by: TaskSortBy = TaskSortBy.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
    ) -> tuple[list[Task], int]:
        offset = (page - 1) * page_size
        normalized_tags = [tag.strip() for tag in (tags or []) if tag.strip()]
        statement = select(Task).options(selectinload(Task.tags))
        count_statement = select(func.count()).select_from(Task)

        if status is not None:
            statement = statement.where(Task.status == status)
            count_statement = count_statement.where(Task.status == status)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
            count_statement = count_statement.where(Task.priority == priority)
        if normalized_tags:
            tag_filter = Task.tags.any(TaskTag.tag.in_(normalized_tags))
            statement = statement.where(tag_filter)
            count_statement = count_statement.where(tag_filter)

        sort_expression = self._build_sort_expression(sort_by)
        if order == SortOrder.ASC:
            statement = statement.order_by(sort_expression.asc(), Task.created_at.asc(), Task.id.asc())
        else:
            statement = statement.order_by(sort_expression.desc(), Task.created_at.desc(), Task.id.desc())

        statement = statement.offset(offset).limit(page_size)
        total = self.db.scalar(count_statement) or 0
        items = list(self.db.scalars(statement).all())
        return items, total

    def get_by_id(self, task_id: str) -> Task | None:
        statement = select(Task).options(selectinload(Task.tags)).where(Task.id == task_id)
        return self.db.scalar(statement)

    def search(self, *, query: str, page: int = 1, page_size: int = 20) -> tuple[list[Task], int]:
        offset = (page - 1) * page_size
        search_term = f"%{query.strip()}%"
        search_filter = or_(
            Task.title.ilike(search_term),
            Task.description.ilike(search_term),
        )

        statement = (
            select(Task)
            .options(selectinload(Task.tags))
            .where(search_filter)
            .order_by(Task.created_at.desc(), Task.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        count_statement = select(func.count()).select_from(Task).where(search_filter)
        total = int(self.db.scalar(count_statement) or 0)
        items = list(self.db.scalars(statement).all())
        return items, total

    def update(self, task: Task, payload: TaskUpdate) -> Task:
        data = payload.model_dump(exclude_unset=True)

        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            task.status = data["status"]
        if "priority" in data:
            task.priority = data["priority"]
        if "tags" in data:
            self._replace_tags(task, data["tags"])

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def has_dependents(self, task_id: str) -> bool:
        statement = select(func.count()).select_from(TaskDependency).where(
            TaskDependency.depends_on_task_id == task_id,
        )
        return bool(self.db.scalar(statement) or 0)

    def has_dependency(self, task_id: str, dependency_id: str) -> bool:
        statement = select(func.count()).select_from(TaskDependency).where(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id == dependency_id,
        )
        return bool(self.db.scalar(statement) or 0)

    def add_dependency(self, task_id: str, dependency_id: str) -> None:
        dependency = TaskDependency(task_id=task_id, depends_on_task_id=dependency_id)
        self.db.add(dependency)
        self.db.commit()

    def remove_dependency(self, task_id: str, dependency_id: str) -> bool:
        statement = select(TaskDependency).where(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id == dependency_id,
        )
        dependency = self.db.scalar(statement)
        if dependency is None:
            return False

        self.db.delete(dependency)
        self.db.commit()
        return True

    def count_incomplete_dependencies(self, task_id: str) -> int:
        statement = (
            select(func.count())
            .select_from(TaskDependency)
            .join(Task, Task.id == TaskDependency.depends_on_task_id)
            .where(
                TaskDependency.task_id == task_id,
                Task.status != TaskStatus.COMPLETED,
            )
        )
        return int(self.db.scalar(statement) or 0)

    def get_direct_dependency_ids(self, task_id: str) -> list[str]:
        statement = select(TaskDependency.depends_on_task_id).where(TaskDependency.task_id == task_id)
        return list(self.db.scalars(statement).all())

    def get_direct_dependencies(self, task_id: str) -> list[Task]:
        statement = (
            select(Task)
            .join(TaskDependency, Task.id == TaskDependency.depends_on_task_id)
            .options(selectinload(Task.tags))
            .where(TaskDependency.task_id == task_id)
            .order_by(Task.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def _replace_tags(self, task: Task, tags: list[str]) -> None:
        # Flush the delete-orphan removals first so reusing an existing tag
        # value does not violate the unique constraint during the same update.
        task.tags.clear()
        self.db.flush()
        task.tags.extend(TaskTag(tag=tag) for tag in tags)

    def _build_sort_expression(self, sort_by: TaskSortBy):
        if sort_by == TaskSortBy.PRIORITY:
            return case(
                (Task.priority == TaskPriority.LOW, 1),
                (Task.priority == TaskPriority.MEDIUM, 2),
                (Task.priority == TaskPriority.HIGH, 3),
                else_=99,
            )
        if sort_by == TaskSortBy.STATUS:
            return case(
                (Task.status == TaskStatus.PENDING, 1),
                (Task.status == TaskStatus.IN_PROGRESS, 2),
                (Task.status == TaskStatus.COMPLETED, 3),
                else_=99,
            )
        return Task.created_at
