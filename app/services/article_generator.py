"""核心文章生成邏輯"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

from app.services.llm_service import llm_service
from app.utils.validators import validator
from app.core.exceptions import ArticleGenerationError, ValidationError
from templates.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class ArticleGenerator:
    """核心文章生成服務"""
    
    def __init__(self):
        """初始化文章生成器"""
        self.llm_service = llm_service
        self.validator = validator
        self.prompt_templates = PromptTemplates
    
    async def generate_article(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: Optional[int] = None,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """生成文章的主要方法"""
        
        try:
            logger.info(f"開始生成文章 - 考試類型: {exam_type}, 主題: {topic}, 難度: {difficulty}")
            
            # 1. 驗證所有參數
            self._validate_parameters(exam_type, topic, difficulty, word_count, style)
            
            # 2. 處理字數要求
            final_word_count = self._process_word_count(exam_type, difficulty, word_count)
            
            # 3. 獲取提示模板
            templates = self._get_prompt_templates(
                exam_type, topic, difficulty, final_word_count, style, focus_points
            )
            
            # 4. 調用 LLM 服務生成文章
            article_content = await self.llm_service.generate_completion(
                prompt=templates["user_prompt"],
                system_message=templates["system_message"],
                max_tokens=final_word_count * 2,  # 給予一些緩衝空間
                temperature=0.7
            )
            
            # 5. 構建回應元數據
            metadata = self._build_metadata(
                exam_type, topic, difficulty, final_word_count, style, focus_points
            )
            
            logger.info("文章生成成功")
            
            return {
                "success": True,
                "article": article_content,
                "metadata": metadata,
                "timestamp": datetime.now()
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
    
    def _get_prompt_templates(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int,
        style: Optional[str],
        focus_points: Optional[List[str]]
    ) -> Dict[str, str]:
        """獲取適當的提示模板"""
        
        return self.prompt_templates.get_template_by_exam_type(
            exam_type=exam_type,
            topic=topic,
            difficulty=difficulty,
            word_count=word_count,
            style=style,
            focus_points=focus_points
        )
    
    def _build_metadata(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int,
        style: Optional[str],
        focus_points: Optional[List[str]]
    ) -> Dict[str, any]:
        """構建回應元數據"""
        
        metadata = {
            "exam_type": exam_type,
            "topic": topic,
            "difficulty": difficulty,
            "target_word_count": word_count,
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
    
    def get_exam_info(self, exam_type: str) -> Dict[str, any]:
        """獲取考試類型的詳細資訊"""
        return self.validator.get_exam_info(exam_type)


# 全域文章生成器實例
article_generator = ArticleGenerator()