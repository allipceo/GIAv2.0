#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
토큰 유효성 검사 스크립트
3개 토큰을 순차적으로 테스트하여 유효한 토큰을 찾습니다.
"""

import os
import sys
import requests
from typing import List, Dict, Any

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def test_token(token: str, db_id: str) -> Dict[str, Any]:
    """단일 토큰의 유효성을 테스트합니다."""
    results = {
        "token": token[:20] + "...",  # 보안을 위해 일부만 표시
        "users_me": {"status": "unknown", "code": 0, "error": ""},
        "databases": {"status": "unknown", "code": 0, "error": ""}
    }
    
    try:
        n = NotionClient(token)
        
        # 1. users/me 테스트
        try:
            user_info = n.users_me()
            results["users_me"] = {"status": "success", "code": 200, "error": ""}
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                results["users_me"] = {"status": "unauthorized", "code": 401, "error": "토큰 무효"}
            elif "403" in error_msg:
                results["users_me"] = {"status": "forbidden", "code": 403, "error": "권한 없음"}
            else:
                results["users_me"] = {"status": "error", "code": 0, "error": error_msg}
        
        # 2. databases/{id} 테스트
        try:
            db_info = n.get_database(db_id)
            results["databases"] = {"status": "success", "code": 200, "error": ""}
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                results["databases"] = {"status": "unauthorized", "code": 401, "error": "토큰 무효"}
            elif "403" in error_msg:
                results["databases"] = {"status": "forbidden", "code": 403, "error": "DB 공유 권한 없음"}
            elif "404" in error_msg:
                results["databases"] = {"status": "not_found", "code": 404, "error": "DB ID 오타"}
            else:
                results["databases"] = {"status": "error", "code": 0, "error": error_msg}
                
    except Exception as e:
        results["error"] = f"클라이언트 생성 실패: {e}"
    
    return results

def main():
    print("토큰 유효성 검사 시작...")
    
    # 테스트할 토큰들 (3개) - 환경변수에서 읽기
    tokens = [
        os.environ.get("NOTION_TOKEN_1", ""),  # 토큰1 (환경변수)
        os.environ.get("NOTION_TOKEN_2", ""),  # 토큰2 (환경변수)
        os.environ.get("NOTION_TOKEN_3", ""),  # 토큰3 (환경변수)
    ]
    
    # 빈 토큰 제거
    tokens = [token for token in tokens if token]
    
    db_id = "5d15b3aa0f174b04bceeb22107e06a03"
    
    print(f"테스트 대상 DB ID: {db_id}")
    print(f"테스트할 토큰 수: {len(tokens)}")
    print()
    
    valid_tokens = []
    
    for i, token in enumerate(tokens, 1):
        print(f"=== 토큰 {i} 검사 ===")
        print(f"토큰: {token[:15]}***{token[-5:]}")  # 보안을 위해 중간 부분 마스킹
        
        results = test_token(token, db_id)
        
        # users/me 결과
        users_status = results["users_me"]["status"]
        users_code = results["users_me"]["code"]
        users_error = results["users_me"]["error"]
        print(f"users/me: {users_code} - {users_status}")
        if users_error:
            print(f"  오류: {users_error}")
        
        # databases 결과
        db_status = results["databases"]["status"]
        db_code = results["databases"]["code"]
        db_error = results["databases"]["error"]
        print(f"databases: {db_code} - {db_status}")
        if db_error:
            print(f"  오류: {db_error}")
        
        # 유효성 판단
        if users_code == 200 and db_code == 200:
            print("SUCCESS: 이 토큰은 유효합니다!")
            valid_tokens.append((i, token))
        else:
            print("ERROR: 이 토큰은 유효하지 않습니다.")
        
        print()
    
    # 결과 요약
    print("=== 검사 결과 요약 ===")
    if valid_tokens:
        print(f"유효한 토큰 {len(valid_tokens)}개 발견:")
        for token_num, token in valid_tokens:
            print(f"  토큰 {token_num}: {token[:15]}***{token[-5:]}")
        print("\n첫 번째 유효한 토큰을 사용하여 다음 단계를 진행하겠습니다.")
    else:
        print("ERROR: 유효한 토큰이 없습니다.")
        print("다음 사항을 확인해 주세요:")
        print("1. 토큰 형식이 올바른지 (ntn_...)")
        print("2. 토큰이 만료되지 않았는지")
        print("3. ZOBIS개발문서DB에 해당 Integration이 Can edit 권한으로 공유되었는지")
    
    return 0 if valid_tokens else 1

if __name__ == "__main__":
    exit(main())
