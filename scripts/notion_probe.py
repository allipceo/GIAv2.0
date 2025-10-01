#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 스크립트: 토큰·DB 프로브 + 스키마 해시 캐시 생성
목적: 토큰 유효성 확인, DB 접근 권한 확인, 스키마 해시 생성
"""

import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient, build_schema_hash

def main():
    print("Notion 토큰·DB 프로브 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    TOKEN = os.environ.get("NOTION_TOKEN")
    DB_ID = os.environ.get("TARGET_DATABASE_ID")
    
    if not TOKEN:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    if not DB_ID:
        print("ERROR: TARGET_DATABASE_ID가 설정되지 않았습니다.")
        return 1
    
    try:
        # NotionClient 인스턴스 생성
        n = NotionClient(TOKEN)
        
        # 1. 토큰 유효성 확인
        print("1. 토큰 유효성 확인...")
        user_info = n.users_me()
        print(f"SUCCESS: users/me: {user_info['object']}")
        
        # 2. DB 접근 권한 확인
        print("2. DB 접근 권한 확인...")
        db_info = n.get_database(DB_ID)
        print(f"SUCCESS: database: {db_info['object']}")
        
        # 3. 스키마 해시 생성 및 캐시 저장
        print("3. 스키마 해시 생성...")
        schema_hash = build_schema_hash(db_info)
        print(f"SUCCESS: schema_hash: {schema_hash}")
        
        # 스키마 해시를 파일로 저장
        with open(".schema_hash.txt", "w", encoding="utf-8") as f:
            f.write(schema_hash)
        print("SUCCESS: 스키마 해시가 .schema_hash.txt에 저장되었습니다.")
        
        print("\n모든 프로브가 성공했습니다!")
        return 0
        
    except Exception as e:
        print(f"ERROR: 프로브 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
