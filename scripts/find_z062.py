#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 스크립트: Z062 테스트 페이지 찾기
목적: ZOBIS개발문서DB에서 "Z062"가 포함된 페이지를 검색
"""

import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def main():
    print("Z062 테스트 페이지 검색 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    DB_ID = os.environ.get("TARGET_DATABASE_ID")
    if not DB_ID:
        print("ERROR: TARGET_DATABASE_ID가 설정되지 않았습니다.")
        return 1
    
    try:
        # NotionClient 인스턴스 생성
        n = NotionClient(os.environ["NOTION_TOKEN"])
        
        # Z062가 포함된 페이지 검색
        print("'Z062'가 포함된 페이지 검색 중...")
        
        # 검색 페이로드 구성
        payload = {
            "filter": {
                "property": "문서 제목",  # 표시명 (실제 DB에서 확인 필요)
                "title": {"contains": "Z062"}
            },
            "page_size": 50
        }
        
        res = n.query_database(DB_ID, payload)
        hits = res.get("results", [])
        
        if not hits:
            print("ERROR: Z062 페이지를 찾지 못했습니다.")
            print("전체 검색으로 재시도하세요.")
            
            # 전체 검색으로 재시도
            print("\n🔄 전체 검색으로 재시도...")
            all_pages = n.query_database(DB_ID, {"page_size": 100})
            all_results = all_pages.get("results", [])
            
            print(f"📋 전체 페이지 수: {len(all_results)}")
            print("📝 제목에 'Z062'가 포함된 페이지:")
            
            found = False
            for page in all_results:
                props = page.get("properties", {})
                title = ""
                
                # 제목 추출
                for prop_name, prop_value in props.items():
                    if prop_value.get("type") == "title":
                        title_parts = prop_value.get("title", [])
                        title = "".join([part["plain_text"] for part in title_parts])
                        break
                
                if "Z062" in title:
                    print(f"✅ 발견: {title} | {page['id']}")
                    found = True
            
            if not found:
                print("❌ 전체 검색에서도 Z062 페이지를 찾지 못했습니다.")
                return 1
        else:
            # Z062 페이지 발견
            page = hits[0]
            page_id = page["id"]
            
            # 제목 추출
            props = page.get("properties", {})
            title = ""
            for prop_name, prop_value in props.items():
                if prop_value.get("type") == "title":
                    title_parts = prop_value.get("title", [])
                    title = "".join([part["plain_text"] for part in title_parts])
                    break
            
            print(f"✅ Z062 페이지 발견!")
            print(f"제목: {title}")
            print(f"페이지 ID: {page_id}")
            
            # 환경변수로 설정하여 다음 단계에서 사용할 수 있도록 함
            print(f"\n💡 다음 명령어로 상세 조회:")
            print(f"PAGE_ID={page_id} python scripts/show_page.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Z062 페이지 검색 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
