# 🔍 Weaviate 向量数据库完全教程

## 📚 目录

1. [Weaviate 基础](#weaviate-基础)
2. [项目集成](#项目集成)
3. [Schema 设计](#schema-设计)
4. [向量嵌入](#向量嵌入)
5. [数据索引](#数据索引)
6. [语义搜索](#语义搜索)
7. [高级查询](#高级查询)
8. [性能优化](#性能优化)
9. [生产部署](#生产部署)
10. [故障排查](#故障排查)

---

## 🎯 Weaviate 基础

### 什么是 Weaviate？

**Weaviate** 是一个开源的向量数据库，专门为 AI/ML 应用设计。

```
传统数据库 vs 向量数据库

传统数据库 (PostgreSQL):
┌─────────────────────────────┐
│ id │ title    │ content      │
├────┼──────────┼──────────────┤
│ 1  │ 晴天     │ 今天天气好   │
│ 2  │ 下雨     │ 今天下雨了   │
└────┴──────────┴──────────────┘
查询: WHERE title = '晴天'  ← 精确匹配

向量数据库 (Weaviate):
┌────────────────────────────────────────┐
│ id │ title │ content │ vector         │
├────┼───────┼─────────┼────────────────┤
│ 1  │ 晴天  │ ...     │ [0.12,-0.45..] │
│ 2  │ 下雨  │ ...     │ [-0.23,0.67..] │
└────┴───────┴─────────┴────────────────┘
查询: 语义搜索 '阳光明媚'
     ↓
找到最相似的向量 → 返回 id=1 (晴天)
```

### 核心概念

#### 1. 向量 (Vector)

```python
# 文本 → 向量
text = "今天天气很好"
vector = [0.123, -0.456, 0.789, ..., 0.321]  # 768 维

# 相似文本 → 相似向量
"今天天气很好" → [0.12, -0.45, 0.78, ...]
"今天阳光明媚" → [0.15, -0.42, 0.81, ...]  # 很接近！
```

#### 2. Schema (数据结构)

```json
{
  "class": "DiaryEntry",
  "properties": [
    {"name": "title", "dataType": ["text"]},
    {"name": "content", "dataType": ["text"]},
    {"name": "userId", "dataType": ["string"]}
  ]
}
```

#### 3. HNSW 索引

**HNSW** = Hierarchical Navigable Small World

```
传统数据库查询: O(N) - 遍历所有记录
Weaviate HNSW:    O(log N) - 层级导航

示例 (1000 条记录):
- 传统: 1000 次比较
- HNSW: ~10 次比较 (100x 更快！)
```

---

## 🔧 项目集成

### 1. Docker 部署

**本项目的 Weaviate 配置**：

```yaml
# docker-compose.yml
services:
  weaviate:
    image: semitechnologies/weaviate:1.23.0
    ports:
      - "8080:8080"
    environment:
      # 查询限制
      - QUERY_DEFAULTS_LIMIT=25
      
      # 允许匿名访问（开发环境）
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      
      # 数据持久化路径
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      
      # 不使用内置向量化器（我们自己生成向量）
      - DEFAULT_VECTORIZER_MODULE=none
      
      # 启用 OpenAI 模块（可选）
      - ENABLE_MODULES=text2vec-openai
      
      # 集群主机名
      - CLUSTER_HOSTNAME=node1
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
```

**启动 Weaviate**：

```bash
# 启动
docker compose up -d weaviate

# 检查状态
docker ps | grep weaviate

# 查看日志
docker logs jd_project-weaviate-1

# 验证运行
curl http://localhost:8080/v1/meta
```

**预期输出**：

```json
{
  "hostname": "http://[::]:8080",
  "modules": {
    "text2vec-openai": {
      "documentationHref": "https://...",
      "name": "text2vec-openai"
    }
  },
  "version": "1.23.0"
}
```

---

### 2. Python 客户端

**安装**：

```bash
pip install weaviate-client==3.26.2
```

**初始化客户端**：

```python
# backend/app/core/weaviate_client.py
import weaviate
from app.core.config import settings

def get_weaviate_client():
    """
    初始化 Weaviate 客户端
    
    配置:
    - URL: http://weaviate:8080 (Docker 内部)
    - Timeout: 5s 连接, 15s 读取
    - Auth: 匿名访问 (开发环境)
    """
    client = weaviate.Client(
        url=settings.weaviate_url,
        timeout_config=(5, 15)
    )
    
    # 测试连接
    try:
        meta = client.get_meta()
        print(f"[Weaviate] ✅ 连接成功，版本: {meta['version']}")
    except Exception as e:
        print(f"[Weaviate] ❌ 连接失败: {e}")
        raise
    
    return client

# 使用
weaviate_client = get_weaviate_client()
```

---

## 📋 Schema 设计

### 1. 创建 Schema

**本项目的 DiaryEntry Schema**：

```python
# backend/app/core/weaviate_client.py (续)

def create_diary_schema(client):
    """
    创建日记 Schema
    
    Schema 设计原则:
    1. class 名称用 PascalCase (DiaryEntry)
    2. property 名称用 camelCase (userId)
    3. 文本字段用 text 类型（可搜索）
    4. ID 字段用 string 类型
    5. vectorizer 设为 none（自定义向量）
    """
    
    schema = {
        "class": "DiaryEntry",
        
        # 不使用内置向量化器
        "vectorizer": "none",
        
        # 向量索引配置
        "vectorIndexConfig": {
            "distance": "cosine",  # 余弦距离
            "ef": 100,             # 构建时的动态列表大小
            "efConstruction": 128, # 插入时的动态列表
            "maxConnections": 64   # 每个节点的最大连接数
        },
        
        # 数据字段
        "properties": [
            {
                "name": "diaryId",
                "dataType": ["string"],
                "description": "日记的唯一标识符",
                "indexInverted": True  # 允许过滤
            },
            {
                "name": "userId",
                "dataType": ["string"],
                "description": "用户 ID",
                "indexInverted": True,      # 允许过滤
                "indexSearchable": True     # 允许搜索
            },
            {
                "name": "title",
                "dataType": ["text"],
                "description": "日记标题",
                "indexInverted": True,
                "tokenization": "word"      # 分词方式
            },
            {
                "name": "content",
                "dataType": ["text"],
                "description": "日记内容",
                "indexInverted": True,
                "tokenization": "word"
            },
            {
                "name": "createdAt",
                "dataType": ["string"],
                "description": "创建时间 (ISO 8601)",
                "indexInverted": False      # 时间戳不需要倒排索引
            }
        ]
    }
    
    # 检查 Schema 是否已存在
    try:
        existing_schema = client.schema.get("DiaryEntry")
        print("[Weaviate] Schema 已存在")
    except:
        # 创建新 Schema
        client.schema.create_class(schema)
        print("[Weaviate] ✅ Schema 创建成功")
```

**数据类型对照表**：

| Weaviate 类型 | 说明 | 示例 | 用途 |
|--------------|------|------|------|
| `string` | 字符串 | "abc123" | ID, 标签 |
| `text` | 文本 | "今天天气很好" | 标题, 内容 |
| `int` | 整数 | 42 | 计数, 年龄 |
| `number` | 浮点数 | 3.14 | 评分, 价格 |
| `boolean` | 布尔 | true | 标志位 |
| `date` | 日期时间 | "2026-01-17T10:00:00Z" | 时间戳 |

---

### 2. 查看 Schema

```python
# 获取所有 class
all_classes = client.schema.get()
print(json.dumps(all_classes, indent=2))

# 获取特定 class
diary_schema = client.schema.get("DiaryEntry")
print(f"Class: {diary_schema['class']}")
print(f"Properties: {len(diary_schema['properties'])}")

for prop in diary_schema['properties']:
    print(f"  - {prop['name']} ({prop['dataType'][0]})")
```

**输出**：

```
Class: DiaryEntry
Properties: 5
  - diaryId (string)
  - userId (string)
  - title (text)
  - content (text)
  - createdAt (string)
```

---

### 3. 更新 Schema

```python
# 添加新字段
client.schema.property.create(
    "DiaryEntry",
    {
        "name": "tags",
        "dataType": ["string[]"],
        "description": "日记标签"
    }
)

# 删除 class (谨慎！)
client.schema.delete_class("DiaryEntry")
```

---

## 🧮 向量嵌入

### 1. 生成向量

**使用 Ollama Embeddings**：

```python
# backend/app/services/llama_rag_service.py
import httpx
from typing import List

async def generate_embedding(text: str) -> List[float]:
    """
    使用 Ollama 生成文本嵌入
    
    输入: "今天天气很好"
    输出: [0.123, -0.456, ..., 0.321] (768 维)
    
    时间: ~2-3 秒
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://ollama:11434/api/embeddings",
            json={
                "model": "llama3.2:1b",
                "prompt": text
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            
            print(f"[Embeddings] 生成 {len(embedding)} 维向量")
            return embedding
        else:
            print(f"[Embeddings] ❌ 失败: {response.status_code}")
            return []

# 使用示例
text = "今天天气很好，心情也不错"
vector = await generate_embedding(text)

print(f"向量维度: {len(vector)}")
print(f"前 5 维: {vector[:5]}")
```

**输出**：

```
[Embeddings] 生成 768 维向量
向量维度: 768
前 5 维: [0.12304688, -0.45117188, 0.78320312, 0.23242188, -0.67187500]
```

---

### 2. 向量相似度

```python
import numpy as np

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算余弦相似度
    
    范围: -1 到 1
    - 1.0: 完全相同
    - 0.0: 正交（无关）
    - -1.0: 完全相反
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # 余弦相似度公式
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    return dot_product / (norm1 * norm2)

# 示例
text1 = "今天天气很好"
text2 = "今天阳光明媚"
text3 = "我讨厌下雨天"

vec1 = await generate_embedding(text1)
vec2 = await generate_embedding(text2)
vec3 = await generate_embedding(text3)

print(f"相似度 (text1, text2): {cosine_similarity(vec1, vec2):.4f}")  # 0.92
print(f"相似度 (text1, text3): {cosine_similarity(vec1, vec3):.4f}")  # 0.15
```

---

## 📥 数据索引

### 1. 添加单个对象

```python
# backend/app/services/llama_rag_service.py

async def index_diary(
    diary_id: str,
    user_id: str,
    title: str,
    content: str,
    created_at: str
):
    """
    索引单个日记到 Weaviate
    
    步骤:
    1. 合并标题和内容
    2. 生成嵌入向量
    3. 存储到 Weaviate
    """
    print(f"[Index] 索引日记 {diary_id}")
    
    # 步骤 1: 合并文本
    full_text = f"{title}\n\n{content}"
    
    # 步骤 2: 生成向量
    embedding = await generate_embedding(full_text)
    
    if not embedding:
        print(f"[Index] ⚠️ 跳过 - 无法生成向量")
        return
    
    # 步骤 3: 存储到 Weaviate
    try:
        uuid = weaviate_client.data_object.create(
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
        
        print(f"[Index] ✅ 成功，Weaviate UUID: {uuid}")
        return uuid
        
    except Exception as e:
        print(f"[Index] ❌ 失败: {e}")
        raise
```

**实际使用**：

```python
# 创建日记时自动索引
await index_diary(
    diary_id="diary_123",
    user_id="user_456",
    title="美好的一天",
    content="今天天气很好，早上起来看到阳光透过窗户照进来...",
    created_at="2026-01-17T10:00:00Z"
)
```

---

### 2. 批量索引

```python
async def batch_index_diaries(diaries: List[dict]):
    """
    批量索引多个日记
    
    优势:
    - 减少网络往返
    - 提高吞吐量
    - 自动重试失败的对象
    """
    print(f"[Batch] 批量索引 {len(diaries)} 个日记")
    
    # 配置批处理
    weaviate_client.batch.configure(
        batch_size=100,           # 每批 100 个对象
        dynamic=True,             # 动态调整批大小
        timeout_retries=3,        # 失败重试次数
        connection_error_retries=3
    )
    
    with weaviate_client.batch as batch:
        for diary in diaries:
            # 生成向量
            full_text = f"{diary['title']}\n\n{diary['content']}"
            embedding = await generate_embedding(full_text)
            
            if not embedding:
                continue
            
            # 添加到批处理
            batch.add_data_object(
                class_name="DiaryEntry",
                data_object={
                    "diaryId": diary['id'],
                    "userId": diary['user_id'],
                    "title": diary['title'],
                    "content": diary['content'],
                    "createdAt": diary['created_at']
                },
                vector=embedding
            )
    
    print(f"[Batch] ✅ 批量索引完成")
```

---

### 3. 更新对象

```python
async def update_diary(diary_id: str, new_title: str, new_content: str):
    """
    更新已索引的日记
    
    步骤:
    1. 查找 Weaviate UUID
    2. 生成新向量
    3. 更新对象
    """
    # 步骤 1: 查找 UUID
    result = (
        weaviate_client.query
        .get("DiaryEntry", ["diaryId"])
        .with_where({
            "path": ["diaryId"],
            "operator": "Equal",
            "valueString": diary_id
        })
        .with_additional(["id"])
        .do()
    )
    
    entries = result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
    
    if not entries:
        print(f"[Update] ⚠️ 未找到 diary_id={diary_id}")
        return
    
    weaviate_uuid = entries[0]["_additional"]["id"]
    
    # 步骤 2: 生成新向量
    full_text = f"{new_title}\n\n{new_content}"
    new_embedding = await generate_embedding(full_text)
    
    # 步骤 3: 更新
    weaviate_client.data_object.update(
        uuid=weaviate_uuid,
        class_name="DiaryEntry",
        data_object={
            "title": new_title,
            "content": new_content
        },
        vector=new_embedding
    )
    
    print(f"[Update] ✅ 更新成功")
```

---

### 4. 删除对象

```python
async def delete_diary(diary_id: str):
    """
    删除日记
    """
    # 查找 UUID
    result = (
        weaviate_client.query
        .get("DiaryEntry", ["diaryId"])
        .with_where({
            "path": ["diaryId"],
            "operator": "Equal",
            "valueString": diary_id
        })
        .with_additional(["id"])
        .do()
    )
    
    entries = result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
    
    if entries:
        weaviate_uuid = entries[0]["_additional"]["id"]
        
        # 删除
        weaviate_client.data_object.delete(
            uuid=weaviate_uuid,
            class_name="DiaryEntry"
        )
        
        print(f"[Delete] ✅ 删除成功")
```

---

## 🔎 语义搜索

### 1. 基础向量搜索

```python
async def search_similar_diaries(
    user_id: str,
    query_text: str,
    limit: int = 5
) -> List[dict]:
    """
    语义搜索相似日记
    
    步骤:
    1. 为查询生成向量
    2. 在 Weaviate 中搜索最近邻
    3. 过滤用户 ID
    4. 返回结果
    """
    print(f"[Search] 查询: '{query_text[:50]}...'")
    
    # 步骤 1: 查询向量
    query_embedding = await generate_embedding(query_text)
    
    if not query_embedding:
        return []
    
    # 步骤 2 & 3: 向量搜索 + 过滤
    result = (
        weaviate_client.query
        .get(
            "DiaryEntry",
            ["diaryId", "title", "content", "createdAt"]
        )
        .with_near_vector({
            "vector": query_embedding,
            "certainty": 0.7  # 最小相似度阈值 (0-1)
        })
        .with_where({
            "path": ["userId"],
            "operator": "Equal",
            "valueString": user_id
        })
        .with_limit(limit)
        .with_additional(["certainty", "distance"])  # 返回相似度分数
        .do()
    )
    
    entries = result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
    
    # 打印结果
    print(f"[Search] ✅ 找到 {len(entries)} 个结果")
    for i, entry in enumerate(entries, 1):
        certainty = entry.get("_additional", {}).get("certainty", 0)
        print(f"  {i}. {entry['title']} - 相似度: {certainty:.4f}")
    
    return entries

# 使用示例
results = await search_similar_diaries(
    user_id="user_456",
    query_text="今天也是晴天，心情很好",
    limit=3
)

for result in results:
    print(f"\n标题: {result['title']}")
    print(f"内容: {result['content'][:100]}...")
    print(f"相似度: {result['_additional']['certainty']:.4f}")
```

**输出示例**：

```
[Search] 查询: '今天也是晴天，心情很好'
[Search] ✅ 找到 3 个结果
  1. 美好的一天 - 相似度: 0.9234
  2. 阳光明媚的早晨 - 相似度: 0.8901
  3. 心情不错 - 相似度: 0.8567

标题: 美好的一天
内容: 今天天气很好，早上起来看到阳光透过窗户照进来，心情特别好...
相似度: 0.9234
```

---

### 2. 混合搜索 (Hybrid Search)

```python
def hybrid_search(
    user_id: str,
    query_text: str,
    limit: int = 5,
    alpha: float = 0.5  # 0=纯BM25, 1=纯向量搜索
) -> List[dict]:
    """
    混合搜索：结合关键词和语义
    
    alpha 调优:
    - 0.0: 100% BM25 (关键词)
    - 0.5: 50% BM25 + 50% 向量
    - 1.0: 100% 向量 (语义)
    """
    result = (
        weaviate_client.query
        .get("DiaryEntry", ["diaryId", "title", "content"])
        .with_hybrid(
            query=query_text,
            alpha=alpha
        )
        .with_where({
            "path": ["userId"],
            "operator": "Equal",
            "valueString": user_id
        })
        .with_limit(limit)
        .with_additional(["score"])
        .do()
    )
    
    entries = result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
    return entries

# 比较不同 alpha 值
for alpha in [0.0, 0.5, 1.0]:
    print(f"\n=== Alpha = {alpha} ===")
    results = hybrid_search(
        user_id="user_456",
        query_text="天气 阳光",
        alpha=alpha
    )
    for r in results:
        print(f"  - {r['title']}")
```

---

## 🚀 高级查询

### 1. 过滤查询

```python
# 时间范围过滤
result = (
    weaviate_client.query
    .get("DiaryEntry", ["title", "createdAt"])
    .with_where({
        "operator": "And",
        "operands": [
            {
                "path": ["userId"],
                "operator": "Equal",
                "valueString": "user_456"
            },
            {
                "path": ["createdAt"],
                "operator": "GreaterThan",
                "valueString": "2026-01-01T00:00:00Z"
            }
        ]
    })
    .do()
)

# 多条件过滤
result = (
    weaviate_client.query
    .get("DiaryEntry", ["title"])
    .with_where({
        "operator": "Or",
        "operands": [
            {
                "path": ["title"],
                "operator": "Like",
                "valueText": "*天气*"
            },
            {
                "path": ["content"],
                "operator": "Like",
                "valueText": "*阳光*"
            }
        ]
    })
    .do()
)
```

**过滤运算符**：

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `Equal` | 等于 | `"value": "user_456"` |
| `NotEqual` | 不等于 | `"value": "spam"` |
| `GreaterThan` | 大于 | `"value": 100` |
| `LessThan` | 小于 | `"value": 50` |
| `Like` | 模糊匹配 | `"valueText": "*weather*"` |
| `ContainsAny` | 包含任意 | `"valueText": ["sunny", "rainy"]` |
| `ContainsAll` | 包含全部 | `"valueText": ["good", "day"]` |

---

### 2. 聚合查询

```python
# 统计每个用户的日记数量
result = (
    weaviate_client.query
    .aggregate("DiaryEntry")
    .with_group_by_filter(["userId"])
    .with_fields("meta { count }")
    .do()
)

for group in result["data"]["Aggregate"]["DiaryEntry"]:
    user_id = group["groupedBy"]["value"]
    count = group["meta"]["count"]
    print(f"用户 {user_id}: {count} 篇日记")

# 统计标题长度
result = (
    weaviate_client.query
    .aggregate("DiaryEntry")
    .with_fields("title { count type }")
    .do()
)
```

---

### 3. GraphQL 查询

```python
# 使用 GraphQL 进行复杂查询
query = """
{
  Get {
    DiaryEntry(
      where: {
        path: ["userId"],
        operator: Equal,
        valueString: "user_456"
      }
      nearVector: {
        vector: [0.12, -0.45, 0.78, ...]
        certainty: 0.8
      }
      limit: 5
    ) {
      diaryId
      title
      content
      _additional {
        certainty
        distance
        id
      }
    }
  }
}
"""

result = weaviate_client.query.raw(query)
```

---

## ⚡ 性能优化

### 1. HNSW 参数调优

```python
# 创建 Schema 时配置
schema = {
    "class": "DiaryEntry",
    "vectorIndexConfig": {
        # 距离度量
        "distance": "cosine",  # 或 "dot", "l2-squared", "manhattan", "hamming"
        
        # 搜索时的动态列表大小
        "ef": 100,  # 默认: -1 (动态)
        # 更大 = 更准确但更慢
        
        # 构建时的动态列表大小
        "efConstruction": 128,  # 默认: 128
        # 更大 = 更好的索引质量，但构建更慢
        
        # 每个节点的最大连接数
        "maxConnections": 64,  # 默认: 64
        # 更多 = 更好的召回率，但内存占用更多
        
        # 是否清理旧连接
        "cleanupIntervalSeconds": 300,  # 5 分钟
        
        # 向量缓存
        "vectorCacheMaxObjects": 1000000  # 缓存 100 万个向量
    }
}
```

**参数对比**：

| 场景 | ef | efConstruction | maxConnections | 说明 |
|------|----|--------------|----|------|
| **快速原型** | -1 | 64 | 32 | 快速构建，中等质量 |
| **平衡** | 100 | 128 | 64 | 默认配置 ✅ |
| **高质量** | 200 | 256 | 128 | 更准确，更慢 |
| **大规模** | 50 | 64 | 32 | 内存优化 |

---

### 2. 批处理优化

```python
# ❌ 慢：逐个插入
for diary in diaries:
    weaviate_client.data_object.create(...)  # 1000 个请求

# ✅ 快：批处理
with weaviate_client.batch as batch:
    batch.configure(batch_size=100)
    for diary in diaries:
        batch.add_data_object(...)  # 10 个请求 (100x 快！)
```

---

### 3. 查询优化

```python
# ❌ 慢：返回所有字段
result = weaviate_client.query.get("DiaryEntry").do()

# ✅ 快：只返回需要的字段
result = (
    weaviate_client.query
    .get("DiaryEntry", ["diaryId", "title"])  # 只要 ID 和标题
    .with_limit(10)  # 限制返回数量
    .do()
)
```

---

## 🏭 生产部署

### 1. 持久化配置

```yaml
# docker-compose.yml
services:
  weaviate:
    volumes:
      - weaviate_data:/var/lib/weaviate  # 数据持久化
    environment:
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate

volumes:
  weaviate_data:
    driver: local  # 本地存储
```

**备份数据**：

```bash
# 备份
docker run --rm \
  -v jd_project_weaviate_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/weaviate_backup.tar.gz -C /data .

# 恢复
docker run --rm \
  -v jd_project_weaviate_data:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/weaviate_backup.tar.gz -C /data
```

---

### 2. 认证配置

```yaml
# docker-compose.yml (生产环境)
services:
  weaviate:
    environment:
      # 禁用匿名访问
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false
      
      # 启用 API Key 认证
      - AUTHENTICATION_APIKEY_ENABLED=true
      - AUTHENTICATION_APIKEY_ALLOWED_KEYS=your-secret-key-here
      - AUTHENTICATION_APIKEY_USERS=admin
```

```python
# Python 客户端（带认证）
client = weaviate.Client(
    url="https://your-weaviate.com",
    auth_client_secret=weaviate.AuthApiKey(api_key="your-secret-key")
)
```

---

### 3. 监控

```python
# 查看统计信息
meta = weaviate_client.get_meta()
print(json.dumps(meta, indent=2))

# 查看对象数量
result = (
    weaviate_client.query
    .aggregate("DiaryEntry")
    .with_fields("meta { count }")
    .do()
)

count = result["data"]["Aggregate"]["DiaryEntry"][0]["meta"]["count"]
print(f"总日记数: {count}")

# 查看磁盘使用
result = weaviate_client.cluster.get_nodes_status()
for node in result:
    print(f"节点: {node['name']}")
    print(f"状态: {node['status']}")
    print(f"对象数: {node['stats']['objectCount']}")
```

---

## 🔧 故障排查

### 1. 连接问题

```python
# 测试连接
try:
    client.get_meta()
    print("✅ 连接成功")
except Exception as e:
    print(f"❌ 连接失败: {e}")

# 检查 Docker
# docker ps | grep weaviate
# docker logs jd_project-weaviate-1
```

---

### 2. 性能问题

```bash
# 查看日志
docker logs jd_project-weaviate-1 --tail 100

# 检查内存使用
docker stats jd_project-weaviate-1

# 检查磁盘空间
docker exec jd_project-weaviate-1 df -h
```

---

### 3. 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `connection refused` | Weaviate 未启动 | `docker compose up weaviate` |
| `class not found` | Schema 未创建 | 运行 `create_diary_schema()` |
| `vector dimension mismatch` | 向量维度不匹配 | 检查 embedding 模型 |
| `timeout` | 查询太慢 | 优化 HNSW 参数 |

---

## 📚 完整示例

```python
# 完整的工作流程示例
import asyncio

async def main():
    # 1. 初始化
    client = get_weaviate_client()
    create_diary_schema(client)
    
    # 2. 索引数据
    await index_diary(
        diary_id="diary_001",
        user_id="user_123",
        title="美好的一天",
        content="今天天气很好...",
        created_at="2026-01-17T10:00:00Z"
    )
    
    # 3. 搜索
    results = await search_similar_diaries(
        user_id="user_123",
        query_text="今天也是晴天",
        limit=5
    )
    
    # 4. 显示结果
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   相似度: {result['_additional']['certainty']:.4f}")
        print(f"   内容: {result['content'][:100]}...")

# 运行
asyncio.run(main())
```

---

## 🎓 学习资源

- [Weaviate 官方文档](https://weaviate.io/developers/weaviate)
- [Python 客户端文档](https://weaviate-python-client.readthedocs.io/)
- [本项目 RAG 流程](./RAG_FLOW_EXPLAINED.md)
- [HNSW 算法论文](https://arxiv.org/abs/1603.09320)

---

## ✅ 总结

本教程展示了 Weaviate 在真实项目中的应用：

✅ **基础**: Schema 设计、数据类型、索引配置  
✅ **向量**: Embeddings 生成、相似度计算  
✅ **搜索**: 语义搜索、混合搜索、过滤查询  
✅ **优化**: HNSW 调优、批处理、查询优化  
✅ **生产**: 持久化、认证、监控、故障排查  

现在你可以：
1. 在项目中使用 Weaviate
2. 设计高效的向量搜索系统
3. 优化查询性能
4. 部署到生产环境

Happy Vector Searching! 🚀

