#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
케이스3: 뉴스클리핑 DB 등록 스크립트
목적: 외부 기사를 표준 스키마로 뉴스클리핑 DB에 등록
"""

import os
import sys
import argparse
import json
from datetime import datetime
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def main():
    parser = argparse.ArgumentParser(description='뉴스클리핑 DB 등록')
    parser.add_argument('--db', required=True, help='뉴스클리핑 DB ID')
    parser.add_argument('--title', required=True, help='기사 제목')
    parser.add_argument('--date', required=True, help='기사 날짜 (YYYY-MM-DD)')
    parser.add_argument('--url', required=True, help='원문 URL')
    parser.add_argument('--source', required=True, help='출처 (매체명)')
    parser.add_argument('--category', default='해상풍력발전', help='분야 (기본값: 해상풍력발전)')
    parser.add_argument('--importance', default='보통', help='중요도 (기본값: 보통)')
    parser.add_argument('--out', help='결과 저장 파일')
    args = parser.parse_args()
    
    print("🌍 케이스3: 뉴스클리핑 DB 등록 시작...")
    print(f"제목: {args.title}")
    print(f"날짜: {args.date}")
    print(f"URL: {args.url}")
    print(f"출처: {args.source}")
    print(f"분야: {args.category}")
    print(f"중요도: {args.importance}")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    try:
        n = NotionClient(token)
        
        # 뉴스클리핑 DB에 페이지 생성
        print("\n📝 뉴스클리핑 DB에 페이지 생성 중...")
        
        # 페이지 속성 구성
        properties = {
            "문서 제목": {
                "title": [
                    {
                        "text": {
                            "content": args.title
                        }
                    }
                ]
            },
            "링크": {
                "url": args.url
            },
            "작성일": {
                "date": {
                    "start": args.date
                }
            },
            "태그": {
                "multi_select": [
                    {
                        "name": args.category
                    }
                ]
            },
            "중요도": {
                "select": {
                    "name": args.importance
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
                            "content": f"출처: {args.source}"
                        }
                    }
                ]
            }
        }
        
        # 페이지 생성
        page_data = {
            "parent": {"database_id": args.db},
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
            "title": args.title,
            "url": args.url,
            "source": args.source,
            "category": args.category,
            "importance": args.importance,
            "status": "success",
            "notion_url": f"https://www.notion.so/{page_id.replace('-', '')}"
        }
        
        if args.out:
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
            with open(args.out, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            print(f"📁 결과 저장: {args.out}")
        
        print(f"🌐 Notion 페이지: {result_data['notion_url']}")
        print("✅ 케이스3 완료: 뉴스클리핑 DB 등록 성공")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: 뉴스클리핑 DB 등록 실패: {e}")
        
        # 실패 결과 저장
        if args.out:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "case": "케이스3",
                "operation": "뉴스클리핑 DB 등록",
                "status": "failed",
                "error": str(e),
                "title": args.title,
                "url": args.url
            }
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
            with open(args.out, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        return 1

if __name__ == "__main__":
    exit(main())
