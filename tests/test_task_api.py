import os
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = ROOT / "test_task_manager.db"
if DB_PATH.exists():
    DB_PATH.unlink()
# Set the database URL before importing the app so the test suite never touches the
# developer's real local database file.
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

from fastapi.testclient import TestClient

from app.core.cache import task_cache
from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database() -> None:
    # Rebuild schema state around every test so cache assertions and dependency
    # scenarios do not leak into each other.
    task_cache.clear()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    task_cache.clear()
    Base.metadata.drop_all(bind=engine)


def teardown_module() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_health_endpoint_returns_service_metadata() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["app_name"] == "Intelligent Task Management System"
        assert payload["version"] == "1.0.0"
        assert payload["database"] is True
        assert isinstance(payload["timestamp"], str)


def test_home_page_returns_dashboard_html() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "智能任务管理系统" in response.text
        assert "/assets/app.js" in response.text
        assert 'id="tag-selector"' in response.text
        assert 'id="filter-tags"' in response.text


def test_task_crud_flow() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/api/tasks",
            json={
                "title": "完成第一小时任务",
                "description": "搭建项目骨架和 CRUD",
                "priority": "high",
                "tags": ["backend", "fastapi"],
            },
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        assert created_task["title"] == "完成第一小时任务"
        assert created_task["priority"] == "high"
        assert created_task["tags"] == ["backend", "fastapi"]

        list_response = client.get("/api/tasks")
        assert list_response.status_code == 200
        listed_tasks = list_response.json()
        assert listed_tasks["total"] == 1
        assert listed_tasks["items"][0]["id"] == task_id

        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == task_id

        update_response = client.patch(
            f"/api/tasks/{task_id}",
            json={"status": "in_progress", "tags": ["backend", "crud"]},
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["status"] == "in_progress"
        assert updated_task["tags"] == ["backend", "crud"]

        delete_response = client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 204

        missing_response = client.get(f"/api/tasks/{task_id}")
        assert missing_response.status_code == 404


def test_task_list_supports_filters_sorting_and_pagination() -> None:
    with TestClient(app) as client:
        first = client.post(
            "/api/tasks",
            json={
                "title": "实现后端接口",
                "status": "pending",
                "priority": "high",
                "tags": ["backend", "api"],
            },
        )
        second = client.post(
            "/api/tasks",
            json={
                "title": "设计前端页面",
                "status": "in_progress",
                "priority": "low",
                "tags": ["frontend"],
            },
        )
        third = client.post(
            "/api/tasks",
            json={
                "title": "补充测试用例",
                "status": "pending",
                "priority": "medium",
                "tags": ["backend", "test"],
            },
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert third.status_code == 201

        response = client.get(
            "/api/tasks",
            params=[
                ("status", "pending"),
                ("tags", "backend"),
                ("sort_by", "priority"),
                ("order", "desc"),
                ("page", 1),
                ("page_size", 1),
            ],
        )
        assert response.status_code == 200

        payload = response.json()
        assert payload["total"] == 2
        assert payload["page"] == 1
        assert payload["page_size"] == 1
        assert len(payload["items"]) == 1
        assert payload["items"][0]["title"] == "实现后端接口"
        assert payload["items"][0]["priority"] == "high"


def test_read_endpoints_use_cache_and_invalidate_after_writes() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/tasks",
            json={
                "title": "缓存验证任务",
                "description": "验证缓存命中和失效",
                "priority": "medium",
                "tags": ["cache"],
            },
        )
        assert created.status_code == 201
        task_id = created.json()["id"]

        first_detail = client.get(f"/api/tasks/{task_id}")
        second_detail = client.get(f"/api/tasks/{task_id}")
        assert first_detail.headers["X-Cache"] == "MISS"
        assert second_detail.headers["X-Cache"] == "HIT"

        first_list = client.get("/api/tasks")
        second_list = client.get("/api/tasks")
        assert first_list.headers["X-Cache"] == "MISS"
        assert second_list.headers["X-Cache"] == "HIT"

        update_response = client.patch(
            f"/api/tasks/{task_id}",
            json={"title": "缓存验证任务-已更新"},
        )
        assert update_response.status_code == 200

        after_update_detail = client.get(f"/api/tasks/{task_id}")
        after_update_list = client.get("/api/tasks")
        assert after_update_detail.headers["X-Cache"] == "MISS"
        assert after_update_list.headers["X-Cache"] == "MISS"
        assert after_update_detail.json()["title"] == "缓存验证任务-已更新"


def test_search_endpoint_matches_title_and_description_and_uses_cache() -> None:
    with TestClient(app) as client:
        create_first = client.post(
            "/api/tasks",
            json={
                "title": "整理发布文档",
                "description": "需要准备 Docker 部署说明和运行步骤",
                "tags": ["docs"],
            },
        )
        create_second = client.post(
            "/api/tasks",
            json={
                "title": "优化缓存策略",
                "description": "为任务详情接口增加本地 TTL 缓存",
                "tags": ["backend", "cache"],
            },
        )
        create_third = client.post(
            "/api/tasks",
            json={
                "title": "设计首页样式",
                "description": "调整页面视觉风格",
                "tags": ["frontend"],
            },
        )

        assert create_first.status_code == 201
        assert create_second.status_code == 201
        assert create_third.status_code == 201

        first_search = client.get("/api/tasks/search", params={"q": "Docker"})
        second_search = client.get("/api/tasks/search", params={"q": "Docker"})
        assert first_search.status_code == 200
        assert second_search.status_code == 200
        assert first_search.headers["X-Cache"] == "MISS"
        assert second_search.headers["X-Cache"] == "HIT"
        docker_payload = first_search.json()
        assert docker_payload["total"] == 1
        assert docker_payload["items"][0]["title"] == "整理发布文档"

        cache_search = client.get("/api/tasks/search", params={"q": "缓存"})
        assert cache_search.status_code == 200
        cache_payload = cache_search.json()
        assert cache_payload["total"] == 1
        assert cache_payload["items"][0]["title"] == "优化缓存策略"

        blank_query = client.get("/api/tasks/search", params={"q": "   "})
        assert blank_query.status_code == 409
        assert blank_query.json() == {
            "error": "conflict",
            "message": "Search query cannot be empty.",
        }


def test_task_dependencies_enforce_completion_rules_and_tree_queries() -> None:
    with TestClient(app) as client:
        task_a = client.post(
            "/api/tasks",
            json={"title": "完成数据库设计", "priority": "high", "tags": ["backend"]},
        ).json()
        task_b = client.post(
            "/api/tasks",
            json={"title": "实现服务层", "priority": "medium", "tags": ["backend"]},
        ).json()
        task_c = client.post(
            "/api/tasks",
            json={"title": "补充集成测试", "priority": "low", "tags": ["test"]},
        ).json()

        add_first = client.post(f"/api/tasks/{task_b['id']}/dependencies/{task_a['id']}")
        assert add_first.status_code == 201

        add_second = client.post(f"/api/tasks/{task_c['id']}/dependencies/{task_b['id']}")
        assert add_second.status_code == 201

        blocked_completion = client.patch(
            f"/api/tasks/{task_b['id']}",
            json={"status": "completed"},
        )
        assert blocked_completion.status_code == 409
        assert "dependencies" in blocked_completion.json()["message"]

        dependency_tree = client.get(f"/api/tasks/{task_c['id']}/dependencies/tree")
        assert dependency_tree.status_code == 200
        tree_payload = dependency_tree.json()
        assert tree_payload["id"] == task_c["id"]
        assert tree_payload["dependencies"][0]["id"] == task_b["id"]
        assert tree_payload["dependencies"][0]["dependencies"][0]["id"] == task_a["id"]

        cycle_attempt = client.post(f"/api/tasks/{task_a['id']}/dependencies/{task_c['id']}")
        assert cycle_attempt.status_code == 409

        delete_blocked = client.delete(f"/api/tasks/{task_a['id']}")
        assert delete_blocked.status_code == 409

        complete_a = client.patch(f"/api/tasks/{task_a['id']}", json={"status": "completed"})
        assert complete_a.status_code == 200

        complete_b = client.patch(f"/api/tasks/{task_b['id']}", json={"status": "completed"})
        assert complete_b.status_code == 200

        remove_dependency = client.delete(f"/api/tasks/{task_b['id']}/dependencies/{task_a['id']}")
        assert remove_dependency.status_code == 204

        delete_a = client.delete(f"/api/tasks/{task_a['id']}")
        assert delete_a.status_code == 204


def test_error_responses_are_returned_in_unified_format() -> None:
    with TestClient(app) as client:
        missing_task = client.get("/api/tasks/not-found")
        assert missing_task.status_code == 404
        assert missing_task.json() == {
            "error": "not_found",
            "message": "Task 'not-found' not found.",
        }

        invalid_payload = client.post(
            "/api/tasks",
            json={"title": "   ", "priority": "urgent"},
        )
        assert invalid_payload.status_code == 422
        body = invalid_payload.json()
        assert body["error"] == "validation_error"
        assert body["message"] == "Request validation failed."
        assert isinstance(body["details"], list)
