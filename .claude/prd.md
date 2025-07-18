# 多考試類型文章生成器 PRD (Product Requirements Document)

## 產品概述
基於多 LLM 提供商的多考試類型閱讀文章自動生成系統，支援 OpenAI GPT 和 Google Gemini 模型，並支援 TOEIC、GRE、IELTS、SAT 等多種考試標準，幫助用戶快速生成符合特定考試要求和主題的閱讀文章。

## 技術架構
- **後端框架**: FastAPI
- **AI 服務**: 
  - OpenAI GPT API (gpt-3.5-turbo, gpt-4, gpt-4-turbo)
  - Google Gemini API (gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro) - 透過 OpenAI SDK 統一調用
- **統一介面**: OpenAI SDK 作為統一的 LLM 調用介面
- **部署環境**: 支援容器化部署

## API 規格

### POST /generate
生成指定考試類型的閱讀文章

#### 請求參數
```json
{
  "exam_type": "string",       // 考試類型: "TOEIC", "GRE", "IELTS", "SAT"
  "topic": "string",           // 文章主題，根據考試類型選擇，見考試範圍定義
  "word_count": "integer",     // 字數，範圍: 50-1500，預設: 150
  "difficulty_score": "number", // 難度分數，依考試類型而異，見考試範圍定義
  "paragraph_count": "integer", // 段落數，範圍: 1-10，預設: 3
  "llm_provider": "string",    // LLM 提供商: "openai", "gemini"，預設: "openai"
  "model": "string"            // 模型名稱，見支援模型列表，預設: "gpt-3.5-turbo"
}
```

#### 支援的 LLM 模型
```json
[
  {
    "exam_name": "TOEIC",
    "topics": [
      "Business Correspondence",
      "Meetings", 
      "Telephone Ordering",
      "Office Work",
      "Travel",
      "Daily Life"
    ],
    "score_range": {
      "min": 10,
      "max": 990,
      "step": 5
    }
  },
  {
    "exam_name": "GRE", 
    "topics": [
      "Philosophy",
      "Psychology",
      "Social Sciences", 
      "Natural Sciences",
      "History",
      "Literature",
      "Politics",
      "Art"
    ],
    "score_range": {
      "min": 130,
      "max": 170,
      "step": 1
    }
  },
  {
    "exam_name": "IELTS",
    "topics": [
      "Daily Life",
      "Workplace", 
      "Education and Learning",
      "Social Issues",
      "Environment and Technology",
      "Culture and Arts",
      "Health and Medicine"
    ],
    "score_range": {
      "min": 0,
      "max": 9,
      "step": 0.5
    }
  },
  {
    "exam_name": "SAT",
    "topics": [
      "U.S. History",
      "Social Studies",
      "Literature Reading", 
      "Science (Biology, Chemistry, Physics)",
      "Math Vocabulary",
      "Writing and Analysis"
    ],
    "score_range": {
      "min": 400,
      "max": 1600,
      "step": 10
    }
  }
]
```

#### 回應格式
```json
{
  "success": true,
  "data": {
    "article": "string",         // 生成的文章內容
    "word_count": "integer",     // 實際字數
    "exam_type": "string",       // 考試類型
    "topic": "string",           // 文章主題
    "difficulty_score": "number", // 難度分數
    "paragraphs": "integer",     // 段落數
    "llm_provider": "string",    // 使用的 LLM 提供商
    "model": "string",           // 使用的模型名稱
    "generation_time": "number", // 生成時間（秒）
    "token_usage": {             // Token 使用統計
      "prompt_tokens": "integer",
      "completion_tokens": "integer", 
      "total_tokens": "integer"
    },
    "generated_at": "datetime"   // 生成時間
  },
  "message": "string"
}
```

## 動態 Prompt 模板系統

### 基礎模板
```
Generate a {{exam_type}} reading passage about {{topic}} of approximately {{word_count}} words, 
targeted at a difficulty level equivalent to a {{exam_type}} score of {{difficulty_score}}.

Structure the text into {{paragraph_count}} clear paragraphs with content appropriate for {{exam_type}} test format.

{{exam_specific_instructions}}

The article should include:
{{exam_specific_requirements}}
```

### 考試特定指令

#### TOEIC 模板
```
exam_specific_instructions: "Use vocabulary and grammar patterns typical of TOEIC Part VII. Focus on realistic workplace and daily life scenarios. Avoid overly specialized technical terms and ensure the content is appropriate for business English learners."

exam_specific_requirements:
- Clear topic sentences for each paragraph
- Practical business vocabulary appropriate for the topic
- Realistic scenarios related to {{topic}}
- Appropriate sentence complexity for the target TOEIC level
- Professional tone suitable for workplace contexts
```

#### GRE 模板  
```
exam_specific_instructions: "Use sophisticated vocabulary and complex sentence structures typical of GRE reading comprehension. Present academic arguments with logical reasoning and evidence-based conclusions."

exam_specific_requirements:
- Academic vocabulary and terminology relevant to {{topic}}
- Complex sentence structures with varied syntax
- Logical argument development with supporting evidence
- Analytical depth appropriate for graduate-level study
- Formal academic tone and style
```

#### IELTS 模板
```
exam_specific_instructions: "Use clear, well-structured prose appropriate for IELTS Academic Reading. Balance accessibility with intellectual rigor, covering {{topic}} in a comprehensive yet approachable manner."

exam_specific_requirements:
- Clear main ideas with supporting details
- Varied vocabulary relevant to {{topic}}
- Logical paragraph structure with smooth transitions
- Balanced presentation of different perspectives
- International English style avoiding regional idioms
```

#### SAT 模板
```
exam_specific_instructions: "Create content suitable for SAT Reading passages, focusing on {{topic}} with attention to analytical reasoning and evidence-based thinking expected of college-bound students."

exam_specific_requirements:
- College-level vocabulary in context
- Clear argumentative or informational structure
- Evidence-based reasoning and examples
- Appropriate complexity for high school students
- Formal but accessible academic tone
```

## 多 LLM 提供商支援

### LLM 統一介面設計
系統採用 OpenAI SDK 作為統一的 LLM 調用介面，透過配置不同的 base_url 和 API 金鑰來支援多個 LLM 提供商。

#### Gemini API 透過 OpenAI SDK 調用
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "object"
  }
}
```

### 錯誤代碼
- `INVALID_EXAM_TYPE`: 不支援的考試類型
- `INVALID_TOPIC`: 該考試類型不支援此主題
- `INVALID_DIFFICULTY_SCORE`: 難度分數超出考試範圍
- `INVALID_WORD_COUNT`: 字數超出範圍 (50-1500)
- `INVALID_PARAGRAPH_COUNT`: 段落數超出範圍 (1-10)
- `OPENAI_API_ERROR`: OpenAI API 呼叫失敗
- `GENERATION_TIMEOUT`: 生成超時
- `TEMPLATE_ERROR`: 模板處理錯誤

## 考試配置管理

### 配置文件結構
```json
{
  "exam_configs": {
    "TOEIC": {
      "name": "Test of English for International Communication",
      "description": "Business English proficiency test",
      "topics": [...],
      "score_range": {...},
      "template_key": "toeic",
      "max_word_count": 1500,
      "recommended_paragraphs": 3
    },
    "GRE": {
      "name": "Graduate Record Examinations", 
      "description": "Graduate school admission test",
      "topics": [...],
      "score_range": {...},
      "template_key": "gre",
      "max_word_count": 1500,
      "recommended_paragraphs": 4
    }
  }
}
```

## 實作優先順序

### Phase 1: 基礎架構 (Week 1-2)
- FastAPI 基礎設定
- OpenAI API 整合
- 基本文章生成功能
- TOEIC 考試類型實作

### Phase 2: 多考試支援 (Week 3-4)
- GRE、IELTS、SAT 考試類型
- 動態模板系統
- 考試配置管理 API
- 參數驗證機制

### Phase 3: 品質與效能 (Week 5-6)
- 錯誤處理完善
- 單元測試與整合測試
- 效能優化
- 監控與日誌系統

## 測試需求

### 單元測試
- 各考試類型模板生成
- 參數驗證邏輯
- 錯誤處理機制
- 覆蓋率 > 85%

## 部署配置

### 環境變數
```bash
# OpenAI
OPENAI_API_KEY=…
OPENAI_MODEL=gpt-3.5-turbo

# Gemini
GEMINI_API_KEY=…
GEMINI_MODEL=gemini-1.5-pro

# 通用
LLM_PROVIDER=openai  # or "gemini"
MAX_CONCURRENT_REQUESTS=100
CACHE_TIMEOUT_MINUTES=60
LOG_LEVEL=INFO
```

### Docker 配置
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 監控指標
- API 回應時間
- 成功率 / 錯誤率
- OpenAI API 使用量
- 各考試類型使用頻率
- 資源使用狀況 (CPU, 記憶體)
