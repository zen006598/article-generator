"""
多考試類型文章生成器 FastAPI 應用程式入口點
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import ArticleGeneratorException
from app.api.routes.generate import router as generate_router


# 配置日誌
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """應用程式生命週期管理"""
    logger.info(f"啟動 {settings.app_name} v{settings.app_version}")
    
    # 啟動時的初始化邏輯
    try:
        # 驗證必要的配置
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            logger.warning("OpenAI API 金鑰未正確設定，請檢查環境變數")
        
        logger.info("應用程式初始化完成")
        yield
        
    except Exception as e:
        logger.error(f"應用程式啟動失敗: {e}")
        raise
    finally:
        # 關閉時的清理邏輯
        logger.info("應用程式關閉")


# 創建 FastAPI 應用程式實例
app = FastAPI(
    title=settings.app_name,
    description="支援多種考試類型的文章生成器，包括 TOEIC、IELTS、托福等",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全域異常處理器
@app.exception_handler(ArticleGeneratorException)
async def article_generator_exception_handler(request, exc: ArticleGeneratorException):
    """處理自定義異常"""
    logger.error(f"應用程式異常: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "error": "應用程式錯誤",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """處理 HTTP 異常"""
    logger.error(f"HTTP 異常: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP 錯誤",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """處理一般異常"""
    logger.error(f"未預期的錯誤: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "伺服器內部錯誤",
            "message": "發生未預期的錯誤，請稍後再試"
        }
    )


# 註冊路由
app.include_router(generate_router, prefix="/api/v1", tags=["文章生成"])


# 健康檢查端點
@app.get("/", tags=["健康檢查"])
async def root():
    """根端點 - 健康檢查"""
    return {
        "message": f"歡迎使用 {settings.app_name}",
        "version": settings.app_version,
        "status": "正常運行"
    }


@app.get("/health", tags=["健康檢查"])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
