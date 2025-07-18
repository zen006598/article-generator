"""請求數據模型"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ArticleGenerationRequest(BaseModel):
    """文章生成請求模型"""
    
    exam_type: str = Field(
        ...,
        description="考試類型（支援：TOEIC、GRE、IELTS、SAT）",
        example="TOEIC"
    )
    
    topic: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="文章主題",
        example="Business Meetings"
    )
    
    difficulty: str = Field(
        ...,
        description="難度等級（依考試類型而異）",
        example="中級"
    )
    
    word_count: Optional[int] = Field(
        None,
        ge=50,
        le=600,
        description="目標字數（可選，會使用預設值）",
        example=200
    )
    
    paragraph_count: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="段落數（可選，預設為3）",
        example=3
    )
    
    style: Optional[str] = Field(
        None,
        description="寫作風格（可選）",
        example="正式商業"
    )
    
    focus_points: Optional[List[str]] = Field(
        None,
        description="重點內容（可選）",
        example=["team collaboration", "communication skills"]
    )
    
    @validator("exam_type")
    def validate_exam_type(cls, v):
        """驗證考試類型格式"""
        allowed_types = ["TOEIC", "GRE", "IELTS", "SAT"]
        v_upper = v.upper().strip()
        if v_upper not in allowed_types:
            raise ValueError(f"考試類型必須是以下之一: {', '.join(allowed_types)}")
        return v_upper
    
    @validator("topic")
    def validate_topic(cls, v):
        """驗證主題格式"""
        return v.strip()
    
    @validator("difficulty")
    def validate_difficulty(cls, v):
        """驗證難度格式"""
        return v.strip()
    
    @validator("style")
    def validate_style(cls, v):
        """驗證風格格式"""
        if v is not None:
            return v.strip()
        return v
    
    @validator("focus_points")
    def validate_focus_points(cls, v):
        """驗證重點內容格式"""
        if v is not None:
            return [point.strip() for point in v if point.strip()]
        return v