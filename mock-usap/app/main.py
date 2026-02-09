from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth_router, users_router

app = FastAPI(
    title="Mock USAP Service",
    description="模拟USAP统一认证平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(users_router, prefix="/api/users", tags=["用户"])


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "mock-usap",
        "version": "1.0.0"
    }
