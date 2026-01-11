#!/bin/bash

# 1. 启动后端容器
# 假设镜像名为 llm-guard-backend，将容器 9001 映射到宿主机 39001
echo "Starting Backend..."
docker run -d \
  --name llm-guard-backend \
  -p 39001:9001 \
  --restart always \
  llm-guard-backend

# 2. 启动前端容器 (方案二)
# 使用 --add-host 让 Nginx 容器可以通过 host.docker.internal 访问宿主机的 39001
echo "Starting Frontend..."
docker run -d \
  --name llm-guard-frontend \
  -p 35173:80 \
  --add-host=host.docker.internal:host-gateway \
  -v /nginx.conf:/etc/nginx/conf.d/default.conf \
  llm-guard-frontend

echo "Deployment complete!"
echo "Backend: http://localhost:39001"
echo "Frontend: http://localhost:80"
