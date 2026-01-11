# LLM Guard Manager - Project Context

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




