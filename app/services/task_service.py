from app.models.task import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    SortOrder,
    TaskCreate,
    TaskDependencyTreeNode,
    TaskSortBy,
    TaskUpdate,
    task_to_dependency_tree_node,
)


class TaskNotFoundError(Exception):
    """Raised when the requested task cannot be found."""


class TaskConflictError(Exception):
    """Raised when a task operation would violate business rules."""


class TaskDependencyNotFoundError(Exception):
    """Raised when a dependency link cannot be found."""


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create_task(self, payload: TaskCreate):
        return self.repository.create(payload)

    def list_tasks(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: TaskStatus | None = None,
        priority=None,
        tags: list[str] | None = None,
        sort_by: TaskSortBy = TaskSortBy.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
    ):
        return self.repository.list(
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            tags=tags,
            sort_by=sort_by,
            order=order,
        )

    def get_task(self, task_id: str):
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task '{task_id}' not found.")
        return task

    def search_tasks(self, *, query: str, page: int = 1, page_size: int = 20):
        normalized_query = query.strip()
        if not normalized_query:
            raise TaskConflictError("Search query cannot be empty.")
        return self.repository.search(query=normalized_query, page=page, page_size=page_size)

    def update_task(self, task_id: str, payload: TaskUpdate):
        task = self.get_task(task_id)
        if payload.status == TaskStatus.COMPLETED and self.repository.count_incomplete_dependencies(task_id) > 0:
            raise TaskConflictError("Cannot complete task before its dependencies are completed.")
        return self.repository.update(task, payload)

    def delete_task(self, task_id: str) -> None:
        task = self.get_task(task_id)
        if self.repository.has_dependents(task_id):
            raise TaskConflictError("Cannot delete task because other tasks depend on it.")
        self.repository.delete(task)

    def add_dependency(self, task_id: str, dependency_id: str) -> None:
        if task_id == dependency_id:
            raise TaskConflictError("A task cannot depend on itself.")

        task = self.get_task(task_id)
        dependency = self.get_task(dependency_id)

        if self.repository.has_dependency(task_id, dependency_id):
            raise TaskConflictError("Dependency already exists.")
        if task.status == TaskStatus.COMPLETED and dependency.status != TaskStatus.COMPLETED:
            raise TaskConflictError(
                "Cannot add an incomplete dependency to a completed task.",
            )
        if self._creates_cycle(task_id, dependency_id):
            raise TaskConflictError("This dependency would create a cycle.")

        self.repository.add_dependency(task_id, dependency_id)

    def remove_dependency(self, task_id: str, dependency_id: str) -> None:
        self.get_task(task_id)
        self.get_task(dependency_id)

        removed = self.repository.remove_dependency(task_id, dependency_id)
        if not removed:
            raise TaskDependencyNotFoundError("Dependency link not found.")

    def get_dependency_tree(self, task_id: str) -> TaskDependencyTreeNode:
        task = self.get_task(task_id)
        return self._build_dependency_tree(task.id, visited=set())

    def _build_dependency_tree(self, task_id: str, visited: set[str]) -> TaskDependencyTreeNode:
        task = self.get_task(task_id)
        next_visited = visited | {task.id}

        dependencies: list[TaskDependencyTreeNode] = []
        for dependency in self.repository.get_direct_dependencies(task.id):
            if dependency.id in next_visited:
                dependencies.append(task_to_dependency_tree_node(dependency, []))
                continue
            dependencies.append(self._build_dependency_tree(dependency.id, next_visited))

        return task_to_dependency_tree_node(task, dependencies)

    def _creates_cycle(self, task_id: str, dependency_id: str) -> bool:
        stack = [dependency_id]
        visited: set[str] = set()

        while stack:
            current_id = stack.pop()
            if current_id == task_id:
                return True
            if current_id in visited:
                continue
            visited.add(current_id)
            stack.extend(self.repository.get_direct_dependency_ids(current_id))

        return False
