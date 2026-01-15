# LLM Guard Manager - Project Context

## **对于系统建设的最重要的几点原则**
* **所有输出，请用中文作答。**
* **绝对不允许删除数据库里面的数据！**
## Project Overview

**LLM Guard Manager** is a full-stack visualization platform designed to manage security and compliance policies for Large Language Model (LLM) applications. It enables administrators to configure:

*   **Meta Tags:** Content classification tags with hierarchical structures.
*   **Global Keywords:** General sensitive word lists (blacklists/whitelists).
*   **Scenario Keywords:** Context-specific keyword lists.
*   **Policies:** Rules defining actions (Block, Pass, Rewrite) based on keyword or tag matches.

## Technology Stack

### Backend
*   **Language:** Python
*   **Framework:** FastAPI
*   **Database ORM:** SQLAlchemy (Async)
*   **Database Driver:** `aiomysql` (MySQL)
*   **Validation:** Pydantic
*   **Testing:** `pytest`

### Frontend
*   **Library:** React
*   **Build Tool:** Vite
*   **Language:** TypeScript
*   **UI Framework:** Ant Design (`antd`)
*   **HTTP Client:** Axios

### Infrastructure
*   **Containerization:** Docker
*   **Web Server/Reverse Proxy:** Nginx

## Architecture

### Backend Structure (`backend/`)
The backend follows a layered architecture to separate concerns:
*   `app/api/v1/`: API route definitions.
*   `app/core/`: Core configuration (`config.py`) and security settings.
*   `app/models/`: SQLAlchemy database models.
*   `app/schemas/`: Pydantic models for request/response validation.
*   `app/repositories/`: Data access layer (CRUD operations).
*   `app/services/`: Business logic layer.
*   `tests/`: Unit and integration tests.

### Frontend Structure (`frontend/`)
Standard Vite + React + TypeScript setup:
*   `src/pages/`: Application views (Dashboard, Keywords, Policies, etc.).
*   `src/api.ts`: Centralized API calls.
*   `src/types.ts`: TypeScript interfaces.

## Development Setup

### Prerequisites
*   Python 3.10+
*   Node.js & npm
*   MySQL Database (Connection string in `backend/app/core/config.py`)

### Backend Setup
1.  Navigate to `backend/`.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Initialize/Seed Database (if applicable):
    ```bash
    python init_db.py
    ```
4.  Run the development server:
    ```bash
    python run.py
    # OR directly with uvicorn
    uvicorn app.main:app --reload --port 9001
    ```
    *API documentation available at `http://localhost:9001/docs`*

### Frontend Setup
1.  Navigate to `frontend/`.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    *Access the app at `http://localhost:5173` (or port specified by Vite)*

### Docker Deployment
The project includes a `run_docker.sh` script to run the application using Docker:
*   **Backend:** Maps host port `39001` to container port `9001`.
*   **Frontend:** Maps host port `35173` to container port `80`. Nginx is configured to proxy `/api/` requests to the backend.

## Key Conventions

*   **API Versioning:** All API endpoints are prefixed with `/api/v1`.
*   **Configuration:** Backend settings (DB URL, Secrets) are managed in `backend/app/core/config.py` using `pydantic-settings`.
*   **Data Flow:** Controller (`api`) -> Service (`services`) -> Repository (`repositories`) -> Database (`models`).
*   **Frontend API:** API calls are typically abstracted in `src/api.ts` or within feature-specific files.

## Updates Log

### 2026-01-12
*   **New Feature - Input Playground (Requirement 2.6.1):**
    *   **Frontend:** Added `InputPlayground.tsx`.
        *   Interactive interface for testing guardrail policies.
        *   Supports scenario selection (`app_id`), text input, and configuration switches (White/Blacklists, Custom Rules).
        *   Visualizes results with color-coded scores (Pass, Rewrite, Block, Manual Review).
    *   **Backend:** Added `Playground` module.
        *   **Schema:** Defined `InputPrompt` schema in `app/schemas/playground.py` for request validation.
        *   **API:** Implemented `POST /api/v1/playground/input` in `app/api/v1/endpoints/playground.py`.
        *   **Logic:** Acts as a proxy, forwarding requests to the internal guardrail service (`http://127.0.0.1:8000/api/input/instance/rule/run`), injecting `request_id` and handling the response.

### 2026-01-11
*   **Frontend - ScenarioPolicies Enhancement:**
    *   Improved `ScenarioPolicies.tsx` to support dynamic tag selection.
    *   Added `MetaTag` fetching logic to the page.
    *   Replaced manual input for `match_value` (when type is TAG) and `extra_condition` (when type is KEYWORD) with an Ant Design `Select` component populated with existing tags.
    *   Ensured form validation and searchability within the tag selection.
*   **Backend - Data Consistency & Uniqueness:**
    *   **Scenario Keywords:** Implemented uniqueness check on create. Validates that `(scenario_id, keyword)` is unique.
    *   **Scenario Policies:** Implemented uniqueness check on create. Validates that `(scenario_id, rule_mode, match_type, match_value)` is unique.
    *   **Global Defaults:** Implemented uniqueness check on create. Validates that `(tag_code, extra_condition)` is unique.
    *   **Repositories:** Added helper methods `get_by_scenario_and_keyword` and `get_duplicate` to support these checks.
    *   **API Endpoints:** Updated `scenario_keywords.py` and `rule_policy.py` to catch `ValueError` from services and raise `HTTPException(400)` with the specific error message. This ensures the frontend receives the detailed "duplicate entry" message instead of a generic server error.
*   **Frontend - Error Handling:**

    *   Updated `ScenarioPolicies.tsx`, `ScenarioKeywords.tsx`, and `GlobalPolicies.tsx` to handle backend errors gracefully.
    *   Enhanced `handleOk` methods to catch API errors and display detailed error messages (e.g., duplicate entry warnings) returned by the backend using `error.response.data.detail`.
    *   **Navigation Fix:** Updated `AppDashboard.tsx` to use explicit `navigate('/apps')` instead of `window.history.back()`. This resolves the navigation loop issue where users could get stuck between the Dashboard and sub-pages (Keywords/Policies) when using the "Back" buttons.

### 2026-01-12 (Cont.)
*   **New Feature - Playground History (Requirement 2.7):**
    *   **Backend:**
        *   **Model:** Added `PlaygroundHistory` model in `app/models/db_meta.py` to store interaction logs (`input_data`, `config_snapshot`, `output_data`, `score`, `playground_type`).
        *   **Repository:** Created `PlaygroundHistoryRepository` for DB operations.
        *   **Service:** Updated `PlaygroundService` to save history records asynchronously after each successful playground run. Fixed ID generation issue by explicitly creating UUIDs.
        *   **API:** Added `GET /api/v1/playground/history` endpoint with filtering by `playground_type` and pagination support.
    *   **Frontend:**
        *   **History Drawer:** Added a "History" button in `InputPlayground.tsx` that opens a drawer listing past interactions.
        *   **Restore Functionality:** Users can click a "Restore" button to reload a previous configuration and input prompt into the form.
        *   **Detail View:** Added a "View Details" modal to inspect full JSON payloads (Input, Config, Output) for deep debugging.
        *   **Visuals:** Added score color coding and formatted timestamps in the history list.

### 2026-01-15
*   **Unit Tests - Expanded Coverage:**
    *   **Playground:** Added `tests/api/v1/test_playground.py` to verify:
        *   Input check success (mocked external service).
        *   Input check error handling (service down).
        *   History retrieval (`GET /history`).
    *   **Uniqueness Constraints:** Updated `test_scenario_keywords.py` and `test_rule_policy.py` to verify backend rejection of duplicate entries for:
        *   Scenario Keywords.
        *   Scenario Policies.
        *   Global Default Policies.