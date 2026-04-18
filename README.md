# Project Title
# 项目标题

智能任务管理系统

一个基于 FastAPI 的任务管理系统，覆盖 `CODING_CHALLENGE.md` 中的后端方向核心要求，并补充了一个可直接演示的前端控制台。

项目支持任务 CRUD、筛选排序分页、依赖关系、搜索、缓存和统一错误处理，同时提供 Docker 与基础 CI 配置，便于本地运行和提交展示。

## Role Track
## 岗位方向

Backend
后端

## Tech Stack
## 技术栈

- Language / 语言：Python 3.13
- Framework / 框架：FastAPI
- Database / 数据库：SQLite
- Other tools / 其他工具：SQLAlchemy, Pydantic v2, pytest, Docker, Docker Compose, GitHub Actions, Vanilla JavaScript

## Features Implemented
## 已实现功能

- [x] Task CRUD API
- [x] 任务的创建、查询、更新、删除
- [x] Filter by status, priority, tags
- [x] 按状态、优先级、标签筛选
- [x] Sort by creation date, priority, status
- [x] 按创建时间、优先级、状态排序
- [x] Pagination support
- [x] 分页支持
- [x] Task dependencies and dependency tree API
- [x] 任务依赖关系与依赖树接口
- [x] Prevent completing tasks with unfinished dependencies
- [x] 未完成依赖时禁止完成任务
- [x] Prevent duplicate/self/cyclic dependencies
- [x] 阻止重复依赖、自依赖和循环依赖
- [x] Keyword search on title and description
- [x] 标题和描述关键词搜索
- [x] Local TTL cache for frequently accessed read endpoints
- [x] 高频读接口本地 TTL 缓存
- [x] Unified validation and error responses
- [x] 统一校验与错误响应
- [x] Browser dashboard for task management and filtering
- [x] 浏览器端任务管理与筛选面板
- [x] Docker / Docker Compose support
- [x] Docker / Docker Compose 支持
- [x] Basic GitHub Actions CI
- [x] 基础 GitHub Actions CI

## Setup Instructions
## 安装与运行说明

### 1. Prerequisites
### 1. 前置依赖

- Python 3.13
- `pip`
- Docker（如果要使用容器运行）

### 2. Installation Steps
### 2. 安装步骤

安装依赖：

```bash
python -m pip install -r requirements.txt
```

### 3. Configuration
### 3. 配置方式

可选环境变量：

- `DATABASE_URL`
  默认值：`sqlite:///./task_manager.db`

- `CACHE_TTL_SECONDS`
  默认值：`60`

### 4. Running the Application
### 4. 启动应用

本地运行：

```bash
uvicorn app.main:app --reload
```

启动后可访问：

- 首页 Dashboard：`http://127.0.0.1:8000/`
- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- 健康检查：`http://127.0.0.1:8000/health`

Docker 运行：

```bash
docker compose up --build
```

停止容器：

```bash
docker compose down
```

## API Documentation
## API 文档

主要接口：

- `GET /health`
- `POST /api/tasks`
- `GET /api/tasks`
- `GET /api/tasks/search`
- `GET /api/tasks/{task_id}`
- `PATCH /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/dependencies/{dependency_id}`
- `DELETE /api/tasks/{task_id}/dependencies/{dependency_id}`
- `GET /api/tasks/{task_id}/dependencies/tree`

### Example 1: Create Task
### 示例 1：创建任务

请求：

```http
POST /api/tasks
Content-Type: application/json
```

```json
{
  "title": "准备发布检查清单",
  "description": "补充文档、镜像和测试结果",
  "status": "pending",
  "priority": "high",
  "tags": ["backend", "release"]
}
```

响应：

```json
{
  "id": "9b6c9f7f-7a1e-4d0b-84ec-7f7fbe7e1d25",
  "title": "准备发布检查清单",
  "description": "补充文档、镜像和测试结果",
  "status": "pending",
  "priority": "high",
  "created_at": "2026-04-18T17:00:00.000000",
  "updated_at": "2026-04-18T17:00:00.000000",
  "tags": ["backend", "release"]
}
```

### Example 2: List Tasks with Filters
### 示例 2：带筛选条件的任务列表

请求：

```http
GET /api/tasks?status=pending&tags=backend&sort_by=priority&order=desc&page=1&page_size=10
```

响应：

```json
{
  "items": [
    {
      "id": "9b6c9f7f-7a1e-4d0b-84ec-7f7fbe7e1d25",
      "title": "准备发布检查清单",
      "description": "补充文档、镜像和测试结果",
      "status": "pending",
      "priority": "high",
      "created_at": "2026-04-18T17:00:00.000000",
      "updated_at": "2026-04-18T17:00:00.000000",
      "tags": ["backend", "release"]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

### Example 3: Dependency Tree
### 示例 3：依赖树查询

请求：

```http
GET /api/tasks/{task_id}/dependencies/tree
```

响应：

```json
{
  "id": "task-c",
  "title": "补充集成测试",
  "description": null,
  "status": "pending",
  "priority": "low",
  "tags": ["test"],
  "dependencies": [
    {
      "id": "task-b",
      "title": "实现服务层",
      "description": null,
      "status": "pending",
      "priority": "medium",
      "tags": ["backend"],
      "dependencies": [
        {
          "id": "task-a",
          "title": "完成数据库设计",
          "description": null,
          "status": "completed",
          "priority": "high",
          "tags": ["backend"],
          "dependencies": []
        }
      ]
    }
  ]
}
```

更完整的接口调试和 schema 可直接查看 Swagger：`/docs`

## Performance Check
## 性能验证

提供了一个轻量基准脚本：

```bash
python scripts/benchmark_basic_ops.py
```

说明：

- 该脚本使用 `TestClient` 在进程内运行，不包含真实网络传输开销
- 它更适合验证“当前实现本身是否明显超出题目要求”，而不是替代正式压测

一次本地参考结果（`2026-04-18`，临时 SQLite 数据库，预置 120 条任务）：

```text
POST /api/tasks                avg=2.29ms  p95=2.64ms  max=2.72ms
GET /api/tasks/{id} MISS       avg=1.59ms  p95=1.82ms  max=3.54ms
GET /api/tasks/{id} HIT        avg=0.65ms  p95=0.71ms  max=0.90ms
GET /api/tasks MISS            avg=2.93ms  p95=3.89ms  max=4.00ms
GET /api/tasks HIT             avg=0.84ms  p95=0.89ms  max=0.92ms
GET /api/tasks/search MISS     avg=2.60ms  p95=3.17ms  max=3.18ms
GET /api/tasks/search HIT      avg=0.79ms  p95=0.87ms  max=1.03ms
```

这组结果说明当前本地实现下，基础操作明显低于题目中提到的 `<100ms` 目标；但它仍然只是开发机上的进程内参考值，不等同于真实线上压测数据。

## Design Decisions
## 设计决策

- 选择 FastAPI，因为它开发效率高、类型提示清晰，并自带 OpenAPI 文档
- 选择 SQLAlchemy 分离数据模型与查询逻辑，便于后续扩展
- 采用 `Router -> Service -> Repository` 分层，降低接口层和数据层耦合
- 选择 SQLite 作为挑战场景下的轻量持久化方案，方便快速运行和验证
- 标签与依赖关系单独建表，便于筛选、约束校验和后续统计
- 读接口使用进程内 TTL 缓存，以较低复杂度提升热点读取性能
- 详细架构说明见：[docs/architecture.md](docs/architecture.md)

## Challenges & Solutions
## 挑战与解决方案

- Challenge / 挑战：前端标签选择和筛选状态一度互相污染  
  Solution / 解决：拆分表单标签状态、筛选标签状态和可选标签统计，避免共享同一份可变状态

- Challenge / 挑战：Dashboard 统计区曾因非法分页参数导致刷新后显示为 0  
  Solution / 解决：改为遵守后端 `page_size <= 100` 限制的分页汇总读取，并补齐前端错误处理

- Challenge / 挑战：GitHub Actions 在干净环境里失败  
  Solution / 解决：补充 `httpx` 到依赖中，因为 `fastapi.testclient.TestClient` 依赖它

- Challenge / 挑战：依赖关系需要同时满足业务规则和结构安全  
  Solution / 解决：在 Service 层增加自依赖、重复依赖、循环依赖和未完成依赖校验

## Known Limitations
## 已知限制

- 当前缓存是进程内缓存，不适合多实例部署
- 当前数据库为 SQLite，更适合本地开发和挑战演示
- 当前搜索是关键词匹配，不是全文检索或语义搜索
- 暂未实现认证、授权和限流
- 测试以 API 集成为主，Repository / Service 层单元测试仍可继续补强

## Future Improvements
## 后续改进

- 切换到 PostgreSQL，并引入 Alembic 做数据库迁移
- 将本地缓存替换为 Redis，并优化更细粒度的失效策略
- 增加全文检索或语义搜索
- 增加认证、授权和接口限流
- 为 100k+ 任务场景增加更明确的索引、游标分页和聚合统计方案
- 增加导出能力、附件能力和更丰富的可观测性

## AI Usage
## AI 工具使用说明

本项目开发过程中使用了 AI 编码助手进行辅助，包括需求理解、文档润色、问题排查、前端交互细节调整和部分实现方案讨论。

本次使用的 AI 工具为：

- Codex / ChatGPT（用于开发辅助、调试分析、README 与架构文档整理）

说明：

- AI 主要作为辅助工具参与分析、重构建议、Bug 排查和文档表达优化
- 开发者本人主要负责 Python 后端实现
- 前端部分的原始目标是使用简单 HTML 做一个基础可视化页面，用于演示后端接口和任务数据
- 在完成基础可视化后，由于原页面较为简约、视觉表现不够理想，因此使用 AI 协助优化了前端展示层
- AI 主要参与了前端页面的美化与交互完善，涉及 CSS、JavaScript 以及部分 HTML 结构调整
- 最终代码结构、功能取舍、测试执行和提交内容由开发者确认与落地
- 项目运行时本身不依赖外部 AI API，也不包含需要额外配置的 AI 服务

## Time Spent
## 耗时

Approximately 4 hours for the original challenge scope, with additional time spent later on bug fixes, UI polishing, CI repair, and documentation refinement.  
核心挑战范围约 3 小时完成，之后又额外投入了一些时间用于修复缺陷、优化界面、修复 CI 和完善文档。
