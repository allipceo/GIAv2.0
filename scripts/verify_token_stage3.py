#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 지시: Stage 3 토큰 유효성 검증
2단계: users/me → databases/{id}
판독: 200,200=정상 / 200,403=DB공유필요 / 401,any=토큰무효
"""

import os
import sys
import requests
from dotenv import load_dotenv

def verify_stage3_token():
    """Stage 3 토큰 유효성 검증"""
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    db_id = "5d15b3aa0f174b04bceeb22107e06a03"
    
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    print("=== 선과장님 지시: Stage 3 토큰 검증 ===")
    print(f"DB ID: {db_id}")
    print(f"토큰: {token[:15]}***{token[-5:]}")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 1단계: users/me
    print("=== 1단계 users/me ===")
    users_status = 0
    try:
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers, timeout=30)
        users_status = response.status_code
        print(f"users/me: {users_status}")
        if users_status == 200:
            print("SUCCESS: 토큰 유효")
        else:
            print(f"ERROR: {response.text[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")
        users_status = 0
    
    print()
    
    # 2단계: databases/{id}
    print("=== 2단계 databases/{id} ===")
    db_status = 0
    try:
        response = requests.get(f"https://api.notion.com/v1/databases/{db_id}", headers=headers, timeout=30)
        db_status = response.status_code
        print(f"databases: {db_status}")
        if db_status == 200:
            print("SUCCESS: DB 접근 권한 OK")
        else:
            print(f"ERROR: {response.text[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")
        db_status = 0
    
    print()
    
    # 판독 가이드 (선과장님 기준)
    print("=== 판독 결과 ===")
    if users_status == 200 and db_status == 200:
        print("결과: 200, 200 → 토큰 유효 + DB 접근 권한 OK")
        print("조치: 바로 목록 조회와 Z062 탐색 실행")
        return 0
    elif users_status == 200 and db_status == 403:
        print("결과: 200, 403 → 토큰 유효, DB 공유 미부여")
        print("조치: 📘 ZOBIS 개발문서 DB에서 해당 Integration을 Share → Connections → Can edit로 초대")
        return 1
    elif users_status == 401:
        print("결과: 401, any → 세션에 주입된 값 무효 또는 만료/회수")
        print("조치: 유효 토큰 재주입 또는 회전")
        return 1
    else:
        print(f"결과: {users_status}, {db_status} → 기타 오류")
        print("조치: 원인 분석 필요")
        return 1

if __name__ == "__main__":
    exit(verify_stage3_token())
