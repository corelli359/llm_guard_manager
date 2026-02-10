"""
门户服务 - Portal Service
提供统一登录入口，跳转到目标应用
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Portal Service", version="1.0.0")

# 配置
USAP_BASE_URL = os.getenv("USAP_BASE_URL", "http://mock-usap-svc:8080")
PORTAL_BASE_PATH = os.getenv("PORTAL_BASE_PATH", "/portal")

# 目标应用配置
TARGET_APPS = {
    "llm-guard-manager": {
        "name": "LLM安全管理平台",
        "url": "/web-manager/",
        "sso_path": "/web-manager/sso/login"
    },
    "llm-guard-manager-v2": {
        "name": "LLM安全管理平台V2",
        "url": "/web-manager-java/",
        "sso_path": "/web-manager-java/sso/login"
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    session_id: str = None
    user_name: str = None
    error: str = None


class JumpRequest(BaseModel):
    session_id: str
    target_app: str


# ============================================
# API 端点
# ============================================

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "portal"}


@app.post("/api/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """用户登录，调用USAP获取Session"""
    print(f"[PORTAL LOGIN] username='{req.username}' password='{req.password}'", flush=True)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(
                f"{USAP_BASE_URL}/api/auth/login",
                json={"username": req.username, "password": req.password}
            )
            data = resp.json()
            print(f"[PORTAL LOGIN] USAP response: status={resp.status_code} body={data}", flush=True)

            if resp.status_code == 200 and data.get("success"):
                return LoginResponse(
                    success=True,
                    session_id=data["session_id"],
                    user_name=data.get("user_name", req.username)
                )
            else:
                return LoginResponse(
                    success=False,
                    error=data.get("detail", "登录失败")
                )
        except Exception as e:
            print(f"[PORTAL LOGIN] Exception: {e}", flush=True)
            return LoginResponse(success=False, error=str(e))


@app.get("/api/apps")
async def list_apps():
    """获取可用应用列表"""
    return [
        {"id": k, "name": v["name"], "url": v["url"]}
        for k, v in TARGET_APPS.items()
    ]


@app.post("/api/jump")
async def jump_to_app(req: JumpRequest):
    """获取Ticket并返回跳转URL"""
    if req.target_app not in TARGET_APPS:
        raise HTTPException(status_code=400, detail="未知的目标应用")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 调用USAP获取Ticket
            resp = await client.post(
                f"{USAP_BASE_URL}/api/auth/ticket",
                json={"session_id": req.session_id, "target_system": req.target_app}
            )
            data = resp.json()

            if resp.status_code == 200 and data.get("success"):
                ticket = data["ticket"]
                app_config = TARGET_APPS[req.target_app]
                redirect_url = f"{app_config['sso_path']}?ticket={ticket}"
                return {"success": True, "redirect_url": redirect_url}
            else:
                raise HTTPException(
                    status_code=400,
                    detail=data.get("detail", "获取Ticket失败")
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"USAP服务不可用: {str(e)}")


# ============================================
# 页面
# ============================================

@app.get("/", response_class=HTMLResponse)
async def index():
    """门户首页 - 登录页面"""
    return get_login_page()


@app.get("/apps", response_class=HTMLResponse)
async def apps_page():
    """应用列表页面"""
    return get_apps_page()


def get_login_page():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>统一认证门户</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #333;
            font-size: 24px;
            font-weight: 600;
        }
        .logo p {
            color: #666;
            font-size: 14px;
            margin-top: 8px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>统一认证门户</h1>
            <p>Enterprise Single Sign-On Portal</p>
        </div>
        <div class="error" id="error"></div>
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" placeholder="请输入用户名" required>
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码" required>
            </div>
            <button type="submit" class="btn" id="submitBtn">登 录</button>
        </form>
        <div class="footer">
            <p>Mock USAP v1.0 | 测试账号: admin / admin123</p>
        </div>
    </div>
    <script>
        const BASE_PATH = window.location.pathname.replace(/\\/$/, '') || '';

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const error = document.getElementById('error');

            btn.disabled = true;
            btn.textContent = '登录中...';
            error.style.display = 'none';

            try {
                const resp = await fetch(BASE_PATH + '/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('username').value,
                        password: document.getElementById('password').value
                    })
                });
                const data = await resp.json();

                if (data.success) {
                    // 保存session，跳转到应用列表
                    sessionStorage.setItem('portal_session', data.session_id);
                    sessionStorage.setItem('portal_user', data.user_name);
                    window.location.href = BASE_PATH + '/apps';
                } else {
                    error.textContent = data.error || '登录失败';
                    error.style.display = 'block';
                }
            } catch (err) {
                error.textContent = '网络错误，请重试';
                error.style.display = 'block';
            } finally {
                btn.disabled = false;
                btn.textContent = '登 录';
            }
        });
    </script>
</body>
</html>
"""


def get_apps_page():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>应用中心 - 统一认证门户</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 20px; }
        .user-info {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .user-info span { font-size: 14px; }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        .logout-btn:hover { background: rgba(255,255,255,0.3); }
        .container {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .section-title {
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }
        .apps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .app-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .app-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        .app-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            margin-bottom: 16px;
        }
        .app-name {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .app-desc {
            font-size: 14px;
            color: #666;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>应用中心</h1>
        <div class="user-info">
            <span id="userName">加载中...</span>
            <button class="logout-btn" onclick="logout()">退出登录</button>
        </div>
    </div>
    <div class="container">
        <h2 class="section-title">可用应用</h2>
        <div class="apps-grid" id="appsGrid">
            <div class="loading">加载中...</div>
        </div>
    </div>
    <script>
        const BASE_PATH = window.location.pathname.replace(/\\/apps$/, '') || '';
        const sessionId = sessionStorage.getItem('portal_session');
        const userName = sessionStorage.getItem('portal_user');

        if (!sessionId) {
            window.location.href = BASE_PATH + '/';
        }

        document.getElementById('userName').textContent = userName || '用户';

        // 加载应用列表
        async function loadApps() {
            try {
                const resp = await fetch(BASE_PATH + '/api/apps');
                const apps = await resp.json();

                const grid = document.getElementById('appsGrid');
                grid.innerHTML = apps.map(app => `
                    <div class="app-card" onclick="jumpToApp('${app.id}')">
                        <div class="app-icon">🛡️</div>
                        <div class="app-name">${app.name}</div>
                        <div class="app-desc">点击进入应用</div>
                    </div>
                `).join('');
            } catch (err) {
                document.getElementById('appsGrid').innerHTML = '<div class="loading">加载失败</div>';
            }
        }

        // 跳转到应用
        async function jumpToApp(appId) {
            try {
                const resp = await fetch(BASE_PATH + '/api/jump', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        target_app: appId
                    })
                });
                const data = await resp.json();

                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert(data.detail || '跳转失败');
                }
            } catch (err) {
                alert('网络错误');
            }
        }

        function logout() {
            sessionStorage.removeItem('portal_session');
            sessionStorage.removeItem('portal_user');
            window.location.href = BASE_PATH + '/';
        }

        loadApps();
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
