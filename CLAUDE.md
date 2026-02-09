# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 部署铁令（CRITICAL - MUST FOLLOW）

**每次部署必须严格遵守以下铁令，这是最高优先级的规则！**

### 铁令 1: 部署标准
1. ✅ **按照云上方式部署**：部署的前缀、挂载路径必须明确写入配置
2. ✅ **部署后必须测试**：确保所有功能正常工作后才算部署完成

### 铁令 2: 测试标准
**所有 HTTP 测试必须返回 200 状态码才算成功！**
- ❌ 错误示例：期望返回 `{"detail":"Incorrect username or password"}` 来证明 API 可访问
- ✅ 正确示例：使用正确的账号密码，期望返回 `{"access_token":"..."}` 和 HTTP 200

### 铁令 3: 部署文档
**必须严格按照 `DEPLOYMENT_STANDARD.md` 文档执行部署、测试和检查！**
- 不得跳过任何测试步骤
- 不得修改测试标准
- 必须填写部署检查表

### 铁令 4: K8s 部署配置
**前端构建必须使用以下环境变量：**
```bash
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
```
- 前端访问路径：`/web-manager/`
- 后端 API 路径：`/dbmanage/api/v1`
- 不得使用其他路径配置

---

## Project Overview

LLM Guard Manager is a full-stack web application for managing LLM (Large Language Model) safety guardrails and content filtering policies. It provides a comprehensive platform for configuring sensitive word libraries, classification tags, filtering rules, and testing content against configured policies.

## Architecture

**Monorepo Structure:**
- `backend/` - FastAPI async Python backend
- `frontend/` - React + TypeScript + Vite frontend
- Nginx reverse proxy for production deployment

**Tech Stack:**
- Backend: FastAPI, SQLAlchemy 2.0 (async), MySQL (aiomysql), JWT auth, Pydantic v2
- Frontend: React 18, TypeScript, Ant Design 5, Axios, React Router v6, Vite 5
- Infrastructure: Docker, Nginx, Uvicorn

## Development Commands

### Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (with hot reload)
python run.py
# Server runs on http://localhost:9001

# Run tests
pytest
# Or run specific test file
pytest tests/api/v1/test_meta_tags.py

# Run tests with verbose output
pytest -v
```

### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (with Vite proxy to backend)
npm run dev
# Server runs on http://localhost:5173
# API requests to /api/* are proxied to http://127.0.0.1:9001

# Build for production
npm run build
# Output to frontend/dist/

# Lint TypeScript/TSX files
npm run lint

# Preview production build
npm run preview
```

### Docker Deployment

```bash
# Build and run both containers
./run_docker.sh

# Backend container: http://localhost:39001
# Frontend container: http://localhost:35173
```

## Database Configuration

**Connection Details:**
- Database: MySQL (llm_safe_db)
- Connection string in `backend/app/core/config.py`
- Default: `mysql+aiomysql://root:Platform#2026@49.233.46.126:38306/llm_safe_db?charset=utf8mb4`

**Database Initialization:**
```bash
cd backend
python init_db.py  # Initialize database schema
```

## Code Architecture

### Backend Layered Architecture

The backend follows a clean 4-layer architecture:

```
API Layer (app/api/v1/endpoints/)
    ↓ HTTP request/response, route definitions
Service Layer (app/services/)
    ↓ Business logic, validation, external service calls
Repository Layer (app/repositories/)
    ↓ Data access, query building, CRUD operations
Model Layer (app/models/db_meta.py)
    ↓ SQLAlchemy ORM definitions
```

**Key Patterns:**
- All database operations are async (AsyncSession)
- Repositories inherit from `BaseRepository` with generic CRUD methods
- Services handle business logic and uniqueness validation
- Pydantic schemas for request/response validation
- JWT authentication via dependency injection (`get_current_user`)

**Adding a New Feature:**
1. Define ORM model in `app/models/db_meta.py`
2. Create Pydantic schemas in `app/schemas/`
3. Implement repository in `app/repositories/` (inherit from `BaseRepository`)
4. Write service logic in `app/services/`
5. Create API endpoints in `app/api/v1/endpoints/`
6. Register router in `app/api/v1/api.py`

### Frontend Component Structure

```
App.tsx (Main Router)
├─ LoginPage (Authentication)
└─ AppLayout (Protected Routes)
    ├─ MetaTags.tsx (Tag Management)
    ├─ GlobalKeywords.tsx (Global Keywords Library)
    ├─ GlobalPolicies.tsx (Global Default Rules)
    ├─ Apps.tsx (Scenario/Application Management)
    ├─ AppDashboard.tsx (App Overview)
    ├─ ScenarioKeywords.tsx (Scenario-specific Keywords)
    ├─ ScenarioPolicies.tsx (Scenario-specific Rules)
    └─ InputPlayground.tsx (Testing Interface with History)
```

**Key Files:**
- `src/api.ts` - Axios client with all API endpoints and JWT interceptor
- `src/types.ts` - TypeScript interfaces for all data models
- `src/App.tsx` - Main routing and authentication layout

## Core Domain Models

### Meta Tags (`meta_tags`)
Hierarchical content classification system with parent-child relationships.
- Fields: `id`, `tag_code` (unique), `tag_name`, `parent_code`, `level`, `is_active`

### Global Keywords (`lib_global_keywords`)
Centralized sensitive word repository shared across all scenarios.
- Fields: `id`, `keyword` (unique), `tag_code`, `risk_level`, `is_active`
- Risk levels: High, Medium, Low

### Scenario Keywords (`lib_scenario_keywords`)
Scenario-specific sensitive words with whitelist/blacklist support.
- Fields: `id`, `scenario_id`, `keyword`, `tag_code`, `category`, `risk_level`
- Category: 0=Whitelist, 1=Blacklist
- Uniqueness: `keyword` + `scenario_id` combination must be unique

### Scenarios (`scenarios`)
Application/scenario definitions with feature flags.
- Fields: `id`, `app_id` (unique), `app_name`, `is_active`, `enable_whitelist`, `enable_blacklist`, `enable_customize_policy`

### Rule Policies
Two-tier policy system:
- **Scenario Policies** (`rule_scenario_policy`): Per-scenario rules with KEYWORD or TAG matching
- **Global Defaults** (`rule_global_defaults`): Fallback policies when scenario rules don't match

### Playground History (`playground_history`)
Audit trail for testing with request/response data and latency metrics.
- Fields: `id`, `request_id`, `app_id`, `input_data` (JSON), `output_data` (JSON), `score`, `latency`, `upstream_latency`

## API Structure

**Base URL:** `/api/v1`

**Authentication:** JWT Bearer token (8-day expiration)

**Endpoint Groups:**
- `/login/access-token` - Authentication
- `/tags/` - Meta tags management
- `/keywords/global/` - Global keywords CRUD
- `/keywords/scenario/{scenarioId}` - Scenario keywords CRUD
- `/policies/scenario/{scenarioId}` - Scenario policies CRUD
- `/policies/defaults/` - Global default policies CRUD
- `/apps/` - Scenario/application management
- `/playground/input` - Test content filtering
- `/playground/history` - Get playground history

## Data Validation & Uniqueness

**Critical Uniqueness Constraints:**
- Global keywords: `keyword` must be globally unique
- Scenario keywords: `keyword` + `scenario_id` must be unique
- Meta tags: `tag_code` must be globally unique
- Scenarios: `app_id` must be globally unique

**Validation Flow:**
1. Pydantic schema validation (type checking, required fields)
2. Service layer business logic validation (uniqueness checks)
3. Database constraints (unique indexes)

## External Service Integration

**Guardrail Service:**
- URL: `http://127.0.0.1:8000/api/input/instance/rule/run`
- Called by `PlaygroundService.run_input_check()`
- Measures total latency and upstream service latency
- Captures response even if upstream service fails

**Decision Scores:**
- 0 = Pass
- 50 = Rewrite
- 100 = Block
- 1000 = Manual Review

## Testing

**Backend Tests:**
- Framework: pytest + pytest-asyncio
- Location: `backend/tests/`
- Configuration: `backend/pytest.ini`
- Run all tests: `pytest`
- Run specific test: `pytest tests/api/v1/test_meta_tags.py`

**Test Structure:**
- `conftest.py` - Test fixtures and database setup
- `tests/api/v1/` - API endpoint tests

## Configuration Files

**Backend:**
- `backend/app/core/config.py` - Settings (database URL, JWT secret, token expiration)
- `backend/run.py` - Uvicorn server entry point
- `backend/requirements.txt` - Python dependencies
- `backend/pytest.ini` - Pytest configuration

**Frontend:**
- `frontend/vite.config.ts` - Vite build config with proxy to backend
- `frontend/package.json` - Node dependencies and scripts
- `frontend/tsconfig.json` - TypeScript configuration

**Deployment:**
- `nginx.conf` - Nginx reverse proxy configuration
- `run_docker.sh` - Docker deployment script

## Development Workflow

**Starting Development:**
1. Start backend: `cd backend && python run.py`
2. Start frontend: `cd frontend && npm run dev`
3. Access frontend at http://localhost:5173
4. API requests automatically proxied to backend at http://localhost:9001

**Making Changes:**
- Backend changes trigger auto-reload (Uvicorn reload=True)
- Frontend changes trigger HMR (Vite Hot Module Replacement)

**Before Committing:**
- Run backend tests: `cd backend && pytest`
- Run frontend linter: `cd frontend && npm run lint`
- Build frontend to verify: `cd frontend && npm run build`

## 工作规则（Working Rules）

### 规则 1: 长文档分段写入
**写入长文档时必须分段写入，不要一次性写入！**
- 每次写入控制在合理长度
- 可以使用 `cat >>` 追加内容
- 避免因内容过长导致写入失败

### 规则 2: 简单问题直接回答
**对于简单问题，先给出直接答案，不要过度工程化！**
- 不要创建不必要的文件
- 不要做不必要的修改
- 先回答问题，再问是否需要更多

### 规则 3: 约束优先
**在实现之前，先确认约束条件！**
- 是否需要修改代码？
- 是否只需要配置修改？
- 使用什么凭据？

---

## Important Notes

**Async/Await Pattern:**
- All database operations use async/await with AsyncSession
- HTTP calls to external services use httpx.AsyncClient
- Enables high concurrency and non-blocking I/O

**Authentication:**
- JWT tokens stored in localStorage on frontend
- Axios interceptor adds token to all requests
- Protected routes redirect to login if unauthenticated
- Token expiration: 8 days (configurable in `config.py`)

**CORS Configuration:**
- Backend allows all origins in development (`allow_origins=["*"]`)
- Production should restrict to specific frontend domain

**Port Configuration:**
- Backend development: 9001
- Frontend development: 5173 (Vite default)
- Backend production (Docker): 39001
- Frontend production (Docker): 35173
