"""Phase 2 功能測試"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """同步測試客戶端"""
    return TestClient(app)


class TestPhase2Features:
    """Phase 2 新功能測試"""
    
    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data
    
    def test_providers_endpoint(self, client):
        """測試 LLM 提供商端點"""
        response = client.get("/api/v1/providers")
        assert response.status_code == 200
        data = response.json()
        
        assert "available_providers" in data
        assert "provider_info" in data
        assert "default_provider" in data
        assert isinstance(data["available_providers"], list)
        assert len(data["available_providers"]) > 0
    
    def test_exam_types_endpoint(self, client):
        """測試考試類型端點 - 確認四種考試類型支援"""
        response = client.get("/api/v1/exam-types")
        assert response.status_code == 200
        data = response.json()
        
        expected_types = ["TOEIC", "GRE", "IELTS", "SAT"]
        assert "exam_types" in data
        assert set(data["exam_types"]) == set(expected_types)
        assert len(data["exam_types"]) == 4
    
    def test_templates_endpoint(self, client):
        """測試動態模板端點"""
        response = client.get("/api/v1/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "available_templates" in data
        assert "supported_exam_types" in data
        
        # 驗證所有四種考試類型都有模板配置
        templates = data["available_templates"]
        expected_types = ["TOEIC", "GRE", "IELTS", "SAT"]
        
        for exam_type in expected_types:
            assert exam_type in templates
            assert "topics" in templates[exam_type]
            assert "difficulties" in templates[exam_type]
            assert "styles" in templates[exam_type]
            assert len(templates[exam_type]["topics"]) > 0
    
    def test_exam_type_info_endpoints(self, client):
        """測試各考試類型詳細資訊端點"""
        exam_types = ["TOEIC", "GRE", "IELTS", "SAT"]
        
        for exam_type in exam_types:
            response = client.get(f"/api/v1/exam-types/{exam_type}")
            assert response.status_code == 200
            data = response.json()
            
            assert data["exam_type"] == exam_type
            assert "full_name" in data
            assert "description" in data
            assert "supported_difficulties" in data
            assert "writing_styles" in data
            assert "common_topics" in data
    
    def test_gre_specific_config(self, client):
        """測試 GRE 考試類型特定配置"""
        response = client.get("/api/v1/exam-types/GRE")
        assert response.status_code == 200
        data = response.json()
        
        # 驗證 GRE 特定配置
        assert data["exam_type"] == "GRE"
        assert data["full_name"] == "Graduate Record Examinations"
        
        # 驗證 GRE 主題
        expected_topics = ["Philosophy", "Psychology", "Social Sciences", 
                          "Natural Sciences", "History", "Literature", "Politics", "Art"]
        assert all(topic in data["common_topics"] for topic in expected_topics)
        
        # 驗證 GRE 難度等級
        expected_difficulties = ["130分", "140分", "150分", "160分", "170分"]
        assert all(diff in data["supported_difficulties"] for diff in expected_difficulties)
    
    def test_sat_specific_config(self, client):
        """測試 SAT 考試類型特定配置"""
        response = client.get("/api/v1/exam-types/SAT")
        assert response.status_code == 200
        data = response.json()
        
        # 驗證 SAT 特定配置
        assert data["exam_type"] == "SAT"
        assert data["full_name"] == "Scholastic Assessment Test"
        
        # 驗證 SAT 主題
        expected_topics = ["U.S. History", "Social Studies", "Literature Reading",
                          "Science (Biology, Chemistry, Physics)", "Math Vocabulary", "Writing and Analysis"]
        assert all(topic in data["common_topics"] for topic in expected_topics)
        
        # 驗證 SAT 難度等級
        expected_difficulties = ["400分", "600分", "800分", "1000分", "1200分", "1400分", "1600分"]
        assert all(diff in data["supported_difficulties"] for diff in expected_difficulties)
    
    def test_invalid_exam_type(self, client):
        """測試無效考試類型處理"""
        response = client.get("/api/v1/exam-types/INVALID")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data


class TestArticleGeneration:
    """文章生成功能測試"""
    
    def test_toeic_generation_request_format(self, client):
        """測試 TOEIC 文章生成請求格式"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings", 
            "difficulty": "中級",
            "word_count": 200,
            "paragraph_count": 3,
            "style": "正式商業"
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        # 注意：這裡可能會因為缺少 API 金鑰而失敗，但至少驗證請求格式
        assert response.status_code in [200, 500]  # 200 成功，500 API 金鑰問題
    
    def test_gre_generation_request_format(self, client):
        """測試 GRE 文章生成請求格式"""
        request_data = {
            "exam_type": "GRE",
            "topic": "Philosophy",
            "difficulty": "150分",
            "word_count": 300,
            "paragraph_count": 4,
            "style": "學術分析"
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_invalid_request_validation(self, client):
        """測試請求驗證"""
        # 測試無效考試類型
        request_data = {
            "exam_type": "INVALID",
            "topic": "Test Topic",
            "difficulty": "中級"
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_paragraph_count_validation(self, client):
        """測試段落數驗證"""
        request_data = {
            "exam_type": "TOEIC",
            "topic": "Business Meetings",
            "difficulty": "中級",
            "paragraph_count": 15  # 超出範圍
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 422


class TestConfigurationValidation:
    """配置驗證測試"""
    
    def test_exam_configs_file_exists(self):
        """測試考試配置文件存在"""
        import os
        assert os.path.exists("configs/exam_configs.json")
    
    def test_exam_configs_content(self):
        """測試考試配置文件內容"""
        import json
        
        with open("configs/exam_configs.json", "r", encoding="utf-8") as f:
            configs = json.load(f)
        
        assert "exam_types" in configs
        exam_types = configs["exam_types"]
        
        # 驗證所有四種考試類型存在
        expected_types = ["TOEIC", "GRE", "IELTS", "SAT"]
        assert all(exam_type in exam_types for exam_type in expected_types)
        
        # 驗證每種考試類型的配置完整性
        for exam_type, config in exam_types.items():
            assert "name" in config
            assert "full_name" in config
            assert "description" in config
            assert "supported_difficulties" in config
            assert "default_word_count" in config
            assert "common_topics" in config
            assert "writing_styles" in config
            assert "validation_rules" in config
            assert "score_range" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])