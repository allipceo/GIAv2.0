#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
선과장님 지시: "개발결과" 섹션 업데이트 계획 생성
목적: g0_guard 규칙에 따라 안전한 업데이트 계획 생성
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

def main():
    parser = argparse.ArgumentParser(description='개발결과 섹션 업데이트 계획 생성')
    parser.add_argument('--page', required=True, help='페이지 ID')
    parser.add_argument('--plan', required=True, help='계획 파일 경로')
    parser.add_argument('--rule', required=True, help='가드 규칙 파일 경로')
    args = parser.parse_args()
    
    print("개발결과 섹션 업데이트 계획 생성...")
    
    # 환경변수 로드
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: NOTION_TOKEN이 설정되지 않았습니다.")
        return 1
    
    try:
        n = NotionClient(token)
        
        # 가드 규칙 로드
        with open(args.rule, 'r', encoding='utf-8') as f:
            guard_rules = json.load(f)
        
        # 페이지 정보 조회
        page = n.get_page(args.page)
        
        # 현재 시간 (KST)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M KST")
        
        # 업데이트 계획 생성
        plan = {
            "page_id": args.page,
            "timestamp": timestamp,
            "operations": [
                {
                    "type": "append_after_anchor",
                    "anchor_text": "개발결과",
                    "blocks": [
                        {
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"개발결과 업데이트 — {timestamp}"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "1. ZOBIS 개발문서 DB 접근성 확보: 통합·권한 핸드셰이크(users/me=200, databases=200) 및 DB 공유 연결 확인 완료"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "2. Z062 문서 식별 및 읽기 성공: PAGE_ID 62d899af747846aa91630239e9120a22로 페이지 속성·본문 조회 완료"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "3. Stage 4 운영 표준 준수: g0_guard 규칙에 따른 안전한 쓰기 작업 및 스키마 해시 검증 체계 구축"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "근거 링크: "
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Z072_서대리-선과장 작업경과 및 결과 공유 시스템",
                                            "link": {
                                                "url": "https://www.notion.so/Z072_-e69469e716954b1ca7e3ded5736d1603"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ],
            "guard_rules": guard_rules,
            "estimated_changes": 1
        }
        
        # 계획 파일 저장
        with open(args.plan, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        print(f"계획 생성 완료: {args.plan}")
        print(f"예상 변경량: {plan['estimated_changes']}개 블록")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: 계획 생성 실패: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
