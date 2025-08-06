#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 뉴스 업로드 테스트 스크립트
"""

import json
import requests
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"
NEWS_DB_ID = "234a613d25ff81aba93ae4cb8f36c920"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def test_upload_single_news():
    """단일 뉴스 업로드 테스트"""
    
    # 테스트 뉴스 데이터
    test_news = {
        "title": "한진중공업, 해상풍력 발전기 2000억원 사업 수주",
        "content": "한진중공업이 국내 최대 규모의 해상풍력 발전기 제조 사업을 수주했다. 이번 사업은 2025년부터 2027년까지 진행되며, 총 사업 규모는 2000억원에 달한다.",
        "url": "https://www.koreaherald.com/view.php?ud=20250806000001",
        "source": "코리아헤럴드",
        "keyword": "한진중공업",
        "publishedAt": "2025-08-06"
    }
    
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {
            "database_id": NEWS_DB_ID
        },
        "properties": {
            "항목명": {
                "title": [
                    {
                        "text": {
                            "content": test_news['title']
                        }
                    }
                ]
            },
            "데이터 유형": {
                "select": {
                    "name": "뉴스"
                }
            },
            "사업 부문": {
                "select": {
                    "name": "중공업"
                }
            },
            "수치값": {
                "number": 1
            },
            "단위": {
                "select": {
                    "name": "건"
                }
            },
            "기준일": {
                "date": {
                    "start": test_news['publishedAt']
                }
            },
            "수집일시": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "중요도": {
                "select": {
                    "name": "보통"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        print("✅ 테스트 뉴스 업로드 성공!")
        print(f"제목: {test_news['title']}")
        print(f"언론사: {test_news['source']}")
        print(f"키워드: {test_news['keyword']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 업로드 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 한진중공업 뉴스 업로드 테스트 시작...")
    test_upload_single_news() 