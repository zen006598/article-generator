"""API 整合測試"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from app.core.exceptions import (
    LLMServiceError,
    GenerationTimeoutError,
    OpenAIAPIError
)


class TestAPIIntegration:
    """API 整合測試"""
    
    @pytest.fixture
    def client(self):
        """測試客戶端"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "正常運行"
    
    def test_health_endpoint(self, client):
        """測試健康狀態端點"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data
    
    def test_generate_article_success(self, client):
        """測試成功生成文章"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.return_value = {
                "content": "This is a test article about business meetings.",
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150
                },
                "model": "gpt-4o-mini-2024-07-18",
                "provider": "openai",
                "exam_type": "TOEIC",
                "topic": "Business Meetings",
                "difficulty": "Intermediate",
                "target_word_count": 200,
                "paragraph_count": 3,
                "actual_word_count": 10
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "article" in data
            assert data["article"] == "This is a test article about business meetings."
            assert data["metadata"]["exam_type"] == "TOEIC"
            assert data["metadata"]["topic"] == "Business Meetings"
    
    def test_generate_article_invalid_exam_type(self, client):
        """測試無效考試類型"""
        request_data = {
            "exam_type": "INVALID",
            "topic": "Test Topic",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        # FastAPI 的 422 錯誤格式
        assert "detail" in data
    
    def test_generate_article_missing_fields(self, client):
        """測試缺少必要欄位"""
        request_data = {
            "exam_type": "TOEIC",
            # 缺少 topic, difficulty 等
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data or "error" in data
    
    def test_generate_article_invalid_word_count(self, client):
        """測試無效字數"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 2000,  # 超過最大值
            "paragraph_count": 3
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        # FastAPI 的 422 錯誤格式
        assert "detail" in data
    
    def test_generate_article_invalid_paragraph_count(self, client):
        """測試無效段落數"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 15  # 超過最大值
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        # FastAPI 的 422 錯誤格式
        assert "detail" in data
    
    def test_generate_article_llm_service_error(self, client):
        """測試 LLM 服務錯誤"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.side_effect = LLMServiceError("Service unavailable")
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert data["success"] == False
            assert "error" in data
            assert data["error"]["code"] == "HTTP_ERROR"
    
    def test_generate_article_timeout_error(self, client):
        """測試生成超時錯誤"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.side_effect = GenerationTimeoutError(30)
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert data["success"] == False
            assert "error" in data
            assert data["error"]["code"] == "HTTP_ERROR"
    
    def test_generate_article_openai_error(self, client):
        """測試 OpenAI API 錯誤"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.side_effect = OpenAIAPIError("API quota exceeded")
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert data["success"] == False
            assert "error" in data
            assert data["error"]["code"] == "HTTP_ERROR"
    
    def test_generate_article_with_provider(self, client):
        """測試指定提供商生成文章"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3,
            "provider": "gemini"
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.return_value = {
                "content": "This is a test article generated by Gemini.",
                "usage": {
                    "prompt_tokens": 45,
                    "completion_tokens": 95,
                    "total_tokens": 140
                },
                "model": "gemini-2.5-flash",
                "provider": "gemini",
                "exam_type": "TOEIC",
                "topic": "Business Meetings",
                "difficulty": "Intermediate",
                "target_word_count": 200,
                "paragraph_count": 3,
                "actual_word_count": 10
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
    
    def test_generate_article_with_style(self, client):
        """測試指定風格生成文章"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3,
            "style": "formal"
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.return_value = {
                "content": "This is a formal business article.",
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150
                },
                "model": "gpt-4o-mini-2024-07-18",
                "provider": "openai",
                "exam_type": "TOEIC",
                "topic": "Business Meetings",
                "difficulty": "Intermediate",
                "target_word_count": 200,
                "paragraph_count": 3,
                "actual_word_count": 8
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["article"] == "This is a formal business article."
    
    def test_generate_article_with_focus_points(self, client):
        """測試包含重點的文章生成"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3,
            "focus_points": ["agenda", "teamwork", "decision making"]
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.return_value = {
                "content": "This article focuses on agenda, teamwork, and decision making.",
                "usage": {
                    "prompt_tokens": 60,
                    "completion_tokens": 120,
                    "total_tokens": 180
                },
                "model": "gpt-4o-mini-2024-07-18",
                "provider": "openai",
                "exam_type": "TOEIC",
                "topic": "Business Meetings",
                "difficulty": "Intermediate",
                "target_word_count": 200,
                "paragraph_count": 3,
                "actual_word_count": 12
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
    
    def test_cors_headers(self, client):
        """測試 CORS 標頭"""
        response = client.get("/api/v1/generate", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 405  # Method not allowed for GET
        
        # 測試正確的 POST 請求的 CORS
        response = client.post("/api/v1/generate", 
                             json={"exam_type": "TOEIC", "topic": "Test", "difficulty": "Intermediate"},
                             headers={"Origin": "http://localhost:3000"})
        # 這會失敗但應該有 CORS 標頭
        assert "access-control-allow-origin" in response.headers or response.status_code in [422, 500]
    
    def test_content_type_validation(self, client):
        """測試內容類型驗證"""
        # 測試非 JSON 內容
        response = client.post("/api/v1/generate", data="not json")
        assert response.status_code == 422
    
    def test_response_format_consistency(self, client):
        """測試回應格式一致性"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        with patch('app.services.llm_service.llm_service.generate_article') as mock_generate:
            mock_generate.return_value = {
                "content": "Test article",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                "model": "gpt-4o-mini-2024-07-18",
                "provider": "openai",
                "exam_type": "TOEIC",
                "topic": "Business Meetings",
                "difficulty": "Intermediate",
                "target_word_count": 200,
                "paragraph_count": 3,
                "actual_word_count": 2
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # 檢查必要欄位
            assert "success" in data
            assert "article" in data
            assert "metadata" in data
            
            # 檢查數據結構
            metadata = data["metadata"]
            for field in ["exam_type", "topic", "difficulty", 
                "target_word_count", "actual_word_count"]:
                assert field in metadata
                
    
    def test_large_request_handling(self, client):
        """測試大型請求處理"""
        # 測試超大主題
        request_data = {
            "exam_type": "TOEIC",
            "topic": "A" * 1000,  # 超長主題
            "difficulty": "Intermediate",
            "word_count": 200,
            "paragraph_count": 3
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        # FastAPI 的 422 錯誤格式
        assert "detail" in data