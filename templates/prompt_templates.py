"""Prompt 模板定義"""

from typing import Dict, List, Optional


class PromptTemplates:
    """提示模板類，包含各種考試類型的模板"""
    
    @staticmethod
    def get_toeic_template(
        topic: str,
        difficulty: str,
        word_count: int,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """獲取 TOEIC 考試的提示模板"""
        
        system_message = f"""你是一個專業的 TOEIC 考試文章生成助手。請根據要求生成高質量的商務英語文章。

TOEIC 考試特點：
- 注重商務和職場情境
- 語言實用且專業
- 句法結構清晰
- 詞彙選擇貼近商務環境
- 內容積極正面

文章要求：
- 難度等級：{difficulty}
- 目標字數：約 {word_count} 字
- 語言自然流暢，符合商務溝通標準
- 結構完整，邏輯清晰"""

        if style:
            system_message += f"\n- 寫作風格：{style}"
        
        user_prompt = f"請生成一篇關於「{topic}」的 TOEIC 考試文章。"
        
        if focus_points:
            points_text = "、".join(focus_points)
            user_prompt += f"\n\n請特別關注以下要點：{points_text}"
        
        user_prompt += "\n\n請直接輸出文章內容，不需要標題或額外說明。"
        
        return {
            "system_message": system_message,
            "user_prompt": user_prompt
        }
    
    @staticmethod
    def get_ielts_template(
        topic: str,
        difficulty: str,
        word_count: int,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """獲取 IELTS 考試的提示模板"""
        
        system_message = f"""你是一個專業的 IELTS 考試文章生成助手。請根據要求生成高質量的學術英語文章。

IELTS 考試特點：
- 學術性和正式性
- 論證結構清晰
- 詞彙豐富多樣
- 句式變化豐富
- 觀點表達明確

文章要求：
- 難度等級：{difficulty}
- 目標字數：約 {word_count} 字
- 語言正式學術，符合 IELTS 標準
- 論證邏輯清晰，結構完整"""

        if style:
            system_message += f"\n- 寫作風格：{style}"
        
        user_prompt = f"請生成一篇關於「{topic}」的 IELTS 考試文章。"
        
        if focus_points:
            points_text = "、".join(focus_points)
            user_prompt += f"\n\n請特別關注以下要點：{points_text}"
        
        user_prompt += "\n\n請直接輸出文章內容，不需要標題或額外說明。"
        
        return {
            "system_message": system_message,
            "user_prompt": user_prompt
        }
    
    @staticmethod
    def get_toefl_template(
        topic: str,
        difficulty: str,
        word_count: int,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """獲取 TOEFL 考試的提示模板"""
        
        system_message = f"""你是一個專業的 TOEFL 考試文章生成助手。請根據要求生成高質量的學術英語文章。

TOEFL 考試特點：
- 學術環境導向
- 個人觀點表達
- 邏輯推理清晰
- 例證支撐充分
- 語言準確流暢

文章要求：
- 難度等級：{difficulty}
- 目標字數：約 {word_count} 字
- 語言學術且自然，符合 TOEFL 標準
- 觀點明確，論證有力"""

        if style:
            system_message += f"\n- 寫作風格：{style}"
        
        user_prompt = f"請生成一篇關於「{topic}」的 TOEFL 考試文章。"
        
        if focus_points:
            points_text = "、".join(focus_points)
            user_prompt += f"\n\n請特別關注以下要點：{points_text}"
        
        user_prompt += "\n\n請直接輸出文章內容，不需要標題或額外說明。"
        
        return {
            "system_message": system_message,
            "user_prompt": user_prompt
        }
    
    @staticmethod
    def get_template_by_exam_type(
        exam_type: str,
        topic: str,
        difficulty: str,
        word_count: int,
        style: Optional[str] = None,
        focus_points: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """根據考試類型獲取對應的模板"""
        
        template_map = {
            "TOEIC": PromptTemplates.get_toeic_template,
            "IELTS": PromptTemplates.get_ielts_template,
            "TOEFL": PromptTemplates.get_toefl_template
        }
        
        if exam_type not in template_map:
            raise ValueError(f"不支援的考試類型: {exam_type}")
        
        return template_map[exam_type](
            topic=topic,
            difficulty=difficulty,
            word_count=word_count,
            style=style,
            focus_points=focus_points
        )