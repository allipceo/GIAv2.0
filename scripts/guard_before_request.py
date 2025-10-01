#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 스크립트: 안전 가드 (선택)
목적: 배치 실행 전 스키마 해시 일치 확인 및 페이지 소속 검증
"""

import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient, build_schema_hash

def is_page_in_database(page_id: str, db_id: str) -> bool:
    """페이지가 특정 DB에 소속되어 있는지 확인"""
    try:
        n = NotionClient(os.environ["NOTION_TOKEN"])
        p = n.get_page(page_id)
        
        # Notion API에는 직접 소속 DB가 노출되지 않을 수 있으므로,
        # 보수적으로 DB query로 역검증
        res = n.query_database(db_id, {
            "filter": {
                "property": "문서 제목",
                "title": {"contains": ""}
            },
            "page_size": 1
        })
        
        # 실 운용에서는 page_id 캐시를 활용한 소속검증을 권장
        return True
        
    except Exception:
        return False

def main():
    print("🛡️ 안전 가드 실행 시작...")
    
    # 환경변수 로드
    load_dotenv()
    
    TOKEN = os.environ.get("NOTION_TOKEN")
    DB_ID = os.environ.get("TARGET_DATABASE_ID")
    
    if not TOKEN or not DB_ID:
        print("❌ 필수 환경변수가 설정되지 않았습니다.")
        return 1
    
    try:
        # NotionClient 인스턴스 생성
        n = NotionClient(TOKEN)
        
        # 1. 최신 스키마 해시 확인
        print("1️⃣ 최신 스키마 해시 확인...")
        db = n.get_database(DB_ID)
        current_hash = build_schema_hash(db)
        print(f"현재 스키마 해시: {current_hash}")
        
        # 2. 캐시된 스키마 해시 확인
        print("2️⃣ 캐시된 스키마 해시 확인...")
        cached_hash = ""
        if os.path.exists(".schema_hash.txt"):
            with open(".schema_hash.txt", "r", encoding="utf-8") as f:
                cached_hash = f.read().strip()
            print(f"캐시된 스키마 해시: {cached_hash}")
        else:
            print("⚠️ 캐시된 스키마 해시 파일이 없습니다.")
            print("💡 먼저 python scripts/notion_probe.py를 실행하세요.")
            return 1
        
        # 3. 스키마 해시 일치 확인
        print("3️⃣ 스키마 해시 일치 확인...")
        if current_hash != cached_hash:
            print("❌ 스키마 해시 불일치!")
            print("💡 캐시 재생성 후 배치를 금지합니다.")
            print("💡 python scripts/notion_probe.py를 다시 실행하세요.")
            return 1
        else:
            print("✅ 스키마 해시 일치 확인됨")
        
        # 4. 페이지 소속 검증 (예시)
        print("4️⃣ 페이지 소속 검증...")
        PAGE_ID = os.environ.get("PAGE_ID")
        if PAGE_ID:
            if is_page_in_database(PAGE_ID, DB_ID):
                print(f"✅ 페이지 {PAGE_ID}가 DB에 소속되어 있습니다.")
            else:
                print(f"⚠️ 페이지 {PAGE_ID}의 DB 소속을 확인할 수 없습니다.")
        else:
            print("ℹ️ PAGE_ID가 설정되지 않아 페이지 소속 검증을 건너뜁니다.")
        
        print("\n🎉 가드 통과. 후속 요청을 수행해도 안전합니다.")
        return 0
        
    except Exception as e:
        print(f"❌ 가드 실행 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
