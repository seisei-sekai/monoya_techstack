# 本地开发工作流程指南

这份指南将带你完成从零开始在本地开发、调试、测试，最后部署到云端的完整流程。

## 📋 目录

1. [环境准备](#环境准备)
2. [本地开发设置](#本地开发设置)
3. [开发工作流](#开发工作流)
4. [调试技巧](#调试技巧)
5. [测试流程](#测试流程)
6. [部署前检查](#部署前检查)
7. [部署到云端](#部署到云端)

---

## 环境准备

### 必需软件

```bash
# 检查 Node.js 版本
node --version  # 应该是 v20+

# 检查 Python 版本
python3 --version  # 应该是 3.11+

# 检查 Docker 版本
docker --version
docker-compose --version
```

如果缺少任何工具，请先安装：
- **Node.js**: https://nodejs.org/
- **Python**: https://www.python.org/downloads/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop

### 代码编辑器推荐

推荐使用 **VS Code**，项目已配置好相关设置：
- 自动格式化
- ESLint 代码检查
- Python 类型检查
- 推荐扩展列表

---

## 本地开发设置

### 步骤 1: 克隆项目

```bash
# 克隆项目
cd ~/Desktop/Stanford/SP26/Monoya
cd JD_Project

# 查看项目结构
ls -la
```

### 步骤 2: 设置 Firebase（必须先完成）

这是最重要的步骤，因为前后端都依赖 Firebase。

#### 2.1 创建 Firebase 项目

1. 访问 [Firebase 控制台](https://console.firebase.google.com)
2. 点击"添加项目"
3. 项目名称：`ai-diary-dev`（或你喜欢的名称）
4. 禁用 Google Analytics（开发环境不需要）
5. 创建项目

#### 2.2 启用身份验证

1. 在 Firebase 控制台，点击左侧菜单 **Authentication**
2. 点击"开始使用"
3. 选择"电子邮件/密码"
4. 启用"电子邮件/密码"
5. 保存

#### 2.3 创建 Firestore 数据库

1. 点击左侧菜单 **Firestore Database**
2. 点击"创建数据库"
3. 选择"以测试模式启动"（开发环境）
4. 选择位置：**us-central（美国中部）**
5. 启用

#### 2.4 获取 Firebase 配置

1. 点击项目设置（齿轮图标）
2. 在"常规"选项卡，向下滚动到"您的应用"
3. 点击 Web 图标（`</>`）
4. 注册应用名称：`ai-diary-web`
5. 复制 Firebase 配置对象

#### 2.5 下载服务账号密钥

1. 在项目设置中，点击"服务账号"选项卡
2. 点击"生成新的私钥"
3. 下载 JSON 文件
4. 将文件重命名为 `service-account.json`
5. 放在项目根目录（`JD_Project/service-account.json`）

### 步骤 3: 获取 OpenAI API 密钥

1. 访问 https://platform.openai.com/api-keys
2. 登录或注册账号
3. 点击"Create new secret key"
4. 复制密钥（只显示一次！）
5. 保存到安全的地方

### 步骤 4: 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 在项目根目录
nano .env
```

填入以下内容（替换为你的实际值）：

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Firebase Frontend 配置（从 Firebase 控制台获取）
VITE_FIREBASE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_FIREBASE_AUTH_DOMAIN=ai-diary-dev.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=ai-diary-dev
VITE_FIREBASE_STORAGE_BUCKET=ai-diary-dev.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:xxxxxxxxxxxxx

# Firebase Backend 配置
FIREBASE_PROJECT_ID=ai-diary-dev

# 本地开发 URL
VITE_API_URL=http://localhost:8000

# Weaviate URL
WEAVIATE_URL=http://localhost:8080
```

保存文件（Ctrl+O，回车，Ctrl+X）

---

## 开发工作流

### 方式一：使用 Docker Compose（推荐，最简单）

这是最简单的方式，一条命令启动所有服务。

```bash
# 启动所有服务（前端、后端、Weaviate）
docker-compose up --build

# 或者在后台运行
docker-compose up -d --build
```

**优点**：
- ✅ 一键启动所有服务
- ✅ 环境一致，避免依赖问题
- ✅ 自动网络配置

**缺点**：
- ❌ 代码热重载可能较慢
- ❌ 调试稍微复杂

**适用场景**：快速测试完整功能

---

### 方式二：手动启动各服务（推荐，开发调试）

这种方式给你最大的控制权，方便调试。

#### 2.1 启动 Weaviate（向量数据库）

```bash
# 在新终端窗口
docker run -d \
  --name weaviate-dev \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e ENABLE_MODULES=text2vec-openai \
  semitechnologies/weaviate:1.23.0

# 检查是否运行
curl http://localhost:8080/v1/.well-known/ready
# 应该返回: {"status":"healthy"}
```

#### 2.2 启动后端（FastAPI）

```bash
# 在新终端窗口
cd backend

# 创建虚拟环境（只需要做一次）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# 安装依赖（只需要做一次）
pip install -r requirements.txt

# 确保 service-account.json 在项目根目录
ls ../service-account.json

# 设置环境变量（临时，每次启动都需要）
export OPENAI_API_KEY="你的OpenAI密钥"
export FIREBASE_PROJECT_ID="ai-diary-dev"
export WEAVIATE_URL="http://localhost:8080"
export GOOGLE_APPLICATION_CREDENTIALS="../service-account.json"

# 启动后端服务器（开发模式，支持热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

你应该看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**测试后端**：
```bash
# 在新终端
curl http://localhost:8000/health
# 应该返回: {"status":"healthy"}

# 查看 API 文档
open http://localhost:8000/docs  # macOS
# 或直接在浏览器访问
```

#### 2.3 启动前端（React + Vite）

```bash
# 在新终端窗口
cd frontend

# 安装依赖（只需要做一次）
npm install

# 启动开发服务器
npm run dev
```

你应该看到：
```
VITE v5.0.8  ready in 432 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h to show help
```

**访问应用**：
在浏览器打开 http://localhost:5173

---

## 调试技巧

### 前端调试

#### 1. Chrome DevTools

```bash
# 在浏览器中按 F12 打开开发者工具
```

**常用技巧**：
- **Console**：查看日志和错误
- **Network**：查看 API 请求和响应
- **Application** > Local Storage：查看存储的数据
- **Sources**：设置断点调试

#### 2. React DevTools

安装 Chrome 扩展：[React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)

**使用**：
- 查看组件树
- 检查组件状态（Zustand store）
- 查看 props 传递

#### 3. 查看前端日志

```bash
# 前端终端会显示实时日志
# 注意观察错误信息
```

**常见问题**：
```javascript
// 如果看到 Firebase 错误
// 检查 .env 文件中的 VITE_FIREBASE_* 配置

// 如果看到 API 调用失败
// 检查 VITE_API_URL 是否正确（http://localhost:8000）
```

### 后端调试

#### 1. 查看日志

后端终端会显示所有请求：
```
INFO:     127.0.0.1:52891 - "GET /diaries HTTP/1.1" 200 OK
INFO:     127.0.0.1:52892 - "POST /diaries HTTP/1.1" 201 Created
```

#### 2. 添加调试日志

在代码中添加 print 语句：

```python
# backend/app/services/diary_service.py
async def create_diary(self, diary: DiaryCreate, user_id: str):
    print(f"Creating diary for user: {user_id}")  # 调试日志
    print(f"Title: {diary.title}, Content: {diary.content}")
    
    # ... 其他代码
```

#### 3. 使用 VS Code 调试器

创建 `.vscode/launch.json`（已包含在项目中）：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

**使用**：
1. 在 VS Code 中打开后端代码
2. 点击行号左侧设置断点
3. 按 F5 启动调试
4. 从前端触发请求
5. 代码会在断点处暂停

#### 4. 测试 API 端点

使用 Swagger UI（自动生成）：
```bash
open http://localhost:8000/docs
```

或使用 curl：
```bash
# 获取所有日记（需要先登录获取 token）
curl -X GET "http://localhost:8000/diaries" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Weaviate 调试

#### 检查向量数据库

```bash
# 查看所有对象
curl http://localhost:8080/v1/objects

# 查看 schema
curl http://localhost:8080/v1/schema

# 查看特定类的对象
curl http://localhost:8080/v1/objects?class=DiaryEntry
```

---

## 测试流程

### 完整功能测试清单

按照以下顺序测试每个功能：

#### ✅ 1. 用户认证

```bash
# 在浏览器打开 http://localhost:5173
```

- [ ] **注册新账号**
  - 输入邮箱：`test@example.com`
  - 输入密码：`Test123456`
  - 点击"创建账号"
  - 应该自动登录并跳转到仪表板

- [ ] **登出**
  - 点击右上角"Logout"
  - 应该回到登录页面

- [ ] **登录**
  - 输入刚才的邮箱和密码
  - 点击"Sign In"
  - 应该成功登录

**检查点**：
- 查看后端日志，应该看到 Firebase token 验证成功
- 查看 Chrome DevTools > Application > Local Storage，不应该存储敏感信息

#### ✅ 2. 创建日记

- [ ] **创建第一篇日记**
  - 点击"New Entry"
  - 标题：`我的第一篇日记`
  - 内容：`今天心情很好，开始学习全栈开发...`（至少写几句话）
  - 点击"Save"
  - 应该看到成功提示并回到仪表板

- [ ] **验证数据存储**
  ```bash
  # 查看 Firestore（在 Firebase 控制台）
  # 应该看到 diaries 集合中有一条记录
  
  # 查看 Weaviate
  curl http://localhost:8080/v1/objects?class=DiaryEntry
  # 应该看到向量嵌入
  ```

- [ ] **创建更多日记**
  - 再创建 2-3 篇不同主题的日记
  - 用于测试 AI 洞察功能

#### ✅ 3. 查看和管理日记

- [ ] **仪表板显示**
  - 应该看到所有日记按时间倒序排列
  - 每个日记卡片显示标题、预览、日期

- [ ] **查看日记详情**
  - 点击任意日记的编辑按钮
  - 应该看到完整内容

- [ ] **更新日记**
  - 修改标题或内容
  - 点击"Save"
  - 应该看到更新成功

- [ ] **删除日记**
  - 点击删除按钮
  - 确认删除
  - 日记应该从列表中消失

**检查点**：
- 后端日志应该显示 CRUD 操作
- Firestore 数据应该同步更新

#### ✅ 4. AI 洞察功能（核心功能）

- [ ] **生成 AI 洞察**
  - 打开任意日记
  - 点击"Get AI Insight"按钮
  - 等待 5-10 秒
  - 应该看到 AI 生成的个性化反馈

**检查后端日志**：
```bash
# 应该看到以下流程：
1. 生成向量嵌入 (OpenAI API call)
2. 搜索相似日记 (Weaviate query)
3. 构建上下文
4. 调用 GPT-3.5 生成洞察
5. 保存洞察到 Firestore
```

**常见问题排查**：
```bash
# 如果 AI 洞察失败，检查：

# 1. OpenAI API 密钥是否正确
echo $OPENAI_API_KEY

# 2. 查看后端错误日志
# 可能是 API 额度不足或网络问题

# 3. 测试 OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### ✅ 5. 边界情况测试

- [ ] **空内容测试**
  - 尝试保存空标题或空内容
  - 应该看到验证错误

- [ ] **长内容测试**
  - 写一篇很长的日记（1000+ 字）
  - 应该能正常保存和显示

- [ ] **特殊字符测试**
  - 在日记中使用 emoji、中文、特殊符号
  - 应该能正常显示

- [ ] **并发测试**
  - 在多个浏览器标签页同时操作
  - 数据应该保持一致

---

## 调试常见问题

### 问题 1: 前端无法连接后端

**症状**：前端显示"Failed to load diaries"或类似错误

**解决方案**：
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查前端环境变量
cat frontend/.env  # 或 .env 文件
# VITE_API_URL 应该是 http://localhost:8000

# 3. 检查 CORS 设置
# 后端应该允许来自 http://localhost:5173 的请求
# 查看 backend/app/main.py 中的 CORS 配置

# 4. 查看浏览器控制台错误
# 按 F12 查看详细错误信息
```

### 问题 2: Firebase Authentication 失败

**症状**："Invalid authentication token"或登录失败

**解决方案**：
```bash
# 1. 检查 Firebase 配置
cat .env | grep FIREBASE

# 2. 验证 service-account.json 存在
ls -la service-account.json

# 3. 检查 Firebase 控制台
# - Authentication 是否启用
# - Email/Password 提供商是否启用

# 4. 查看后端日志
# 应该看到 Firebase 初始化信息
```

### 问题 3: Weaviate 连接失败

**症状**："Failed to connect to Weaviate"

**解决方案**：
```bash
# 1. 检查 Weaviate 是否运行
docker ps | grep weaviate

# 2. 测试连接
curl http://localhost:8080/v1/.well-known/ready

# 3. 重启 Weaviate
docker stop weaviate-dev
docker rm weaviate-dev
# 然后重新运行启动命令

# 4. 查看 Weaviate 日志
docker logs weaviate-dev
```

### 问题 4: OpenAI API 调用失败

**症状**："Failed to generate AI insight"

**解决方案**：
```bash
# 1. 验证 API 密钥
echo $OPENAI_API_KEY

# 2. 测试 API 可用性
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 3. 检查账户余额
# 访问 https://platform.openai.com/account/usage

# 4. 查看详细错误
# 后端日志会显示 OpenAI 的具体错误信息
```

### 问题 5: 端口已被占用

**症状**："Address already in use"

**解决方案**：
```bash
# 查找占用端口的进程
lsof -ti:8000  # 后端
lsof -ti:5173  # 前端
lsof -ti:8080  # Weaviate

# 终止进程
kill -9 $(lsof -ti:8000)

# 或者更改端口
# 前端: vite.config.ts 中修改 port
# 后端: uvicorn --port 8001
```

---

## 部署前检查

在部署到云端之前，完成以下检查：

### ✅ 代码质量检查

```bash
# 1. 前端代码检查
cd frontend
npm run lint
npm run build  # 确保能成功构建

# 2. 后端代码检查
cd backend
source venv/bin/activate
flake8 app --max-line-length=120

# 3. 类型检查
# TypeScript 会在编译时检查
# Python 可以用 mypy（可选）
```

### ✅ 功能测试

- [ ] 所有核心功能都正常工作
- [ ] 没有控制台错误
- [ ] API 响应时间合理（< 2 秒）
- [ ] AI 洞察生成成功
- [ ] 数据正确存储和检索

### ✅ 安全检查

- [ ] 没有硬编码的密钥或密码
- [ ] `.env` 文件在 `.gitignore` 中
- [ ] `service-account.json` 在 `.gitignore` 中
- [ ] 敏感数据不在前端暴露

### ✅ 性能检查

```bash
# 检查前端包大小
cd frontend
npm run build
ls -lh dist/

# 应该小于 5MB
```

### ✅ Git 提交

```bash
# 确保所有更改都已提交
git status

# 如果有未提交的更改
git add .
git commit -m "feat: 完成本地开发和测试"

# 推送到远程仓库
git push origin main
```

---

## 部署到云端

一切本地测试通过后，开始部署到 GCP！

### 方式一：使用 Terraform（推荐）

```bash
# 1. 安装 Terraform
brew install terraform  # macOS
# 或访问 https://www.terraform.io/downloads

# 2. 创建 GCP 项目
export PROJECT_ID="ai-diary-prod"
gcloud projects create $PROJECT_ID

# 3. 配置 Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # 填入你的值

# 4. 初始化 Terraform
terraform init

# 5. 查看执行计划
terraform plan

# 6. 应用配置（创建所有资源）
terraform apply

# 7. 记录输出的 URL
terraform output
```

详细部署步骤请查看：[DEPLOYMENT_CN.md](DEPLOYMENT_CN.md)

### 方式二：使用部署脚本

```bash
# 设置项目 ID
export PROJECT_ID="ai-diary-prod"

# 运行部署脚本
chmod +x scripts/deploy-gcp.sh
./scripts/deploy-gcp.sh
```

### 方式三：使用 GitHub Actions（自动化）

```bash
# 1. 在 GitHub 仓库设置 Secrets

# 2. 推送到 main 分支
git push origin main

# 3. 在 GitHub Actions 标签页查看部署进度

# 4. 部署完成后获取 URL
```

---

## 开发最佳实践

### 1. 分支管理

```bash
# 创建功能分支
git checkout -b feature/add-diary-tags

# 开发完成后
git add .
git commit -m "feat: 添加日记标签功能"
git push origin feature/add-diary-tags

# 创建 Pull Request
# 在 GitHub 上合并到 main
```

### 2. 频繁提交

```bash
# 小改动就提交
git add .
git commit -m "fix: 修复日记删除bug"

# 遵循 Conventional Commits 规范
# feat: 新功能
# fix: bug修复
# docs: 文档更新
# style: 代码格式
# refactor: 重构
# test: 测试
# chore: 其他修改
```

### 3. 环境隔离

```bash
# 开发环境
.env              # 本地开发

# 生产环境
.env.production   # 生产配置（不要提交到 Git！）
```

### 4. 日志管理

```python
# 使用 logging 而不是 print
import logging

logger = logging.getLogger(__name__)
logger.info("Creating diary for user: %s", user_id)
logger.error("Failed to generate insight: %s", error)
```

### 5. 定期备份

```bash
# 备份 Firestore（本地开发可选）
# 生产环境一定要做！

# 备份代码
git push origin main
```

---

## 常用命令速查

### Docker Compose

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 重新构建并启动
docker-compose up --build

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 重启单个服务
docker-compose restart backend
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

### 后端开发

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest

# 代码格式化
black app/

# 代码检查
flake8 app/
```

### Git 操作

```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "描述信息"

# 推送
git push origin main

# 拉取最新代码
git pull origin main

# 查看日志
git log --oneline

# 撤销更改
git checkout -- filename
```

---

## 总结

完整的开发流程：

1. **准备环境** → 安装必需软件
2. **设置 Firebase** → 创建项目、启用服务
3. **配置密钥** → `.env` 文件和 `service-account.json`
4. **本地开发** → 启动服务、编写代码
5. **调试测试** → 使用 DevTools 和日志
6. **功能测试** → 完整测试所有功能
7. **代码检查** → Lint 和构建
8. **Git 提交** → 保存代码
9. **部署上线** → Terraform 或脚本部署
10. **监控维护** → 查看日志和性能

记住：
- ✅ 先在本地测试通过
- ✅ 提交前检查代码质量
- ✅ 部署前做好备份
- ✅ 部署后验证功能

祝你开发顺利！🚀

有问题随时查看：
- [README_CN.md](README_CN.md) - 项目总览
- [ARCHITECTURE_CN.md](ARCHITECTURE_CN.md) - 架构详解
- [DEPLOYMENT_CN.md](DEPLOYMENT_CN.md) - 部署指南

