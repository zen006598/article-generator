"""LLM 統一調用服務"""

import logging
from typing import Dict, List, Optional
import asyncio

from openai import AsyncOpenAI
from app.core.config import settings
from app.core.exceptions import LLMServiceError, ConfigurationError

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服務類，負責與 OpenAI API 的統一調用"""
    
    def __init__(self):
        """初始化 LLM 服務"""
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            raise ConfigurationError("OpenAI API 金鑰未正確設定")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.timeout = settings.generation_timeout
    
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ) -> str:
        """生成文本補全"""
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"發送請求到 OpenAI，模型: {self.model}")
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens or settings.max_article_length,
                    temperature=temperature,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                ),
                timeout=self.timeout
            )
            
            content = response.choices[0].message.content
            if not content:
                raise LLMServiceError("OpenAI API 返回空內容")
            
            logger.info("成功獲得 OpenAI 回應")
            return content.strip()
            
        except asyncio.TimeoutError:
            raise LLMServiceError(f"請求超時（{self.timeout}秒）")
        except Exception as e:
            logger.error(f"OpenAI API 調用失敗: {str(e)}")
            raise LLMServiceError(f"OpenAI API 調用失敗: {str(e)}")
    
    async def generate_article(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        additional_requirements: Optional[Dict] = None
    ) -> str:
        """生成文章的高級接口"""
        try:
            # 構建系統消息
            system_message = self._build_system_message(exam_type, difficulty)
            
            # 構建用戶提示
            user_prompt = self._build_user_prompt(
                exam_type, topic, difficulty, additional_requirements
            )
            
            # 調用生成服務
            article = await self.generate_completion(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.7
            )
            
            return article
            
        except Exception as e:
            logger.error(f"文章生成失敗: {str(e)}")
            raise LLMServiceError(f"文章生成失敗: {str(e)}")
    
    def _build_system_message(self, exam_type: str, difficulty: str) -> str:
        """構建系統消息"""
        return f"""你是一個專業的{exam_type}考試文章生成助手。請根據用戶的要求生成高質量的文章。

要求：
- 文章難度：{difficulty}
- 語言自然流暢
- 結構清晰完整
- 符合{exam_type}考試標準
- 內容積極正面
- 字數控制在適當範圍內"""
    
    def _build_user_prompt(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        additional_requirements: Optional[Dict] = None
    ) -> str:
        """構建用戶提示"""
        prompt = f"請為{exam_type}考試生成一篇關於「{topic}」的文章，難度為{difficulty}。"
        
        if additional_requirements:
            if additional_requirements.get("word_count"):
                prompt += f"\n字數要求：約{additional_requirements['word_count']}字"
            
            if additional_requirements.get("style"):
                prompt += f"\n寫作風格：{additional_requirements['style']}"
            
            if additional_requirements.get("focus_points"):
                points = ", ".join(additional_requirements["focus_points"])
                prompt += f"\n重點內容：{points}"
        
        prompt += "\n\n請直接輸出文章內容，不需要額外的說明或標題。"
        
        return prompt


# 全域 LLM 服務實例
llm_service = LLMService()