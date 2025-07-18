"""文章生成 API 端點"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.request import ArticleGenerationRequest
from app.models.response import (
    ArticleGenerationResponse,
    ErrorResponse,
    ExamTypesResponse,
    ExamInfoResponse
)
from app.services.article_generator import article_generator
from app.core.exceptions import (
    ArticleGeneratorException,
    ValidationError,
    ExamTypeNotSupportedError
)

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter()


@router.post(
    "/generate",
    response_model=ArticleGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="生成文章",
    description="根據指定的考試類型、主題和難度生成文章"
)
async def generate_article(request: ArticleGenerationRequest) -> ArticleGenerationResponse:
    """
    生成文章的主要 API 端點
    
    Args:
        request: 文章生成請求
        
    Returns:
        ArticleGenerationResponse: 包含生成文章的回應
        
    Raises:
        HTTPException: 當參數驗證失敗或生成過程出錯時
    """
    try:
        logger.info(f"收到文章生成請求: {request.exam_type} - {request.topic}")
        
        # 調用文章生成服務
        result = await article_generator.generate_article(
            exam_type=request.exam_type,
            topic=request.topic,
            difficulty=request.difficulty,
            word_count=request.word_count,
            style=request.style,
            focus_points=request.focus_points
        )
        
        return ArticleGenerationResponse(**result)
        
    except ValidationError as e:
        logger.warning(f"參數驗證失敗: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "參數驗證錯誤",
                "message": e.message,
                "details": e.details
            }
        )
    
    except ExamTypeNotSupportedError as e:
        logger.warning(f"不支援的考試類型: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "不支援的考試類型",
                "message": e.message,
                "details": e.details
            }
        )
    
    except ArticleGeneratorException as e:
        logger.error(f"文章生成錯誤: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "文章生成失敗",
                "message": e.message,
                "details": e.details
            }
        )
    
    except Exception as e:
        logger.error(f"未預期的錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "伺服器內部錯誤",
                "message": "發生未預期的錯誤，請稍後再試"
            }
        )


@router.get(
    "/exam-types",
    response_model=ExamTypesResponse,
    summary="獲取支援的考試類型",
    description="返回所有支援的考試類型列表"
)
async def get_exam_types() -> ExamTypesResponse:
    """
    獲取所有支援的考試類型
    
    Returns:
        ExamTypesResponse: 包含考試類型列表的回應
    """
    try:
        exam_types = article_generator.get_supported_exam_types()
        return ExamTypesResponse(exam_types=exam_types)
    
    except Exception as e:
        logger.error(f"獲取考試類型列表失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "伺服器內部錯誤",
                "message": "無法獲取考試類型列表"
            }
        )


@router.get(
    "/exam-types/{exam_type}",
    response_model=ExamInfoResponse,
    responses={
        400: {"model": ErrorResponse}
    },
    summary="獲取考試類型詳細資訊",
    description="返回指定考試類型的詳細資訊"
)
async def get_exam_info(exam_type: str) -> ExamInfoResponse:
    """
    獲取指定考試類型的詳細資訊
    
    Args:
        exam_type: 考試類型名稱
        
    Returns:
        ExamInfoResponse: 包含考試詳細資訊的回應
        
    Raises:
        HTTPException: 當考試類型不存在時
    """
    try:
        exam_type = exam_type.upper().strip()
        exam_info = article_generator.get_exam_info(exam_type)
        
        return ExamInfoResponse(
            exam_type=exam_info["name"],
            full_name=exam_info["full_name"],
            description=exam_info["description"],
            supported_difficulties=exam_info["supported_difficulties"],
            writing_styles=exam_info["writing_styles"],
            common_topics=exam_info["common_topics"]
        )
    
    except ExamTypeNotSupportedError as e:
        logger.warning(f"查詢不存在的考試類型: {exam_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "不支援的考試類型",
                "message": e.message,
                "details": e.details
            }
        )
    
    except Exception as e:
        logger.error(f"獲取考試資訊失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "伺服器內部錯誤",
                "message": "無法獲取考試資訊"
            }
        )


@router.get(
    "/health",
    summary="健康檢查",
    description="檢查文章生成服務的健康狀態"
)
async def health_check() -> Dict[str, Any]:
    """
    健康檢查端點
    
    Returns:
        Dict: 包含服務狀態的回應
    """
    return {
        "status": "healthy",
        "service": "文章生成服務",
        "supported_exam_types": article_generator.get_supported_exam_types()
    }