"""核心文章生成邏輯"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

from app.services.llm_service import llm_service
from app.utils.validators import validator
from app.core.exceptions import ArticleGenerationError, ValidationError

logger = logging.getLogger(__name__)


class ArticleGenerator:
    """核心文章生成服務"""
    
    def __init__(self):
        """初始化文章生成器"""
        self.llm_service = llm_service
        self.validator = validator
    
    async def generate_article(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: Optional[int] = None,
        paragraph_count: Optional[int] = None,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成文章的主要方法"""
        
        try:
            logger.info(f"開始生成文章 - 考試類型: {exam_type}, 主題: {topic}, 難度: {difficulty}, 提供商: {provider}")
            
            # 1. 驗證所有參數
            self._validate_parameters(exam_type, topic, difficulty, word_count, paragraph_count, style)
            
            # 2. 處理預設值
            final_word_count = self._process_word_count(exam_type, difficulty, word_count)
            final_paragraph_count = paragraph_count or 3
            
            # 3. 使用 LLM 服務的高級介面
            response = await self.llm_service.generate_article(
                exam_type=exam_type,
                topic=topic,
                difficulty=difficulty,
                word_count=final_word_count,
                paragraph_count=final_paragraph_count,
                style=style,
                focus_points=focus_points,
                provider=provider
            )
            
            # 4. 構建回應元數據
            metadata = self._build_metadata(
                exam_type, topic, difficulty, final_word_count, 
                final_paragraph_count, style, focus_points, response
            )
            
            logger.info("文章生成成功")
            
            return {
                "success": True,
                "article": response["content"],
                "metadata": metadata,
                "generation_info": {
                    "provider": response.get("provider", "unknown"),
                    "model": response.get("model", "unknown"),
                    "usage": response.get("usage", {})
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"文章生成失敗: {str(e)}")
            raise ArticleGenerationError(f"文章生成失敗: {str(e)}")
    
    def _validate_parameters(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: Optional[int],
        paragraph_count: Optional[int],
        style: Optional[str]
    ) -> None:
        """驗證所有輸入參數"""
        
        # 驗證考試類型
        self.validator.validate_exam_type(exam_type)
        
        # 驗證主題
        self.validator.validate_topic(exam_type, topic)
        
        # 驗證難度
        self.validator.validate_difficulty(exam_type, difficulty)
        
        # 驗證字數
        if word_count is not None:
            self.validator.validate_word_count(exam_type, word_count)
        
        # 驗證段落數
        if paragraph_count is not None:
            if paragraph_count < 1 or paragraph_count > 10:
                raise ValidationError("段落數必須在 1-10 之間")
        
        # 驗證風格
        self.validator.validate_style(exam_type, style)
    
    def _process_word_count(
        self,
        exam_type: str,
        difficulty: str,
        word_count: Optional[int]
    ) -> int:
        """處理字數要求，返回最終使用的字數"""
        
        if word_count is not None:
            return word_count
        
        # 使用預設字數
        return self.validator.get_default_word_count(exam_type, difficulty)
    
    def _build_metadata(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int,
        paragraph_count: int,
        style: Optional[str],
        focus_points: Optional[List[str]],
        llm_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """構建回應元數據"""
        
        metadata = {
            "exam_type": exam_type,
            "topic": topic,
            "difficulty": difficulty,
            "target_word_count": word_count,
            "target_paragraph_count": paragraph_count,
            "actual_word_count": llm_response.get("actual_word_count", 0),
            "generation_time": datetime.now().isoformat()
        }
        
        if style:
            metadata["style"] = style
        
        if focus_points:
            metadata["focus_points"] = focus_points
        
        # 添加考試類型的基本資訊
        exam_info = self.validator.get_exam_info(exam_type)
        metadata["exam_info"] = {
            "full_name": exam_info["full_name"],
            "description": exam_info["description"]
        }
        
        return metadata
    
    def get_supported_exam_types(self) -> List[str]:
        """獲取支援的考試類型"""
        return self.validator.get_supported_exam_types()
    
    def get_exam_info(self, exam_type: str) -> Dict[str, Any]:
        """獲取考試類型的詳細資訊"""
        return self.validator.get_exam_info(exam_type)
    
    def get_available_providers(self) -> List[str]:
        """獲取可用的 LLM 提供商"""
        return self.llm_service.get_available_providers()
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """獲取提供商詳細信息"""
        return self.llm_service.get_provider_info()


# 全域文章生成器實例
article_generator = ArticleGenerator()