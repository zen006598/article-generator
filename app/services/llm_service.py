"""LLM 統一調用服務"""

import logging
from typing import Dict, List, Optional, Any
import asyncio
import os
import time
from functools import wraps

from openai import AsyncOpenAI
from app.core.config import settings
from app.core.exceptions import (
    LLMServiceError, 
    ConfigurationError, 
    OpenAIAPIError, 
    GenerationTimeoutError
)

logger = logging.getLogger(__name__)


def retry_async(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """異步重試裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff_factor ** attempt)
                        logger.warning(
                            f"調用失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}, "
                            f"等待 {wait_time:.2f} 秒後重試"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"所有重試都失敗了: {str(e)}")
                        
            raise last_exception
        return wrapper
    return decorator


class LLMProvider:
    """LLM 提供商基礎類"""
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """生成文本補全，返回標準化的回應"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI 提供商"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini-2024-07-18"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    @retry_async(max_retries=3, delay=1.0)
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """使用 OpenAI API 生成文本"""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or 1500,
                temperature=temperature,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            end_time = time.time()
            
            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": self.model,
                "provider": "openai",
                "api_response_time": round(end_time - start_time, 3)
            }
            
            logger.info(f"OpenAI API 調用成功，耗時 {result['api_response_time']:.3f} 秒")
            return result
            
        except Exception as e:
            raise OpenAIAPIError(f"OpenAI API 調用失敗: {str(e)}", details={"error": str(e)})


class GeminiProvider(LLMProvider):
    """Gemini 提供商（透過 OpenAI SDK 調用）"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        # 使用 OpenAI SDK 調用 Gemini
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model
    
    @retry_async(max_retries=3, delay=1.0)
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """使用 Gemini API（透過 OpenAI SDK）生成文本"""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or 1500,
                temperature=temperature
            )
            
            end_time = time.time()
            
            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "model": self.model,
                "provider": "gemini",
                "api_response_time": round(end_time - start_time, 3)
            }
            
            logger.info(f"Gemini API 調用成功，耗時 {result['api_response_time']:.3f} 秒")
            return result
            
        except Exception as e:
            raise LLMServiceError(f"Gemini API 調用失敗: {str(e)}", details={"error": str(e), "provider": "gemini"})


class LLMService:
    """LLM 服務類，支援多個提供商的統一調用"""
    
    def __init__(self):
        """初始化 LLM 服務"""
        self.timeout = settings.generation_timeout
        self.providers = self._initialize_providers()
        self.default_provider = settings.default_llm_provider
    
    def _initialize_providers(self) -> Dict[str, LLMProvider]:
        """初始化所有可用的 LLM 提供商"""
        providers = {}
        
        # 初始化 OpenAI
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            if settings.openai_api_key != "your_openai_api_key_here":
                providers['openai'] = OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model
                )
                logger.info("OpenAI 提供商初始化成功")
        
        # 初始化 Gemini
        if hasattr(settings, 'gemini_api_key') and settings.gemini_api_key:
            if settings.gemini_api_key != "your_gemini_api_key_here":
                providers['gemini'] = GeminiProvider(
                    api_key=settings.gemini_api_key,
                    model=settings.gemini_model
                )
            logger.info("Gemini 提供商初始化成功")
        
        if not providers:
            logger.warning("沒有可用的 LLM 提供商，請檢查 API 金鑰配置")
        
        return providers
    
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成文本補全"""
        try:
            # 檢查是否有可用的提供商
            if not self.providers:
                raise LLMServiceError("沒有可用的 LLM 提供商，請檢查 API 金鑰配置")
            
            # 選擇提供商
            provider_name = provider or self.default_provider
            if provider_name not in self.providers:
                available = list(self.providers.keys())
                raise LLMServiceError(f"提供商 '{provider_name}' 不可用。可用提供商: {available}")
            
            selected_provider = self.providers[provider_name]
            
            # 構建消息
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            logger.info(f"發送請求到 {provider_name.upper()}")
            
            # 執行生成
            response = await asyncio.wait_for(
                selected_provider.generate_completion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                ),
                timeout=self.timeout
            )
            
            if not response.get("content"):
                raise LLMServiceError(f"{provider_name.upper()} API 返回空內容")
            
            logger.info(f"成功獲得 {provider_name.upper()} 回應")
            return response
            
        except asyncio.TimeoutError:
            raise GenerationTimeoutError(self.timeout)
        except Exception as e:
            logger.error(f"LLM API 調用失敗: {str(e)}")
            raise
    
    async def generate_article(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int = 200,
        paragraph_count: int = 3,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成文章的高級接口"""
        try:
            # 使用動態模板服務
            from app.services.template_service import template_service
            
            # 建立動態模板
            template = template_service.build_dynamic_template(
                exam_type=exam_type,
                topic=topic,
                difficulty=difficulty,
                word_count=word_count,
                paragraph_count=paragraph_count,
                style=style,
                focus_points=focus_points
            )
            
            # 調用生成服務
            response = await self.generate_completion(
                prompt=template["user_prompt"],
                system_message=template["system_message"],
                temperature=0.7,
                provider=provider
            )
            
            # 添加生成元數據
            response.update({
                "exam_type": exam_type,
                "topic": topic,
                "difficulty": difficulty,
                "target_word_count": word_count,
                "paragraph_count": paragraph_count,
                "actual_word_count": len(response["content"].split())
            })
            
            return response
            
        except Exception as e:
            logger.error(f"文章生成失敗: {str(e)}")
            raise LLMServiceError(f"文章生成失敗: {str(e)}")
    
    def get_available_providers(self) -> List[str]:
        """獲取可用的提供商列表"""
        return list(self.providers.keys())
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """獲取提供商信息"""
        info = {}
        for name, provider in self.providers.items():
            if isinstance(provider, OpenAIProvider):
                info[name] = {
                    "provider": "OpenAI",
                    "model": provider.model,
                    "available": True
                }
            elif isinstance(provider, GeminiProvider):
                info[name] = {
                    "provider": "Google Gemini",
                    "model": provider.model,
                    "available": True
                }
        return info


# 全域 LLM 服務實例
llm_service = LLMService()