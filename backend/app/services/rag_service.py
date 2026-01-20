from typing import List
from openai import OpenAI
from app.core.config import settings
from app.core.weaviate_client import get_weaviate_client
from app.models.diary import DiaryResponse

class RAGService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.weaviate_client = get_weaviate_client()

    async def index_diary(
        self,
        diary_id: str,
        user_id: str,
        title: str,
        content: str,
        created_at: str
    ):
        """Index a diary entry in Weaviate"""
        try:
            # Create embedding using OpenAI
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=f"{title}\n\n{content}"
            )
            
            embedding = embedding_response.data[0].embedding
            
            # Store in Weaviate
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
        except Exception as e:
            print(f"Error indexing diary: {e}")

    async def update_diary(
        self,
        diary_id: str,
        user_id: str,
        title: str,
        content: str
    ):
        """Update a diary entry in Weaviate"""
        try:
            # Find the object by diary ID
            result = (
                self.weaviate_client.query
                .get("DiaryEntry", ["diaryId"])
                .with_where({
                    "path": ["diaryId"],
                    "operator": "Equal",
                    "valueString": diary_id
                })
                .with_additional(["id"])
                .do()
            )
            
            if result.get("data", {}).get("Get", {}).get("DiaryEntry"):
                weaviate_id = result["data"]["Get"]["DiaryEntry"][0]["_additional"]["id"]
                
                # Create new embedding
                embedding_response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=f"{title}\n\n{content}"
                )
                
                embedding = embedding_response.data[0].embedding
                
                # Update in Weaviate
                self.weaviate_client.data_object.update(
                    data_object={
                        "title": title,
                        "content": content
                    },
                    class_name="DiaryEntry",
                    uuid=weaviate_id,
                    vector=embedding
                )
        except Exception as e:
            print(f"Error updating diary: {e}")

    async def delete_diary(self, diary_id: str):
        """Delete a diary entry from Weaviate"""
        try:
            # Find and delete the object
            result = (
                self.weaviate_client.query
                .get("DiaryEntry", ["diaryId"])
                .with_where({
                    "path": ["diaryId"],
                    "operator": "Equal",
                    "valueString": diary_id
                })
                .with_additional(["id"])
                .do()
            )
            
            if result.get("data", {}).get("Get", {}).get("DiaryEntry"):
                weaviate_id = result["data"]["Get"]["DiaryEntry"][0]["_additional"]["id"]
                self.weaviate_client.data_object.delete(
                    uuid=weaviate_id,
                    class_name="DiaryEntry"
                )
        except Exception as e:
            print(f"Error deleting diary: {e}")

    async def search_similar_diaries(
        self,
        user_id: str,
        query_text: str,
        limit: int = 5
    ) -> List[dict]:
        """Search for similar diary entries using semantic search"""
        try:
            # Create embedding for the query
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query_text
            )
            
            embedding = embedding_response.data[0].embedding
            
            # Search in Weaviate
            result = (
                self.weaviate_client.query
                .get("DiaryEntry", ["diaryId", "title", "content", "createdAt"])
                .with_near_vector({
                    "vector": embedding
                })
                .with_where({
                    "path": ["userId"],
                    "operator": "Equal",
                    "valueString": user_id
                })
                .with_limit(limit)
                .do()
            )
            
            entries = result.get("data", {}).get("Get", {}).get("DiaryEntry", [])
            return entries
        except Exception as e:
            print(f"Error searching diaries: {e}")
            return []

    async def generate_insight(
        self,
        current_diary: DiaryResponse,
        user_id: str
    ) -> str:
        """Generate personalized AI insight based on user's diary history"""
        # Search for similar past diaries
        similar_diaries = await self.search_similar_diaries(
            user_id=user_id,
            query_text=f"{current_diary.title}\n\n{current_diary.content}",
            limit=5
        )
        
        # Filter out the current diary from results
        similar_diaries = [
            d for d in similar_diaries 
            if d.get("diaryId") != current_diary.id
        ]
        
        # Build context from similar diaries
        context = ""
        if similar_diaries:
            context = "\n\n---Previous related entries---\n"
            for diary in similar_diaries[:3]:  # Use top 3
                context += f"\nTitle: {diary.get('title', 'Untitled')}\n"
                context += f"Content: {diary.get('content', '')[:200]}...\n"
        
        # Generate insight using OpenAI
        prompt = f"""You are a compassionate AI journal companion. Based on the user's current diary entry and their past related entries, provide a personalized, thoughtful insight.

Current Entry:
Title: {current_diary.title}
Content: {current_diary.content}
{context}

Provide a warm, empathetic response that:
1. Acknowledges their current feelings and thoughts
2. Notes any patterns or growth compared to past entries (if available)
3. Offers gentle encouragement or perspective
4. Keep it under 150 words

Response:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a compassionate AI journal companion who provides thoughtful, personalized insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            insight = response.choices[0].message.content.strip()
            return insight
        except Exception as e:
            print(f"Error generating insight: {e}")
            return "Thank you for sharing your thoughts. Keep writing to help me understand you better!"

