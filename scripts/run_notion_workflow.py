#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 협업 워크플로우 실행 스크립트
목적: 케이스1,2,3의 재활용 가능한 통합 실행
"""

import os
import sys
import argparse
import json
from datetime import datetime

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.workflows.notion_collaboration import NotionCollaborationWorkflow

def main():
    parser = argparse.ArgumentParser(description="Notion 협업 워크플로우 실행")
    parser.add_argument("--case", choices=["1", "2", "3", "all"], default="all", 
                       help="실행할 케이스 (1: 핸드셰이크, 2: 페이지식별, 3: 뉴스등록, all: 전체)")
    parser.add_argument("--target", default="Z062", help="대상 키워드 (기본값: Z062)")
    parser.add_argument("--out", help="결과 저장 파일 경로")
    parser.add_argument("--config", default="config.env", help="설정 파일 경로")
    parser.add_argument("--verbose", action="store_true", help="상세 로그 출력")
    args = parser.parse_args()
    
    print("🚀 Notion 협업 워크플로우 실행 시작...")
    print(f"실행 케이스: {args.case}")
    print(f"대상 키워드: {args.target}")
    print(f"설정 파일: {args.config}")
    
    try:
        # 워크플로우 초기화
        workflow = NotionCollaborationWorkflow(args.config)
        
        if not workflow.client:
            print("❌ ERROR: NotionClient 초기화 실패")
            print("config.env 파일의 NOTION_TOKEN과 TARGET_DATABASE_ID를 확인하세요.")
            return 1
        
        # 케이스별 실행
        if args.case == "1":
            print("\n📋 케이스1: 통합·권한 핸드셰이크 실행...")
            result = workflow.case1_handshake()
            
        elif args.case == "2":
            print(f"\n📋 케이스2: '{args.target}' 페이지 식별 실행...")
            result = workflow.case2_page_identification(args.target)
            
        elif args.case == "3":
            print(f"\n📋 케이스3: '{args.target}' 뉴스클리핑 DB 등록 실행...")
            news_data = {
                "title": f"[파일럿] {args.target} 관련 뉴스 테스트 등록",
                "url": f"https://example.com/{args.target.lower()}-news",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "테스트 매체",
                "category": "해상풍력발전",
                "importance": "보통"
            }
            result = workflow.case3_news_registration(news_data)
                
        else:  # all
            print(f"\n📋 전체 워크플로우: '{args.target}' 대상 전체 실행...")
            result = workflow.run_full_workflow(args.target)
        
        # 결과 출력
        print(f"\n📊 실행 결과: {result.get('overall_status', 'unknown')}")
        
        if args.verbose:
            print("\n🔍 상세 결과:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 결과 저장
        if args.out:
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
            with open(args.out, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"📁 결과 저장: {args.out}")
        
        # 성공/실패 판정
        if result.get('overall_status') == 'success':
            print("✅ 워크플로우 실행 성공!")
            return 0
        else:
            print("❌ 워크플로우 실행 실패!")
            return 1
            
    except Exception as e:
        print(f"❌ ERROR: 워크플로우 실행 중 오류 발생: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
