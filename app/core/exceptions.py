"""自定義異常類定義"""

from typing import Any, Dict, Optional


class ArticleGeneratorException(Exception):
    """基礎異常類"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(self.message)


class ConfigurationError(ArticleGeneratorException):
    """配置錯誤異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            user_message="系統配置錯誤，請聯絡管理員"
        )


class LLMServiceError(ArticleGeneratorException):
    """LLM 服務異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="LLM_SERVICE_ERROR",
            details=details,
            user_message="AI 服務暫時無法使用，請稍後再試"
        )


class ValidationError(ArticleGeneratorException):
    """驗證錯誤異常"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        error_code = "VALIDATION_ERROR"
        user_message = f"輸入參數錯誤: {message}"
        
        if field:
            details = details or {}
            details["field"] = field
            
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            user_message=user_message
        )


class InvalidExamTypeError(ArticleGeneratorException):
    """不支援的考試類型異常"""
    
    def __init__(self, exam_type: str, supported_types: list):
        message = f"不支援的考試類型: {exam_type}"
        super().__init__(
            message=message,
            error_code="INVALID_EXAM_TYPE",
            details={"exam_type": exam_type, "supported_types": supported_types},
            user_message=f"不支援的考試類型 '{exam_type}'，支援的類型: {', '.join(supported_types)}"
        )


class InvalidTopicError(ArticleGeneratorException):
    """不支援的主題異常"""
    
    def __init__(self, topic: str, exam_type: str, supported_topics: list):
        message = f"考試類型 {exam_type} 不支援主題: {topic}"
        super().__init__(
            message=message,
            error_code="INVALID_TOPIC",
            details={"topic": topic, "exam_type": exam_type, "supported_topics": supported_topics},
            user_message=f"'{exam_type}' 不支援主題 '{topic}'，支援的主題: {', '.join(supported_topics)}"
        )


class InvalidDifficultyScoreError(ArticleGeneratorException):
    """難度分數錯誤異常"""
    
    def __init__(self, score: float, exam_type: str, min_score: float, max_score: float):
        message = f"難度分數 {score} 超出 {exam_type} 範圍 ({min_score}-{max_score})"
        super().__init__(
            message=message,
            error_code="INVALID_DIFFICULTY_SCORE",
            details={"score": score, "exam_type": exam_type, "min_score": min_score, "max_score": max_score},
            user_message=f"難度分數 {score} 超出範圍，{exam_type} 分數範圍為 {min_score}-{max_score}"
        )


class InvalidWordCountError(ArticleGeneratorException):
    """字數錯誤異常"""
    
    def __init__(self, word_count: int, min_count: int = 50, max_count: int = 1500):
        message = f"字數 {word_count} 超出範圍 ({min_count}-{max_count})"
        super().__init__(
            message=message,
            error_code="INVALID_WORD_COUNT",
            details={"word_count": word_count, "min_count": min_count, "max_count": max_count},
            user_message=f"字數 {word_count} 超出範圍，應在 {min_count}-{max_count} 字之間"
        )


class InvalidParagraphCountError(ArticleGeneratorException):
    """段落數錯誤異常"""
    
    def __init__(self, paragraph_count: int, min_count: int = 1, max_count: int = 10):
        message = f"段落數 {paragraph_count} 超出範圍 ({min_count}-{max_count})"
        super().__init__(
            message=message,
            error_code="INVALID_PARAGRAPH_COUNT",
            details={"paragraph_count": paragraph_count, "min_count": min_count, "max_count": max_count},
            user_message=f"段落數 {paragraph_count} 超出範圍，應在 {min_count}-{max_count} 段之間"
        )


class OpenAIAPIError(ArticleGeneratorException):
    """OpenAI API 錯誤異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="OPENAI_API_ERROR",
            details=details,
            user_message="AI 服務暫時無法使用，請稍後再試"
        )


class GenerationTimeoutError(ArticleGeneratorException):
    """生成超時異常"""
    
    def __init__(self, timeout_seconds: int):
        message = f"文章生成超時 ({timeout_seconds} 秒)"
        super().__init__(
            message=message,
            error_code="GENERATION_TIMEOUT",
            details={"timeout_seconds": timeout_seconds},
            user_message=f"文章生成超時，請稍後再試 (超時時間: {timeout_seconds} 秒)"
        )


class TemplateError(ArticleGeneratorException):
    """模板處理錯誤異常"""
    
    def __init__(self, message: str, template_name: str = None, details: Optional[Dict[str, Any]] = None):
        template_details = details or {}
        if template_name:
            template_details["template_name"] = template_name
            
        super().__init__(
            message=message,
            error_code="TEMPLATE_ERROR",
            details=template_details,
            user_message="模板處理錯誤，請聯絡管理員"
        )


class ArticleGenerationError(ArticleGeneratorException):
    """文章生成異常"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ARTICLE_GENERATION_ERROR",
            details=details,
            user_message="文章生成失敗，請稍後再試"
        )


class APIError(ArticleGeneratorException):
    """API 錯誤異常"""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        api_details = details or {}
        api_details["status_code"] = status_code
        
        super().__init__(
            message=message,
            error_code="API_ERROR",
            details=api_details,
            user_message="API 請求處理失敗，請檢查請求參數"
        )


# 向後兼容
ExamTypeNotSupportedError = InvalidExamTypeError