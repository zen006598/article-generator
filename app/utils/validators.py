"""參數驗證工具"""

import json
import os
from typing import Dict, List, Optional, Any

from app.core.exceptions import ValidationError, ExamTypeNotSupportedError


class ExamConfigValidator:
    """考試配置驗證器"""
    
    def __init__(self):
        """初始化驗證器，載入考試配置"""
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "configs",
            "exam_configs.json"
        )
        self.exam_configs = self._load_exam_configs()
    
    def _load_exam_configs(self) -> Dict[str, Any]:
        """載入考試配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValidationError(f"考試配置文件不存在: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"考試配置文件格式錯誤: {str(e)}")
    
    def validate_exam_type(self, exam_type: str) -> bool:
        """驗證考試類型是否支援"""
        if exam_type not in self.exam_configs["exam_types"]:
            raise ExamTypeNotSupportedError(
                f"不支援的考試類型: {exam_type}",
                {"supported_types": list(self.exam_configs["exam_types"].keys())}
            )
        return True
    
    def validate_difficulty(self, exam_type: str, difficulty: str) -> bool:
        """驗證難度等級是否有效"""
        self.validate_exam_type(exam_type)
        
        config = self.exam_configs["exam_types"][exam_type]
        supported_difficulties = config["supported_difficulties"]
        
        if difficulty not in supported_difficulties:
            raise ValidationError(
                f"{exam_type} 不支援的難度等級: {difficulty}",
                {
                    "exam_type": exam_type,
                    "provided_difficulty": difficulty,
                    "supported_difficulties": supported_difficulties
                }
            )
        return True
    
    def validate_topic(self, exam_type: str, topic: str) -> bool:
        """驗證主題是否有效"""
        self.validate_exam_type(exam_type)
        
        config = self.exam_configs["exam_types"][exam_type]
        validation_rules = config["validation_rules"]
        
        # 檢查主題長度
        topic_length = len(topic.strip())
        if topic_length < validation_rules["topic_min_length"]:
            raise ValidationError(
                f"主題太短，最少需要 {validation_rules['topic_min_length']} 個字符",
                {"topic": topic, "length": topic_length}
            )
        
        if topic_length > validation_rules["topic_max_length"]:
            raise ValidationError(
                f"主題太長，最多允許 {validation_rules['topic_max_length']} 個字符",
                {"topic": topic, "length": topic_length}
            )
        
        return True
    
    def validate_word_count(self, exam_type: str, word_count: Optional[int]) -> int:
        """驗證並返回字數要求"""
        self.validate_exam_type(exam_type)
        
        config = self.exam_configs["exam_types"][exam_type]
        validation_rules = config["validation_rules"]
        
        if word_count is None:
            # 返回預設字數（使用中級難度的預設值）
            default_word_counts = config["default_word_count"]
            if "中級" in default_word_counts:
                return default_word_counts["中級"]
            else:
                # 如果沒有中級，取第一個值
                return list(default_word_counts.values())[0]
        
        # 驗證字數範圍
        if word_count < validation_rules["word_count_min"]:
            raise ValidationError(
                f"字數太少，最少需要 {validation_rules['word_count_min']} 字",
                {"word_count": word_count}
            )
        
        if word_count > validation_rules["word_count_max"]:
            raise ValidationError(
                f"字數太多，最多允許 {validation_rules['word_count_max']} 字",
                {"word_count": word_count}
            )
        
        return word_count
    
    def validate_style(self, exam_type: str, style: Optional[str]) -> bool:
        """驗證寫作風格是否有效"""
        if style is None:
            return True
        
        self.validate_exam_type(exam_type)
        
        config = self.exam_configs["exam_types"][exam_type]
        supported_styles = config["writing_styles"]
        
        if style not in supported_styles:
            raise ValidationError(
                f"{exam_type} 不支援的寫作風格: {style}",
                {
                    "exam_type": exam_type,
                    "provided_style": style,
                    "supported_styles": supported_styles
                }
            )
        
        return True
    
    def get_exam_info(self, exam_type: str) -> Dict[str, Any]:
        """獲取考試類型的詳細資訊"""
        self.validate_exam_type(exam_type)
        return self.exam_configs["exam_types"][exam_type]
    
    def get_supported_exam_types(self) -> List[str]:
        """獲取所有支援的考試類型"""
        return list(self.exam_configs["exam_types"].keys())
    
    def get_default_word_count(self, exam_type: str, difficulty: str) -> int:
        """獲取預設字數"""
        self.validate_exam_type(exam_type)
        self.validate_difficulty(exam_type, difficulty)
        
        config = self.exam_configs["exam_types"][exam_type]
        return config["default_word_count"][difficulty]


# 全域驗證器實例
validator = ExamConfigValidator()