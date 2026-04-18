PYTHON ?= python

.PHONY: install run test clean docker-up docker-down

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -q

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f task_manager.db test_task_manager.db

docker-up:
	docker compose up --build

docker-down:
	docker compose down

