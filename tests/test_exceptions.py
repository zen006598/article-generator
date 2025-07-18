"""測試異常處理機制"""

import pytest
from app.core.exceptions import (
    ArticleGeneratorException,
    ConfigurationError,
    LLMServiceError,
    ValidationError,
    InvalidExamTypeError,
    InvalidTopicError,
    InvalidDifficultyScoreError,
    InvalidWordCountError,
    InvalidParagraphCountError,
    OpenAIAPIError,
    GenerationTimeoutError,
    TemplateError,
    ArticleGenerationError,
    APIError
)


class TestArticleGeneratorException:
    """測試基礎異常類"""
    
    def test_basic_exception_creation(self):
        """測試基礎異常創建"""
        exc = ArticleGeneratorException("Test message")
        assert exc.message == "Test message"
        assert exc.error_code == "UNKNOWN_ERROR"
        assert exc.details == {}
        assert exc.user_message == "Test message"
    
    def test_exception_with_all_params(self):
        """測試包含所有參數的異常"""
        details = {"key": "value"}
        exc = ArticleGeneratorException(
            message="Internal message",
            error_code="TEST_ERROR",
            details=details,
            user_message="User friendly message"
        )
        assert exc.message == "Internal message"
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == details
        assert exc.user_message == "User friendly message"


class TestSpecificExceptions:
    """測試特定異常類"""
    
    def test_configuration_error(self):
        """測試配置錯誤異常"""
        exc = ConfigurationError("Config missing")
        assert exc.error_code == "CONFIGURATION_ERROR"
        assert exc.user_message == "系統配置錯誤，請聯絡管理員"
    
    def test_llm_service_error(self):
        """測試 LLM 服務異常"""
        exc = LLMServiceError("API down")
        assert exc.error_code == "LLM_SERVICE_ERROR"
        assert exc.user_message == "AI 服務暫時無法使用，請稍後再試"
    
    def test_validation_error(self):
        """測試驗證錯誤異常"""
        exc = ValidationError("Invalid value", field="exam_type")
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details["field"] == "exam_type"
        assert "Invalid value" in exc.user_message
    
    def test_invalid_exam_type_error(self):
        """測試無效考試類型異常"""
        supported_types = ["TOEIC", "GRE", "IELTS", "SAT"]
        exc = InvalidExamTypeError("INVALID", supported_types)
        assert exc.error_code == "INVALID_EXAM_TYPE"
        assert exc.details["exam_type"] == "INVALID"
        assert exc.details["supported_types"] == supported_types
        assert "INVALID" in exc.user_message
    
    def test_invalid_topic_error(self):
        """測試無效主題異常"""
        supported_topics = ["Business", "Technology"]
        exc = InvalidTopicError("Art", "TOEIC", supported_topics)
        assert exc.error_code == "INVALID_TOPIC"
        assert exc.details["topic"] == "Art"
        assert exc.details["exam_type"] == "TOEIC"
        assert exc.details["supported_topics"] == supported_topics
    
    def test_invalid_difficulty_score_error(self):
        """測試無效難度分數異常"""
        exc = InvalidDifficultyScoreError(1000, "TOEIC", 10, 990)
        assert exc.error_code == "INVALID_DIFFICULTY_SCORE"
        assert exc.details["score"] == 1000
        assert exc.details["exam_type"] == "TOEIC"
        assert exc.details["min_score"] == 10
        assert exc.details["max_score"] == 990
    
    def test_invalid_word_count_error(self):
        """測試無效字數異常"""
        exc = InvalidWordCountError(2000)
        assert exc.error_code == "INVALID_WORD_COUNT"
        assert exc.details["word_count"] == 2000
        assert exc.details["min_count"] == 50
        assert exc.details["max_count"] == 1500
    
    def test_invalid_paragraph_count_error(self):
        """測試無效段落數異常"""
        exc = InvalidParagraphCountError(15)
        assert exc.error_code == "INVALID_PARAGRAPH_COUNT"
        assert exc.details["paragraph_count"] == 15
        assert exc.details["min_count"] == 1
        assert exc.details["max_count"] == 10
    
    def test_openai_api_error(self):
        """測試 OpenAI API 異常"""
        exc = OpenAIAPIError("Rate limit exceeded")
        assert exc.error_code == "OPENAI_API_ERROR"
        assert exc.user_message == "AI 服務暫時無法使用，請稍後再試"
    
    def test_generation_timeout_error(self):
        """測試生成超時異常"""
        exc = GenerationTimeoutError(30)
        assert exc.error_code == "GENERATION_TIMEOUT"
        assert exc.details["timeout_seconds"] == 30
        assert "30" in exc.user_message
    
    def test_template_error(self):
        """測試模板錯誤異常"""
        exc = TemplateError("Template not found", template_name="toeic")
        assert exc.error_code == "TEMPLATE_ERROR"
        assert exc.details["template_name"] == "toeic"
        assert exc.user_message == "模板處理錯誤，請聯絡管理員"
    
    def test_article_generation_error(self):
        """測試文章生成異常"""
        exc = ArticleGenerationError("Generation failed")
        assert exc.error_code == "ARTICLE_GENERATION_ERROR"
        assert exc.user_message == "文章生成失敗，請稍後再試"
    
    def test_api_error(self):
        """測試 API 異常"""
        exc = APIError("Request failed", status_code=422)
        assert exc.error_code == "API_ERROR"
        assert exc.details["status_code"] == 422
        assert exc.user_message == "API 請求處理失敗，請檢查請求參數"