# 快速参考卡片 🚀

## 📋 一页纸速查表

### 🎯 项目现状

```
✅ TypeScript → JavaScript 转换完成
✅ XdfClassArranger 整合完成
✅ FullCalendar 依赖已添加
✅ 生产 Dockerfile 已创建
✅ 测试和部署文档已完成
```

---

## 🚀 本地启动（3种方式）

### 方式 1: Docker Compose（最简单）

```bash
docker-compose up --build
# 访问 http://localhost:5173
```

### 方式 2: 手动启动（推荐调试）

```bash
# 终端 1 - Weaviate
docker run -d --name weaviate-dev -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  semitechnologies/weaviate:1.23.0

# 终端 2 - 后端
cd backend && source venv/bin/activate
export OPENAI_API_KEY="你的密钥"
export FIREBASE_PROJECT_ID="你的项目ID"
export WEAVIATE_URL="http://localhost:8080"
export GOOGLE_APPLICATION_CREDENTIALS="../service-account.json"
uvicorn app.main:app --reload --port 8000

# 终端 3 - 前端
cd frontend && npm install && npm run dev
```

### 方式 3: 使用 Makefile

```bash
make dev          # 启动所有服务
make dev-frontend # 只启动前端
make dev-backend  # 只启动后端
```

---

## 🧪 测试流程

1. **注册/登录** → `test@example.com / Test123456`
2. **创建3篇日记** → 不同主题
3. **生成AI洞察** → 点击 "Get AI Insight"
4. **访问课程安排器** → 点击 "Class Arranger"
5. **添加课程** → 在日历上点击
6. **拖拽课程** → 测试交互

详细测试清单：[LOCAL_TEST_GUIDE_CN.md](LOCAL_TEST_GUIDE_CN.md)

---

## ☁️ GCP 部署（$5-15/月）

```bash
# 1. 设置项目
export PROJECT_ID="ai-diary-lite-$(date +%s)"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# 2. 启用 API
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com

# 3. 创建 Artifact Registry
gcloud artifacts repositories create ai-diary-images \
  --repository-format=docker \
  --location=us-central1

# 4. 构建镜像
gcloud auth configure-docker us-central1-docker.pkg.dev

# 后端
cd backend
docker build -f Dockerfile.prod -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest

# 前端
cd ../frontend
docker build -f Dockerfile.prod -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest

# 5. 部署（自动脚本）
# 见 GCP_DEPLOYMENT_BUDGET_CN.md 完整步骤
```

详细部署步骤：[GCP_DEPLOYMENT_BUDGET_CN.md](GCP_DEPLOYMENT_BUDGET_CN.md)

---

## 📊 成本估算

| 场景 | 日请求 | 月成本 |
|------|--------|--------|
| 个人使用 | 50-100 | $5-8 |
| 小团队 | 500-1000 | $10-15 |
| 中等流量 | 2000+ | $20-30 |

**节省成本的关键**：
- min-instances = 0
- 最小内存配置
- 合理使用 OpenAI API

---

## 🗂️ 文件结构（关键文件）

```
JD_Project/
├── frontend/
│   ├── src/
│   │   ├── main.jsx              ⭐ TS→JS
│   │   ├── App.jsx               ⭐ TS→JS + XDF路由
│   │   ├── pages/*.jsx           ⭐ TS→JS
│   │   ├── api/*.js              ⭐ TS→JS
│   │   └── XdfClassArranger/     ⭐ 整合完成
│   ├── package.json              ⭐ 添加 FullCalendar
│   ├── Dockerfile.prod           ⭐ 新增
│   └── nginx.conf                ⭐ 新增
├── backend/
│   ├── Dockerfile.prod           ⭐ 新增
│   └── app/                      （保持不变）
└── 文档/
    ├── LOCAL_TEST_GUIDE_CN.md       ⭐ 测试指南
    ├── GCP_DEPLOYMENT_BUDGET_CN.md  ⭐ 部署指南
    └── INTEGRATION_SUMMARY_CN.md    ⭐ 总结文档
```

---

## 🔧 常用命令

### 前端

```bash
cd frontend
npm install              # 安装依赖
npm run dev              # 开发模式
npm run build            # 构建生产版本
npm run lint             # 代码检查
```

### 后端

```bash
cd backend
source venv/bin/activate # 激活虚拟环境
pip install -r requirements.txt  # 安装依赖
uvicorn app.main:app --reload    # 开发模式
```

### Docker

```bash
docker-compose up        # 启动所有服务
docker-compose down      # 停止所有服务
docker-compose logs -f   # 查看日志
docker ps                # 查看运行中的容器
docker logs CONTAINER_ID # 查看特定容器日志
```

### GCP

```bash
gcloud projects list     # 列出项目
gcloud config set project PROJECT_ID  # 设置项目
gcloud run services list # 列出服务
gcloud run services describe SERVICE_NAME --region=us-central1  # 查看服务详情
gcloud run logs read SERVICE_NAME --limit=50  # 查看日志
```

---

## 🐛 快速故障排除

| 问题 | 解决方案 |
|------|---------|
| 前端无法启动 | `rm -rf node_modules && npm install` |
| 后端无法连接 Firestore | 检查 `service-account.json` 和环境变量 |
| Weaviate 连接失败 | `curl http://localhost:8080/v1/.well-known/ready` |
| OpenAI API 失败 | 检查 API 密钥和账户余额 |
| FullCalendar 不显示 | `npm install @fullcalendar/react` |
| 路由 404 | 检查 `App.jsx` 中的路由配置 |

---

## 📚 文档导航

| 文档 | 用途 | 何时查看 |
|------|------|---------|
| [INTEGRATION_SUMMARY_CN.md](INTEGRATION_SUMMARY_CN.md) | 项目总结 | ⭐ 第一个看 |
| [LOCAL_TEST_GUIDE_CN.md](LOCAL_TEST_GUIDE_CN.md) | 测试指南 | 测试前 |
| [GCP_DEPLOYMENT_BUDGET_CN.md](GCP_DEPLOYMENT_BUDGET_CN.md) | 部署指南 | 部署前 |
| [LOCAL_DEVELOPMENT_CN.md](LOCAL_DEVELOPMENT_CN.md) | 开发指南 | 开发时 |
| [ARCHITECTURE_CN.md](ARCHITECTURE_CN.md) | 架构说明 | 深入了解 |

---

## ✅ 检查清单

### 开始前
- [ ] 安装 Node.js 20+
- [ ] 安装 Python 3.11+
- [ ] 安装 Docker
- [ ] 获取 Firebase 配置
- [ ] 获取 OpenAI API 密钥
- [ ] 创建 `.env` 文件
- [ ] 下载 `service-account.json`

### 本地测试
- [ ] 启动所有服务
- [ ] 注册/登录成功
- [ ] 创建日记成功
- [ ] AI 洞察生成成功
- [ ] XdfClassArranger 显示正常
- [ ] 课程添加/编辑成功
- [ ] 无控制台错误

### 部署前
- [ ] 本地测试全部通过
- [ ] 创建 GCP 项目
- [ ] 关联计费账户
- [ ] 设置预算警报
- [ ] 准备好所有密钥

---

## 🎯 下一步行动

```
1️⃣  阅读 INTEGRATION_SUMMARY_CN.md（5分钟）
     ↓
2️⃣  本地测试（按照 LOCAL_TEST_GUIDE_CN.md）（30分钟）
     ↓
3️⃣  准备 GCP 项目（15分钟）
     ↓
4️⃣  部署到 GCP（按照 GCP_DEPLOYMENT_BUDGET_CN.md）（45分钟）
     ↓
5️⃣  监控成本和性能（持续）
```

---

## 💡 提示

- 💰 开发时使用 Docker Compose，部署时用 Cloud Run
- 🔐 所有密钥都用环境变量或 Secret Manager
- 📊 设置预算警报，避免意外超支
- 🧪 本地测试通过后再部署
- 📝 遇到问题先查文档，再查日志

---

## 📞 需要帮助？

1. 查看详细文档（见上方表格）
2. 检查日志：
   - 前端：F12 Console
   - 后端：终端输出
   - Docker：`docker logs CONTAINER_NAME`
3. 常见问题都有解决方案在文档中

---

**祝你使用愉快！** 🎉

有问题就查文档，文档里都有答案！

