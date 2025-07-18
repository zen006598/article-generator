"""回應數據模型"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ArticleGenerationResponse(BaseModel):
    """文章生成回應模型"""
    
    success: bool = Field(
        ...,
        description="請求是否成功"
    )
    
    article: Optional[str] = Field(
        None,
        description="生成的文章內容"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="生成元數據"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="生成時間"
    )


class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    
    success: bool = Field(
        default=False,
        description="請求是否成功"
    )
    
    error: str = Field(
        ...,
        description="錯誤類型"
    )
    
    message: str = Field(
        ...,
        description="錯誤訊息"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="錯誤詳細資訊"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="發生時間"
    )


class ExamTypesResponse(BaseModel):
    """支援的考試類型回應模型"""
    
    exam_types: List[str] = Field(
        ...,
        description="支援的考試類型列表"
    )


class ExamInfoResponse(BaseModel):
    """考試類型詳細資訊回應模型"""
    
    exam_type: str = Field(
        ...,
        description="考試類型"
    )
    
    full_name: str = Field(
        ...,
        description="考試全名"
    )
    
    description: str = Field(
        ...,
        description="考試描述"
    )
    
    supported_difficulties: List[str] = Field(
        ...,
        description="支援的難度等級"
    )
    
    writing_styles: List[str] = Field(
        ...,
        description="支援的寫作風格"
    )
    
    common_topics: List[str] = Field(
        ...,
        description="常見主題"
    )