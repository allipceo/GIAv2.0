#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 접근 권한만 확인하는 스크립트
토큰은 유효하지만 DB 공유 권한 문제인지 확인
"""

import os
import sys
import requests
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_db_access_only():
    """DB 접근 권한만 테스트"""
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    db_id = "5d15b3aa0f174b04bceeb22107e06a03"
    
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    print(f"DB ID: {db_id}")
    print(f"토큰: {token[:15]}***{token[-5:]}")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 1. users/me 테스트 (토큰 유효성)
    print("1. users/me 테스트 (토큰 유효성 확인)...")
    try:
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   SUCCESS: 토큰은 유효합니다!")
        else:
            print(f"   ERROR: {response.text[:200]}")
            return 1
    except Exception as e:
        print(f"   ERROR: {e}")
        return 1
    
    print()
    
    # 2. databases/{id} 테스트 (DB 접근 권한)
    print("2. databases/{id} 테스트 (DB 접근 권한 확인)...")
    try:
        response = requests.get(f"https://api.notion.com/v1/databases/{db_id}", headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   SUCCESS: DB 접근 권한이 있습니다!")
            db_info = response.json()
            print(f"   DB 제목: {db_info.get('title', [{}])[0].get('plain_text', 'N/A')}")
            return 0
        elif response.status_code == 403:
            print("   ERROR: 403 Forbidden - DB 공유 권한이 없습니다!")
            print("   해결방법: ZOBIS개발문서DB → Share → Connections → 해당 Integration을 Can edit로 초대")
            return 1
        elif response.status_code == 404:
            print("   ERROR: 404 Not Found - DB ID가 잘못되었습니다!")
            return 1
        else:
            print(f"   ERROR: {response.text[:200]}")
            return 1
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit(test_db_access_only())
