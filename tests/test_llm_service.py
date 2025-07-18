"""測試 LLM 服務"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from app.services.llm_service import LLMService, OpenAIProvider, GeminiProvider
from app.core.exceptions import (
    LLMServiceError,
    OpenAIAPIError,
    GenerationTimeoutError
)


class TestOpenAIProvider:
    """測試 OpenAI 提供商"""
    
    def test_provider_initialization(self):
        """測試提供商初始化"""
        provider = OpenAIProvider("test-key", "gpt-4")
        assert provider.model == "gpt-4"
        assert provider.client is not None
    
    @pytest.mark.asyncio
    async def test_successful_completion(self):
        """測試成功的文本生成"""
        provider = OpenAIProvider("test-key")
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test article content"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 60
        
        with patch.object(provider.client.chat.completions, 'create', 
                         new_callable=AsyncMock, return_value=mock_response) as mock_create:
            result = await provider.generate_completion(
                messages=[{"role": "user", "content": "Generate article"}],
                max_tokens=100,
                temperature=0.7
            )
            
            assert result["content"] == "Test article content"
            assert result["usage"]["prompt_tokens"] == 10
            assert result["usage"]["completion_tokens"] == 50
            assert result["usage"]["total_tokens"] == 60
            assert result["model"] == "gpt-4o-mini-2024-07-18"
            assert result["provider"] == "openai"
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """測試 API 錯誤處理"""
        provider = OpenAIProvider("test-key")
        
        with patch.object(provider.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(OpenAIAPIError) as exc_info:
                await provider.generate_completion(
                    messages=[{"role": "user", "content": "Generate article"}]
                )
            
            assert "API Error" in str(exc_info.value)
            assert exc_info.value.error_code == "OPENAI_API_ERROR"


class TestGeminiProvider:
    """測試 Gemini 提供商"""
    
    def test_provider_initialization(self):
        """測試 Gemini 提供商初始化"""
        provider = GeminiProvider("test-key", "gemini-pro")
        assert provider.model == "gemini-pro"
        assert provider.client is not None
    
    @pytest.mark.asyncio
    async def test_successful_completion(self):
        """測試成功的文本生成"""
        provider = GeminiProvider("test-key")
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test article content"
        mock_response.usage.prompt_tokens = 15
        mock_response.usage.completion_tokens = 45
        mock_response.usage.total_tokens = 60
        
        with patch.object(provider.client.chat.completions, 'create', 
                         new_callable=AsyncMock, return_value=mock_response) as mock_create:
            result = await provider.generate_completion(
                messages=[{"role": "user", "content": "Generate article"}],
                max_tokens=100,
                temperature=0.7
            )
            
            assert result["content"] == "Test article content"
            assert result["usage"]["prompt_tokens"] == 15
            assert result["usage"]["completion_tokens"] == 45
            assert result["usage"]["total_tokens"] == 60
            assert result["model"] == "gemini-2.5-flash"
            assert result["provider"] == "gemini"
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """測試 API 錯誤處理"""
        provider = GeminiProvider("test-key")
        
        with patch.object(provider.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(LLMServiceError) as exc_info:
                await provider.generate_completion(
                    messages=[{"role": "user", "content": "Generate article"}]
                )
            
            assert "API Error" in str(exc_info.value)
            assert exc_info.value.error_code == "LLM_SERVICE_ERROR"


class TestLLMService:
    """測試 LLM 服務"""
    
    def test_service_initialization(self):
        """測試服務初始化"""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model = "gpt-4"
            
            service = LLMService()
            assert service.timeout == 30
            assert service.default_provider == "openai"
            assert len(service.providers) >= 1
    
    def test_no_providers_available(self):
        """測試沒有可用提供商時的處理"""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = ""
            mock_settings.gemini_api_key = ""
            
            service = LLMService()
            assert len(service.providers) == 0
    
    @pytest.mark.asyncio
    async def test_generate_completion_success(self):
        """測試成功的文本生成"""
        mock_provider = Mock()
        mock_provider.generate_completion = AsyncMock(return_value={
            "content": "Test article",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "model": "gpt-4",
            "provider": "openai"
        })
        
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            service.providers = {"openai": mock_provider}
            
            result = await service.generate_completion(
                prompt="Generate article",
                max_tokens=100,
                temperature=0.7
            )
            
            assert result["content"] == "Test article"
            assert result["usage"]["total_tokens"] == 30
            mock_provider.generate_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_completion_no_providers(self):
        """測試沒有可用提供商時的錯誤處理"""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            service.providers = {}
            
            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate_completion(prompt="Generate article")
            
            assert "沒有可用的 LLM 提供商" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_completion_timeout(self):
        """測試請求超時處理"""
        mock_provider = Mock()
        mock_provider.generate_completion = AsyncMock(side_effect=asyncio.TimeoutError())
        
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 1
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            service.providers = {"openai": mock_provider}
            
            with pytest.raises(GenerationTimeoutError) as exc_info:
                await service.generate_completion(prompt="Generate article")
            
            assert exc_info.value.error_code == "GENERATION_TIMEOUT"
    
    @pytest.mark.asyncio
    async def test_generate_completion_provider_not_available(self):
        """測試指定的提供商不可用"""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            service.providers = {"openai": Mock()}
            
            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate_completion(
                    prompt="Generate article",
                    provider="gemini"
                )
            
            assert "提供商 'gemini' 不可用" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_completion_empty_response(self):
        """測試空回應處理"""
        mock_provider = Mock()
        mock_provider.generate_completion = AsyncMock(return_value={
            "content": "",
            "usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
            "model": "gpt-4",
            "provider": "openai"
        })
        
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            service.providers = {"openai": mock_provider}
            
            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate_completion(prompt="Generate article")
            
            assert "返回空內容" in str(exc_info.value)
    
    def test_get_available_providers(self):
        """測試獲取可用提供商"""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            service.providers = {"openai": Mock(), "gemini": Mock()}
            
            providers = service.get_available_providers()
            assert "openai" in providers
            assert "gemini" in providers
    
    def test_get_provider_info(self):
        """測試獲取提供商資訊"""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.generation_timeout = 30
            mock_settings.default_llm_provider = "openai"
            
            service = LLMService()
            
            openai_provider = OpenAIProvider("test-key", "gpt-4")
            gemini_provider = GeminiProvider("test-key", "gemini-pro")
            
            service.providers = {
                "openai": openai_provider,
                "gemini": gemini_provider
            }
            
            info = service.get_provider_info()
            
            assert "openai" in info
            assert "gemini" in info
            assert info["openai"]["provider"] == "OpenAI"
            assert info["openai"]["model"] == "gpt-4"
            assert info["gemini"]["provider"] == "Google Gemini"
            assert info["gemini"]["model"] == "gemini-pro"