#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 /generate API 端點
"""

import requests
import json

def test_generate_api():
    """測試文章生成 API"""
    
    # API 端點
    url = "http://localhost:8000/api/v1/generate"
    
    # 測試數據
    test_data = {
        "exam_type": "TOEIC",
        "topic": "商業會議",
        "difficulty": "中級"
    }
    
    # 發送請求
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        print("測試 /generate API 端點...")
        print(f"請求數據: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            url, 
            json=test_data, 
            headers=headers,
            timeout=30
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✅ API 測試成功!")
        else:
            print("❌ API 測試失敗!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求失敗: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失敗: {e}")
        print(f"原始回應: {response.text}")

if __name__ == "__main__":
    test_generate_api()