"""動態模板服務"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.core.exceptions import ValidationError


class TemplateService:
    """動態模板管理服務"""
    
    def __init__(self):
        """初始化模板服務"""
        self.config_path = Path("configs/exam_configs.json")
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
    
    def build_dynamic_template(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int,
        paragraph_count: int = 3,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """建立動態模板"""
        
        # 驗證考試類型
        if exam_type not in self.exam_configs["exam_types"]:
            raise ValidationError(f"不支援的考試類型: {exam_type}")
        
        exam_config = self.exam_configs["exam_types"][exam_type]
        
        # 建立基礎模板
        base_template = self._get_base_template(exam_type, topic, word_count, paragraph_count)
        
        # 添加考試特定指令
        exam_specific = self._get_exam_specific_instructions(exam_type, exam_config)
        
        # 添加考試特定要求
        exam_requirements = self._get_exam_specific_requirements(exam_type, topic)
        
        # 組合最終模板
        system_message = base_template["system"].format(
            exam_type=exam_type,
            topic=topic,
            word_count=word_count,
            paragraph_count=paragraph_count,
            difficulty=difficulty,
            exam_specific_instructions=exam_specific,
            exam_specific_requirements=exam_requirements
        )
        
        user_prompt = base_template["user"].format(
            exam_type=exam_type,
            topic=topic
        )
        
        # 添加可選參數
        if style:
            system_message += f"\n- 寫作風格：{style}"
        
        if focus_points:
            points_text = "、".join(focus_points)
            user_prompt += f"\n\n請特別關注以下要點：{points_text}"
        
        user_prompt += "\n\n請直接輸出文章內容，不需要標題或額外說明。"
        
        return {
            "system_message": system_message,
            "user_prompt": user_prompt
        }
    
    def _get_base_template(self, exam_type: str, topic: str, word_count: int, paragraph_count: int) -> Dict[str, str]:
        """獲取基礎模板"""
        return {
            "system": """Generate a {exam_type} reading passage about {topic} of approximately {word_count} words, 
targeted at a difficulty level of {difficulty}.

Structure the text into {paragraph_count} clear paragraphs with content appropriate for {exam_type} test format.

{exam_specific_instructions}

The article should include:
{exam_specific_requirements}""",
            "user": "請生成一篇關於「{topic}」的 {exam_type} 考試文章。"
        }
    
    def _get_exam_specific_instructions(self, exam_type: str, exam_config: Dict[str, Any]) -> str:
        """獲取考試特定指令"""
        instructions = {
            "TOEIC": "Use vocabulary and grammar patterns typical of TOEIC Part VII. Focus on realistic workplace and daily life scenarios. Avoid overly specialized technical terms and ensure the content is appropriate for business English learners.",
            "GRE": "Use sophisticated vocabulary and complex sentence structures typical of GRE reading comprehension. Present academic arguments with logical reasoning and evidence-based conclusions.",
            "IELTS": "Use clear, well-structured prose appropriate for IELTS Academic Reading. Balance accessibility with intellectual rigor, covering the topic in a comprehensive yet approachable manner.",
            "SAT": "Create content suitable for SAT Reading passages, focusing on analytical reasoning and evidence-based thinking expected of college-bound students."
        }
        return instructions.get(exam_type, "")
    
    def _get_exam_specific_requirements(self, exam_type: str, topic: str) -> str:
        """獲取考試特定要求"""
        requirements = {
            "TOEIC": f"""- Clear topic sentences for each paragraph
- Practical business vocabulary appropriate for the topic
- Realistic scenarios related to {topic}
- Appropriate sentence complexity for the target TOEIC level
- Professional tone suitable for workplace contexts""",
            "GRE": f"""- Academic vocabulary and terminology relevant to {topic}
- Complex sentence structures with varied syntax
- Logical argument development with supporting evidence
- Analytical depth appropriate for graduate-level study
- Formal academic tone and style""",
            "IELTS": f"""- Clear main ideas with supporting details
- Varied vocabulary relevant to {topic}
- Logical paragraph structure with smooth transitions
- Balanced presentation of different perspectives
- International English style avoiding regional idioms""",
            "SAT": f"""- College-level vocabulary in context
- Clear argumentative or informational structure
- Evidence-based reasoning and examples
- Appropriate complexity for high school students
- Formal but accessible academic tone"""
        }
        return requirements.get(exam_type, "")
    
    def get_available_templates(self) -> Dict[str, List[str]]:
        """獲取可用的模板類型"""
        result = {}
        for exam_type, config in self.exam_configs["exam_types"].items():
            result[exam_type] = {
                "topics": config["common_topics"],
                "difficulties": config["supported_difficulties"],
                "styles": config["writing_styles"]
            }
        return result
    
    def validate_template_parameters(
        self,
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int,
        paragraph_count: int = 3
    ) -> bool:
        """驗證模板參數"""
        # 驗證考試類型
        if exam_type not in self.exam_configs["exam_types"]:
            raise ValidationError(f"不支援的考試類型: {exam_type}")
        
        exam_config = self.exam_configs["exam_types"][exam_type]
        
        # 驗證難度
        if difficulty not in exam_config["supported_difficulties"]:
            raise ValidationError(f"{exam_type} 不支援的難度等級: {difficulty}")
        
        # 驗證字數
        validation_rules = exam_config["validation_rules"]
        if word_count < validation_rules["word_count_min"] or word_count > validation_rules["word_count_max"]:
            raise ValidationError(f"字數必須在 {validation_rules['word_count_min']}-{validation_rules['word_count_max']} 之間")
        
        # 驗證段落數
        if paragraph_count < 1 or paragraph_count > 10:
            raise ValidationError("段落數必須在 1-10 之間")
        
        return True


# 全域模板服務實例
template_service = TemplateService()