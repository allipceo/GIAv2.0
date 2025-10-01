#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 스크립트: DB 전체 목록 조회 (페이지네이션)
목적: ZOBIS개발문서DB의 모든 페이지를 조회하고 제목/ID 출력
"""

import os
import sys
import time
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def iter_db(db_id: str, page_size=50, filter=None, sorts=None):
    """DB 페이지를 페이지네이션으로 순회하는 제너레이터"""
    n = NotionClient(os.environ["NOTION_TOKEN"])
    
    payload = {"page_size": page_size}
    if filter:
        payload["filter"] = filter
    if sorts:
        payload["sorts"] = sorts
    
    cursor = None
    
    while True:
        if cursor:
            payload["start_cursor"] = cursor
        
        res = n.query_database(db_id, payload)
        
        for item in res.get("results", []):
            yield item
        
        if not res.get("has_more"):
            break
        
        cursor = res.get("next_cursor")
        time.sleep(0.2)  # 정중한 API 호출

def extract_title_from_properties(props):
    """페이지 속성에서 제목 추출"""
    for prop_name, prop_value in props.items():
        if prop_value.get("type") == "title":
            title_parts = prop_value.get("title", [])
            return "".join([part["plain_text"] for part in title_parts])
    return "제목 없음"

def main():
    print("ZOBIS개발문서DB 전체 목록 조회 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    DB_ID = os.environ.get("TARGET_DATABASE_ID")
    if not DB_ID:
        print("ERROR: TARGET_DATABASE_ID가 설정되지 않았습니다.")
        return 1
    
    try:
        # 최신 작성일 내림차순으로 100건까지 조회
        print("최신 작성일 내림차순으로 조회 중...")
        
        count = 0
        for page in iter_db(
            DB_ID, 
            page_size=50, 
            sorts=[{"timestamp": "last_edited_time", "direction": "descending"}]
        ):
            count += 1
            page_id = page["id"]
            title = extract_title_from_properties(page.get("properties", {}))
            
            # UTF-8 인코딩으로 안전하게 출력
            try:
                print(f"[{count:03}] {title} | {page_id}")
            except UnicodeEncodeError:
                # 유니코드 문제가 있는 경우 ASCII로 변환
                safe_title = title.encode('ascii', 'replace').decode('ascii')
                print(f"[{count:03}] {safe_title} | {page_id}")
            
            if count >= 100:
                break
        
        print(f"\nSUCCESS: 총 {count}개 페이지를 조회했습니다.")
        return 0
        
    except Exception as e:
        print(f"ERROR: 목록 조회 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
