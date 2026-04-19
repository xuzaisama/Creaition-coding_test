from __future__ import annotations

import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * ratio))))
    return ordered[index]


def summarize(label: str, samples: list[float]) -> str:
    return (
        f"{label:<30} "
        f"avg={statistics.mean(samples):>7.2f}ms "
        f"p95={percentile(samples, 0.95):>7.2f}ms "
        f"max={max(samples):>7.2f}ms"
    )


def measure(iterations: int, fn) -> list[float]:
    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - started) * 1000)
    return samples


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "benchmark.db"
        # Benchmark against an isolated temporary database so repeated runs do not
        # depend on whatever data happens to be in the developer's local DB.
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

        from fastapi.testclient import TestClient

        from app.core.cache import task_cache
        from app.core.database import Base, engine
        from app.main import app

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        task_cache.clear()

        with TestClient(app) as client:
            seeded_ids: list[str] = []
            for index in range(120):
                response = client.post(
                    "/api/tasks",
                    json={
                        "title": f"seed task {index}",
                        "description": "benchmark seed data",
                        "status": "pending",
                        "priority": "medium",
                        "tags": ["benchmark", "seed"],
                    },
                )
                response.raise_for_status()
                seeded_ids.append(response.json()["id"])

            target_id = seeded_ids[0]

            def create_task() -> None:
                response = client.post(
                    "/api/tasks",
                    json={
                        "title": f"benchmark create {uuid4()}",
                        "description": "create benchmark sample",
                        "status": "pending",
                        "priority": "high",
                        "tags": ["benchmark", "create"],
                    },
                )
                response.raise_for_status()

            def detail_uncached() -> None:
                task_cache.clear()
                response = client.get(f"/api/tasks/{target_id}")
                response.raise_for_status()

            def detail_cached() -> None:
                response = client.get(f"/api/tasks/{target_id}")
                response.raise_for_status()

            def list_uncached() -> None:
                task_cache.clear()
                response = client.get("/api/tasks?page=1&page_size=20&sort_by=created_at&order=desc")
                response.raise_for_status()

            def list_cached() -> None:
                response = client.get("/api/tasks?page=1&page_size=20&sort_by=created_at&order=desc")
                response.raise_for_status()

            def search_uncached() -> None:
                task_cache.clear()
                response = client.get("/api/tasks/search?q=seed&page=1&page_size=20")
                response.raise_for_status()

            def search_cached() -> None:
                response = client.get("/api/tasks/search?q=seed&page=1&page_size=20")
                response.raise_for_status()

            task_cache.clear()
            client.get(f"/api/tasks/{target_id}").raise_for_status()
            task_cache.clear()
            client.get("/api/tasks?page=1&page_size=20&sort_by=created_at&order=desc").raise_for_status()
            task_cache.clear()
            client.get("/api/tasks/search?q=seed&page=1&page_size=20").raise_for_status()

            create_samples = measure(20, create_task)
            detail_uncached_samples = measure(30, detail_uncached)
            task_cache.clear()
            # Warm cache-backed endpoints once before measuring the HIT path.
            client.get(f"/api/tasks/{target_id}").raise_for_status()
            detail_cached_samples = measure(30, detail_cached)
            list_uncached_samples = measure(30, list_uncached)
            task_cache.clear()
            client.get("/api/tasks?page=1&page_size=20&sort_by=created_at&order=desc").raise_for_status()
            list_cached_samples = measure(30, list_cached)
            search_uncached_samples = measure(30, search_uncached)
            task_cache.clear()
            client.get("/api/tasks/search?q=seed&page=1&page_size=20").raise_for_status()
            search_cached_samples = measure(30, search_cached)

        print("Benchmark scope: in-process FastAPI TestClient with temporary SQLite database")
        print("Seeded tasks: 120")
        print(summarize("POST /api/tasks", create_samples))
        print(summarize("GET /api/tasks/{id} MISS", detail_uncached_samples))
        print(summarize("GET /api/tasks/{id} HIT", detail_cached_samples))
        print(summarize("GET /api/tasks MISS", list_uncached_samples))
        print(summarize("GET /api/tasks HIT", list_cached_samples))
        print(summarize("GET /api/tasks/search MISS", search_uncached_samples))
        print(summarize("GET /api/tasks/search HIT", search_cached_samples))


if __name__ == "__main__":
    main()
