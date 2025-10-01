#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 지시: Z062 문서 식별(데이터베이스 쿼리)
목적: 필터 규칙으로 Z062 문서 검색
"""

import os
import sys
import argparse
import json
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def main():
    parser = argparse.ArgumentParser(description='DB 쿼리로 Z062 문서 식별')
    parser.add_argument('--db', required=True, help='DB ID')
    parser.add_argument('--filter', required=True, help='필터 JSON 파일 경로')
    parser.add_argument('--limit', type=int, default=10, help='결과 제한 수')
    parser.add_argument('--out', required=True, help='출력 파일 경로')
    args = parser.parse_args()
    
    print("Z062 문서 식별 시작...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    try:
        n = NotionClient(token)
        
        # 필터 로드
        with open(args.filter, 'r', encoding='utf-8') as f:
            filter_config = json.load(f)
        
        print(f"필터 로드: {args.filter}")
        
        # DB 쿼리 실행
        print("DB 쿼리 실행 중...")
        
        # Notion API 쿼리 페이로드 구성
        payload = {
            "page_size": args.limit
        }
        
        # 필터 적용 (Notion API 형식으로 변환)
        if "title_contains" in filter_config:
            # 제목 포함 검색
            payload["filter"] = {
                "property": "문서 제목",
                "title": {"contains": filter_config["title_contains"]}
            }
        elif "or" in filter_config:
            # OR 조건 처리
            or_conditions = []
            for condition in filter_config["or"]:
                if "title_contains" in condition:
                    or_conditions.append({
                        "property": "문서 제목",
                        "title": {"contains": condition["title_contains"]}
                    })
                elif "property" in condition and "equals" in condition:
                    or_conditions.append({
                        "property": condition["property"],
                        "rich_text": {"equals": condition["equals"]}
                    })
            
            if or_conditions:
                payload["filter"] = {"or": or_conditions}
        
        # 정렬 적용
        if "sort" in filter_config:
            sorts = []
            for sort_item in filter_config["sort"]:
                if "last_edited_time" in sort_item:
                    direction = sort_item["last_edited_time"]
                    if direction == "desc":
                        direction = "descending"
                    elif direction == "asc":
                        direction = "ascending"
                    sorts.append({
                        "timestamp": "last_edited_time",
                        "direction": direction
                    })
            if sorts:
                payload["sorts"] = sorts
        
        # 쿼리 실행
        result = n.query_database(args.db, payload)
        
        # 결과 처리
        results = result.get("results", [])
        print(f"쿼리 결과: {len(results)}건")
        
        # 결과 저장
        output_data = {
            "query_time": result.get("query_time", ""),
            "has_more": result.get("has_more", False),
            "next_cursor": result.get("next_cursor", ""),
            "results": []
        }
        
        for item in results:
            # 제목 추출
            title = ""
            properties = item.get("properties", {})
            for prop_name, prop_value in properties.items():
                if prop_value.get("type") == "title":
                    title_parts = prop_value.get("title", [])
                    title = "".join([part["plain_text"] for part in title_parts])
                    break
            
            output_data["results"].append({
                "id": item["id"],
                "title": title,
                "last_edited_time": item.get("last_edited_time", ""),
                "created_time": item.get("created_time", ""),
                "properties": properties
            })
        
        # 파일 저장
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"결과 저장: {args.out}")
        print(f"Z062 후보: {len(results)}건")
        
        if results:
            print("상위 후보:")
            for i, item in enumerate(results[:3], 1):
                print(f"  {i}. {item['title']} | {item['id']}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: DB 쿼리 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
