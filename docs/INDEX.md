# 📚 AI Diary 项目文档中心

欢迎来到 AI Diary 项目文档中心！本文档索引帮助你快速找到所需的信息。

---

## 🚀 快速导航

### 我是新手，想快速开始

→ [快速开始指南 (中文)](./QUICKSTART_CN.md)  
→ [快速参考手册](./QUICK_REFERENCE_CN.md)

### 我想了解项目架构

→ [架构设计文档 (中文)](./ARCHITECTURE_CN.md)  
→ [RAG 流程详解](./RAG_FLOW_EXPLAINED.md)

### 我想本地开发

→ [本地开发指南](./LOCAL_DEVELOPMENT_CN.md)  
→ [本地测试指南](./LOCAL_TEST_GUIDE_CN.md)

### 我想部署到云端

→ [GCP 部署指南 (中文)](./DEPLOYMENT_CN.md)  
→ [GCP 成本预算指南](./GCP_DEPLOYMENT_BUDGET_CN.md)

### 我想学习特定技术

→ [Weaviate 向量数据库教程](./WEAVIATE_TUTORIAL.md)  
→ [Terraform IaC 教程](./TERRAFORM_TUTORIAL.md)  
→ [Llama 本地模型设置](./LLAMA_SETUP.md)

### 我想申请工作

→ [Full-Stack Engineer 技能展示](./FULLSTACK_ENGINEER_GUIDE.md)  
→ [AI/ML Engineer 技能展示](./AI_ML_ENGINEER_GUIDE.md)

---

## 📖 文档分类

### 1️⃣ 快速开始

| 文档                                             | 说明                        | 适合人群  |
| ------------------------------------------------ | --------------------------- | --------- |
| [QUICKSTART_CN.md](./QUICKSTART_CN.md)           | 快速开始指南（中文）        | 所有人 ⭐ |
| [QUICKSTART.md](./QUICKSTART.md)                 | Quick Start Guide (English) | Everyone  |
| [QUICK_REFERENCE_CN.md](./QUICK_REFERENCE_CN.md) | 常用命令速查表              | 开发者    |

**推荐阅读顺序**：QUICKSTART_CN.md → QUICK_REFERENCE_CN.md

---

### 2️⃣ 架构与设计

| 文档                                             | 说明                          | 技术深度 |
| ------------------------------------------------ | ----------------------------- | -------- |
| [ARCHITECTURE_CN.md](./ARCHITECTURE_CN.md)       | 系统架构设计（中文）          | ⭐⭐⭐   |
| [ARCHITECTURE.md](./ARCHITECTURE.md)             | System Architecture (English) | ⭐⭐⭐   |
| [RAG_FLOW_EXPLAINED.md](./RAG_FLOW_EXPLAINED.md) | RAG 工作流程详解              | ⭐⭐⭐⭐ |

**核心概念**：

- 前后端分离架构
- RAG (Retrieval-Augmented Generation)
- 向量数据库与语义搜索
- 微服务架构

---

### 3️⃣ 开发指南

| 文档                                                 | 说明                | 场景        |
| ---------------------------------------------------- | ------------------- | ----------- |
| [LOCAL_DEVELOPMENT_CN.md](./LOCAL_DEVELOPMENT_CN.md) | 本地开发环境搭建    | 日常开发 ⭐ |
| [LOCAL_TEST_GUIDE_CN.md](./LOCAL_TEST_GUIDE_CN.md)   | 本地测试指南        | 测试验证    |
| [LLAMA_SETUP.md](./LLAMA_SETUP.md)                   | Llama 本地 LLM 设置 | AI 功能开发 |

**开发工作流**：

```
1. 阅读 LOCAL_DEVELOPMENT_CN.md 搭建环境
2. 参考 LLAMA_SETUP.md 配置 AI 功能
3. 使用 LOCAL_TEST_GUIDE_CN.md 进行测试
4. 参考 QUICK_REFERENCE_CN.md 查找命令
```

---

### 4️⃣ 部署指南

| 文档                                                         | 说明                           | 云平台 |
| ------------------------------------------------------------ | ------------------------------ | ------ |
| [DEPLOYMENT_CN.md](./DEPLOYMENT_CN.md)                       | GCP 部署完整指南               | GCP ⭐ |
| [DEPLOYMENT.md](./DEPLOYMENT.md)                             | GCP Deployment Guide (English) | GCP    |
| [GCP_DEPLOYMENT_BUDGET_CN.md](./GCP_DEPLOYMENT_BUDGET_CN.md) | 成本优化与预算控制             | GCP 💰 |

**部署流程**：

```
开发环境 → 测试验证 → 云端部署 → 成本优化
    ↓          ↓           ↓           ↓
LOCAL_*    TEST_GUIDE   DEPLOYMENT  BUDGET
```

**估算成本**：

- 开发/测试：~$5-10/月
- 生产（低流量）：~$20-50/月
- 生产（高流量）：~$100-200/月

---

### 5️⃣ 技术教程

#### 🔍 Weaviate 向量数据库

**[WEAVIATE_TUTORIAL.md](./WEAVIATE_TUTORIAL.md)** - 完整教程

**内容大纲**：

1. Weaviate 基础概念（向量、Schema、HNSW）
2. 项目集成（Docker 部署、Python 客户端）
3. Schema 设计（数据结构、字段类型）
4. 向量嵌入（Embeddings 生成、相似度计算）
5. 数据索引（增删改查）
6. 语义搜索（向量搜索、混合搜索）
7. 高级查询（GraphQL、聚合）
8. 性能优化（HNSW 调优、批处理）
9. 生产部署（持久化、认证、监控）
10. 故障排查

**适合人群**：

- ✅ 想学习向量数据库的开发者
- ✅ 需要实现语义搜索的工程师
- ✅ AI/ML 工程师

**前置知识**：Python 基础、Docker 基础

---

#### 🏗️ Terraform 基础设施即代码

**[TERRAFORM_TUTORIAL.md](./TERRAFORM_TUTORIAL.md)** - 完整教程

**内容大纲**：

1. Terraform 基础（IaC 概念、声明式配置）
2. 项目架构（GCP 架构、文件结构）
3. 环境配置（安装、GCP SDK）
4. Provider 配置（版本管理、初始化）
5. 资源管理（Cloud Run、Firestore、IAM）
6. 状态管理（本地/远程状态、锁定）
7. 变量与输出（输入变量、敏感信息）
8. 模块化（模块创建、复用）
9. 最佳实践（文件组织、安全管理）
10. 故障排查

**适合人群**：

- ✅ DevOps 工程师
- ✅ 需要自动化部署的开发者
- ✅ Full-Stack 工程师

**前置知识**：云平台基础、命令行操作

---

#### 🦙 Llama 本地 LLM

**[LLAMA_SETUP.md](./LLAMA_SETUP.md)** - 设置指南

**内容**：

- Ollama 安装与配置
- Llama 3.2 1B 模型下载
- Docker 集成
- API 使用示例
- 故障排查

**适合人群**：

- ✅ AI 功能开发者
- ✅ 想使用本地 LLM 的工程师

---

#### 🤖 RAG 流程详解

**[RAG_FLOW_EXPLAINED.md](./RAG_FLOW_EXPLAINED.md)** - 深度解析

**内容**：

- RAG 概念详解
- 检索（Retrieval）步骤
- 增强（Augmented）步骤
- 生成（Generation）步骤
- 完整代码示例
- 性能分析

**适合人群**：

- ✅ AI/ML 工程师
- ✅ 想深入理解 RAG 的开发者

---

### 6️⃣ 职位申请

#### 💼 Full-Stack Engineer

**[FULLSTACK_ENGINEER_GUIDE.md](./FULLSTACK_ENGINEER_GUIDE.md)** - 技能展示指南

**内容结构**：

1. 端到端功能开发（Schema → API → React UI）
2. LLM 集成与 RAG 系统
3. 性能优化（Firestore、开发模式）
4. Docker 与 CI/CD（多服务编排、Terraform）
5. 认证与授权（Firebase Auth）
6. 可观测性（日志、监控）

**技能覆盖**：

- ✅ React + Vite + Tailwind CSS
- ✅ FastAPI + Python async
- ✅ Docker Compose (4 个微服务)
- ✅ Terraform IaC
- ✅ GitHub Actions CI/CD
- ✅ Firebase Auth + Firestore
- ✅ RAG + Weaviate

**简历模板**：文档中包含直接可用的简历描述

---

#### 🤖 AI/ML Engineer

**[AI_ML_ENGINEER_GUIDE.md](./AI_ML_ENGINEER_GUIDE.md)** - 技能展示指南

**内容结构**：

1. LLM 驱动的 AI 系统（Ollama 部署）
2. 向量嵌入与语义搜索（Embeddings + Weaviate）
3. 完整的 RAG Pipeline（检索-增强-生成）
4. 模型评估与优化（A/B 测试、指标）
5. 从原型到生产（Notebook → Service）
6. 多语言支持（JA-EN-ZH）
7. 监控与可观测性

**技能覆盖**：

- ✅ Ollama LLM 本地部署
- ✅ Embeddings API (768 维向量)
- ✅ Weaviate 向量数据库（HNSW 算法）
- ✅ 完整 RAG 实现（带性能分析）
- ✅ 评估框架（Precision@K, Recall@K）
- ✅ A/B 测试系统
- ✅ 多语言语义搜索

**简历模板**：文档中包含直接可用的简历描述

---

## 🎯 学习路径

### 路径 1：快速上手（1-3 天）

```
第 1 天：环境搭建
├── 1. 阅读 README_CN.md（项目根目录）
├── 2. 按照 QUICKSTART_CN.md 启动项目
└── 3. 熟悉 QUICK_REFERENCE_CN.md 常用命令

第 2 天：理解架构
├── 1. 阅读 ARCHITECTURE_CN.md
├── 2. 查看 RAG_FLOW_EXPLAINED.md
└── 3. 体验 AI 功能

第 3 天：本地开发
├── 1. 参考 LOCAL_DEVELOPMENT_CN.md
├── 2. 修改代码，观察效果
└── 3. 运行测试（LOCAL_TEST_GUIDE_CN.md）
```

---

### 路径 2：深入学习（1-2 周）

```
Week 1：核心技术
├── Day 1-2: Weaviate 教程
│   └── 完成 WEAVIATE_TUTORIAL.md 所有示例
├── Day 3-4: RAG 系统
│   └── 深入研究 RAG_FLOW_EXPLAINED.md
└── Day 5-7: 实践项目
    └── 修改 RAG 参数，优化效果

Week 2：部署与运维
├── Day 1-3: Terraform 教程
│   └── 学习 TERRAFORM_TUTORIAL.md
├── Day 4-5: 本地部署
│   └── 按照 DEPLOYMENT_CN.md 部署到 GCP
└── Day 6-7: 成本优化
    └── 应用 GCP_DEPLOYMENT_BUDGET_CN.md 策略
```

---

### 路径 3：职位申请准备（1 周）

```
Full-Stack Engineer 申请：
├── Day 1-2: 熟悉项目
│   ├── QUICKSTART_CN.md
│   ├── ARCHITECTURE_CN.md
│   └── 运行项目
├── Day 3-4: 学习技能展示
│   └── 精读 FULLSTACK_ENGINEER_GUIDE.md
├── Day 5: 准备简历
│   └── 使用文档中的简历模板
└── Day 6-7: 面试准备
    └── 熟悉技术权衡和架构决策

AI/ML Engineer 申请：
├── Day 1-2: RAG 系统
│   ├── RAG_FLOW_EXPLAINED.md
│   └── WEAVIATE_TUTORIAL.md
├── Day 3-4: 学习技能展示
│   └── 精读 AI_ML_ENGINEER_GUIDE.md
├── Day 5: 实践优化
│   ├── 修改 RAG 参数
│   └── 添加评估指标
└── Day 6-7: 面试准备
    └── 准备讨论模型评估和优化
```

---

## 🔍 按需查找

### 我想找...

#### 命令和配置

- **Docker 命令** → [QUICK_REFERENCE_CN.md](./QUICK_REFERENCE_CN.md) 的 "Docker 命令"
- **API 端点** → [ARCHITECTURE_CN.md](./ARCHITECTURE_CN.md) 的 "API 设计"
- **环境变量** → [LOCAL_DEVELOPMENT_CN.md](./LOCAL_DEVELOPMENT_CN.md) 的 "环境配置"

#### 代码示例

- **React 组件** → [FULLSTACK_ENGINEER_GUIDE.md](./FULLSTACK_ENGINEER_GUIDE.md) 第一部分
- **FastAPI 路由** → [FULLSTACK_ENGINEER_GUIDE.md](./FULLSTACK_ENGINEER_GUIDE.md) 第一部分
- **RAG 实现** → [RAG_FLOW_EXPLAINED.md](./RAG_FLOW_EXPLAINED.md) 或 [AI_ML_ENGINEER_GUIDE.md](./AI_ML_ENGINEER_GUIDE.md) 第三部分
- **Weaviate 查询** → [WEAVIATE_TUTORIAL.md](./WEAVIATE_TUTORIAL.md) 第六部分
- **Terraform 资源** → [TERRAFORM_TUTORIAL.md](./TERRAFORM_TUTORIAL.md) 第五部分

#### 故障排查

- **Docker 问题** → [LOCAL_DEVELOPMENT_CN.md](./LOCAL_DEVELOPMENT_CN.md) 故障排查
- **Weaviate 问题** → [WEAVIATE_TUTORIAL.md](./WEAVIATE_TUTORIAL.md) 第十部分
- **Terraform 问题** → [TERRAFORM_TUTORIAL.md](./TERRAFORM_TUTORIAL.md) 第十部分
- **部署问题** → [DEPLOYMENT_CN.md](./DEPLOYMENT_CN.md) 故障排查

#### 性能优化

- **Firestore 优化** → [FULLSTACK_ENGINEER_GUIDE.md](./FULLSTACK_ENGINEER_GUIDE.md) 第三部分
- **Weaviate 优化** → [WEAVIATE_TUTORIAL.md](./WEAVIATE_TUTORIAL.md) 第八部分
- **RAG 优化** → [AI_ML_ENGINEER_GUIDE.md](./AI_ML_ENGINEER_GUIDE.md) 第四部分
- **成本优化** → [GCP_DEPLOYMENT_BUDGET_CN.md](./GCP_DEPLOYMENT_BUDGET_CN.md)

---

## 📊 文档统计

| 类别     | 文档数量 | 总页数（估算） |
| -------- | -------- | -------------- |
| 快速开始 | 3        | ~50 页         |
| 架构设计 | 3        | ~40 页         |
| 开发指南 | 3        | ~60 页         |
| 部署指南 | 3        | ~70 页         |
| 技术教程 | 4        | ~200 页        |
| 职位展示 | 2        | ~100 页        |
| **总计** | **18**   | **~520 页**    |

---

## 🎓 贡献指南

如果你想改进文档：

1. **发现错误** → 提交 Issue
2. **改进内容** → 创建 Pull Request
3. **添加示例** → 欢迎贡献代码示例
4. **翻译文档** → 帮助翻译成其他语言

---

## 📞 获取帮助

- **GitHub Issues**: 项目问题和 Bug 报告
- **文档反馈**: 如果文档有不清楚的地方，请提交 Issue
- **技术讨论**: 欢迎在 Issues 中讨论技术细节

---

## 🔗 外部资源

### 官方文档

- [React 文档](https://react.dev/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Weaviate 文档](https://weaviate.io/developers/weaviate)
- [Terraform 文档](https://www.terraform.io/docs)
- [Google Cloud 文档](https://cloud.google.com/docs)

### 相关技术

- [OpenAI API](https://platform.openai.com/docs)
- [Ollama](https://ollama.ai/)
- [Firebase](https://firebase.google.com/docs)
- [Docker](https://docs.docker.com/)

---

## 📝 文档更新日志

| 日期       | 更新内容                           |
| ---------- | ---------------------------------- |
| 2026-01-20 | ✅ 创建文档中心索引                |
| 2026-01-20 | ✅ 整理所有文档到 docs/ 文件夹     |
| 2026-01-17 | ✅ 添加 Weaviate 和 Terraform 教程 |
| 2026-01-17 | ✅ 添加职位技能展示指南            |
| 2026-01-15 | ✅ 完成 RAG 流程文档               |
| 2026-01-10 | ✅ 初始文档创建                    |

---

## ✨ 快速链接

**最常用的 5 个文档**：

1. [快速开始 (中文)](./QUICKSTART_CN.md) ⭐⭐⭐⭐⭐
2. [架构设计 (中文)](./ARCHITECTURE_CN.md) ⭐⭐⭐⭐
3. [本地开发指南](./LOCAL_DEVELOPMENT_CN.md) ⭐⭐⭐⭐
4. [Weaviate 教程](./WEAVIATE_TUTORIAL.md) ⭐⭐⭐⭐
5. [Full-Stack 技能展示](./FULLSTACK_ENGINEER_GUIDE.md) ⭐⭐⭐⭐

**推荐学习顺序**：

```
QUICKSTART_CN.md
    ↓
ARCHITECTURE_CN.md
    ↓
RAG_FLOW_EXPLAINED.md
    ↓
WEAVIATE_TUTORIAL.md
    ↓
DEPLOYMENT_CN.md
```

---

**祝你学习愉快！🚀**

如有问题，请查阅相关文档或提交 Issue。
