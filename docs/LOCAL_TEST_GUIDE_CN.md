# 本地测试完整指南

## 🎯 概述

本指南将教你如何在本地测试整个项目（AI日记 + XdfClassArranger课程安排系统）。

## 📋 前置条件

确保已完成：
1. ✅ Firebase 项目设置
2. ✅ OpenAI API 密钥获取
3. ✅ `.env` 文件配置
4. ✅ `service-account.json` 放在项目根目录

如果还没完成，请先查看 [LOCAL_DEVELOPMENT_CN.md](LOCAL_DEVELOPMENT_CN.md)

## 🚀 快速开始测试

### 方式一：使用 Docker Compose（最简单）

```bash
# 1. 确保在项目根目录
cd /Users/benz/Desktop/Stanford/SP26/Monoya/JD_Project

# 2. 确认 .env 文件存在并包含所有必需的配置
cat .env

# 3. 启动所有服务
docker-compose up --build

# 等待所有服务启动，你会看到：
# ✓ Weaviate ready on http://localhost:8080
# ✓ Backend ready on http://localhost:8000
# ✓ Frontend ready on http://localhost:5173
```

**访问应用**：
- 前端：http://localhost:5173
- 后端API文档：http://localhost:8000/docs
- Weaviate：http://localhost:8080

---

### 方式二：手动启动（推荐，方便调试）

#### 终端 1 - 启动 Weaviate

```bash
docker run -d \
  --name weaviate-dev \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e ENABLE_MODULES=text2vec-openai \
  semitechnologies/weaviate:1.23.0

# 验证 Weaviate 运行正常
curl http://localhost:8080/v1/.well-known/ready
# 应该返回: {"status":"healthy"}
```

#### 终端 2 - 启动后端

```bash
cd backend

# 创建并激活虚拟环境（首次运行）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 设置环境变量（每次启动都需要）
export OPENAI_API_KEY="你的OpenAI密钥"
export FIREBASE_PROJECT_ID="你的Firebase项目ID"
export WEAVIATE_URL="http://localhost:8080"
export GOOGLE_APPLICATION_CREDENTIALS="../service-account.json"

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 你应该看到：
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

#### 终端 3 - 启动前端

```bash
cd frontend

# 删除旧的 TypeScript 文件（如果还存在）
rm -f src/main.tsx src/App.tsx src/config/firebase.ts src/store/authStore.ts
rm -f src/types/diary.ts src/api/client.ts src/api/diaries.ts
rm -rf src/pages/*.tsx

# 删除 TypeScript 配置文件
rm -f tsconfig.json tsconfig.node.json vite.config.ts

# 安装依赖（包含 FullCalendar）
npm install

# 启动前端
npm run dev

# 你应该看到：
# VITE v5.0.8  ready in 432 ms
# ➜  Local:   http://localhost:5173/
```

---

## 🧪 完整功能测试清单

### 测试 1: 基础认证功能

#### 1.1 注册新账号

1. 打开浏览器访问 http://localhost:5173
2. 点击 "Sign Up" 标签
3. 输入测试邮箱：`test@example.com`
4. 输入密码：`Test123456`（至少6个字符）
5. 点击 "Create Account"

**预期结果**：
- ✅ 看到 "Account created successfully!" 提示
- ✅ 自动跳转到仪表板（Dashboard）
- ✅ 后端终端显示 Firebase token 验证日志

**常见问题**：
- ❌ "Firebase: Error (auth/invalid-api-key)" → 检查 `.env` 中的 `VITE_FIREBASE_API_KEY`
- ❌ "Firebase: Error (auth/operation-not-allowed)" → 在 Firebase 控制台启用 Email/Password 认证

#### 1.2 登出和登录

1. 点击右上角 "Logout"
2. 应该回到登录页面
3. 点击 "Sign In" 标签
4. 输入刚才的邮箱和密码
5. 点击 "Sign In"

**预期结果**：
- ✅ 成功登录并看到仪表板

---

### 测试 2: AI 日记功能

#### 2.1 创建第一篇日记

1. 在仪表板点击 "New Entry"
2. 标题：`我的第一篇日记`
3. 内容（至少写几句话）：
   ```
   今天是我第一次使用 AI 日记应用。
   我感觉这个项目很有意思，学到了很多关于全栈开发的知识。
   包括 React、FastAPI、Firebase、OpenAI、Weaviate 等技术。
   我对未来的学习充满期待！
   ```
4. 点击 "Save"

**预期结果**：
- ✅ 看到 "Diary created successfully!" 提示
- ✅ 回到仪表板
- ✅ 看到新创建的日记卡片

**检查后端日志**：
```bash
# 应该看到类似的日志：
INFO:     127.0.0.1:xxxxx - "POST /diaries HTTP/1.1" 201 Created
# Firestore 保存成功
# Weaviate 索引成功
```

**检查 Firestore**：
1. 访问 Firebase 控制台
2. Firestore Database
3. 应该看到 `diaries` 集合中有一条记录

**检查 Weaviate**：
```bash
curl http://localhost:8080/v1/objects?class=DiaryEntry
# 应该看到向量嵌入数据
```

#### 2.2 创建更多日记

创建 2-3 篇不同主题的日记，用于测试 AI 洞察功能：

**日记 2**：
```
标题：学习 React Hooks
内容：今天深入学习了 React Hooks，特别是 useState 和 useEffect。
这些 Hooks 让函数组件变得非常强大，代码也更加简洁。
我理解了组件生命周期和副作用管理的概念。
```

**日记 3**：
```
标题：部署到云端的挑战
内容：今天研究了如何将应用部署到 GCP。
学习了 Terraform、Cloud Run、Docker 等技术。
虽然有些复杂，但逐步理解了云原生架构的优势。
```

#### 2.3 查看和编辑日记

1. 在仪表板点击任意日记的编辑按钮（铅笔图标）
2. 修改标题或内容
3. 点击 "Save"

**预期结果**：
- ✅ 看到 "Diary updated successfully!" 提示
- ✅ 更新后的内容在仪表板显示

#### 2.4 生成 AI 洞察（核心功能）

1. 打开任意已保存的日记
2. 点击 "Get AI Insight" 按钮
3. 等待 5-15 秒

**预期结果**：
- ✅ 看到加载指示器
- ✅ 生成个性化的 AI 反馈
- ✅ 反馈显示在页面底部的紫色卡片中

**后端日志应该显示**：
```
1. 获取日记内容
2. 生成 OpenAI 嵌入 (text-embedding-ada-002)
3. 在 Weaviate 中搜索相似日记
4. 调用 GPT-3.5 生成洞察
5. 保存洞察到 Firestore
```

**AI 洞察示例**：
```
我注意到你对技术学习充满热情！从你的日记中可以看出，你
正在积极地探索全栈开发的各个方面。保持这种学习态度，
你一定会取得很大进步。建议你可以多实践项目，将学到的
知识应用到实际中。加油！
```

**故障排除**：
- ❌ "Failed to generate AI insight"
  - 检查 OpenAI API 密钥是否正确
  - 检查 OpenAI 账户余额
  - 查看后端日志详细错误信息

#### 2.5 删除日记

1. 在仪表板点击日记的删除按钮（垃圾桶图标）
2. 确认删除

**预期结果**：
- ✅ 日记从列表中消失
- ✅ Firestore 中的记录被删除
- ✅ Weaviate 中的向量被删除

---

### 测试 3: XdfClassArranger 课程安排系统

#### 3.1 访问课程安排器

1. 在仪表板点击右上角的 "Class Arranger" 按钮
2. 应该进入 XdfClassArranger 界面

**预期结果**：
- ✅ 看到 FullCalendar 日历界面
- ✅ 预置的示例课程显示在日历上
- ✅ 可以切换月/周/日/列表视图

#### 3.2 添加新课程

1. 在日历上点击任意日期/时间
2. 在弹出的对话框中输入课程信息：
   - 标题：`测试课程 - 学生姓名`
   - 学生：`测试学生`
   - 老师：`测试老师`
   - 校区：`测试校区`
   - 教室：`教室1`
3. 点击保存

**预期结果**：
- ✅ 新课程显示在日历上
- ✅ 带有随机颜色
- ✅ 显示课程详细信息

#### 3.3 拖拽和调整课程

1. **拖动课程**：点击并拖动课程到不同日期/时间
2. **调整时长**：拖动课程边缘来改变时长

**预期结果**：
- ✅ 课程时间更新
- ✅ 视觉反馈流畅

#### 3.4 查看和删除课程

1. 点击日历上的任意课程
2. 查看详细信息
3. 点击 "确定" 按钮删除课程

**预期结果**：
- ✅ 课程从日历中消失

#### 3.5 切换视图

测试所有视图：
- **月视图**：整月概览
- **周视图**：带时间轴的周视图
- **日视图**：单日详情
- **列表视图**：简洁列表

**预期结果**：
- ✅ 所有视图正常工作
- ✅ 课程在所有视图中正确显示
- ✅ 中文界面显示正常

---

### 测试 4: 导航和路由

测试所有路由：

1. `/` → 自动重定向到 `/dashboard`
2. `/login` → 登录页面
3. `/dashboard` → 仪表板
4. `/diary/new` → 新建日记
5. `/diary/:id` → 编辑日记
6. `/xdf-class-arranger` → 课程安排器

**预期结果**：
- ✅ 所有路由正常工作
- ✅ 未登录用户重定向到登录页
- ✅ 登录用户可以访问所有功能页面

---

## 🐛 常见问题排查

### 问题 1: 前端无法启动

**症状**：`npm run dev` 报错

**解决方案**：
```bash
# 1. 清除 node_modules
rm -rf node_modules package-lock.json

# 2. 重新安装
npm install

# 3. 检查 Node.js 版本
node --version  # 应该是 v20+

# 4. 检查 .eslintrc.cjs 配置
cat .eslintrc.cjs
```

### 问题 2: FullCalendar 不显示

**症状**：XdfClassArranger 页面空白或报错

**解决方案**：
```bash
# 1. 确认 FullCalendar 包已安装
npm list @fullcalendar/react

# 2. 重新安装 FullCalendar
npm install @fullcalendar/react @fullcalendar/core @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction @fullcalendar/list

# 3. 检查 CSS 文件是否正确导入
ls src/XdfClassArranger/XdfClassArranger.css
```

### 问题 3: 后端无法连接 Weaviate

**症状**："Failed to connect to Weaviate"

**解决方案**：
```bash
# 1. 检查 Weaviate 是否运行
docker ps | grep weaviate

# 2. 测试 Weaviate 连接
curl http://localhost:8080/v1/.well-known/ready

# 3. 查看 Weaviate 日志
docker logs weaviate-dev

# 4. 重启 Weaviate
docker stop weaviate-dev
docker rm weaviate-dev
# 然后重新运行启动命令
```

### 问题 4: Firebase 认证失败

**症状**："Invalid authentication token"

**解决方案**：
```bash
# 1. 检查 .env 文件
cat .env | grep FIREBASE

# 2. 验证 service-account.json
ls -la service-account.json

# 3. 在 Firebase 控制台检查
# - Authentication 是否启用
# - Email/Password 提供商是否启用
# - 项目 ID 是否正确

# 4. 清除浏览器缓存
# Chrome: Cmd+Shift+Delete (Mac) / Ctrl+Shift+Delete (Windows)
```

### 问题 5: OpenAI API 调用失败

**症状**："Failed to generate AI insight"

**解决方案**：
```bash
# 1. 测试 API 密钥
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 2. 检查账户余额
# 访问 https://platform.openai.com/account/usage

# 3. 检查 API 配额
# 免费账户有使用限制

# 4. 查看后端详细错误
# 后端终端会显示 OpenAI 的错误信息
```

---

## 📊 测试结果记录

用以下表格记录测试结果：

| 功能模块 | 测试项 | 状态 | 备注 |
|---------|-------|------|------|
| 认证 | 注册账号 | ⬜ | |
| 认证 | 登录/登出 | ⬜ | |
| AI日记 | 创建日记 | ⬜ | |
| AI日记 | 编辑日记 | ⬜ | |
| AI日记 | 删除日记 | ⬜ | |
| AI日记 | 生成洞察 | ⬜ | |
| XdfClassArranger | 显示日历 | ⬜ | |
| XdfClassArranger | 添加课程 | ⬜ | |
| XdfClassArranger | 拖拽课程 | ⬜ | |
| XdfClassArranger | 删除课程 | ⬜ | |
| XdfClassArranger | 切换视图 | ⬜ | |
| 导航 | 路由跳转 | ⬜ | |

✅ = 通过 | ❌ = 失败 | ⬜ = 未测试

---

## 🎯 性能测试

### 响应时间基准

| 操作 | 预期时间 | 实际时间 | 状态 |
|------|---------|---------|------|
| 登录 | < 2秒 | | |
| 加载日记列表 | < 1秒 | | |
| 创建日记 | < 2秒 | | |
| 生成 AI 洞察 | 5-15秒 | | |
| 加载日历 | < 1秒 | | |
| 拖拽课程 | 实时 | | |

---

## 🧹 测试后清理

测试完成后，清理测试数据：

```bash
# 1. 停止所有服务
docker-compose down  # 如果用 docker-compose
# 或分别停止各个终端的进程 (Ctrl+C)

# 2. 清理 Docker 容器
docker stop weaviate-dev
docker rm weaviate-dev

# 3. 清理测试数据（可选）
# 在 Firebase 控制台手动删除测试用户和日记数据

# 4. 清理 Docker 卷（可选，会删除所有数据）
docker volume prune
```

---

## 📝 下一步

测试通过后，你可以：

1. **继续本地开发**：添加新功能
2. **准备部署**：查看 [GCP_DEPLOYMENT_BUDGET_CN.md](GCP_DEPLOYMENT_BUDGET_CN.md)
3. **优化性能**：根据测试结果优化慢的部分
4. **添加更多测试**：编写自动化测试

---

## 🆘 需要帮助？

如果测试过程中遇到问题：

1. 查看详细日志：
   - 前端：浏览器 Console (F12)
   - 后端：终端输出
   - Docker：`docker logs CONTAINER_NAME`

2. 查看文档：
   - [LOCAL_DEVELOPMENT_CN.md](LOCAL_DEVELOPMENT_CN.md) - 本地开发指南
   - [ARCHITECTURE_CN.md](ARCHITECTURE_CN.md) - 架构说明
   - [XdfClassArranger/快速启动指南.md](frontend/src/XdfClassArranger/快速启动指南.md) - 课程安排器指南

3. 检查配置：
   - `.env` 文件
   - `service-account.json`
   - Firebase 控制台设置

祝测试顺利！🎉

