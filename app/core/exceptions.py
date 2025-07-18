"""自定義異常類定義"""

from typing import Any, Dict, Optional


class ArticleGeneratorException(Exception):
    """基礎異常類"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(ArticleGeneratorException):
    """配置錯誤異常"""
    pass


class LLMServiceError(ArticleGeneratorException):
    """LLM 服務異常"""
    pass


class ValidationError(ArticleGeneratorException):
    """驗證錯誤異常"""
    pass


class ExamTypeNotSupportedError(ArticleGeneratorException):
    """不支援的考試類型異常"""
    pass


class ArticleGenerationError(ArticleGeneratorException):
    """文章生成異常"""
    pass


class APIError(ArticleGeneratorException):
    """API 錯誤異常"""
    pass