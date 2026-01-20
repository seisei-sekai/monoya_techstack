# GCP 便宜部署方案指南

## 💰 目标

使用 GCP 最便宜的方案部署整个项目（AI日记 + XdfClassArranger），预计月成本：**$5-15**

## 🎯 成本优化策略

### 核心原则
1. ✅ 使用 Cloud Run（按使用付费，可缩放到0）
2. ✅ 最小化资源配置
3. ✅ 使用 Firestore 免费额度
4. ✅ 合理使用 OpenAI API
5. ✅ 避免持久化存储（Weaviate 不使用持久卷）

### 预估成本（月度）

| 服务 | 配置 | 月成本 |
|------|------|--------|
| Cloud Run - 前端 | 128MB, 0-1实例 | $0-2 |
| Cloud Run - 后端 | 256MB, 0-1实例 | $2-5 |
| Cloud Run - Weaviate | 512MB, 0-1实例 | $3-8 |
| Firestore | < 50K 读写 | $0-1 |
| Artifact Registry | 存储镜像 | $0.5 |
| Cloud Logging | 基础日志 | $0-1 |
| OpenAI API | ~100次调用 | $1-3 |
| **总计** | | **$5-15** |

> 注：实际成本取决于使用量。低流量情况下可能更便宜！

---

## 📋 部署前准备

### 1. 创建 GCP 项目

```bash
# 安装 gcloud CLI
# macOS: brew install --cask google-cloud-sdk
# Windows: 下载安装包 https://cloud.google.com/sdk/docs/install

# 登录
gcloud auth login

# 创建项目（使用便宜的命名）
export PROJECT_ID="ai-diary-lite-$(date +%s)"
gcloud projects create $PROJECT_ID --name="AI Diary Lite"

# 设置为默认项目
gcloud config set project $PROJECT_ID

# 关联计费账户（必须！）
# 访问 https://console.cloud.google.com/billing
# 选择项目 → 关联计费账户
```

### 2. 启用必需的 API

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com
```

### 3. 设置预算警报（重要！）

```bash
# 访问 GCP 控制台设置预算警报
# https://console.cloud.google.com/billing/budgets

# 建议设置：
# - 每月预算：$20
# - 警报阈值：50%, 80%, 100%
# - 发送邮件通知
```

---

## 🏗️ 便宜部署架构

```
┌──────────────────────────────────────────┐
│       Cloud Run (按请求付费)             │
│                                          │
│  前端 (128MB) ───┐                       │
│                  │                       │
│  后端 (256MB) ───┼─> Firestore (免费额度)│
│                  │                       │
│  Weaviate (512MB)─┘                      │
└──────────────────────────────────────────┘
            │
            ├─> OpenAI API (按使用付费)
            └─> Firebase Auth (免费)
```

**关键优化**：
- 所有服务 min-instances = 0（无请求时不收费）
- 使用最小内存配置
- Weaviate 不使用持久卷（重启后数据会丢失，但省钱）

---

## 🚀 部署步骤

### 步骤 1: 创建 Artifact Registry

```bash
gcloud artifacts repositories create ai-diary-images \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker images for AI Diary"

# 配置 Docker 认证
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 步骤 2: 构建并推送 Docker 镜像

#### 2.1 后端镜像（优化版）

创建优化的 Dockerfile：

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# 只复制必需文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# 使用非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建并推送：

```bash
cd backend

# 构建镜像
docker build -f Dockerfile.prod -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .

# 推送到 Artifact Registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest
```

#### 2.2 前端镜像（优化版）

创建优化的 Dockerfile：

```dockerfile
# frontend/Dockerfile.prod
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# 生产阶段 - 使用 nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# 配置 nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

创建 nginx 配置：

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 启用 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

构建并推送：

```bash
cd frontend

# 构建镜像
docker build -f Dockerfile.prod -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .

# 推送到 Artifact Registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest
```

### 步骤 3: 部署到 Cloud Run（便宜配置）

#### 3.1 部署 Weaviate（最小配置）

```bash
gcloud run deploy ai-diary-weaviate \
  --image=semitechnologies/weaviate:1.23.0 \
  --platform=managed \
  --region=us-central1 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --set-env-vars="AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true,PERSISTENCE_DATA_PATH=/tmp/weaviate,DEFAULT_VECTORIZER_MODULE=none,ENABLE_MODULES=text2vec-openai" \
  --no-allow-unauthenticated \
  --timeout=300

# 获取 Weaviate URL
WEAVIATE_URL=$(gcloud run services describe ai-diary-weaviate \
  --region=us-central1 \
  --format='value(status.url)')

echo "Weaviate URL: $WEAVIATE_URL"
```

**重要说明**：
- `PERSISTENCE_DATA_PATH=/tmp/weaviate` - 使用临时存储（不收费，但重启会丢失数据）
- `min-instances=0` - 无请求时缩放到0（节省成本）
- `--no-allow-unauthenticated` - 仅内部访问

#### 3.2 创建服务账号（用于后端）

```bash
# 创建服务账号
gcloud iam service-accounts create ai-diary-backend \
  --display-name="AI Diary Backend"

# 授予 Firestore 权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ai-diary-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# 授予调用 Weaviate 的权限
gcloud run services add-iam-policy-binding ai-diary-weaviate \
  --region=us-central1 \
  --member="serviceAccount:ai-diary-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

#### 3.3 部署后端（最小配置）

```bash
gcloud run deploy ai-diary-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest \
  --platform=managed \
  --region=us-central1 \
  --memory=256Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="FIREBASE_PROJECT_ID=$PROJECT_ID,WEAVIATE_URL=$WEAVIATE_URL" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --service-account=ai-diary-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --timeout=60

# 获取后端 URL
BACKEND_URL=$(gcloud run services describe ai-diary-backend \
  --region=us-central1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

**重要说明**：
- `memory=256Mi` - 最小内存（对于 FastAPI 足够）
- `cpu=1` - 1个 vCPU
- `min-instances=0` - 节省成本
- `timeout=60` - 60秒超时（AI 洞察生成需要时间）

#### 3.4 部署前端（最小配置）

```bash
gcloud run deploy ai-diary-frontend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest \
  --platform=managed \
  --region=us-central1 \
  --memory=128Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --port=80 \
  --allow-unauthenticated \
  --timeout=30

# 获取前端 URL
FRONTEND_URL=$(gcloud run services describe ai-diary-frontend \
  --region=us-central1 \
  --format='value(status.url)')

echo "前端 URL: $FRONTEND_URL"
echo "请访问: $FRONTEND_URL"
```

**重要说明**：
- `memory=128Mi` - 最小内存（静态文件服务器）
- Nginx 非常轻量，128MB 足够

### 步骤 4: 配置 Firestore

```bash
# 创建 Firestore 数据库（选择 Native 模式）
gcloud firestore databases create \
  --location=us-central \
  --type=firestore-native

# 创建索引（可选，但推荐）
gcloud firestore indexes composite create \
  --collection-group=diaries \
  --query-scope=COLLECTION \
  --field-config field-path=userId,order=ASCENDING \
  --field-config field-path=createdAt,order=DESCENDING
```

### 步骤 5: 更新前端环境变量

前端需要重新构建，包含正确的后端 URL：

```bash
cd frontend

# 创建生产环境变量文件
cat > .env.production << EOF
VITE_API_URL=$BACKEND_URL
VITE_FIREBASE_API_KEY=你的Firebase API Key
VITE_FIREBASE_AUTH_DOMAIN=$PROJECT_ID.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=$PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=$PROJECT_ID.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=你的Sender ID
VITE_FIREBASE_APP_ID=你的App ID
EOF

# 重新构建并推送
docker build -f Dockerfile.prod \
  --build-arg VITE_API_URL=$BACKEND_URL \
  -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .

docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest

# 重新部署
gcloud run deploy ai-diary-frontend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest \
  --region=us-central1
```

---

## 🔐 配置 Secrets（安全存储密钥）

```bash
# 启用 Secret Manager API
gcloud services enable secretmanager.googleapis.com

# 创建 OpenAI API 密钥 secret
echo -n "你的OpenAI API密钥" | \
  gcloud secrets create openai-api-key --data-file=-

# 授予后端服务账号访问权限
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:ai-diary-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 💡 进一步优化成本的技巧

### 1. 减少 OpenAI API 调用

```python
# backend/app/services/rag_service.py

# 添加缓存机制
from functools import lru_cache

@lru_cache(maxsize=100)
def get_embedding(text):
    # 缓存嵌入，避免重复调用
    response = openai.embeddings.create(...)
    return response.data[0].embedding
```

### 2. 使用更便宜的 OpenAI 模型

```python
# 将 GPT-3.5-turbo 改为 gpt-3.5-turbo-0125（更便宜）
response = openai.chat.completions.create(
    model="gpt-3.5-turbo-0125",  # 更便宜的版本
    messages=[...],
    max_tokens=150  # 限制 token 数量
)
```

### 3. 设置请求限制

```python
# backend/app/main.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/diaries/{id}/ai-insight")
@limiter.limit("5/minute")  # 每分钟最多5次请求
async def get_ai_insight(...):
    ...
```

### 4. Weaviate 数据持久化（可选，会增加成本）

如果需要持久化 Weaviate 数据：

```bash
# 创建持久化磁盘
gcloud compute disks create weaviate-data \
  --size=10GB \
  --type=pd-standard \
  --region=us-central1

# 部署时挂载磁盘（会增加 ~$0.40/月）
gcloud run deploy ai-diary-weaviate \
  --add-volume=name=weaviate-data,type=cloud-storage,bucket=weaviate-data-bucket \
  --add-volume-mount=volume=weaviate-data,mount-path=/var/lib/weaviate
```

### 5. 使用 Cloud Scheduler 定期预热（可选）

```bash
# 创建一个定时任务，每小时请求一次（保持实例热启动）
gcloud scheduler jobs create http keep-alive \
  --schedule="0 * * * *" \
  --uri="$BACKEND_URL/health" \
  --http-method=GET
```

---

## 📊 监控成本

### 1. 查看实时成本

```bash
# 查看当前月成本
gcloud billing accounts list

# 查看详细账单
# 访问: https://console.cloud.google.com/billing
```

### 2. 设置成本警报

在 GCP 控制台设置：
1. 导航到 **计费** > **预算和提醒**
2. 创建预算：$20/月
3. 设置警报：50%, 80%, 100%
4. 添加邮件通知

### 3. 查看服务使用情况

```bash
# 查看 Cloud Run 指标
gcloud run services describe ai-diary-backend \
  --region=us-central1 \
  --format="value(status.traffic)"

# 查看请求数
# 访问: https://console.cloud.google.com/run/detail/us-central1/ai-diary-backend/metrics
```

---

## 🧹 清理资源（停止计费）

如果要删除所有资源：

```bash
# 删除所有 Cloud Run 服务
gcloud run services delete ai-diary-frontend --region=us-central1 --quiet
gcloud run services delete ai-diary-backend --region=us-central1 --quiet
gcloud run services delete ai-diary-weaviate --region=us-central1 --quiet

# 删除 Artifact Registry 镜像
gcloud artifacts repositories delete ai-diary-images \
  --location=us-central1 --quiet

# 删除 Secret
gcloud secrets delete openai-api-key --quiet

# 删除 Firestore 数据库（慎重！）
# 需要在控制台手动删除

# 删除整个项目（最彻底）
gcloud projects delete $PROJECT_ID
```

---

## 🎓 成本估算示例

### 低流量场景（个人使用）

假设每天：
- 5次登录
- 创建3篇日记
- 生成1次AI洞察
- 浏览20次页面

**月成本**：
```
Cloud Run 请求费: ~$1
Cloud Run 内存使用: ~$3
Firestore 操作: ~$0.5
OpenAI API: ~$2
其他: ~$1
────────────────
总计: ~$7.50
```

### 中等流量场景（小团队）

假设每天：
- 50次登录
- 30篇日记
- 10次AI洞察
- 200次页面浏览

**月成本**：
```
Cloud Run 请求费: ~$3
Cloud Run 内存使用: ~$8
Firestore 操作: ~$2
OpenAI API: ~$5
其他: ~$2
────────────────
总计: ~$20
```

---

## ⚠️ 注意事项

### 1. Weaviate 数据丢失

使用 `/tmp` 存储时，Weaviate 重启会丢失数据。解决方案：
- 重新索引所有日记（从 Firestore）
- 或使用持久化存储（增加成本）

### 2. 冷启动延迟

`min-instances=0` 会导致第一次请求较慢（2-5秒）。解决方案：
- 接受冷启动（省钱）
- 或设置 `min-instances=1`（增加 ~$5/月）

### 3. OpenAI API 配额

免费账户有使用限制。建议：
- 升级到付费账户
- 设置请求速率限制
- 添加缓存机制

---

## 🚀 部署后验证

```bash
# 测试后端
curl $BACKEND_URL/health
# 应该返回: {"status":"healthy"}

# 测试前端
curl -I $FRONTEND_URL
# 应该返回 200 OK

# 访问应用
echo "访问: $FRONTEND_URL"
```

---

## 📝 总结

使用此方案，你可以以 **$5-15/月** 的成本运行完整的 AI 日记应用！

**关键要点**：
- ✅ Cloud Run 按使用付费，非常适合低流量应用
- ✅ min-instances=0 是最大的成本节省措施
- ✅ 合理使用 OpenAI API，避免过度调用
- ✅ 使用 Firestore 免费额度
- ✅ 设置预算警报，避免意外超支

**下一步**：
1. 部署应用
2. 监控成本
3. 根据实际使用优化配置

祝你部署顺利！🎉

