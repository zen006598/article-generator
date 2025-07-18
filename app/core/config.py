"""應用程式配置管理"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定類"""
    
    # OpenAI API 設定
    openai_api_key: str = Field(..., description="OpenAI API 金鑰")
    openai_model: str = Field(default="gpt-3.5-turbo", description="使用的 OpenAI 模型")
    
    # Gemini API 設定
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API 金鑰")
    gemini_model: str = Field(default="gemini-1.5-pro", description="使用的 Gemini 模型")
    
    # LLM 提供商設定
    default_llm_provider: str = Field(default="openai", description="預設 LLM 提供商")
    
    # 應用程式設定
    app_name: str = Field(default="ArticleGenerator", description="應用程式名稱")
    app_version: str = Field(default="0.2.0", description="應用程式版本")
    debug: bool = Field(default=False, description="是否為除錯模式")
    log_level: str = Field(default="INFO", description="日誌級別")
    
    # API 設定
    api_host: str = Field(default="0.0.0.0", description="API 主機位址")
    api_port: int = Field(default=8000, description="API 端口")
    
    # 文章生成設定
    max_article_length: int = Field(default=2000, description="文章最大長度")
    default_language: str = Field(default="zh-TW", description="預設語言")
    generation_timeout: int = Field(default=30, description="生成超時時間（秒）")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全域設定實例
settings = Settings()