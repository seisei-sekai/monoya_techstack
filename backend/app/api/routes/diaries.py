from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from app.models.diary import DiaryCreate, DiaryUpdate, DiaryResponse, AIInsightResponse
from app.api.dependencies import get_current_user
from app.services.diary_service import DiaryService
from app.services.llama_rag_service import LlamaRAGService

router = APIRouter()
diary_service = DiaryService()
llama_rag_service = LlamaRAGService()

class RecommendationRequest(BaseModel):
    title: str = ""
    content: str

@router.get("", response_model=List[DiaryResponse])
async def get_all_diaries(
    current_user: dict = Depends(get_current_user)
):
    """Get all diaries for the current user"""
    user_id = current_user["uid"]
    return await diary_service.get_all_diaries(user_id)

@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_diary(
    diary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific diary by ID"""
    user_id = current_user["uid"]
    diary = await diary_service.get_diary(diary_id, user_id)
    
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary not found"
        )
    
    return diary

@router.post("", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(
    diary: DiaryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new diary entry"""
    user_id = current_user["uid"]
    return await diary_service.create_diary(diary, user_id)

@router.put("/{diary_id}", response_model=DiaryResponse)
async def update_diary(
    diary_id: str,
    diary: DiaryUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing diary"""
    user_id = current_user["uid"]
    updated_diary = await diary_service.update_diary(diary_id, diary, user_id)
    
    if not updated_diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary not found"
        )
    
    return updated_diary

@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary(
    diary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a diary"""
    user_id = current_user["uid"]
    success = await diary_service.delete_diary(diary_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary not found"
        )

@router.post("/{diary_id}/ai-insight", response_model=AIInsightResponse)
async def get_ai_insight(
    diary_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI insight for a diary based on user's history"""
    user_id = current_user["uid"]
    
    try:
        insight = await diary_service.generate_ai_insight(diary_id, user_id)
        return {"insight": insight}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI insight: {str(e)}"
        )

@router.post("/recommend", response_model=AIInsightResponse)
async def get_llama_recommendation(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """使用本地 Llama 模型生成写作推荐"""
    user_id = current_user["uid"]
    
    try:
        recommendation = await llama_rag_service.generate_recommendation(
            user_id=user_id,
            current_content=request.content,
            current_title=request.title
        )
        return {"insight": recommendation}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}"
        )

@router.get("/ollama/status")
async def check_ollama_status(
    current_user: dict = Depends(get_current_user)
):
    """检查 Ollama 服务状态"""
    status = await llama_rag_service.check_ollama_status()
    return status

