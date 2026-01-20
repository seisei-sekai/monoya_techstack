from datetime import datetime
from typing import List, Optional
from app.models.diary import DiaryCreate, DiaryUpdate, DiaryResponse
from app.core.firebase import get_firestore_db
from app.services.rag_service import RAGService
from app.services.llama_rag_service import LlamaRAGService

class DiaryService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = "diaries"
        self.rag_service = RAGService()
        self.llama_rag_service = LlamaRAGService()  # 添加 Llama RAG 服务

    async def get_all_diaries(self, user_id: str) -> List[DiaryResponse]:
        """Get all diaries for a user"""
        diaries_ref = self.db.collection(self.collection_name)
        query = diaries_ref.where("userId", "==", user_id).order_by("createdAt", direction="DESCENDING")
        
        docs = query.stream()
        diaries = []
        
        for doc in docs:
            data = doc.to_dict()
            diaries.append(DiaryResponse(
                id=doc.id,
                **data
            ))
        
        return diaries

    async def get_diary(self, diary_id: str, user_id: str) -> Optional[DiaryResponse]:
        """Get a specific diary"""
        doc_ref = self.db.collection(self.collection_name).document(diary_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        
        # Verify ownership
        if data.get("userId") != user_id:
            return None
        
        return DiaryResponse(
            id=doc.id,
            **data
        )

    async def create_diary(self, diary: DiaryCreate, user_id: str) -> DiaryResponse:
        """Create a new diary entry"""
        now = datetime.utcnow()
        
        diary_data = {
            "userId": user_id,
            "title": diary.title,
            "content": diary.content,
            "createdAt": now,
            "updatedAt": now,
            "aiInsight": None
        }
        
        # Add to Firestore
        doc_ref = self.db.collection(self.collection_name).document()
        doc_ref.set(diary_data)
        
        # Index in Weaviate for both RAG systems
        # 1. OpenAI RAG (使用 OpenAI embeddings)
        await self.rag_service.index_diary(
            diary_id=doc_ref.id,
            user_id=user_id,
            title=diary.title,
            content=diary.content,
            created_at=now.isoformat()
        )
        
        # 2. Llama RAG (使用 Ollama embeddings)
        await self.llama_rag_service.index_diary(
            diary_id=doc_ref.id,
            user_id=user_id,
            title=diary.title,
            content=diary.content,
            created_at=now.isoformat()
        )
        
        return DiaryResponse(
            id=doc_ref.id,
            **diary_data
        )

    async def update_diary(
        self, 
        diary_id: str, 
        diary: DiaryUpdate, 
        user_id: str
    ) -> Optional[DiaryResponse]:
        """Update an existing diary"""
        doc_ref = self.db.collection(self.collection_name).document(diary_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        
        # Verify ownership
        if data.get("userId") != user_id:
            return None
        
        # Update fields
        update_data = {"updatedAt": datetime.utcnow()}
        
        if diary.title is not None:
            update_data["title"] = diary.title
        if diary.content is not None:
            update_data["content"] = diary.content
        
        doc_ref.update(update_data)
        
        # Update in Weaviate if content changed
        if diary.content is not None or diary.title is not None:
            updated_title = diary.title if diary.title is not None else data.get("title")
            updated_content = diary.content if diary.content is not None else data.get("content")
            
            await self.rag_service.update_diary(
                diary_id=diary_id,
                user_id=user_id,
                title=updated_title,
                content=updated_content
            )
        
        # Get updated document
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        return DiaryResponse(
            id=diary_id,
            **updated_data
        )

    async def delete_diary(self, diary_id: str, user_id: str) -> bool:
        """Delete a diary"""
        doc_ref = self.db.collection(self.collection_name).document(diary_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        data = doc.to_dict()
        
        # Verify ownership
        if data.get("userId") != user_id:
            return False
        
        # Delete from Firestore
        doc_ref.delete()
        
        # Delete from Weaviate
        await self.rag_service.delete_diary(diary_id)
        
        return True

    async def generate_ai_insight(self, diary_id: str, user_id: str) -> str:
        """Generate AI insight for a diary using RAG"""
        # Get the current diary
        diary = await self.get_diary(diary_id, user_id)
        
        if not diary:
            raise ValueError("Diary not found")
        
        # Generate insight using RAG
        insight = await self.rag_service.generate_insight(
            current_diary=diary,
            user_id=user_id
        )
        
        # Update diary with the insight
        doc_ref = self.db.collection(self.collection_name).document(diary_id)
        doc_ref.update({
            "aiInsight": insight,
            "updatedAt": datetime.utcnow()
        })
        
        return insight

