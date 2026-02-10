# Mock USAP Service

模拟USAP统一认证平台，用于V2版本开发和测试。

## 快速开始

### 本地运行
```bash
cd mock-usap
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Docker运行
```bash
docker build -t mock-usap:v1.0 .
docker run -p 8080:8080 mock-usap:v1.0
```

## API接口

### 认证接口

#### 1. 用户登录
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "zhangsan", "password": "123456"}'
```

#### 2. 获取Ticket
```bash
curl -X POST http://localhost:8080/api/auth/ticket \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SES_xxx", "target_system": "llm-guard-manager"}'
```

#### 3. 验证Ticket
```bash
curl -X POST http://localhost:8080/api/auth/validate-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket": "TK_xxx"}'
```

### 用户接口

#### 4. 获取用户信息
```bash
curl http://localhost:8080/api/users/U001
```

#### 5. 批量获取用户
```bash
curl -X POST http://localhost:8080/api/users/batch \
  -H "Content-Type: application/json" \
  -d '{"user_ids": ["U001", "U002"]}'
```

### 健康检查
```bash
curl http://localhost:8080/api/health
```

## 测试用户

| 用户名 | 密码 | user_id | 状态 |
|--------|------|---------|------|
| zhangsan | 123456 | U001 | active |
| lisi | 123456 | U002 | active |
| wangwu | 123456 | U003 | active |
| zhaoliu | 123456 | U004 | active |
| sunqi | 123456 | U005 | active |
| zhouba | 123456 | U006 | **inactive** |
| wujiu | 123456 | U007 | active |
| zhengshi | 123456 | U008 | active |
| admin | admin123 | U009 | active |
| test | test123 | U010 | active |
