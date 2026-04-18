# 智能任务管理系统

基于 `CODING_CHALLENGE.md` 实现的任务管理系统，包含可运行的后端 API 和一个直接连接后端的前端控制台。

本项目主要覆盖后端方向要求，并补充了一个可演示的前端界面，便于直接体验任务创建、筛选、搜索、依赖管理和状态流转。

## 挑战要求覆盖情况

### 核心要求

- 支持任务 CRUD
- 任务字段包含 `id`、`title`、`description`、`status`、`priority`、`created_at`、`updated_at`、`tags`
- 使用 SQLite 做数据持久化
- 具备输入校验、统一错误处理和基础文档

### 后端方向能力

- 任务列表支持按状态、优先级、标签筛选
- 支持按创建时间、优先级、状态排序
- 支持分页
- 支持任务依赖关系
- 未完成依赖时不可将任务标记为完成
- 支持依赖树查询
- 阻止自依赖、重复依赖和循环依赖
- 对高频读接口实现了本地 TTL 缓存
- 支持标题和描述关键词搜索
- 提供简要架构文档：[docs/architecture.md](docs/architecture.md)

### 额外交付

- 浏览器端 Dashboard，可直接操作任务
- Docker / Docker Compose 运行支持
- GitHub Actions 基础 CI

## 技术栈

- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic v2
- SQLite
- pytest
- 原生 HTML / CSS / JavaScript

## 如何运行

### 本地运行

安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动服务：

```bash
uvicorn app.main:app --reload
```

启动后可访问：

- 首页：`http://127.0.0.1:8000/`
- Swagger 文档：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- 健康检查：`http://127.0.0.1:8000/health`

### Docker 运行

```bash
docker compose up --build
```

停止：

```bash
docker compose down
```

## 如何测试

运行测试：

```bash
pytest -q
```

当前测试主要覆盖：

- 健康检查
- 首页可访问性
- 任务 CRUD
- 筛选、排序、分页
- 搜索
- 缓存命中与失效
- 依赖关系与依赖树
- 错误响应

## 主要接口

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

更完整的请求结构和在线调试可以直接查看 Swagger：`/docs`

## 项目结构

```text
Creaition-coding_test/
├── app/
│   ├── api/            # 路由层
│   ├── core/           # 配置、数据库、缓存
│   ├── models/         # ORM 模型
│   ├── repositories/   # 数据访问层
│   ├── schemas/        # 请求/响应模型
│   ├── services/       # 业务逻辑层
│   ├── static/         # 前端页面资源
│   └── main.py         # 应用入口
├── docs/
│   └── architecture.md
├── tests/
│   └── test_task_api.py
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 设计说明

- 使用 FastAPI 提升开发效率，并直接提供 OpenAPI 文档
- 使用 SQLAlchemy 做清晰的模型映射与分层访问
- 采用 `Router -> Service -> Repository` 分层，便于隔离接口、业务规则和数据库逻辑
- 使用 SQLite 作为挑战场景下的轻量持久化方案，便于快速运行和验证
- 标签与依赖关系独立建表，方便扩展和约束校验
- 读接口使用进程内 TTL 缓存，写操作后统一失效，降低重复读取成本

## 已知取舍与后续可改进点

- 当前缓存是进程内缓存，不适合多实例部署
- 当前数据库为 SQLite，更适合本地开发和挑战演示
- 搜索是关键词匹配，不是全文检索或语义搜索
- 暂未实现认证、授权和限流
- 测试以 API 集成为主，Repository / Service 层还能继续补单元测试

## 环境变量

- `DATABASE_URL`
  默认值：`sqlite:///./task_manager.db`

- `CACHE_TTL_SECONDS`
  默认值：`60`
