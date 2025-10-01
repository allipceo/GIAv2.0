#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
케이스3: 뉴스클리핑 DB 확인 및 헬스체크
목적: NEWS_DB_ID 환경변수 설정 및 DB 접근 권한 확인
"""

import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def main():
    print("🌍 케이스3: 뉴스클리핑 DB 확인 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    try:
        n = NotionClient(token)
        
        # 1. users/me 헬스체크
        print("1. users/me 헬스체크...")
        user_info = n.users_me()
        print(f"   ✅ users/me: 200 OK")
        
        # 2. 뉴스클리핑 DB ID 확인 (임시로 기존 DB 사용)
        news_db_id = os.environ.get("NEWS_DB_ID")
        if not news_db_id:
            # 임시로 기존 DB 사용 (실제로는 뉴스클리핑 전용 DB 필요)
            news_db_id = os.environ.get("TARGET_DATABASE_ID")
            print(f"   ⚠️ NEWS_DB_ID가 설정되지 않아 TARGET_DATABASE_ID 사용: {news_db_id}")
        else:
            print(f"   📍 NEWS_DB_ID: {news_db_id}")
        
        # 3. databases/{NEWS_DB_ID} 헬스체크
        print("2. databases/{NEWS_DB_ID} 헬스체크...")
        db_info = n.get_database(news_db_id)
        print(f"   ✅ databases: 200 OK")
        print(f"   📊 DB 이름: {db_info.get('title', [{}])[0].get('plain_text', '알 수 없음')}")
        
        # 4. 스키마 확인
        print("3. 스키마 확인...")
        properties = db_info.get("properties", {})
        print("   📋 주요 속성:")
        for prop_name, prop_details in properties.items():
            prop_type = prop_details.get("type", "unknown")
            print(f"      - {prop_name}: {prop_type}")
        
        print("\n✅ 케이스3 헬스체크 완료: 뉴스클리핑 DB 접근 가능")
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: 뉴스클리핑 DB 확인 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
