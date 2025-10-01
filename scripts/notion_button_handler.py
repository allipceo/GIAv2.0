#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 실행버튼 전용 핸들러
목적: 웹훅 요청을 받아서 해당 케이스 실행 및 결과 반환
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workflows.notion_collaboration import NotionCollaborationWorkflow

def handle_case1(target="Z062", notion_page_id=None):
    """케이스1 실행버튼 처리"""
    print(f"🔧 케이스1 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    result = workflow.case1_handshake()
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "케이스1", result)
    
    return result

def handle_case2(target="Z062", notion_page_id=None):
    """케이스2 실행버튼 처리"""
    print(f"🔧 케이스2 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    result = workflow.case2_page_identification(target)
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "케이스2", result)
    
    return result

def handle_case3(target="Z062", notion_page_id=None):
    """케이스3 실행버튼 처리"""
    print(f"🔧 케이스3 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    news_data = {
        "title": f"[실행버튼] {target} 관련 뉴스 등록",
        "url": f"https://example.com/{target.lower()}-news",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "실행버튼 매체",
        "category": "해상풍력발전",
        "importance": "보통"
    }
    result = workflow.case3_news_registration(news_data)
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "케이스3", result)
    
    return result

def handle_all(target="Z062", notion_page_id=None):
    """전체 워크플로우 실행버튼 처리"""
    print(f"🚀 전체 워크플로우 실행버튼 처리: {target}")
    
    workflow = NotionCollaborationWorkflow()
    result = workflow.run_full_workflow(target)
    
    # Notion 페이지 업데이트
    if notion_page_id:
        update_notion_result(notion_page_id, "전체 워크플로우", result)
    
    return result

def update_notion_result(notion_page_id, case_name, result):
    """Notion 페이지에 실행 결과 업데이트"""
    from src.utils.notion_api import NotionClient
    import os
    
    try:
        client = NotionClient(os.environ.get("NOTION_TOKEN"))
        
        # 실행 결과를 페이지에 추가
        status = "성공" if result.get('overall_status') == 'success' else "실패"
        message = f"{case_name} 실행 {status}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 페이지 속성 업데이트
        properties = {
            "실행 상태": {
                "select": {"name": status}
            },
            "실행 메시지": {
                "rich_text": [{"text": {"content": message}}]
            },
            "실행 시간": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
        
        client._req("PATCH", f"/pages/{notion_page_id}", json={"properties": properties})
        print(f"✅ Notion 페이지 업데이트 완료: {notion_page_id}")
        
    except Exception as e:
        print(f"❌ Notion 페이지 업데이트 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description="Notion 실행버튼 핸들러")
    parser.add_argument("--case", choices=["1", "2", "3", "all"], required=True, help="실행할 케이스")
    parser.add_argument("--target", default="Z062", help="대상 키워드")
    parser.add_argument("--notion-page-id", help="Notion 페이지 ID")
    args = parser.parse_args()
    
    print(f"🚀 Notion 실행버튼 핸들러 시작...")
    print(f"케이스: {args.case}")
    print(f"대상: {args.target}")
    print(f"Notion 페이지 ID: {args.notion_page_id}")
    
    if args.case == "1":
        result = handle_case1(args.target, args.notion_page_id)
    elif args.case == "2":
        result = handle_case2(args.target, args.notion_page_id)
    elif args.case == "3":
        result = handle_case3(args.target, args.notion_page_id)
    elif args.case == "all":
        result = handle_all(args.target, args.notion_page_id)
    
    print(f"📊 실행 결과: {result.get('overall_status', 'unknown')}")
    return 0 if result.get('overall_status') == 'success' else 1

if __name__ == "__main__":
    exit(main())
