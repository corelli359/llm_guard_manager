# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建参数：支持子路径部署
ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}

# 构建生产版本
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置模板
COPY nginx.conf /etc/nginx/templates/default.conf.template

# 创建启动脚本来替换环境变量
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    echo 'set -e' >> /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    echo 'if [ -z "$BACKEND_SERVICE_URL" ]; then' >> /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    echo '  echo "Warning: BACKEND_SERVICE_URL not set, using default"' >> /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    echo '  export BACKEND_SERVICE_URL="http://backend:9001"' >> /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    echo 'fi' >> /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    echo 'envsubst "\$BACKEND_SERVICE_URL" < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.d/40-envsubst-on-templates.sh && \
    chmod +x /docker-entrypoint.d/40-envsubst-on-templates.sh

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
