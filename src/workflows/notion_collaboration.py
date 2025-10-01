#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZOBIS Notion 협업 워크플로우 시스템
목적: 케이스1,2,3의 재활용 가능한 모듈화된 워크플로우
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.notion_api import NotionClient

class NotionCollaborationWorkflow:
    """Notion 협업 워크플로우 통합 클래스"""
    
    def __init__(self, config_file: str = "config.env"):
        """워크플로우 초기화"""
        load_dotenv(config_file)
        self.token = os.environ.get("NOTION_TOKEN")
        self.db_id = os.environ.get("TARGET_DATABASE_ID")
        self.client = NotionClient(self.token) if self.token else None
        
    def case1_handshake(self) -> Dict[str, Any]:
        """케이스1: 통합·권한 핸드셰이크"""
        print("케이스1: 통합·권한 핸드셰이크 시작...")
        
        results = {
            "case": "케이스1",
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # 1. users/me 테스트
            user_info = self.client.users_me()
            results["steps"].append({
                "step": "users_me",
                "status": "success",
                "code": 200,
                "message": "토큰 유효성 확인 완료"
            })
            
            # 2. databases 테스트
            db_info = self.client.get_database(self.db_id)
            results["steps"].append({
                "step": "databases",
                "status": "success", 
                "code": 200,
                "message": "DB 접근 권한 확인 완료"
            })
            
            results["overall_status"] = "success"
            print("✅ 케이스1 완료: 통합·권한 핸드셰이크 성공")
            
        except Exception as e:
            results["steps"].append({
                "step": "error",
                "status": "failed",
                "message": str(e)
            })
            results["overall_status"] = "failed"
            print(f"❌ 케이스1 실패: {e}")
            
        return results
    
    def case2_page_identification(self, target_keyword: str = "Z062") -> Dict[str, Any]:
        """케이스2: 페이지 식별 및 읽기"""
        print(f"케이스2: '{target_keyword}' 페이지 식별 시작...")
        
        results = {
            "case": "케이스2",
            "timestamp": datetime.now().isoformat(),
            "target_keyword": target_keyword,
            "steps": []
        }
        
        try:
            # 1. DB 쿼리로 페이지 검색
            payload = {
                "filter": {
                    "property": "문서 제목",
                    "title": {"contains": target_keyword}
                },
                "page_size": 10
            }
            
            query_result = self.client.query_database(self.db_id, payload)
            hits = query_result.get("results", [])
            
            if not hits:
                results["steps"].append({
                    "step": "query",
                    "status": "failed",
                    "message": f"'{target_keyword}' 페이지를 찾지 못했습니다"
                })
                results["overall_status"] = "failed"
                return results
            
            # 2. 첫 번째 결과 선택
            target_page = hits[0]
            page_id = target_page["id"]
            
            # 3. 페이지 상세 정보 조회
            page_info = self.client.get_page(page_id)
            
            results["steps"].append({
                "step": "query",
                "status": "success",
                "page_id": page_id,
                "message": f"'{target_keyword}' 페이지 식별 완료"
            })
            
            results["steps"].append({
                "step": "page_info",
                "status": "success",
                "page_id": page_id,
                "message": "페이지 상세 정보 조회 완료"
            })
            
            results["page_id"] = page_id
            results["overall_status"] = "success"
            print(f"✅ 케이스2 완료: '{target_keyword}' 페이지 식별 성공 (ID: {page_id})")
            
        except Exception as e:
            results["steps"].append({
                "step": "error",
                "status": "failed",
                "message": str(e)
            })
            results["overall_status"] = "failed"
            print(f"❌ 케이스2 실패: {e}")
            
        return results
    
    def case3_news_registration(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """케이스3: 뉴스클리핑 DB 등록"""
        print("케이스3: 뉴스클리핑 DB 등록 시작...")
        
        results = {
            "case": "케이스3",
            "timestamp": datetime.now().isoformat(),
            "news_data": news_data,
            "steps": []
        }
        
        try:
            # 1. 뉴스클리핑 DB 헬스체크
            user_info = self.client.users_me()
            db_info = self.client.get_database(self.db_id)
            results["steps"].append({
                "step": "health_check",
                "status": "success",
                "message": "뉴스클리핑 DB 헬스체크 완료"
            })
            
            # 2. 표준 스키마로 뉴스 등록
            properties = {
                "문서 제목": {
                    "title": [{"text": {"content": news_data["title"]}}]
                },
                "링크": {"url": news_data["url"]},
                "작성일": {"date": {"start": news_data["date"]}},
                "태그": {"multi_select": [{"name": news_data["category"]}]},
                "중요도": {"select": {"name": news_data["importance"]}},
                "문서 성격": {"select": {"name": "뉴스클리핑"}},
                "핵심내용": {"rich_text": [{"text": {"content": f"출처: {news_data['source']}"}}]}
            }
            
            page_data = {
                "parent": {"database_id": self.db_id},
                "properties": properties
            }
            
            result = self.client._req("POST", "/pages", json=page_data)
            page_id = result["id"]
            
            results["steps"].append({
                "step": "news_registration",
                "status": "success",
                "message": "뉴스클리핑 DB 등록 완료",
                "page_id": page_id,
                "notion_url": f"https://www.notion.so/{page_id.replace('-', '')}"
            })
            
            results["page_id"] = page_id
            results["notion_url"] = f"https://www.notion.so/{page_id.replace('-', '')}"
            results["overall_status"] = "success"
            print(f"✅ 케이스3 완료: 뉴스클리핑 DB 등록 성공 (ID: {page_id})")
            
        except Exception as e:
            results["steps"].append({
                "step": "error",
                "status": "failed",
                "message": str(e)
            })
            results["overall_status"] = "failed"
            print(f"❌ 케이스3 실패: {e}")
            
        return results
    
    def run_full_workflow(self, target_keyword: str = "Z062") -> Dict[str, Any]:
        """전체 워크플로우 실행 (케이스1+2+3)"""
        print("🚀 전체 Notion 협업 워크플로우 시작...")
        
        workflow_results = {
            "workflow": "Notion 협업 워크플로우",
            "timestamp": datetime.now().isoformat(),
            "target_keyword": target_keyword,
            "cases": {}
        }
        
        # 케이스1: 핸드셰이크
        case1_result = self.case1_handshake()
        workflow_results["cases"]["case1"] = case1_result
        
        if case1_result["overall_status"] != "success":
            workflow_results["overall_status"] = "failed"
            return workflow_results
        
        # 케이스2: 페이지 식별
        case2_result = self.case2_page_identification(target_keyword)
        workflow_results["cases"]["case2"] = case2_result
        
        if case2_result["overall_status"] != "success":
            workflow_results["overall_status"] = "failed"
            return workflow_results
        
        # 케이스3: 뉴스클리핑 DB 등록
        news_data = {
            "title": f"[파일럿] {target_keyword} 관련 뉴스 테스트 등록",
            "url": f"https://example.com/{target_keyword.lower()}-news",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "테스트 매체",
            "category": "해상풍력발전",
            "importance": "보통"
        }
        
        case3_result = self.case3_news_registration(news_data)
        workflow_results["cases"]["case3"] = case3_result
        
        # 전체 결과 판정
        all_success = all(
            case["overall_status"] == "success" 
            for case in workflow_results["cases"].values()
        )
        workflow_results["overall_status"] = "success" if all_success else "failed"
        
        print(f"🎯 전체 워크플로우 완료: {workflow_results['overall_status']}")
        return workflow_results

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Notion 협업 워크플로우 실행")
    parser.add_argument("--case", choices=["1", "2", "3", "all"], default="all", help="실행할 케이스")
    parser.add_argument("--target", default="Z062", help="대상 키워드")
    parser.add_argument("--out", help="결과 저장 파일")
    args = parser.parse_args()
    
    # 워크플로우 초기화
    workflow = NotionCollaborationWorkflow()
    
    if not workflow.client:
        print("ERROR: NotionClient 초기화 실패")
        return 1
    
    # 케이스별 실행
    if args.case == "1":
        result = workflow.case1_handshake()
    elif args.case == "2":
        result = workflow.case2_page_identification(args.target)
    elif args.case == "3":
        # 케이스3은 page_id가 필요하므로 케이스2를 먼저 실행
        case2_result = workflow.case2_page_identification(args.target)
        if case2_result["overall_status"] == "success":
            update_content = {"summary": ["테스트 업데이트"]}
            result = workflow.case3_content_update(case2_result["page_id"], update_content)
        else:
            result = case2_result
    else:  # all
        result = workflow.run_full_workflow(args.target)
    
    # 결과 출력
    print(f"\n📊 실행 결과: {result.get('overall_status', 'unknown')}")
    
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"결과 저장: {args.out}")
    
    return 0 if result.get('overall_status') == 'success' else 1

if __name__ == "__main__":
    exit(main())
