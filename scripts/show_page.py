#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 스크립트: 개별 페이지 속성/본문 조회
목적: 특정 페이지의 속성과 본문 내용을 상세 조회
"""

import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def extract_title_from_properties(props):
    """페이지 속성에서 제목 추출"""
    for prop_name, prop_value in props.items():
        if prop_value.get("type") == "title":
            title_parts = prop_value.get("title", [])
            return "".join([part["plain_text"] for part in title_parts])
    return "제목 없음"

def extract_status_from_properties(props):
    """페이지 속성에서 상태 추출"""
    for prop_name, prop_value in props.items():
        if prop_value.get("type") == "status" and prop_value.get("status"):
            return prop_value["status"]["name"]
    return "상태 없음"

def extract_date_from_properties(props):
    """페이지 속성에서 날짜 추출"""
    for prop_name, prop_value in props.items():
        if prop_value.get("type") == "date" and prop_value.get("date"):
            return prop_value["date"]["start"]
    return "날짜 없음"

def main():
    print("개별 페이지 상세 조회 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    PAGE_ID = os.environ.get("PAGE_ID")
    if not PAGE_ID:
        print("❌ PAGE_ID가 설정되지 않았습니다.")
        print("사용법: PAGE_ID=your_page_id python scripts/show_page.py")
        return 1
    
    try:
        # NotionClient 인스턴스 생성
        n = NotionClient(os.environ["NOTION_TOKEN"])
        
        # 페이지 정보 조회
        print(f"페이지 조회 중: {PAGE_ID}")
        page = n.get_page(PAGE_ID)
        
        # 속성 정보 추출
        props = page["properties"]
        title = extract_title_from_properties(props)
        status = extract_status_from_properties(props)
        date = extract_date_from_properties(props)
        
        print("\n페이지 속성:")
        print(f"제목: {title}")
        print(f"상태: {status}")
        print(f"작성일: {date}")
        
        # 본문 상위 10개 블록 조회
        print("\n본문 상위 10개 블록:")
        try:
            res = n.list_block_children(PAGE_ID, page_size=100)
            
            for i, block in enumerate(res.get("results", [])):
                block_type = block["type"]
                text_content = ""
                
                # 블록 타입별 텍스트 추출
                if "rich_text" in block.get(block_type, {}):
                    rich_text = block[block_type]["rich_text"]
                    text_content = "".join([t["plain_text"] for t in rich_text])
                elif block_type == "paragraph" and "paragraph" in block:
                    rich_text = block["paragraph"].get("rich_text", [])
                    text_content = "".join([t["plain_text"] for t in rich_text])
                elif block_type == "heading_1" and "heading_1" in block:
                    rich_text = block["heading_1"].get("rich_text", [])
                    text_content = "".join([t["plain_text"] for t in rich_text])
                elif block_type == "heading_2" and "heading_2" in block:
                    rich_text = block["heading_2"].get("rich_text", [])
                    text_content = "".join([t["plain_text"] for t in rich_text])
                elif block_type == "heading_3" and "heading_3" in block:
                    rich_text = block["heading_3"].get("rich_text", [])
                    text_content = "".join([t["plain_text"] for t in rich_text])
                
                print(f"- ({block_type}) {text_content[:120]}")
                
                if i >= 9:  # 상위 10개만
                    break
                    
        except Exception as e:
            print(f"본문 조회 중 오류: {e}")
        
        print("\n페이지 조회가 완료되었습니다.")
        return 0
        
    except Exception as e:
        print(f"❌ 페이지 조회 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
