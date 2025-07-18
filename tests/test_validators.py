"""測試驗證器"""

import pytest
from unittest.mock import patch, mock_open, Mock
import json
import os
from app.utils.validators import ExamConfigValidator
from app.core.exceptions import ValidationError, ExamTypeNotSupportedError


class TestExamConfigValidator:
    """測試考試配置驗證器"""
    
    @pytest.fixture
    def mock_exam_config(self):
        """模擬考試配置"""
        return {
            "exam_types": {
                "TOEIC": {
                    "name": "Test of English for International Communication",
                    "description": "Business English proficiency test",
                    "supported_difficulties": ["初級", "中級", "高級"],
                    "validation_rules": {
                        "topic_min_length": 3,
                        "topic_max_length": 100,
                        "word_count_min": 50,
                        "word_count_max": 1500
                    },
                    "default_word_count": {
                        "初級": 150,
                        "中級": 200,
                        "高級": 300
                    },
                    "writing_styles": ["formal", "informal", "business"]
                },
                "GRE": {
                    "name": "Graduate Record Examinations",
                    "description": "Graduate school admission test",
                    "supported_difficulties": ["低", "中", "高"],
                    "validation_rules": {
                        "topic_min_length": 5,
                        "topic_max_length": 150,
                        "word_count_min": 100,
                        "word_count_max": 2000
                    },
                    "default_word_count": {
                        "低": 200,
                        "中": 300,
                        "高": 500
                    },
                    "writing_styles": ["academic", "analytical", "argumentative"]
                }
            }
        }
    
    @pytest.fixture
    def validator_with_config(self, mock_exam_config):
        """創建帶有模擬配置的驗證器"""
        mock_config_content = json.dumps(mock_exam_config)
        with patch("builtins.open", mock_open(read_data=mock_config_content)):
            validator = ExamConfigValidator()
            return validator
    
    def test_validator_initialization(self, validator_with_config):
        """測試驗證器初始化"""
        assert validator_with_config.exam_configs is not None
        assert "exam_types" in validator_with_config.exam_configs
        assert "TOEIC" in validator_with_config.exam_configs["exam_types"]
        assert "GRE" in validator_with_config.exam_configs["exam_types"]
    
    def test_load_exam_configs_file_not_found(self):
        """測試配置文件不存在"""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            with pytest.raises(ValidationError) as exc_info:
                ExamConfigValidator()
            assert "考試配置文件不存在" in str(exc_info.value)
    
    def test_load_exam_configs_json_error(self):
        """測試配置文件格式錯誤"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(ValidationError) as exc_info:
                ExamConfigValidator()
            assert "考試配置文件格式錯誤" in str(exc_info.value)
    
    def test_validate_exam_type_success(self, validator_with_config):
        """測試有效考試類型驗證"""
        assert validator_with_config.validate_exam_type("TOEIC") == True
        assert validator_with_config.validate_exam_type("GRE") == True
    
    def test_validate_exam_type_invalid(self, validator_with_config):
        """測試無效考試類型驗證"""
        with pytest.raises(ExamTypeNotSupportedError) as exc_info:
            validator_with_config.validate_exam_type("INVALID")
        
        assert exc_info.value.error_code == "INVALID_EXAM_TYPE"
        assert "INVALID" in str(exc_info.value)
    
    def test_validate_difficulty_success(self, validator_with_config):
        """測試有效難度驗證"""
        assert validator_with_config.validate_difficulty("TOEIC", "初級") == True
        assert validator_with_config.validate_difficulty("TOEIC", "中級") == True
        assert validator_with_config.validate_difficulty("GRE", "高") == True
    
    def test_validate_difficulty_invalid(self, validator_with_config):
        """測試無效難度驗證"""
        with pytest.raises(ValidationError) as exc_info:
            validator_with_config.validate_difficulty("TOEIC", "超級")
        
        assert "不支援的難度等級" in str(exc_info.value)
        assert "超級" in str(exc_info.value)
    
    def test_validate_topic_success(self, validator_with_config):
        """測試有效主題驗證"""
        assert validator_with_config.validate_topic("TOEIC", "Business Meeting") == True
        assert validator_with_config.validate_topic("GRE", "Philosophy of Science") == True
    
    def test_validate_topic_too_short(self, validator_with_config):
        """測試主題太短"""
        with pytest.raises(ValidationError) as exc_info:
            validator_with_config.validate_topic("TOEIC", "AB")
        
        assert "主題太短" in str(exc_info.value)
        assert "最少需要 3 個字符" in str(exc_info.value)
    
    def test_validate_topic_too_long(self, validator_with_config):
        """測試主題太長"""
        long_topic = "A" * 101
        with pytest.raises(ValidationError) as exc_info:
            validator_with_config.validate_topic("TOEIC", long_topic)
        
        assert "主題太長" in str(exc_info.value)
        assert "最多允許 100 個字符" in str(exc_info.value)
    
    def test_validate_word_count_success(self, validator_with_config):
        """測試有效字數驗證"""
        assert validator_with_config.validate_word_count("TOEIC", 200) == 200
        assert validator_with_config.validate_word_count("GRE", 300) == 300
    
    def test_validate_word_count_none(self, validator_with_config):
        """測試空字數返回預設值"""
        result = validator_with_config.validate_word_count("TOEIC", None)
        assert result == 200  # 中級的預設值
    
    def test_validate_word_count_too_low(self, validator_with_config):
        """測試字數太少"""
        with pytest.raises(ValidationError) as exc_info:
            validator_with_config.validate_word_count("TOEIC", 30)
        
        assert "字數太少" in str(exc_info.value)
        assert "最少需要 50 字" in str(exc_info.value)
    
    def test_validate_word_count_too_high(self, validator_with_config):
        """測試字數太多"""
        with pytest.raises(ValidationError) as exc_info:
            validator_with_config.validate_word_count("TOEIC", 2000)
        
        assert "字數太多" in str(exc_info.value)
        assert "最多允許 1500 字" in str(exc_info.value)
    
    def test_validate_style_success(self, validator_with_config):
        """測試有效風格驗證"""
        assert validator_with_config.validate_style("TOEIC", "formal") == True
        assert validator_with_config.validate_style("GRE", "academic") == True
        assert validator_with_config.validate_style("TOEIC", None) == True  # None 是有效的
    
    def test_validate_style_invalid(self, validator_with_config):
        """測試無效風格驗證"""
        with pytest.raises(ValidationError) as exc_info:
            validator_with_config.validate_style("TOEIC", "casual")
        
        assert "不支援的寫作風格" in str(exc_info.value)
        assert "casual" in str(exc_info.value)
    
    def test_get_exam_info(self, validator_with_config):
        """測試獲取考試資訊"""
        info = validator_with_config.get_exam_info("TOEIC")
        assert info["name"] == "Test of English for International Communication"
        assert "初級" in info["supported_difficulties"]
        assert "formal" in info["writing_styles"]
    
    def test_get_supported_exam_types(self, validator_with_config):
        """測試獲取支援的考試類型"""
        types = validator_with_config.get_supported_exam_types()
        assert "TOEIC" in types
        assert "GRE" in types
        assert len(types) == 2
    
    def test_get_default_word_count(self, validator_with_config):
        """測試獲取預設字數"""
        count = validator_with_config.get_default_word_count("TOEIC", "中級")
        assert count == 200
        
        count = validator_with_config.get_default_word_count("GRE", "高")
        assert count == 500
    
    def test_get_default_word_count_invalid_difficulty(self, validator_with_config):
        """測試無效難度的預設字數"""
        with pytest.raises(ValidationError):
            validator_with_config.get_default_word_count("TOEIC", "超級")
    
    def test_config_path_construction(self):
        """測試配置文件路徑構造"""
        with patch("builtins.open", mock_open(read_data='{"exam_types": {}}')):
            validator = ExamConfigValidator()
            # 檢查路徑是否正確構造
            assert validator.config_path.endswith("exam_configs.json")
            assert "configs" in validator.config_path
    
    def test_edge_cases_whitespace_topic(self, validator_with_config):
        """測試主題空白字符處理"""
        # 測試前後有空白的主題
        assert validator_with_config.validate_topic("TOEIC", "  Business  ") == True
        
        # 測試只有空白的主題
        with pytest.raises(ValidationError):
            validator_with_config.validate_topic("TOEIC", "   ")
    
    def test_case_sensitivity(self, validator_with_config):
        """測試大小寫敏感性"""
        # 考試類型應該是大小寫敏感的
        with pytest.raises(ExamTypeNotSupportedError):
            validator_with_config.validate_exam_type("toeic")
        
        # 難度可能是大小寫敏感的
        with pytest.raises(ValidationError):
            validator_with_config.validate_difficulty("TOEIC", "初级")  # 簡體字