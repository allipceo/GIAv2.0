#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 지시: 통합·권한 핸드셰이크
목적: users/me=200, databases=200 확인
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def mask_token(token: str) -> str:
    """토큰을 앞 8자리만 마스킹하여 반환"""
    if len(token) <= 8:
        return "***"
    return token[:8] + "***"

def main():
    parser = argparse.ArgumentParser(description='통합·권한 핸드셰이크')
    parser.add_argument('--token', help='Notion 토큰 (선택사항)')
    args = parser.parse_args()
    
    print("통합·권한 핸드셰이크 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    # 토큰 확인
    token = args.token or os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    print(f"토큰: {mask_token(token)}")
    
    try:
        # NotionClient 인스턴스 생성
        n = NotionClient(token)
        
        # 1. users/me 테스트
        print("1. users/me 테스트...")
        try:
            user_info = n.users_me()
            print(f"   users/me: 200 OK")
            print(f"   사용자: {user_info.get('name', 'N/A')}")
        except Exception as e:
            print(f"   users/me: ERROR - {e}")
            return 1
        
        # 2. databases 테스트 (DEV_DB_ID 사용)
        print("2. databases 테스트...")
        db_id = os.environ.get("DEV_DB_ID")
        if not db_id:
            print("   ERROR: DEV_DB_ID가 설정되지 않았습니다.")
            return 1
        
        try:
            db_info = n.get_database(db_id)
            print(f"   databases: 200 OK")
            print(f"   DB 제목: {db_info.get('title', [{}])[0].get('plain_text', 'N/A')}")
        except Exception as e:
            print(f"   databases: ERROR - {e}")
            return 1
        
        print("\nSUCCESS: 통합·권한 핸드셰이크 완료!")
        return 0
        
    except Exception as e:
        print(f"ERROR: 핸드셰이크 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
