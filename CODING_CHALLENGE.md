# Intern Coding Challenge: Intelligent Task Management System
# 实习生编程挑战：智能任务管理系统

## Overview
## 概述

Build a **Task Management System** with intelligent features that demonstrates your coding abilities across different specializations. This challenge is designed to evaluate candidates for various roles including Backend, Frontend, Full-Stack, and AI/LLM Development positions.

构建一个带有**智能功能**的**任务管理系统**，以展示你在不同技术方向上的编码能力。这个挑战旨在评估候选人在后端、前端、全栈以及 AI/LLM 开发等不同岗位上的综合表现。

**Time Limit:** 2-4 hours  
**时间限制：** 2-4 小时  
**Submission:** Git repository with clear README and commit history  
**提交形式：** Git 仓库，并附带清晰的 README 与提交历史

---

## Problem Statement
## 题目说明

Create a task management system that allows users to create, organize, and manage tasks with intelligent assistance. The system should have a backend API and can optionally include a frontend interface and/or AI-powered features.

创建一个任务管理系统，使用户能够在智能辅助下创建、组织和管理任务。系统应包含一个后端 API，并可选择性地包含前端界面和/或 AI 驱动功能。

---

## Core Requirements (All Candidates)
## 核心要求（所有候选人都需完成）

### 1. Task CRUD Operations
### 1. 任务 CRUD 操作

Implement a RESTful API or service layer with the following endpoints:

实现一个 RESTful API 或服务层，包含以下接口：

- **CREATE** - Add a new task
- **CREATE** - 新增任务
- **READ** - Get task(s) by ID or list all tasks
- **READ** - 根据 ID 获取任务，或获取全部任务列表
- **UPDATE** - Modify task details
- **UPDATE** - 修改任务详情
- **DELETE** - Remove a task
- **DELETE** - 删除任务

### 2. Task Properties
### 2. 任务属性

Each task should have:

每个任务应包含：

- `id` (unique identifier)
- `id`（唯一标识）
- `title` (string, required)
- `title`（字符串，必填）
- `description` (string, optional)
- `description`（字符串，可选）
- `status` (enum: "pending", "in_progress", "completed")
- `status`（枚举：`"pending"`、`"in_progress"`、`"completed"`）
- `priority` (enum: "low", "medium", "high")
- `priority`（枚举：`"low"`、`"medium"`、`"high"`）
- `created_at` (timestamp)
- `created_at`（时间戳）
- `updated_at` (timestamp)
- `updated_at`（时间戳）
- `tags` (array of strings, optional)
- `tags`（字符串数组，可选）

### 3. Data Persistence
### 3. 数据持久化

Choose appropriate storage:

请选择合适的存储方案：

- **Simple**: JSON file or SQLite
- **简单方案：** JSON 文件或 SQLite
- **Recommended**: MySQL, PostgreSQL, MongoDB, or Redis
- **推荐方案：** MySQL、PostgreSQL、MongoDB 或 Redis
- **Advanced**: Combination of database + cache layer
- **进阶方案：** 数据库 + 缓存层组合

### 4. Code Quality Requirements
### 4. 代码质量要求

- Clean, readable, and well-organized code
- 代码整洁、可读性高、组织清晰
- Proper error handling
- 具备适当的错误处理
- Input validation
- 具备输入校验
- At least basic documentation (README)
- 至少提供基础文档（README）
- Clear commit messages
- Git commit 信息清晰明确

---

## Role-Specific Features (Choose Based on Your Target Role)
## 岗位方向功能要求（根据目标岗位选择）

### Option A: Backend Developer Track
### 选项 A：后端开发方向

Implement these advanced backend features:

请实现以下高级后端功能：

1. **Task Filtering & Sorting**
1. **任务筛选与排序**
   - Filter by status, priority, tags
   - 支持按状态、优先级、标签筛选
   - Sort by creation date, priority, status
   - 支持按创建时间、优先级、状态排序
   - Pagination support
   - 支持分页

2. **Task Dependencies**
2. **任务依赖关系**
   - Tasks can depend on other tasks
   - 任务可以依赖其他任务
   - Cannot mark task as completed if dependencies aren't done
   - 若依赖任务尚未完成，则该任务不能被标记为完成
   - API to query task dependency tree
   - 提供查询任务依赖树的 API

3. **Performance Optimization**
3. **性能优化**
   - Implement caching for frequently accessed data
   - 为高频访问数据实现缓存
   - Database query optimization
   - 优化数据库查询
   - API response time < 100ms for basic operations
   - 基础操作的 API 响应时间应小于 100ms

4. **System Design**
4. **系统设计**
   - Design considerations for scaling to 100k+ tasks
   - 考虑系统扩展到 10 万以上任务时的设计方案
   - Include a brief architecture document
   - 附带一份简要架构文档

**Bonus Points:**
**加分项：**
- Implement search functionality (full-text search)
- 实现搜索功能（全文检索）
- Add user authentication/authorization
- 增加用户认证 / 授权
- Rate limiting for API endpoints
- 为 API 接口添加限流
- Containerization (Docker)
- 使用容器化（Docker）

---

### Option B: Frontend Developer Track
### 选项 B：前端开发方向

Build a user interface with these features:

构建一个具备以下功能的用户界面：

1. **Task Dashboard**
1. **任务仪表盘**
   - Display all tasks in an organized view (list/kanban/calendar)
   - 以有组织的方式展示所有任务（列表 / 看板 / 日历）
   - Visual indicators for priority and status
   - 用可视化方式标识优先级和状态
   - Responsive design (mobile-friendly)
   - 响应式设计（适配移动端）

2. **Interactive Task Management**
2. **交互式任务管理**
   - Drag-and-drop to change status or reorder
   - 支持拖拽修改状态或调整顺序
   - Quick actions (mark complete, delete, edit)
   - 支持快捷操作（标记完成、删除、编辑）
   - Real-time search/filter
   - 支持实时搜索 / 筛选

3. **User Experience**
3. **用户体验**
   - Smooth animations and transitions
   - 流畅的动画和过渡效果
   - Loading states and error messages
   - 加载状态与错误提示
   - Form validation with helpful feedback
   - 表单校验并提供有帮助的反馈

4. **State Management**
4. **状态管理**
   - Proper state management (Context/Redux/Vuex/Pinia)
   - 使用合理的状态管理方案（Context / Redux / Vuex / Pinia）
   - Optimistic UI updates
   - 支持乐观更新
   - Handle edge cases gracefully
   - 优雅处理边界情况

**Tech Stack Options:**
**技术栈可选：**
- React + TypeScript + Tailwind/MUI
- React + TypeScript + Tailwind / MUI
- Vue 3 + TypeScript + Element Plus
- Vue 3 + TypeScript + Element Plus
- Vanilla JavaScript (if you want to show fundamentals)
- 原生 JavaScript（如果你想展示基础能力）

**Bonus Points:**
**加分项：**
- Dark mode support
- 支持深色模式
- Keyboard shortcuts
- 键盘快捷键
- Offline support (PWA)
- 离线支持（PWA）
- Data visualization (charts/graphs)
- 数据可视化（图表 / 统计图）

---

### Option C: Full-Stack Developer Track
### 选项 C：全栈开发方向

Combine backend and frontend requirements:

结合后端与前端要求：

1. **Complete Application**
1. **完整应用**
   - Working backend API (choose from Backend Track features)
   - 可运行的后端 API（从后端方向功能中选择）
   - Functional frontend UI (choose from Frontend Track features)
   - 可用的前端界面（从前端方向功能中选择）
   - Proper integration between frontend and backend
   - 前后端之间集成完整、正确

2. **System Architecture**
2. **系统架构**
   - Clear separation of concerns
   - 清晰的关注点分离
   - RESTful API design or GraphQL
   - RESTful API 设计或 GraphQL
   - Error handling on both layers
   - 前后端都具备错误处理

3. **Deployment Consideration**
3. **部署考虑**
   - Docker compose setup OR deployment instructions
   - 提供 Docker Compose 配置，或部署说明
   - Environment configuration management
   - 管理环境配置
   - Basic CI/CD setup (optional but impressive)
   - 基础 CI/CD 配置（可选，但会加分）

**Bonus Points:**
**加分项：**
- WebSocket for real-time updates
- 使用 WebSocket 实现实时更新
- File upload for task attachments
- 支持任务附件上传
- Export tasks (JSON/CSV/PDF)
- 支持任务导出（JSON / CSV / PDF）

---

### Option D: AI/LLM Developer Track
### 选项 D：AI/LLM 开发方向

Build intelligent features using AI/ML/LLM:

使用 AI / ML / LLM 构建智能功能：

1. **Intelligent Task Generation**
1. **智能任务生成**
   - Natural language task creation: "Remind me to buy groceries tomorrow at 3pm"
   - 支持自然语言创建任务，例如：`"Remind me to buy groceries tomorrow at 3pm"`
   - Extract: title, description, due date, priority from natural language
   - 从自然语言中提取：标题、描述、截止时间、优先级

2. **Smart Task Organization**
2. **智能任务组织**
   - Automatic tag suggestion based on task content
   - 根据任务内容自动推荐标签
   - Priority recommendation using simple ML or LLM
   - 使用简单的 ML 或 LLM 进行优先级推荐
   - Task categorization
   - 任务自动分类

3. **AI Assistant Features** (Choose at least 2)
3. **AI 助手功能**（至少选择 2 项）
   - Task breakdown: split complex task into subtasks
   - 任务拆解：将复杂任务拆分为子任务
   - Task summarization: generate summary of daily/weekly tasks
   - 任务摘要：生成每日 / 每周任务摘要
   - Similar task detection: find related tasks
   - 相似任务检测：查找相关任务
   - Smart search: semantic search instead of keyword matching
   - 智能搜索：使用语义搜索替代关键词匹配

4. **Implementation Options**
4. **实现方式可选**
   - Use OpenAI API / Anthropic API (provide API key handling)
   - 使用 OpenAI API / Anthropic API（需说明 API Key 的处理方式）
   - Use local models (HuggingFace, LangChain)
   - 使用本地模型（HuggingFace、LangChain）
   - Use embeddings + vector database (ChromaDB, FAISS)
   - 使用 embedding + 向量数据库（ChromaDB、FAISS）
   - Build simple ML classifier (sklearn, PyTorch)
   - 构建简单的 ML 分类器（sklearn、PyTorch）

**Bonus Points:**
**加分项：**
- RAG implementation for task knowledge base
- 为任务知识库实现 RAG
- Multi-agent system (planning agent + execution agent)
- 多智能体系统（规划 Agent + 执行 Agent）
- Fine-tuned model for task domain
- 针对任务领域进行模型微调
- Prompt optimization and testing
- Prompt 优化与测试

---

## Technical Constraints
## 技术约束

### Backend Frameworks (Choose one):
### 后端框架（任选其一）：
- **Python**: FastAPI, Flask, Django
- **Python：** FastAPI、Flask、Django
- **Node.js**: Express, NestJS, Fastify
- **Node.js：** Express、NestJS、Fastify
- **Java**: Spring Boot
- **Java：** Spring Boot
- **Go**: Gin, Echo
- **Go：** Gin、Echo
- **Any other**: Justify your choice
- **其他技术：** 需说明你的选择理由

### Database Options:
### 数据库可选：
- SQL: PostgreSQL, MySQL, SQLite
- SQL：PostgreSQL、MySQL、SQLite
- NoSQL: MongoDB, Redis
- NoSQL：MongoDB、Redis
- Vector DB (for AI track): ChromaDB, Pinecone, FAISS
- 向量数据库（AI 方向）：ChromaDB、Pinecone、FAISS

### Frontend Frameworks (if applicable):
### 前端框架（如适用）：
- React, Vue, Angular, Svelte
- React、Vue、Angular、Svelte
- Or vanilla HTML/CSS/JavaScript
- 或原生 HTML / CSS / JavaScript

---

## Evaluation Criteria
## 评估标准

### Code Quality (30%)
### 代码质量（30%）
- Clean, readable code with consistent style
- 代码整洁、可读性强、风格一致
- Proper project structure and organization
- 项目结构合理、组织清晰
- Meaningful variable/function names
- 变量 / 函数命名具有实际含义
- Comments where necessary (not excessive)
- 在必要处添加注释（不过度）
- Error handling and edge cases
- 具备错误处理并考虑边界情况

### Problem-Solving (30%)
### 问题解决能力（30%）
- Correct implementation of requirements
- 正确实现需求
- Algorithmic efficiency
- 算法效率合理
- Handling of edge cases
- 能处理边界情况
- Creative solutions to challenges
- 对挑战有创造性的解决方案

### System Design (25%)
### 系统设计（25%）
- Appropriate architecture choices
- 架构选择合理
- Scalability considerations
- 考虑可扩展性
- Database schema design
- 数据库 schema 设计合理
- API design (RESTful principles or GraphQL)
- API 设计规范（遵循 RESTful 原则或使用 GraphQL）
- Separation of concerns
- 做到良好的关注点分离

### Documentation (15%)
### 文档（15%）
- Clear README with:
- 提供清晰的 README，包含：
  - Project description
  - 项目说明
  - Setup instructions
  - 安装与启动说明
  - API documentation
  - API 文档
  - Design decisions and trade-offs
  - 设计决策与取舍
  - Known limitations
  - 已知限制
  - Future improvements
  - 后续可改进点
- Code comments where appropriate
- 在适当位置添加代码注释
- Commit history quality
- Git 提交历史质量良好

---

## Submission Requirements
## 提交要求

### 1. Git Repository
### 1. Git 仓库
- Initialize git from the start
- 从项目一开始就初始化 git
- Make meaningful commits (not just one big commit)
- 做有意义的提交（不要只提交一次大改动）
- Include a `.gitignore` file
- 包含 `.gitignore` 文件
- **Do NOT commit**: API keys, node_modules, venv, IDE configs
- **不要提交：** API Key、`node_modules`、`venv`、IDE 配置等内容

### 2. README.md
### 2. README.md

Must include:

必须包含：

```markdown
# Project Title
# 项目标题

## Role Track
## 岗位方向
[Backend / Frontend / Full-Stack / AI-LLM]
[后端 / 前端 / 全栈 / AI-LLM]

## Tech Stack
## 技术栈
- Language:
- 语言：
- Framework:
- 框架：
- Database:
- 数据库：
- Other tools:
- 其他工具：

## Features Implemented
## 已实现功能
- [ ] Feature 1
- [ ] 功能 1
- [ ] Feature 2
- [ ] 功能 2
...

## Setup Instructions
## 安装与运行说明
1. Prerequisites
1. 前置依赖
2. Installation steps
2. 安装步骤
3. Configuration
3. 配置方式
4. Running the application
4. 启动应用

## API Documentation
## API 文档
[Endpoints, request/response examples]
[接口列表、请求 / 响应示例]

## Design Decisions
## 设计决策
[Why you chose certain technologies or approaches]
[为什么选择这些技术或方案]

## Challenges & Solutions
## 挑战与解决方案
[Problems you faced and how you solved them]
[你遇到了哪些问题，以及如何解决]

## Future Improvements
## 后续改进
[What you would add with more time]
[如果有更多时间，你会补充什么]

## Time Spent
## 耗时
Approximately X hours
约 X 小时
```

### 3. Code Structure Example
### 3. 代码结构示例

```text
project/
├── README.md
├── requirements.txt / package.json
├── .gitignore
├── src/
│   ├── models/
│   ├── controllers/
│   ├── services/
│   ├── routes/
│   └── utils/
├── tests/ (optional but recommended / 可选但推荐)
└── docs/ (optional / 可选)
```

---

## Bonus Points (Optional)
## 加分项（可选）

- **Testing**: Unit tests, integration tests
- **测试：** 单元测试、集成测试
- **CI/CD**: GitHub Actions workflow
- **CI/CD：** GitHub Actions 工作流
- **Logging**: Structured logging implementation
- **日志：** 结构化日志实现
- **Monitoring**: Health check endpoints
- **监控：** 健康检查接口
- **Security**: SQL injection prevention, XSS protection, CORS setup
- **安全：** 防 SQL 注入、XSS 防护、CORS 配置
- **Performance**: Load testing results, optimization documentation
- **性能：** 压测结果、性能优化文档
- **Accessibility**: WCAG compliance (for frontend)
- **无障碍：** 符合 WCAG 标准（前端方向）

---

## FAQs
## 常见问题

**Q: Can I use external libraries/frameworks?**  
**问：我可以使用外部库 / 框架吗？**  
A: Yes, but justify your choices. Using too many unnecessary libraries may count against you.  
答：可以，但请说明你的选择理由。使用过多不必要的库可能会影响评价。

**Q: Can I use AI assistants (ChatGPT, Copilot)?**  
**问：我可以使用 AI 助手（ChatGPT、Copilot）吗？**  
A: Mention it in your README if you do. We value your understanding and decision-making more than perfect code.  
答：可以，但如果使用了，请在 README 中说明。我们更看重你的理解能力和决策过程，而不仅仅是“完美代码”。

**Q: What if I can't finish everything?**  
**问：如果我没法把所有内容都做完怎么办？**  
A: Submit what you have with clear documentation of what's complete and what's pending. Quality > Quantity.  
答：提交你已完成的部分，并清楚说明哪些已完成、哪些仍待完成。质量比数量更重要。

**Q: Can I choose multiple tracks?**  
**问：我可以同时选择多个方向吗？**  
A: Advanced candidates can combine tracks (e.g., Full-Stack + AI features), but ensure quality doesn't suffer.  
答：可以。进阶候选人可以组合多个方向（例如全栈 + AI 功能），但前提是不要因此牺牲整体质量。

**Q: Should I deploy the application?**  
**问：我需要部署应用吗？**  
A: Not required, but providing a live demo is impressive. At minimum, provide clear local setup instructions.  
答：不是必须，但如果你能提供在线演示会很加分。至少请提供清晰的本地运行说明。

---

Good luck! We're looking forward to seeing your solution. Remember: we value **clean code, good design, and clear thinking** over feature completeness.

祝你好运！我们很期待看到你的解决方案。请记住：相比功能是否全部做完，我们更看重**代码整洁、设计合理以及思路清晰**。
