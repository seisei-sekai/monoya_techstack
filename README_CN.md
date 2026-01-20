# AI 日记 - 基于 AI 的个性化日记应用

一个全栈 AI 驱动的日记应用，使用 React、FastAPI、Firebase 和 RAG（检索增强生成）技术构建。用户可以创建、管理日记，并根据日记历史获得个性化的 AI 洞察。

---

## 📚 文档中心

**→ [📖 完整文档索引](./docs/INDEX.md)** - 查找所有技术文档、教程、指南

**快速链接**：
- [🚀 快速开始](./docs/QUICKSTART_CN.md)
- [🏗️ 架构设计](./docs/ARCHITECTURE_CN.md)
- [💻 本地开发](./docs/LOCAL_DEVELOPMENT_CN.md)
- [☁️ 云端部署](./docs/DEPLOYMENT_CN.md)
- [🔍 Weaviate 教程](./docs/WEAVIATE_TUTORIAL.md)
- [🏗️ Terraform 教程](./docs/TERRAFORM_TUTORIAL.md)

---

## 🎯 功能特点

- **用户认证**：使用 Firebase Auth 进行安全的登录和注册
- **日记管理**：创建、阅读、更新和删除日记条目
- **AI 智能洞察**：使用 RAG 基于你的日记历史生成个性化反馈
- **语义搜索**：利用 Weaviate 向量数据库进行上下文理解
- **现代化 UI**：使用 React 和 Tailwind CSS 构建的美观响应式界面
- **云原生**：可使用 Terraform 部署到 Google Cloud Platform

## 🛠️ 技术栈

### 前端

- **React** with TypeScript
- **Vite** 快速开发构建
- **Tailwind CSS** 样式设计
- **Firebase SDK** 用户认证
- **Zustand** 状态管理
- **Axios** API 调用

### 后端

- **FastAPI** (Python) REST API
- **Firebase Admin SDK** 认证管理
- **OpenAI API** AI 洞察生成
- **Weaviate** 向量数据库用于 RAG
- **Google Firestore** 数据持久化

### 基础设施

- **Docker** 和 Docker Compose 容器化
- **Google Cloud Run** 无服务器部署
- **Terraform** 基础设施即代码
- **GitHub Actions** CI/CD
- **Artifact Registry** Docker 镜像存储

## 📁 项目结构

```
JD_Project/
├── frontend/                 # React前端应用
│   ├── src/
│   │   ├── api/             # API客户端和端点
│   │   ├── components/      # 可重用的React组件
│   │   ├── config/          # Firebase配置
│   │   ├── pages/           # 页面组件（登录、仪表板、编辑器）
│   │   ├── store/           # Zustand状态管理
│   │   └── types/           # TypeScript类型定义
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                  # FastAPI后端应用
│   ├── app/
│   │   ├── api/             # API路由和依赖
│   │   ├── core/            # 核心配置和客户端
│   │   ├── models/          # Pydantic模型
│   │   └── services/        # 业务逻辑（日记、RAG）
│   ├── Dockerfile
│   └── requirements.txt
│
├── terraform/                # 基础设施即代码
│   ├── main.tf              # 主Terraform配置
│   ├── variables.tf         # 变量定义
│   ├── outputs.tf           # 输出值
│   └── terraform.tfvars.example
│
├── .github/
│   └── workflows/           # CI/CD管道
│       ├── deploy.yml       # 构建和部署工作流
│       └── test.yml         # 测试工作流
│
├── docker-compose.yml       # 本地开发设置
└── env.example              # 环境变量模板
```

## 🚀 快速开始

### 前置要求

- Node.js 20+
- Python 3.11+
- Docker 和 Docker Compose
- Google Cloud Platform 账号
- Firebase 项目
- OpenAI API 密钥

### 本地开发设置

1. **克隆仓库**

```bash
git clone <repository-url>
cd JD_Project
```

2. **设置环境变量**

```bash
cp env.example .env
# 使用实际凭据编辑.env
```

3. **设置 Firebase**

   - 在 https://console.firebase.google.com 创建 Firebase 项目
   - 启用 Firebase Authentication（Email/Password）
   - 启用 Firestore Database
   - 下载服务账号密钥并保存为项目根目录的 `service-account.json`
   - 将 Firebase 配置复制到 `.env`

4. **使用 Docker Compose 启动应用**

```bash
docker-compose up --build
```

服务将在以下地址可用：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- Weaviate：http://localhost:8080

### 手动设置（不使用 Docker）

#### 后端设置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows系统: venv\Scripts\activate
pip install -r requirements.txt

# 单独启动Weaviate或使用docker
docker run -d -p 8080:8080 semitechnologies/weaviate:1.23.0

# 运行后端
uvicorn app.main:app --reload --port 8000
```

#### 前端设置

```bash
cd frontend
npm install
npm run dev
```

## 🌐 部署到 GCP

### 前置要求

- 安装 Google Cloud SDK
- 安装 Terraform
- 已创建并启用计费的 GCP 项目

### 步骤 1：初始化 Terraform

```bash
cd terraform

# 为Terraform状态创建GCS存储桶
gsutil mb gs://YOUR-PROJECT-terraform-state

# 复制并编辑terraform.tfvars
cp terraform.tfvars.example terraform.tfvars
# 使用你的值编辑terraform.tfvars

# 初始化Terraform
terraform init
```

### 步骤 2：部署基础设施

```bash
# 查看计划
terraform plan

# 应用配置
terraform apply
```

### 步骤 3：构建并推送 Docker 镜像

```bash
# 使用Artifact Registry进行身份验证
gcloud auth configure-docker us-central1-docker.pkg.dev

# 设置项目ID
export PROJECT_ID=your-project-id

# 构建并推送后端
cd backend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest

# 构建并推送前端
cd ../frontend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest
```

### 步骤 4：使用 GitHub Actions 设置 CI/CD

1. 创建以下 GitHub Secrets：

   - `GCP_PROJECT_ID`：你的 GCP 项目 ID
   - `GCP_SA_KEY`：服务账号 JSON 密钥（具有必要权限）
   - `OPENAI_API_KEY`：你的 OpenAI API 密钥
   - `VITE_API_URL`：Cloud Run 后端 URL
   - `VITE_FIREBASE_API_KEY`：Firebase API 密钥
   - `VITE_FIREBASE_AUTH_DOMAIN`：Firebase 认证域
   - `VITE_FIREBASE_PROJECT_ID`：Firebase 项目 ID

2. 推送到 `main` 分支以触发部署：

```bash
git push origin main
```

## 📚 API 文档

后端运行后，访问：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### 主要端点

- `GET /diaries` - 获取当前用户的所有日记
- `POST /diaries` - 创建新日记条目
- `GET /diaries/{id}` - 获取特定日记
- `PUT /diaries/{id}` - 更新日记
- `DELETE /diaries/{id}` - 删除日记
- `POST /diaries/{id}/ai-insight` - 为日记生成 AI 洞察

## 🔐 安全性

- Firebase Authentication 用于用户管理
- JWT 令牌用于 API 身份验证
- 具有最小权限的服务账号
- 使用环境变量保护密钥
- Firestore 安全规则（在 Firebase 控制台配置）

## 🧪 测试

```bash
# 前端测试
cd frontend
npm run lint
npm run build

# 后端测试
cd backend
pip install pytest pytest-asyncio
pytest
```

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证。

## 🆘 故障排除

### 常见问题

**Firebase 身份验证错误**

- 确保 `.env` 中的 Firebase 配置正确
- 检查 Firebase 控制台中是否启用了身份验证
- 验证服务账号具有适当的权限

**Weaviate 连接问题**

- 确保 Weaviate 在端口 8080 上运行
- 检查 `WEAVIATE_URL` 环境变量
- 验证服务之间的网络连接

**OpenAI API 错误**

- 验证你的 API 密钥是否有效
- 检查 API 使用限制
- 确保 OpenAI 账户中有足够的额度

**GCP 部署问题**

- 验证服务账号权限
- 检查 Cloud Run 服务日志：`gcloud run logs read SERVICE_NAME`
- 确保启用了所有必需的 API

## 📧 支持

如有问题和支持，请在 GitHub 仓库中开启 issue。

## 🎓 学习资源

- [React 文档](https://react.dev/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Firebase 文档](https://firebase.google.com/docs)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Weaviate 文档](https://weaviate.io/developers/weaviate)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Run 文档](https://cloud.google.com/run/docs)

## 🌟 便捷命令

```bash
# 使用Makefile
make setup          # 初始化项目
make dev            # 启动开发环境
make build          # 构建Docker镜像
make clean          # 清理容器和镜像
make test-frontend  # 运行前端测试
make test-backend   # 运行后端测试
make deploy-gcp     # 部署到GCP
make tf-init        # 初始化Terraform
make tf-apply       # 应用Terraform配置
make logs-backend   # 查看后端日志（GCP）
make logs-frontend  # 查看前端日志（GCP）
```

## 🎯 功能演示

### 创建日记

1. 登录你的账号
2. 点击"新建日记"
3. 输入标题和内容
4. 点击"保存"

### 获取 AI 洞察

1. 打开已保存的日记
2. 点击"获取 AI 洞察"按钮
3. 等待 AI 分析你的日记（基于历史记录）
4. 查看个性化反馈

### RAG 系统工作原理

1. 系统将你的日记内容转换为向量嵌入（OpenAI Embeddings）
2. 存储在 Weaviate 向量数据库中
3. 当你请求洞察时，系统会搜索相似的历史日记
4. 使用检索到的上下文，GPT-3.5 生成个性化建议
5. 洞察基于你的写作模式和情感趋势

## 💡 最佳实践

### 本地开发

- 使用 `docker-compose` 保持环境一致
- 定期拉取最新的依赖更新
- 使用 `.env` 文件管理密钥，切勿提交到 Git

### 生产部署

- 使用 Terraform 管理基础设施
- 通过 GitHub Actions 实现自动化部署
- 配置 Cloud Logging 和监控
- 设置预算警报以控制成本
- 定期备份 Firestore 数据

### 安全建议

- 定期轮换 API 密钥
- 使用最小权限原则配置 IAM 角色
- 启用 Firebase 安全规则
- 在生产环境中使用 HTTPS
- 实施速率限制和 API 配额

## 🔮 未来增强

计划中的功能：

- 📱 移动应用（React Native）
- 📊 高级分析仪表板
- 📄 导出日记为 PDF
- 🎤 语音转文字日记输入
- 🌍 多语言支持
- 😊 情感分析
- 🔔 每日提醒通知
- 🎯 目标设定和跟踪

AI 增强：

- 根据用户数据微调模型
- 时间轴情绪追踪
- 写作提示建议
- 主题检测和分类
- 自动标签生成

## 📞 联系方式

- 项目仓库：[GitHub 链接]
- 问题反馈：[GitHub Issues]
- 文档：查看项目中的其他.md 文件

---

使用愉快！如果觉得有用，请给个 ⭐️！
