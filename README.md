# 智能任务管理系统

## 当前版本

**V1.0.0**

这是当前的**第一版本**，定位为一套可运行、可测试、可演示、可继续扩展的后端任务管理系统。
项目已经完成基础任务管理能力、依赖关系管理、搜索、缓存、错误处理、Docker 运行支持和基础 CI 配置。

---

## 岗位方向

后端开发

---

## 项目简介

本项目是基于实习生编程挑战实现的一套智能任务管理系统后端服务。
使用 FastAPI 构建，目标是在较短时间内交付一版结构清晰、业务规则完整、接口易于演示、后续可扩展的系统。

当前第一版本已经支持：

- 任务的创建、查询、更新、删除
- 任务列表筛选、排序、分页
- 任务依赖关系管理
- 依赖树查询
- 依赖未完成时禁止完成任务
- 阻止循环依赖
- 阻止删除被依赖任务
- 标题和描述关键词搜索
- 热点读接口本地 TTL 缓存
- 统一错误响应格式
- 首页 Dashboard 可视化操作界面
- 首页支持实时时间显示与标签可视化选择
- Docker 部署支持
- GitHub Actions 自动测试工作流

---

## 技术栈

- 语言：Python 3.13
- 框架：FastAPI
- 数据库：SQLite
- ORM：SQLAlchemy 2.x
- 数据校验：Pydantic v2
- 测试：pytest
- 容器化：Docker、Docker Compose
- 自动化：GitHub Actions

---

## 第一版本功能详解

### 1. 任务 CRUD

第一版本已经实现完整任务 CRUD：

- 创建任务
- 查询任务详情
- 查询任务列表
- 更新任务
- 删除任务

每个任务支持以下字段：

- `id`
- `title`
- `description`
- `status`
- `priority`
- `created_at`
- `updated_at`
- `tags`

其中：

- `status` 支持：`pending`、`in_progress`、`completed`
- `priority` 支持：`low`、`medium`、`high`

### 2. 列表筛选、排序、分页

第一版本支持对任务列表进行：

- 按状态筛选
- 按优先级筛选
- 按标签筛选
- 按创建时间排序
- 按优先级排序
- 按状态排序
- 分页查询

支持的参数包括：

- `status`
- `priority`
- `tags`
- `sort_by`
- `order`
- `page`
- `page_size`

### 3. 任务依赖关系

第一版本支持任务之间建立依赖关系，例如：

- 任务 B 依赖任务 A
- 如果任务 A 未完成，则任务 B 不允许被标记为完成

已实现的约束包括：

- 不允许依赖自己
- 不允许重复依赖
- 不允许循环依赖
- 被其他任务依赖的任务不可直接删除

### 4. 依赖树查询

第一版本支持查看某个任务的依赖树，便于明确任务的前置完成关系。

### 5. 搜索能力

第一版本支持根据关键词搜索任务：

- 搜索范围：`title`、`description`
- 搜索方式：关键词匹配
- 支持分页

### 6. 缓存能力

第一版本实现了轻量级本地 TTL 缓存，主要用于热点读接口。

已缓存接口：

- `GET /api/tasks`
- `GET /api/tasks/search`
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/dependencies/tree`

响应头中会带上：

- `X-Cache: MISS`
- `X-Cache: HIT`

### 7. 统一错误响应

第一版本已经将错误响应统一为固定结构：

```json
{
  "error": "not_found",
  "message": "Task 'not-found' not found."
}
```

参数校验错误还会带 `details` 字段，便于前端或调用方处理。

### 8. 健康检查

第一版本健康检查接口不只是简单返回 `ok`，还会返回服务名、版本号、数据库状态和当前时间，用于部署验证与调试。

---

## 项目结构

```text
project/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .dockerignore
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── cache.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   └── task.py
│   ├── schemas/
│   │   └── task.py
│   ├── repositories/
│   │   └── task_repository.py
│   ├── services/
│   │   └── task_service.py
│   └── api/
│       └── task_routes.py
├── tests/
│   └── test_task_api.py
└── docs/
    └── architecture.md
```

---

## 运行方式

### 方式一：本地运行

#### 前置依赖

- Python 3.13
- `pip`

#### 安装依赖

```bash
python -m pip install -r requirements.txt
```

#### 启动服务

```bash
uvicorn app.main:app --reload
```

#### 访问地址

- 首页 Dashboard：`http://127.0.0.1:8000/`
- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- Health：`http://127.0.0.1:8000/health`

### 方式二：使用 Makefile

安装依赖：

```bash
make install
```

启动服务：

```bash
make run
```

运行测试：

```bash
make test
```

清理缓存和本地数据库：

```bash
make clean
```

### 方式三：Docker 运行

#### 前置依赖

- Docker
- Docker Compose

#### 构建并启动

```bash
docker compose up --build
```

启动后访问：

- `http://127.0.0.1:8000`

停止服务：

```bash
docker compose down
```

---

## 可选环境变量

- `DATABASE_URL`
  默认值：`sqlite:///./task_manager.db`

- `CACHE_TTL_SECONDS`
  默认值：`60`

- `APP_VERSION`
  默认值：`1.0.0`

---

## 第一版本接口用法详解

### 1. 健康检查

- `GET /health`

示例响应：

```json
{
  "status": "ok",
  "app_name": "Intelligent Task Management System",
  "version": "1.0.0",
  "database": true,
  "timestamp": "2026-04-18T10:00:00+00:00"
}
```

### 2. 创建任务

- `POST /api/tasks`

示例请求：

```json
{
  "title": "准备后端发布版本",
  "description": "整理文档、Docker 文件和测试用例",
  "status": "pending",
  "priority": "high",
  "tags": ["backend", "release"]
}
```

示例命令：

```bash
curl -X POST "http://127.0.0.1:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "准备后端发布版本",
    "description": "整理文档、Docker 文件和测试用例",
    "status": "pending",
    "priority": "high",
    "tags": ["backend", "release"]
  }'
```

### 3. 查询任务列表

- `GET /api/tasks`

支持参数：

- `status`
- `priority`
- `tags`
- `sort_by`
- `order`
- `page`
- `page_size`

示例命令：

```bash
curl "http://127.0.0.1:8000/api/tasks?status=pending&tags=backend&sort_by=priority&order=desc&page=1&page_size=10"
```

### 4. 查询任务详情

- `GET /api/tasks/{task_id}`

示例命令：

```bash
curl "http://127.0.0.1:8000/api/tasks/<task_id>"
```

### 5. 更新任务

- `PATCH /api/tasks/{task_id}`

示例命令：

```bash
curl -X PATCH "http://127.0.0.1:8000/api/tasks/<task_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "tags": ["backend", "api"]
  }'
```

### 6. 删除任务

- `DELETE /api/tasks/{task_id}`

示例命令：

```bash
curl -X DELETE "http://127.0.0.1:8000/api/tasks/<task_id>"
```

### 7. 搜索任务

- `GET /api/tasks/search?q=<关键词>`

示例命令：

```bash
curl "http://127.0.0.1:8000/api/tasks/search?q=Docker"
```

### 8. 添加依赖关系

- `POST /api/tasks/{task_id}/dependencies/{dependency_id}`

示例命令：

```bash
curl -X POST "http://127.0.0.1:8000/api/tasks/<task_id>/dependencies/<dependency_id>"
```

### 9. 删除依赖关系

- `DELETE /api/tasks/{task_id}/dependencies/{dependency_id}`

示例命令：

```bash
curl -X DELETE "http://127.0.0.1:8000/api/tasks/<task_id>/dependencies/<dependency_id>"
```

### 10. 查询依赖树

- `GET /api/tasks/{task_id}/dependencies/tree`

示例命令：

```bash
curl "http://127.0.0.1:8000/api/tasks/<task_id>/dependencies/tree"
```

---

## 缓存说明

第一版本已经实现本地 TTL 缓存。

说明如下：

- 列表、搜索、详情、依赖树查询都可能命中缓存
- 响应头 `X-Cache` 可用于判断本次结果是否来自缓存
- 一旦有任务写操作发生，相关读缓存会统一失效

这种实现方式的优点是简单、稳定、易解释，适合第一版作业交付。

---

## 错误响应说明

### 常见错误结构

```json
{
  "error": "conflict",
  "message": "Cannot complete task before its dependencies are completed."
}
```

### 常见错误类型

- `not_found`
- `dependency_not_found`
- `conflict`
- `validation_error`
- `internal_server_error`

---

## 测试方式

### 本地测试

```bash
pytest -q
```

### Makefile 测试

```bash
make test
```

### 自动化测试

项目已补充 GitHub Actions 工作流文件：

- `.github/workflows/ci.yml`

当仓库接入 GitHub 后，可在 `push` 和 `pull_request` 时自动执行测试。

---

## 设计决策

- 选择 FastAPI，是因为它开发效率高、类型提示清晰，并且自带自动生成的 API 文档。
- 选择 SQLite，是为了在挑战时间内快速交付可运行版本，同时保留升级到 PostgreSQL 的空间。
- 标签使用独立关系表建模，避免后续扩展时受限。
- 依赖关系单独建表，便于实现循环依赖检测和依赖树查询。
- 本地 TTL 缓存适合作为第一版性能优化方案，复杂度低、说明成本低。
- 错误结构统一化后，前后端联调更稳定。
- 增加 Makefile 和 GitHub Actions，能明显提升项目可用性与交付完整度。

---

## 第一版本的不足

虽然第一版本已经可运行并具备较完整的基础能力，但仍有这些限制：

- 当前缓存是进程内缓存，不适用于多实例部署
- 暂未实现用户系统、认证与授权
- 搜索仍是关键词匹配，而不是全文检索或语义搜索
- 使用的是 SQLite，更适合作业和单机开发，不适合高并发生产场景
- 目前测试主要集中在 API 层，service/repository 层单元测试仍可增强

---

## 改进版本规划

### V1.0.0

当前版本，也就是第一版本。

已完成：

- 基础任务管理能力
- 依赖关系能力
- 搜索能力
- 缓存能力
- 统一错误处理
- Docker 支持
- GitHub Actions 测试工作流
- 详细 README 文档

### V1.1.0

建议作为第一轮增强版本：

- 增加结构化日志
- 增加更完整的健康检查和 readiness 检查
- 增加更多 service / repository 单元测试
- 增加 `.env.example`
- 增加更明确的业务错误码

### V2.0.0

建议作为进阶版本：

- 数据库切换到 PostgreSQL
- 缓存切换到 Redis
- 引入 Alembic 做数据库迁移
- 增加用户认证与授权
- 增加接口限流
- 增加更完整的部署配置

### V3.0.0

建议作为智能增强版本：

- 接入自然语言建任务
- 自动标签推荐
- 任务优先级推荐
- 任务摘要生成
- 语义搜索
- LLM/Agent 能力扩展

---

## 本轮继续优化内容

相较于前一版 README 和基础实现，本轮新增或优化了以下内容：

- 明确当前项目版本为 `V1.0.0`
- 升级健康检查接口，返回版本、数据库状态、时间戳
- 增加 `Makefile`，简化安装、运行、测试、清理操作
- 增加 GitHub Actions `CI` 工作流
- 增加首页 Dashboard，可直接在浏览器中管理任务
- 将 README 重写为版本化文档
- 补充第一版本功能说明、用法说明、接口示例和版本演进路线

---

## 运行总结

如果你要快速体验当前第一版本，最简单的步骤如下：

1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

2. 启动服务

```bash
uvicorn app.main:app --reload
```

3. 打开 Swagger

```text
http://127.0.0.1:8000/docs
```

4. 运行测试

```bash
pytest -q
```

---

## 耗时

约 4 小时以上，当前已在原始版本基础上继续做了若干交付层优化。
