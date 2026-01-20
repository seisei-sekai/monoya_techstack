from typing import List
import httpx
from app.core.config import settings
from app.core.firebase import get_firestore_db
from app.core.weaviate_client import get_weaviate_client

class LlamaRAGService:
    """
    Llama RAG 服务 - 使用 Weaviate 向量数据库进行语义搜索
    
    工作流程：
    1. 索引阶段：当创建/更新日记时，生成嵌入向量并存储到 Weaviate
    2. 查询阶段：用户写新日记时，查找语义相似的历史日记
    3. 生成阶段：使用相关历史日记作为上下文，生成个性化推荐
    """
    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.model = settings.ollama_model
        self.db = get_firestore_db()
        self.collection_name = "diaries"
        self.weaviate_client = get_weaviate_client()
        self.weaviate_class = "DiaryEntry"

    async def generate_embedding(self, text: str) -> List[float]:
        """
        步骤 1: 生成文本嵌入向量
        
        使用 Ollama 的 embedding 功能将文本转换为向量表示
        这样可以进行语义相似度搜索
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("embedding", [])
                else:
                    print(f"[Llama RAG] Embedding failed: {response.status_code}")
                    return []
        except Exception as e:
            print(f"[Llama RAG] Error generating embedding: {e}")
            return []

    async def index_diary(
        self,
        diary_id: str,
        user_id: str,
        title: str,
        content: str,
        created_at: str
    ):
        """
        步骤 2: 索引日记到 Weaviate
        
        流程：
        1. 合并标题和内容
        2. 生成嵌入向量
        3. 存储到 Weaviate 向量数据库
        
        这样后续可以进行语义搜索
        """
        try:
            print(f"[Llama RAG] Indexing diary {diary_id}")
            
            # 合并标题和内容生成嵌入
            full_text = f"{title}\n\n{content}"
            embedding = await self.generate_embedding(full_text)
            
            if not embedding:
                print(f"[Llama RAG] Skip indexing - no embedding generated")
                return
            
            # 存储到 Weaviate
            self.weaviate_client.data_object.create(
                class_name=self.weaviate_class,
                data_object={
                    "diaryId": diary_id,
                    "userId": user_id,
                    "title": title,
                    "content": content,
                    "createdAt": created_at
                },
                vector=embedding
            )
            
            print(f"[Llama RAG] Successfully indexed diary {diary_id}")
            
        except Exception as e:
            print(f"[Llama RAG] Error indexing diary: {e}")

    async def search_similar_diaries(
        self,
        user_id: str,
        query_text: str,
        limit: int = 5
    ) -> List[dict]:
        """
        步骤 3: 语义搜索相似日记
        
        流程：
        1. 为查询文本生成嵌入向量
        2. 在 Weaviate 中搜索语义最相似的日记
        3. 只返回同一用户的日记
        4. 按相似度排序
        
        这是 RAG 的核心 - 检索相关上下文
        """
        try:
            print(f"[Llama RAG] Searching similar diaries for user {user_id}")
            
            # 为查询生成嵌入
            query_embedding = await self.generate_embedding(query_text)
            
            if not query_embedding:
                print(f"[Llama RAG] Skip search - no embedding generated")
                return []
            
            # 在 Weaviate 中进行向量搜索
            result = (
                self.weaviate_client.query
                .get(self.weaviate_class, ["diaryId", "title", "content", "createdAt"])
                .with_near_vector({
                    "vector": query_embedding
                })
                .with_where({
                    "path": ["userId"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_limit(limit)
                .do()
            )
            
            entries = result.get("data", {}).get("Get", {}).get(self.weaviate_class, [])
            print(f"[Llama RAG] Found {len(entries)} similar diaries")
            
            return entries
            
        except Exception as e:
            print(f"[Llama RAG] Error searching diaries: {e}")
            return []

    async def generate_recommendation(
        self,
        user_id: str,
        current_content: str,
        current_title: str = ""
    ) -> str:
        """
        步骤 4: 生成个性化推荐
        
        完整 RAG 流程：
        1. 【检索 Retrieval】使用 Weaviate 语义搜索找到最相关的历史日记
        2. 【增强 Augmented】将相关日记作为上下文添加到提示词
        3. 【生成 Generation】使用 Llama 模型生成个性化建议
        
        这就是 RAG (Retrieval-Augmented Generation) 的核心！
        """
        try:
            print(f"[Llama RAG] ====== RAG 流程开始 ======")
            print(f"[Llama RAG] 用户 ID: {user_id}")
            print(f"[Llama RAG] 当前内容长度: {len(current_content)} 字符")
            
            # ===== 步骤 1: 检索 (Retrieval) =====
            print(f"[Llama RAG] 步骤 1/3: 检索相关日记...")
            query_text = f"{current_title}\n\n{current_content}"
            # 这个返回的是 Weaviate 里存储的日记的 text 字段内容（如 title、content），而不是 vector（嵌入向量）内容。
            similar_diaries = await self.search_similar_diaries(
                user_id=user_id,
                query_text=query_text,
                limit=3  # 只取最相关的 3 篇
            )
            
            # ===== 步骤 2: 增强 (Augmented) =====
            print(f"[Llama RAG] 步骤 2/3: 构建增强上下文...")
            context = ""
            if similar_diaries:
                context = "用户的相关历史日记（按相似度排序）：\n\n"
                for i, diary in enumerate(similar_diaries, 1):
                    context += f"【相关日记 {i}】\n"
                    context += f"标题: {diary.get('title', '无标题')}\n"
                    context += f"内容: {diary.get('content', '')[:300]}...\n\n"
                print(f"[Llama RAG] 找到 {len(similar_diaries)} 篇相关日记")
            else:
                context = "用户还没有历史日记，这是第一篇。\n\n"
                print(f"[Llama RAG] 无历史日记，将提供通用建议")
            
            # 构建增强的提示词（包含检索到的上下文）
            prompt = f"""你是一个智能日记助手。根据用户的相关历史日记和当前正在写的内容，提供有帮助的建议。

{context}

当前正在写的日记：
标题: {current_title}
内容: {current_content[:500]}

请提供：
1. 对当前内容的简短评论
2. 与历史日记的联系或主题观察
3. 1-2条写作建议或思考方向

用中文回复，保持温暖和鼓励的语气，不超过150字。"""

            # ===== 步骤 3: 生成 (Generation) =====
            print(f"[Llama RAG] 步骤 3/3: 使用 Llama 生成推荐...")
            print(f"[Llama RAG] 调用 Ollama API: {self.ollama_url}")
            
            # 调用 Ollama API
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    response = await client.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.7,
                                "num_predict": 200
                            }
                        }
                    )
                    
                    print(f"[Llama RAG] Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        recommendation = result.get("response", "")
                        if recommendation:
                            print(f"[Llama RAG] ✅ 成功生成推荐: {len(recommendation)} 字符")
                            print(f"[Llama RAG] ====== RAG 流程完成 ======")
                            return recommendation
                        else:
                            error_msg = result.get("error", "未知错误")
                            print(f"[Llama RAG] No response in result: {error_msg}")
                            return f"⚠️ Ollama 返回空结果。可能是模型未加载。错误: {error_msg}"
                    else:
                        error_text = response.text
                        print(f"[Llama RAG] Error response: {error_text}")
                        return f"⚠️ Ollama 服务错误 (状态码 {response.status_code}): {error_text[:200]}"
                        
                except httpx.TimeoutException as e:
                    print(f"[Llama RAG] Timeout error: {e}")
                    return "⚠️ 请求超时。模型可能正在加载，请稍后再试（30-60秒）。"
                except httpx.ConnectError as e:
                    print(f"[Llama RAG] Connection error: {e}")
                    return "⚠️ 无法连接到 Ollama 服务。请检查服务是否运行: docker ps | grep ollama"
                    
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[Llama RAG] Unexpected error: {error_trace}")
            return f"生成推荐时出错: {type(e).__name__}: {str(e)}"

    async def check_ollama_status(self) -> dict:
        """检查 Ollama 服务状态"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    has_model = any(self.model in m.get("name", "") for m in models)
                    return {
                        "status": "running",
                        "model_available": has_model,
                        "models": [m.get("name") for m in models]
                    }
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e)
            }

