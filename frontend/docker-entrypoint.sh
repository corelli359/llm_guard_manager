#!/bin/sh
# Nginx 启动脚本 - 支持动态子路径配置
# 通过环境变量 BASE_PATH 配置子路径

set -e

# 默认值
BASE_PATH="${BASE_PATH:-/}"
BACKEND_SERVICE_URL="${BACKEND_SERVICE_URL:-http://backend:9001}"

echo "=========================================="
echo "Nginx 配置初始化"
echo "BASE_PATH: ${BASE_PATH}"
echo "BACKEND_SERVICE_URL: ${BACKEND_SERVICE_URL}"
echo "=========================================="

# 去掉尾部斜杠（如果有）
BASE_PATH_CLEAN=$(echo "$BASE_PATH" | sed 's:/*$::')

# 如果是根路径，设置为空字符串
if [ "$BASE_PATH_CLEAN" = "" ] || [ "$BASE_PATH_CLEAN" = "/" ]; then
    BASE_PATH_CLEAN=""
    echo "部署在根路径"
else
    echo "部署在子路径: ${BASE_PATH_CLEAN}"
fi

# 生成 Nginx 配置
cat > /etc/nginx/conf.d/default.conf <<EOF
server {
    listen 8080;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # 动态替换 HTML 中的静态资源路径
    sub_filter_once off;
    sub_filter_types text/html;
    sub_filter '"/assets/' '"${BASE_PATH_CLEAN}/assets/';
    sub_filter "'/assets/" "'${BASE_PATH_CLEAN}/assets/";
    sub_filter 'src="/assets/' 'src="${BASE_PATH_CLEAN}/assets/';
    sub_filter 'href="/assets/' 'href="${BASE_PATH_CLEAN}/assets/';

EOF

# 如果是子路径部署，添加子路径相关配置
if [ -n "$BASE_PATH_CLEAN" ]; then
    cat >> /etc/nginx/conf.d/default.conf <<EOF
    # 静态资源路径映射
    location ~ ^${BASE_PATH_CLEAN}/assets/(.*)$ {
        alias /usr/share/nginx/html/assets/\$1;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location ${BASE_PATH_CLEAN}/api/ {
        rewrite ^${BASE_PATH_CLEAN}(/api/.*)$ \$1 break;
        proxy_pass ${BACKEND_SERVICE_URL};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 前端路由支持（SPA）
    location ${BASE_PATH_CLEAN}/ {
        rewrite ^${BASE_PATH_CLEAN}/(.*)$ /\$1 break;
        try_files \$uri \$uri/ /index.html;
    }
EOF
else
    # 根路径部署配置
    cat >> /etc/nginx/conf.d/default.conf <<EOF
    # API 代理
    location /api/ {
        proxy_pass ${BACKEND_SERVICE_URL};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
EOF
fi

# 添加通用配置
cat >> /etc/nginx/conf.d/default.conf <<EOF

    # 根路径访问
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
}
EOF

echo "Nginx 配置生成完成"
echo "=========================================="
cat /etc/nginx/conf.d/default.conf
echo "=========================================="

# 启动 Nginx
exec nginx -g "daemon off;"
