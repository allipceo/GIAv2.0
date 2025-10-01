#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 지시: DB 공유 연결 확인
목적: 403/404면 "ZOBIS 개발문서 DB → 공유 → 통합(No5_API) 초대" 안내
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

def mask_token(token: str) -> str:
    """토큰을 앞 8자리만 마스킹하여 반환"""
    if len(token) <= 8:
        return "***"
    return token[:8] + "***"

def main():
    parser = argparse.ArgumentParser(description='DB 공유 연결 확인')
    parser.add_argument('--db', required=True, help='DB ID')
    parser.add_argument('--out', required=True, help='출력 파일 경로')
    args = parser.parse_args()
    
    print("DB 공유 연결 확인 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    print(f"토큰: {mask_token(token)}")
    print(f"DB ID: {args.db}")
    
    try:
        n = NotionClient(token)
        
        # DB 접근 테스트
        print("DB 접근 테스트 중...")
        try:
            db_info = n.get_database(args.db)
            print("SUCCESS: DB 접근 성공!")
            
            # 성공 리포트 생성
            report = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "db_id": args.db,
                "db_title": db_info.get('title', [{}])[0].get('plain_text', 'N/A'),
                "properties_count": len(db_info.get('properties', {})),
                "message": "DB 공유 연결 정상"
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"ERROR: DB 접근 실패 - {error_msg}")
            
            # 실패 리포트 생성
            report = {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "db_id": args.db,
                "error": error_msg,
                "message": "DB 공유 연결 실패"
            }
            
            if "403" in error_msg:
                report["solution"] = "ZOBIS 개발문서 DB → Share → Connections → 통합(No5_API) 초대 필요"
            elif "404" in error_msg:
                report["solution"] = "DB ID 확인 필요"
            else:
                report["solution"] = "토큰 권한 또는 DB 설정 확인 필요"
        
        # 리포트 저장
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"리포트 저장: {args.out}")
        
        # 성공/실패에 따른 종료 코드
        return 0 if report["status"] == "success" else 1
        
    except Exception as e:
        print(f"ERROR: DB 확인 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
