# 🦙 Llama RAG 工作流程详解

## 📊 完整 RAG 架构

```
用户写日记
    ↓
[创建/更新] → Firestore (存储) + Weaviate (向量索引)
    ↓
用户点击"获取建议"
    ↓
[RAG 流程开始]
    ↓
┌─────────────────────────────────────────────┐
│ 步骤 1: 检索 (Retrieval)                    │
│ - 当前日记内容 → Ollama Embedding API      │
│ - 生成 768 维向量                           │
│ - Weaviate 语义搜索最相似的 3 篇历史日记   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 步骤 2: 增强 (Augmented)                    │
│ - 构建提示词                                │
│ - 包含检索到的相关历史日记作为上下文       │
│ - 当前正在写的内容                          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 步骤 3: 生成 (Generation)                   │
│ - 增强的提示词 → Llama 3.2 1B 模型         │
│ - 生成个性化推荐                            │
│ - 返回给用户                                │
└─────────────────────────────────────────────┘
```

---

## 🔍 逐行代码解释

### 1️⃣ 生成嵌入向量 (`generate_embedding`)

```python
async def generate_embedding(self, text: str) -> List[float]:
    """
    将文本转换为向量表示

    输入: "今天天气很好，心情也不错"
    输出: [0.123, -0.456, 0.789, ..., 0.321]  # 768 维向量

    为什么需要？
    - 计算机无法直接理解文本的"意思"
    - 向量可以表示文本的语义
    - 相似的文本会有相似的向量
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{self.ollama_url}/api/embeddings",  # 调用 Ollama 的 embedding 端点
            json={
                "model": self.model,  # llama3.2:1b
                "prompt": text
            }
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("embedding", [])  # 返回向量
```

**实际例子**：

```python
# 输入
text = "今天天气很好"

# 输出（简化版，实际是 768 维）
embedding = [0.12, -0.45, 0.78, 0.23, -0.67, ...]

# 语义相似的文本会有相似的向量
"今天天气很好" → [0.12, -0.45, 0.78, ...]
"今天阳光明媚" → [0.15, -0.42, 0.81, ...]  # 很接近！
"我讨厌下雨"   → [-0.23, 0.67, -0.45, ...] # 很不同
```

---

### 2️⃣ 索引日记 (`index_diary`)

```python
async def index_diary(
    self,
    diary_id: str,      # "diary_123"
    user_id: str,       # "user_456"
    title: str,         # "美好的一天"
    content: str,       # "今天天气很好..."
    created_at: str     # "2026-01-17T10:00:00"
):
    """
    将日记存储到 Weaviate 向量数据库

    流程：
    1. 合并标题和内容
    2. 生成嵌入向量
    3. 存储到 Weaviate
    """
    # 步骤 1: 合并文本
    full_text = f"{title}\n\n{content}"
    # 结果: "美好的一天\n\n今天天气很好..."

    # 步骤 2: 生成向量
    embedding = await self.generate_embedding(full_text)
    # 结果: [0.12, -0.45, 0.78, ..., 0.23]

    # 步骤 3: 存储到 Weaviate
    self.weaviate_client.data_object.create(
        class_name="DiaryEntry",
        data_object={
            "diaryId": diary_id,
            "userId": user_id,
            "title": title,
            "content": content,
            "createdAt": created_at
        },
        vector=embedding  # 关键！存储向量用于后续搜索
    )
```

**Weaviate 中的数据结构**：

```json
{
  "id": "weaviate_uuid_123",
  "class": "DiaryEntry",
  "properties": {
    "diaryId": "diary_123",
    "userId": "user_456",
    "title": "美好的一天",
    "content": "今天天气很好...",
    "createdAt": "2026-01-17T10:00:00"
  },
  "vector": [0.12, -0.45, 0.78, ..., 0.23]  // 768 维
}
```

---

### 3️⃣ 语义搜索 (`search_similar_diaries`)

```python
async def search_similar_diaries(
    self,
    user_id: str,       # "user_456"
    query_text: str,    # "今天也是晴天"
    limit: int = 5      # 返回最相似的 5 篇
) -> List[dict]:
    """
    在 Weaviate 中搜索语义最相似的日记

    这是 RAG 的核心 - 检索相关上下文！
    """
    # 步骤 1: 为查询生成向量
    query_embedding = await self.generate_embedding(query_text)
    # 结果: [0.15, -0.42, 0.81, ..., 0.25]

    # 步骤 2: 向量搜索
    result = (
        self.weaviate_client.query
        .get("DiaryEntry", ["diaryId", "title", "content", "createdAt"])
        .with_near_vector({
            "vector": query_embedding  # 使用向量搜索
        })
        .with_where({
            "path": ["userId"],
            "operator": "Equal",
            "valueString": user_id  # 只搜索该用户的日记
        })
        .with_limit(limit)  # 只返回前 5 个
        .do()
    )

    return result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
```

**向量搜索原理**：

```python
# Weaviate 会计算余弦相似度
查询: "今天也是晴天"     → [0.15, -0.42, 0.81, ...]

数据库中的日记：
日记1: "今天天气很好"   → [0.12, -0.45, 0.78, ...]  相似度: 0.95 ⭐⭐⭐
日记2: "我讨厌下雨"     → [-0.23, 0.67, -0.45, ...] 相似度: 0.12
日记3: "阳光明媚的早晨" → [0.18, -0.40, 0.85, ...]  相似度: 0.92 ⭐⭐

# 返回相似度最高的 3 篇
返回: [日记1, 日记3]
```

---

### 4️⃣ 生成推荐 (`generate_recommendation`)

```python
async def generate_recommendation(
    self,
    user_id: str,           # "user_456"
    current_content: str,   # "今天也是晴天，心情很好"
    current_title: str = "" # "又是美好的一天"
) -> str:
    """
    完整的 RAG 流程
    """
    # ===== 步骤 1: 检索 (Retrieval) =====
    query_text = f"{current_title}\n\n{current_content}"
    similar_diaries = await self.search_similar_diaries(
        user_id=user_id,
        query_text=query_text,
        limit=3  # 只取最相关的 3 篇
    )

    # 结果示例：
    # similar_diaries = [
    #     {"title": "美好的一天", "content": "今天天气很好..."},
    #     {"title": "阳光明媚", "content": "早上起来看到阳光..."},
    #     {"title": "心情不错", "content": "最近天气都很好..."}
    # ]

    # ===== 步骤 2: 增强 (Augmented) =====
    context = "用户的相关历史日记：\n\n"
    for i, diary in enumerate(similar_diaries, 1):
        context += f"【相关日记 {i}】\n"
        context += f"标题: {diary['title']}\n"
        context += f"内容: {diary['content'][:300]}...\n\n"

    # 构建增强的提示词
    prompt = f"""你是一个智能日记助手。

{context}  # ← 这里包含了检索到的相关历史日记！

当前正在写的日记：
标题: {current_title}
内容: {current_content}

请提供建议..."""

    # ===== 步骤 3: 生成 (Generation) =====
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,  # 包含上下文的提示词
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200
                }
            }
        )

        result = response.json()
        return result.get("response", "")
```

**实际提示词示例**：

```
你是一个智能日记助手。

用户的相关历史日记：

【相关日记 1】
标题: 美好的一天
内容: 今天天气很好，早上起来看到阳光透过窗户照进来，心情特别好...

【相关日记 2】
标题: 阳光明媚
内容: 早上起来看到阳光，想起了上次也是这样的好天气...

当前正在写的日记：
标题: 又是美好的一天
内容: 今天也是晴天，心情很好

请提供：
1. 对当前内容的简短评论
2. 与历史日记的联系或主题观察
3. 1-2条写作建议或思考方向
```

**Llama 的回复**：

```
看到你又迎来了一个阳光明媚的日子！从你的历史日记来看，好天气总是能让你心情愉悦。
建议：可以记录一下这次好天气带来的具体感受，或者对比一下与之前几次晴天的不同之处。
```

---

## 🎯 为什么这是 RAG？

### 传统 LLM（没有 RAG）

```
用户: "今天也是晴天，心情很好"
    ↓
Llama: "很高兴听到你心情好！保持积极的心态很重要。"
    ↑
通用回复，不了解用户历史
```

### RAG 系统（有 Weaviate）

```
用户: "今天也是晴天，心情很好"
    ↓
Weaviate 检索: 找到 3 篇相似的历史日记
    ↓
Llama + 历史上下文: "看到你又迎来了阳光明媚的日子！
                     从你的历史日记来看，好天气总是能让你心情愉悦。
                     上次也是晴天时，你提到了..."
    ↑
个性化回复，基于用户历史！
```

---

## 🔄 完整数据流

### 写日记时（索引）

```
1. 用户创建日记 "今天天气很好"
   ↓
2. DiaryService.create_diary()
   ↓
3. 存储到 Firestore (持久化)
   ↓
4. LlamaRAGService.index_diary()
   ↓
5. 生成嵌入向量 [0.12, -0.45, ...]
   ↓
6. 存储到 Weaviate (向量索引)
```

### 获取建议时（查询）

```
1. 用户点击"获取 Llama 建议"
   ↓
2. 前端发送当前内容到后端
   ↓
3. LlamaRAGService.generate_recommendation()
   ↓
4. 生成查询向量 [0.15, -0.42, ...]
   ↓
5. Weaviate 向量搜索 → 找到 3 篇相似日记
   ↓
6. 构建增强提示词（包含历史日记）
   ↓
7. 调用 Llama 生成推荐
   ↓
8. 返回个性化建议给用户
```

---

## 📊 技术对比

| 特性     | 简单拼接              | RAG (Weaviate)   |
| -------- | --------------------- | ---------------- |
| 检索方式 | 时间顺序（最近 N 篇） | 语义相似度       |
| 相关性   | 低（可能不相关）      | 高（真正相关）   |
| 效率     | 低（读取所有）        | 高（向量搜索快） |
| 质量     | 通用                  | 个性化           |

**示例**：

```
用户写: "今天考试没考好，有点沮丧"

简单拼接: 返回最近 3 篇日记
- "昨天吃了火锅" ❌ 不相关
- "上周去旅游" ❌ 不相关
- "前天天气很好" ❌ 不相关

RAG 搜索: 返回语义相似的 3 篇
- "上次考试也没考好" ✅ 相关！
- "感觉学习压力很大" ✅ 相关！
- "对自己有点失望" ✅ 相关！
```

---

## 🎨 关键技术点

### 1. 向量嵌入 (Embeddings)

- 将文本转换为数字向量
- 语义相似的文本 → 相似的向量
- 使用 Ollama 的 embedding API

### 2. 向量数据库 (Weaviate)

- 专门存储和搜索向量
- 支持高效的相似度搜索
- 比传统数据库快 1000 倍

### 3. 语义搜索

- 不是关键词匹配
- 理解文本的"意思"
- "天气好" 能匹配到 "阳光明媚"

### 4. 上下文增强

- 将检索到的相关内容添加到提示词
- LLM 基于这些上下文生成回复
- 实现个性化和准确性

---

## ✨ 总结

**RAG = Retrieval (检索) + Augmented (增强) + Generation (生成)**

1. **检索**: Weaviate 向量搜索找到相关历史日记
2. **增强**: 将相关日记添加到提示词作为上下文
3. **生成**: Llama 基于增强的上下文生成个性化推荐

这就是为什么叫 **Retrieval-Augmented Generation**！🎉
