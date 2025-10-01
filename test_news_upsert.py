#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
케이스3: 뉴스클리핑 DB 등록 테스트
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.utils.notion_api import NotionClient

def main():
    print("🌍 케이스3: 뉴스클리핑 DB 등록 테스트 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    db_id = os.environ.get("TARGET_DATABASE_ID")
    
    if not token or not db_id:
        print("ERROR: NOTION_TOKEN 또는 TARGET_DATABASE_ID가 설정되지 않았습니다.")
        return 1
    
    try:
        n = NotionClient(token)
        
        # 뉴스클리핑 DB에 페이지 생성
        print("📝 뉴스클리핑 DB에 페이지 생성 중...")
        
        # 페이지 속성 구성
        properties = {
            "문서 제목": {
                "title": [
                    {
                        "text": {
                            "content": "[파일럿] 해상풍력 사고 동향 기사 테스트 등록"
                        }
                    }
                ]
            },
            "링크": {
                "url": "https://example.com/offshore-wind-accident"
            },
            "작성일": {
                "date": {
                    "start": "2025-10-01"
                }
            },
            "태그": {
                "multi_select": [
                    {
                        "name": "해상풍력발전"
                    }
                ]
            },
            "중요도": {
                "select": {
                    "name": "보통"
                }
            },
            "문서 성격": {
                "select": {
                    "name": "뉴스클리핑"
                }
            },
            "핵심내용": {
                "rich_text": [
                    {
                        "text": {
                            "content": "출처: 에너지데일리"
                        }
                    }
                ]
            }
        }
        
        # 페이지 생성
        page_data = {
            "parent": {"database_id": db_id},
            "properties": properties
        }
        
        # Notion API로 페이지 생성
        result = n._req("POST", "/pages", json=page_data)
        
        page_id = result["id"]
        print(f"✅ 페이지 생성 완료: {page_id}")
        
        # 결과 저장
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "case": "케이스3",
            "operation": "뉴스클리핑 DB 등록",
            "page_id": page_id,
            "title": "[파일럿] 해상풍력 사고 동향 기사 테스트 등록",
            "url": "https://example.com/offshore-wind-accident",
            "source": "에너지데일리",
            "category": "해상풍력발전",
            "importance": "보통",
            "status": "success",
            "notion_url": f"https://www.notion.so/{page_id.replace('-', '')}"
        }
        
        # 결과 저장
        os.makedirs("logs", exist_ok=True)
        with open("logs/news_upsert_1.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 결과 저장: logs/news_upsert_1.json")
        print(f"🌐 Notion 페이지: {result_data['notion_url']}")
        print("✅ 케이스3 완료: 뉴스클리핑 DB 등록 성공")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: 뉴스클리핑 DB 등록 실패: {e}")
        
        # 실패 결과 저장
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "case": "케이스3",
            "operation": "뉴스클리핑 DB 등록",
            "status": "failed",
            "error": str(e),
            "title": "[파일럿] 해상풍력 사고 동향 기사 테스트 등록"
        }
        
        os.makedirs("logs", exist_ok=True)
        with open("logs/news_upsert_1.json", "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        return 1

if __name__ == "__main__":
    exit(main())
