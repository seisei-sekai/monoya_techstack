# 🚀 Full-Stack Engineer 技能展示指南

## 📋 职位要求对照表

基于 Monoya Full-Stack Engineer JD，本项目展示了以下技能：

| JD 要求 | 本项目实现 | 代码位置 |
|---------|-----------|---------|
| **Frontend: React (TypeScript, Vite, Tailwind)** | ✅ React + Vite + Tailwind CSS | `frontend/` |
| **Backend: Python (FastAPI)** | ✅ FastAPI RESTful API | `backend/app/` |
| **AI/Search: RAG, vector DB (Weaviate)** | ✅ Llama RAG + Weaviate | `backend/app/services/llama_rag_service.py` |
| **Data: Firestore** | ✅ Firestore + Mock 开发模式 | `backend/app/core/firebase.py` |
| **Infra: Docker, Cloud Run, CI/CD** | ✅ Docker Compose + Terraform + GitHub Actions | `docker-compose.yml`, `terraform/`, `.github/workflows/` |
| **Auth: Firebase Auth** | ✅ Firebase Auth + Mock 开发模式 | `frontend/src/config/firebase.js` |

---

## 🎯 第一部分：端到端功能开发

### 1.1 完整功能：AI 日记系统

**职位要求**：
> Build end-to-end features: schema → API → React UI, shipping to prod weekly.

**本项目实现**：完整的日记 CRUD 系统，从数据模型到前端 UI

#### 📊 步骤 1: 数据模型设计 (Schema)

```python
# backend/app/models/diary.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DiaryCreate(BaseModel):
    """创建日记的请求模型"""
    title: str
    content: str

class DiaryUpdate(BaseModel):
    """更新日记的请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None

class DiaryResponse(BaseModel):
    """日记响应模型 - 返回给前端"""
    id: str
    userId: str
    title: str
    content: str
    createdAt: datetime
    updatedAt: datetime
    aiInsight: Optional[str] = None
```

**设计要点**：
- 使用 Pydantic 进行数据验证
- 区分 Create/Update/Response 模型
- 类型安全，自动生成 OpenAPI 文档

---

#### 🔌 步骤 2: FastAPI 后端 API

```python
# backend/app/api/routes/diaries.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter()

@router.get("", response_model=List[DiaryResponse])
async def get_all_diaries(
    current_user: dict = Depends(get_current_user)
):
    """获取用户所有日记"""
    user_id = current_user["uid"]
    return await diary_service.get_all_diaries(user_id)

@router.post("", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(
    diary: DiaryCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建新日记"""
    user_id = current_user["uid"]
    return await diary_service.create_diary(diary, user_id)

@router.put("/{diary_id}", response_model=DiaryResponse)
async def update_diary(
    diary_id: str,
    diary: DiaryUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新日记"""
    user_id = current_user["uid"]
    return await diary_service.update_diary(diary_id, diary, user_id)
```

**技术亮点**：
- RESTful API 设计
- 依赖注入 (Dependency Injection)
- 自动认证和授权
- 类型安全的请求/响应

---

#### ⚛️ 步骤 3: React 前端 UI

```jsx
// frontend/src/pages/Dashboard.jsx
import { useState, useEffect } from 'react'
import { diaryApi } from '../api/diaries'

export default function Dashboard() {
  const [diaries, setDiaries] = useState([])
  const [loading, setLoading] = useState(true)

  // 加载日记列表
  useEffect(() => {
    loadDiaries()
  }, [])

  const loadDiaries = async () => {
    try {
      const data = await diaryApi.getAll()
      setDiaries(data)
    } catch (error) {
      toast.error('Failed to load diaries')
    } finally {
      setLoading(false)
    }
  }

  // 删除日记
  const handleDelete = async (id) => {
    if (!confirm('确定删除？')) return
    
    try {
      await diaryApi.delete(id)
      toast.success('Diary deleted')
      loadDiaries() // 重新加载
    } catch (error) {
      toast.error('Failed to delete')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 日记列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {diaries.map(diary => (
          <DiaryCard 
            key={diary.id} 
            diary={diary}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  )
}
```

**前端技术栈**：
- React Hooks (useState, useEffect)
- Tailwind CSS 响应式设计
- Axios API 客户端
- React Hot Toast 通知
- React Router 路由管理

---

### 1.2 API 客户端封装

```javascript
// frontend/src/api/diaries.js
import apiClient from './client'

export const diaryApi = {
  // 获取所有日记
  getAll: async () => {
    const response = await apiClient.get('/diaries')
    return response.data
  },

  // 获取单个日记
  getById: async (id) => {
    const response = await apiClient.get(`/diaries/${id}`)
    return response.data
  },

  // 创建日记
  create: async (data) => {
    const response = await apiClient.post('/diaries', data)
    return response.data
  },

  // 更新日记
  update: async (id, data) => {
    const response = await apiClient.put(`/diaries/${id}`, data)
    return response.data
  },

  // 删除日记
  delete: async (id) => {
    await apiClient.delete(`/diaries/${id}`)
  },

  // 获取 AI 洞察
  getAiInsight: async (id) => {
    const response = await apiClient.post(`/diaries/${id}/ai-insight`)
    return response.data
  }
}
```

**设计模式**：
- Service Layer 模式
- 集中式 API 管理
- 错误处理统一
- TypeScript-ready 结构

---

## 🤖 第二部分：LLM 集成与 RAG

### 2.1 RAG 系统架构

**职位要求**：
> Integrate LLM-based workflows (chatbot, inquiry classification, content summarisation) using RAG and semantic search.

**本项目实现**：完整的 Llama RAG 系统 + Weaviate 向量数据库

```python
# backend/app/services/llama_rag_service.py
class LlamaRAGService:
    """
    完整的 RAG (Retrieval-Augmented Generation) 实现
    """
    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.model = "llama3.2:1b"
        self.weaviate_client = get_weaviate_client()
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        步骤 1: 生成文本嵌入向量
        使用 Ollama embeddings API
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            return response.json().get("embedding", [])
    
    async def index_diary(self, diary_id, user_id, title, content, created_at):
        """
        步骤 2: 索引到向量数据库
        """
        # 生成嵌入
        full_text = f"{title}\n\n{content}"
        embedding = await self.generate_embedding(full_text)
        
        # 存储到 Weaviate
        self.weaviate_client.data_object.create(
            class_name="DiaryEntry",
            data_object={
                "diaryId": diary_id,
                "userId": user_id,
                "title": title,
                "content": content,
                "createdAt": created_at
            },
            vector=embedding
        )
    
    async def search_similar_diaries(self, user_id, query_text, limit=5):
        """
        步骤 3: 语义搜索
        """
        # 为查询生成嵌入
        query_embedding = await self.generate_embedding(query_text)
        
        # 向量搜索
        result = (
            self.weaviate_client.query
            .get("DiaryEntry", ["diaryId", "title", "content"])
            .with_near_vector({"vector": query_embedding})
            .with_where({
                "path": ["userId"],
                "operator": "Equal",
                "valueString": user_id
            })
            .with_limit(limit)
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
    
    async def generate_recommendation(self, user_id, current_content, current_title):
        """
        步骤 4: RAG 生成推荐
        """
        # 1. 检索相关日记
        query_text = f"{current_title}\n\n{current_content}"
        similar_diaries = await self.search_similar_diaries(
            user_id=user_id,
            query_text=query_text,
            limit=3
        )
        
        # 2. 构建增强上下文
        context = "用户的相关历史日记：\n\n"
        for diary in similar_diaries:
            context += f"标题: {diary['title']}\n"
            context += f"内容: {diary['content'][:300]}...\n\n"
        
        # 3. 生成推荐
        prompt = f"""
{context}

当前正在写的日记：
标题: {current_title}
内容: {current_content}

请提供个性化建议...
"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            return response.json().get("response", "")
```

**技术要点**：
- ✅ **Embeddings**: 文本向量化
- ✅ **Vector DB**: Weaviate 语义搜索
- ✅ **RAG Pipeline**: 检索 → 增强 → 生成
- ✅ **Local LLM**: Ollama (llama3.2:1b)
- ✅ **Production-ready**: 错误处理、日志、超时

---

### 2.2 前端集成

```jsx
// frontend/src/pages/DiaryEditor.jsx
const handleGetLlamaRecommendation = async () => {
  if (!content.trim()) {
    toast.error('请先写一些内容')
    return
  }

  setLoadingRecommendation(true)
  
  try {
    const response = await apiClient.post('/diaries/recommend', {
      title: title,
      content: content
    })
    
    setLlamaRecommendation(response.data.insight)
    toast.success('Llama 推荐生成成功！')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || 'Failed'
    toast.error(errorMsg)
  } finally {
    setLoadingRecommendation(false)
  }
}

return (
  <div>
    {/* 编辑器 */}
    <textarea value={content} onChange={...} />
    
    {/* Llama RAG 按钮 */}
    <button 
      onClick={handleGetLlamaRecommendation}
      disabled={loadingRecommendation}
    >
      🦙 获取 Llama 写作建议
    </button>
    
    {/* 显示推荐 */}
    {llamaRecommendation && (
      <div className="recommendation-card">
        {llamaRecommendation}
      </div>
    )}
  </div>
)
```

---

## ⚡ 第三部分：性能优化

### 3.1 Firestore 查询优化

**职位要求**：
> Tune performance: Firestore query design, Cloud Run cold-start mitigation

**优化案例**：

```python
# ❌ 差的实现 - 读取所有数据然后过滤
async def get_all_diaries_bad(self, user_id: str):
    all_docs = self.db.collection("diaries").stream()
    user_diaries = [doc for doc in all_docs if doc.to_dict().get("userId") == user_id]
    return user_diaries

# ✅ 好的实现 - 在数据库层面过滤
async def get_all_diaries(self, user_id: str):
    query = (
        self.db.collection("diaries")
        .where("userId", "==", user_id)
        .order_by("createdAt", direction="DESCENDING")
    )
    return query.stream()
```

**性能提升**：
- 减少网络传输
- 降低内存使用
- 提高查询速度 10-100x

---

### 3.2 开发模式优化

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # 开发模式 - 跳过 Firebase 连接
    dev_mode: bool = True
    
    # 如果没有配置，使用 mock 值
    openai_api_key: str = "sk-mock-key-for-dev"
    firebase_project_id: str = "mock-project"
```

```python
# backend/app/core/firebase.py
def initialize_firebase():
    """智能初始化 - 开发模式使用 Mock"""
    if settings.dev_mode:
        print("🔧 DEV MODE - Using mock Firestore")
        return MockFirestore()
    
    # 生产模式使用真实 Firebase
    return firestore.client()
```

**优势**：
- 无需 Firebase 配置即可开发
- 快速启动，无外部依赖
- 生产环境无缝切换

---

### 3.3 前端优化

```javascript
// frontend/src/config/firebase.js
const isDevMode = !import.meta.env.VITE_FIREBASE_API_KEY

if (isDevMode) {
  // 开发模式 - 使用 Mock Auth
  auth = new MockAuth()
} else {
  // 生产模式 - 真实 Firebase
  const app = initializeApp(firebaseConfig)
  auth = getAuth(app)
}
```

---

## 🐳 第四部分：Docker 与 CI/CD

### 4.1 Docker Compose 多服务编排

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端服务
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
  
  # 后端服务
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEV_MODE=true
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - weaviate
      - ollama
  
  # Weaviate 向量数据库
  weaviate:
    image: semitechnologies/weaviate:1.23.0
    ports:
      - "8080:8080"
    volumes:
      - weaviate_data:/var/lib/weaviate
  
  # Ollama 本地 LLM
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

**架构亮点**：
- 4 个微服务协同工作
- 服务间网络通信
- 数据持久化
- 开发环境热重载

---

### 4.2 GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Build and Push Docker Images
        run: |
          docker build -t gcr.io/$PROJECT_ID/frontend:$GITHUB_SHA ./frontend
          docker push gcr.io/$PROJECT_ID/frontend:$GITHUB_SHA
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy frontend \
            --image gcr.io/$PROJECT_ID/frontend:$GITHUB_SHA \
            --region us-central1 \
            --allow-unauthenticated
```

---

### 4.3 Terraform 基础设施即代码

```hcl
# terraform/main.tf
resource "google_cloud_run_service" "frontend" {
  name     = "ai-diary-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/frontend:latest"
        
        env {
          name  = "VITE_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service" "backend" {
  name     = "ai-diary-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/backend:latest"
        
        resources {
          limits = {
            cpu    = "2"
            memory = "1Gi"
          }
        }
      }
    }
  }
}

resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}
```

**IaC 优势**：
- 版本控制基础设施
- 可重复部署
- 多环境管理
- 自动化配置

---

## 🔐 第五部分：认证与授权

### 5.1 Firebase Auth 集成

```javascript
// frontend/src/config/firebase.js
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth'

export const auth = getAuth(app)

// 登录
export const login = async (email, password) => {
  return await signInWithEmailAndPassword(auth, email, password)
}

// 注册
export const register = async (email, password) => {
  return await createUserWithEmailAndPassword(auth, email, password)
}
```

```python
# backend/app/api/dependencies.py
from firebase_admin import auth as firebase_auth

async def get_current_user(authorization: str = Header(None)):
    """验证 Firebase token 并返回用户信息"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    # 开发模式 - 返回 mock 用户
    if settings.dev_mode:
        return {"uid": "dev-user-123", "email": "dev@example.com"}
    
    # 生产模式 - 验证 token
    token = authorization.replace("Bearer ", "")
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 📊 第六部分：可观测性

### 6.1 结构化日志

```python
# backend/app/services/llama_rag_service.py
async def generate_recommendation(self, user_id, current_content, current_title):
    print(f"[Llama RAG] ====== RAG 流程开始 ======")
    print(f"[Llama RAG] 用户 ID: {user_id}")
    print(f"[Llama RAG] 当前内容长度: {len(current_content)} 字符")
    
    # 步骤 1
    print(f"[Llama RAG] 步骤 1/3: 检索相关日记...")
    similar_diaries = await self.search_similar_diaries(user_id, query_text, limit=3)
    print(f"[Llama RAG] 找到 {len(similar_diaries)} 篇相关日记")
    
    # 步骤 2
    print(f"[Llama RAG] 步骤 2/3: 构建增强上下文...")
    
    # 步骤 3
    print(f"[Llama RAG] 步骤 3/3: 使用 Llama 生成推荐...")
    
    print(f"[Llama RAG] ✅ 成功生成推荐: {len(recommendation)} 字符")
    print(f"[Llama RAG] ====== RAG 流程完成 ======")
```

**查看日志**：
```bash
docker logs jd_project-backend-1 -f | grep "Llama RAG"
```

---

## 🎓 学习路径与资源

### 快速上手（1-2 周）

1. **克隆并运行项目**
   ```bash
   git clone [your-repo]
   cd JD_Project
   docker compose up
   ```

2. **理解项目结构**
   - 阅读 `README_CN.md`
   - 查看 `ARCHITECTURE_CN.md`
   - 运行 `RAG_FLOW_EXPLAINED.md` 中的示例

3. **修改功能**
   - 添加新的 API 端点
   - 创建新的 React 组件
   - 调整 RAG 提示词

### 深入学习（1-2 月）

1. **FastAPI 精通**
   - [官方文档](https://fastapi.tiangolo.com/)
   - 学习依赖注入、中间件、异步编程

2. **React 进阶**
   - Custom Hooks
   - Context API
   - 性能优化（useMemo, useCallback）

3. **RAG 系统**
   - LangChain 教程
   - Weaviate 文档
   - OpenAI Embeddings

4. **DevOps**
   - Docker 多阶段构建
   - Terraform modules
   - GitHub Actions 进阶

---

## 💼 如何展示此项目

### 简历描述

```
AI 日记应用 - Full-Stack + RAG 系统
技术栈: React, FastAPI, Weaviate, Docker, GCP

• 构建端到端功能：从 Pydantic 数据模型到 React UI，完整的 CRUD 系统
• 集成 LLM RAG: 使用 Ollama (Llama 3.2 1B) + Weaviate 实现语义搜索和个性化推荐
• 性能优化: Firestore 查询优化，开发/生产模式切换，降低冷启动时间
• DevOps: Docker Compose 多服务编排，Terraform IaC，GitHub Actions CI/CD
• 认证授权: Firebase Auth 集成，JWT token 验证，RBAC 权限控制
```

### 面试讨论要点

1. **架构决策**
   - 为什么选择 FastAPI over Django/Flask?
   - Weaviate vs Pinecone vs Milvus?
   - Firestore vs PostgreSQL?

2. **技术挑战**
   - 如何处理 LLM 超时？
   - Firestore 查询限制如何解决？
   - Docker 网络如何配置？

3. **优化案例**
   - 开发模式 Mock 减少启动时间
   - 向量搜索提升推荐准确度
   - API 客户端封装提高可维护性

---

## ✅ 总结

本项目完整展示了 Monoya Full-Stack Engineer 所需的所有技能：

✅ **Frontend**: React + Vite + Tailwind  
✅ **Backend**: FastAPI + async Python  
✅ **AI/LLM**: RAG pipeline + Weaviate + Ollama  
✅ **Data**: Firestore + vector DB  
✅ **Infra**: Docker + Terraform + GitHub Actions  
✅ **Auth**: Firebase Auth + JWT  
✅ **Observability**: 结构化日志 + 错误处理  

**下一步**：
1. 部署到 GCP Cloud Run (参考 `DEPLOYMENT_CN.md`)
2. 添加更多 AI 功能（分类、摘要）
3. 实现移动端 API
4. 性能监控和优化

---

**相关文档**：
- [Architecture](./ARCHITECTURE_CN.md)
- [RAG Flow](./RAG_FLOW_EXPLAINED.md)
- [Deployment](./DEPLOYMENT_CN.md)

