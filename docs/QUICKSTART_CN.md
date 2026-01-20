# 快速开始指南

在 5 分钟内运行你的 AI 日记应用！

## 前置要求

确保你已安装以下软件：

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Node.js 20+](https://nodejs.org/)
- [Python 3.11+](https://www.python.org/downloads/)

## 步骤 1：克隆和设置

```bash
# 克隆仓库
git clone <your-repo-url>
cd JD_Project

# 运行设置脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## 步骤 2：配置环境

在项目根目录创建 `.env` 文件：

```bash
cp env.example .env
```

编辑 `.env` 并添加你的凭据：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Firebase（从Firebase控制台获取）
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123:web:abc123

# 后端
FIREBASE_PROJECT_ID=your-project-id
VITE_API_URL=http://localhost:8000
```

## 步骤 3：设置 Firebase

1. **创建 Firebase 项目**

   - 访问 [Firebase 控制台](https://console.firebase.google.com)
   - 点击"添加项目"
   - 按照设置向导操作

2. **启用身份验证**

   - 在项目中，转到"Authentication"
   - 点击"开始使用"
   - 启用"Email/Password"登录方式

3. **创建 Firestore 数据库**

   - 转到"Firestore Database"
   - 点击"创建数据库"
   - 以生产模式启动
   - 选择位置（例如：us-central）

4. **下载服务账号密钥**
   - 转到项目设置 > 服务账号
   - 点击"生成新的私钥"
   - 将文件保存为项目根目录的 `service-account.json`

## 步骤 4：启动应用

```bash
# 使用Docker Compose启动所有服务
docker-compose up
```

等待所有服务启动。你应该看到：

- ✅ 前端运行在 http://localhost:5173
- ✅ 后端 API 在 http://localhost:8000
- ✅ Weaviate 在 http://localhost:8080

## 步骤 5：使用应用

1. **打开浏览器** 访问 http://localhost:5173

2. **创建账号**

   - 点击"注册"
   - 输入你的邮箱和密码
   - 点击"创建账号"

3. **创建你的第一篇日记**

   - 点击"新建日记"
   - 写标题和内容
   - 点击"保存"

4. **获取 AI 洞察**
   - 打开你的日记
   - 点击"获取 AI 洞察"
   - 等待 AI 分析你的条目
   - 查看个性化反馈！

## 故障排除

### 端口已被使用

如果看到端口错误，停止其他服务：

```bash
# 停止所有运行的服务
docker-compose down

# 终止占用端口的进程
lsof -ti:5173,8000,8080 | xargs kill -9
```

### Firebase 身份验证错误

确保：

- Firebase Authentication 已启用
- `.env` 中的 API 密钥正确
- `service-account.json` 在项目根目录

### 无法连接到后端

检查：

- 后端容器正在运行：`docker ps`
- 查看后端日志：`docker-compose logs backend`
- API 端点：http://localhost:8000/health

### Weaviate 连接问题

```bash
# 重启Weaviate
docker-compose restart weaviate

# 检查Weaviate健康状态
curl http://localhost:8080/v1/.well-known/ready
```

## 下一步

- 📖 阅读完整的 [README_CN.md](README_CN.md) 详细文档
- 🚀 了解 [部署指南](DEPLOYMENT_CN.md) 到 GCP
- 🏗️ 理解 [架构文档](ARCHITECTURE_CN.md)
- 💻 探索 [API 文档](http://localhost:8000/docs)

## 有用的命令

```bash
# 查看所有服务
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 清理所有内容
make clean
```

## 开发工作流

### 前端开发

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行代码检查
npm run lint
```

### 后端开发

```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Windows系统: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务器
uvicorn app.main:app --reload

# 运行测试
pytest
```

## 使用技巧

### 写日记的最佳实践

1. **保持规律** - 每天在固定时间写作
2. **诚实表达** - AI 会根据你的真实情感提供更好的洞察
3. **详细描述** - 提供更多上下文让 AI 理解你的情况
4. **定期回顾** - 查看过往日记和 AI 洞察来追踪成长

### 获得更好的 AI 洞察

1. **写完整的日记** - 至少几个段落让 AI 有足够的上下文
2. **保持一致** - 写更多日记让 AI 了解你的模式
3. **多样化主题** - 写不同话题让系统学习你的多个方面
4. **使用"获取洞察"功能** - 在写了几篇日记后获得最佳效果

## 功能演示

### 登录页面

- 简洁美观的设计
- 登录/注册切换
- Firebase 身份验证

### 仪表板

- 查看所有日记条目
- 按时间排序
- 快速编辑和删除
- 创建新日记

### 日记编辑器

- 实时保存
- AI 洞察生成
- 富文本编辑
- 响应式设计

### AI 洞察

- 基于历史的个性化反馈
- 情感识别
- 模式分析
- 鼓励和建议

## 数据隐私

你的数据安全是我们的首要任务：

- 🔒 所有数据使用 Firebase 加密
- 🔐 仅你可以访问你的日记
- 🚫 我们不会与第三方分享你的数据
- ✅ 你可以随时删除你的数据

## 性能提示

### 减少冷启动时间

```bash
# 保持Weaviate运行（不要设置min-instances=0）
# 在terraform/main.tf中设置：
# "autoscaling.knative.dev/minScale" = "1"
```

### 优化成本

- 本地开发时使用 `docker-compose`
- 仅在需要时部署到 GCP
- 监控 Cloud Run 使用情况
- 设置预算警报

## 支持

如果遇到任何问题：

1. 查看日志：`docker-compose logs`
2. 验证你的 `.env` 配置
3. 确保所有前置要求已安装
4. 在 GitHub 上开启 issue

## 常见问题

**Q: 为什么 AI 洞察需要这么长时间？**
A: 第一次生成洞察时，需要创建向量嵌入并搜索历史记录。通常需要 5-10 秒。

**Q: 我可以使用其他 LLM 模型吗？**
A: 可以！编辑 `backend/app/services/rag_service.py` 中的模型名称。

**Q: 如何备份我的数据？**
A: Firestore 有自动备份。你也可以使用导出功能（未来版本将添加）。

**Q: 支持移动设备吗？**
A: Web 界面是响应式的，在移动设备上也能正常工作。原生移动应用在规划中。

**Q: 可以离线使用吗？**
A: 目前需要互联网连接。离线模式是未来计划的功能。

## 快速参考

| 操作         | 命令                              |
| ------------ | --------------------------------- |
| 启动所有服务 | `docker-compose up`               |
| 停止所有服务 | `docker-compose down`             |
| 查看日志     | `docker-compose logs -f`          |
| 重启服务     | `docker-compose restart`          |
| 清理         | `make clean`                      |
| 运行测试     | `make test-frontend test-backend` |
| 部署         | `make deploy-gcp`                 |

祝你写日记愉快！✨

如果你喜欢这个项目，请给我们一个 ⭐️！
