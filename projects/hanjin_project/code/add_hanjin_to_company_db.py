#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회사 정보 마스터 DB에 한진중공업 항목 추가 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업 프로젝트 Phase 0 - 회사 정보 마스터 DB에 한진중공업 항목 추가
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"  # 검증된 노션 API 토큰
COMPANY_DB_ID = "235a613d-25ff-817b-a072-e801efbfc91e"  # 회사 정보 마스터 DB (하이픈 포함)

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_hanjin_to_company_db():
    """
    회사 정보 마스터 DB에 한진중공업 항목 추가
    """
    print("🎯 회사 정보 마스터 DB에 한진중공업 항목 추가 중...")
    
    url = f"https://api.notion.com/v1/pages"
    
    # 한진중공업 정보
    payload = {
        "parent": {
            "database_id": COMPANY_DB_ID
        },
        "properties": {
            "회사명": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 (HJ중공업)"
                        }
                    }
                ]
            },
            "대표이사": {
                "rich_text": [
                    {
                        "text": {
                            "content": "조원국"
                        }
                    }
                ]
            },
            "매출규모": {
                "select": {
                    "name": "1조 이상"
                }
            },
            "본사위치": {
                "rich_text": [
                    {
                        "text": {
                            "content": "부산광역시 영도구 봉래동"
                        }
                    }
                ]
            },
            "상장여부": {
                "checkbox": True
            },
            "생성일": {
                "date": {
                    "start": datetime.now().strftime("%Y-%m-%d")
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 한진중공업 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def main():
    """
    메인 실행 함수
    """
    print("="*80)
    print("🚀 한진중공업 프로젝트 Phase 0: 회사 정보 마스터 DB 항목 추가")
    print("="*80)
    
    # 한진중공업 항목 추가
    page_id, page_url = add_hanjin_to_company_db()
    
    if page_id:
        print("\n" + "="*80)
        print("🎉 한진중공업 항목 추가 완료!")
        print("="*80)
        print(f"✅ Page ID: {page_id}")
        print(f"✅ URL: {page_url}")
        print("✅ 회사 정보 마스터 DB에 한진중공업 항목이 성공적으로 추가되었습니다.")
        
        # 결과를 JSON 파일로 저장
        result_data = {
            "company_name": "한진중공업 (HJ중공업)",
            "page_id": page_id,
            "page_url": page_url,
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        result_file = f"../data/hanjin_company_added_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 파일 저장: {result_file}")
        
    else:
        print("\n❌ 한진중공업 항목 추가 실패")
    
    return page_id, page_url

if __name__ == "__main__":
    main() 