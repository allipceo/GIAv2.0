#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 DB의 parent page ID 확인 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 기존 DB의 parent page ID를 확인하여 새로운 DB 생성에 활용
"""

import requests

# 노션 API 설정
NOTION_TOKEN = ""
EXISTING_DB_ID = "22aa613d25ff80888257c652d865f85a"  # 기존 뉴스 클리핑 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_database_info(database_id):
    """DB 정보 조회"""
    url = f"https://api.notion.com/v1/databases/{database_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"📋 DB 정보:")
        print(f"   - DB ID: {result['id']}")
        print(f"   - DB 제목: {result['title'][0]['text']['content'] if result['title'] else 'N/A'}")
        print(f"   - DB URL: {result.get('url', 'N/A')}")
        
        # Parent 정보 확인
        parent = result.get('parent', {})
        parent_type = parent.get('type', 'N/A')
        
        if parent_type == 'page_id':
            parent_page_id = parent['page_id']
            print(f"   - Parent Type: {parent_type}")
            print(f"   - Parent Page ID: {parent_page_id}")
            return parent_page_id
        else:
            print(f"   - Parent Type: {parent_type}")
            print(f"   - Parent Info: {parent}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ DB 정보 조회 실패: {e}")
        return None

def main():
    """메인 실행 함수"""
    print("🔍 기존 DB의 parent page ID 확인 중...")
    print("=" * 50)
    
    parent_page_id = get_database_info(EXISTING_DB_ID)
    
    if parent_page_id:
        print(f"\n✅ Parent Page ID 확인 완료: {parent_page_id}")
        print(f"📝 이 ID를 새로운 DB 생성에 사용할 수 있습니다.")
        
        # 파일에 저장
        with open('parent_page_id.txt', 'w') as f:
            f.write(parent_page_id)
        
        print(f"💾 Parent Page ID가 'parent_page_id.txt' 파일에 저장되었습니다.")
    else:
        print(f"\n❌ Parent Page ID를 확인할 수 없습니다.")
        print(f"📝 조대표님께서 직접 페이지 ID를 제공해 주셔야 합니다.")

if __name__ == "__main__":
    main()
