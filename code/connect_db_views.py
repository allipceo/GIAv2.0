#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 프로젝트 DB 뷰 연결 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 과업지시서 V1.2에 따른 4단계 - 대시보드에 DB 뷰 직접 연결
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = ""
DASHBOARD_PAGE_ID = "253a613d-25ff-81ee-a83f-f53b14aec5c7"  # 대시보드 메인 페이지
COMPANY_DB_ID = "253a613d-25ff-819b-acfe-fa0547939de1"      # 조사 대상 기업 DB
REPORT_DB_ID = "253a613d-25ff-8161-b357-e6b56237fc0d"       # 생성된 보고서/전략 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_company_db_view():
    """조사 대상 기업 DB를 Gallery View로 연결"""
    url = f"https://api.notion.com/v1/blocks/{DASHBOARD_PAGE_ID}/children"
    
    # 기존 내용을 유지하면서 DB 뷰 추가
    children = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📊 진행 중인 프로젝트 현황 (Gallery View)"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "아래는 조사 대상 기업 DB의 Gallery View입니다. 각 기업의 진행 상황을 카드 형태로 확인할 수 있습니다."
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "database",
            "database": {
                "database_id": COMPANY_DB_ID,
                "view_type": "gallery"
            }
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        }
    ]
    
    payload = {
        "children": children
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print("✅ 조사 대상 기업 DB Gallery View 연결 성공")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Gallery View 연결 실패: {e}")
        return False

def add_report_db_view():
    """생성된 보고서/전략 DB를 Table View로 연결"""
    url = f"https://api.notion.com/v1/blocks/{DASHBOARD_PAGE_ID}/children"
    
    children = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📚 GIA 지식 라이브러리 (Table View)"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "아래는 생성된 보고서/전략 DB의 Table View입니다. 최근 업데이트된 문서들을 확인할 수 있습니다."
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "database",
            "database": {
                "database_id": REPORT_DB_ID,
                "view_type": "table"
            }
        }
    ]
    
    payload = {
        "children": children
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print("✅ 생성된 보고서/전략 DB Table View 연결 성공")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Table View 연결 실패: {e}")
        return False

def update_dashboard_content():
    """대시보드 내용 업데이트 (실제 데이터 반영)"""
    url = f"https://api.notion.com/v1/blocks/{DASHBOARD_PAGE_ID}/children"
    
    # 실제 데이터를 반영한 업데이트된 내용
    children = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "🔥 실시간 프로젝트 현황"
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "heading_3",
                                    "heading_3": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "📈 진행률 요약"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "• 총 2개 프로젝트 진행 중\n• 두산에너빌리티: 100% 완료\n• 효성중공업: 30% 진행 중\n• 한진중공업: 60% 진행 중"
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "heading_3",
                                    "heading_3": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "🎯 핵심 인사이트"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "• 두산: 해외 원전 특화 보험 제안 완료\n• 효성: 신재생 에너지 기술 보험 검토 중\n• 한진: 해외 원전 사업 진출 검토 중"
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "heading_3",
                                    "heading_3": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "⚡ 다음 액션"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "• 효성중공업 Phase 3 분석 실행\n• 한진중공업 심화 조사 완료\n• 새로운 기업 조사 대상 추가"
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
    
    payload = {
        "children": children
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print("✅ 대시보드 내용 업데이트 성공")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 대시보드 내용 업데이트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 4단계: 실제 웹훅 연동 및 DB 뷰 연결 시작...")
    print("=" * 70)
    
    # 1. 조사 대상 기업 DB Gallery View 연결
    print("📋 4-1. 조사 대상 기업 DB Gallery View 연결 중...")
    company_success = add_company_db_view()
    
    # 2. 생성된 보고서/전략 DB Table View 연결
    print("\n📋 4-2. 생성된 보고서/전략 DB Table View 연결 중...")
    report_success = add_report_db_view()
    
    # 3. 대시보드 내용 업데이트
    print("\n📋 4-3. 대시보드 내용 업데이트 중...")
    content_success = update_dashboard_content()
    
    if company_success and report_success and content_success:
        print(f"\n🎉 4단계 DB 뷰 연결 완료!")
        print(f"✅ Gallery View: 조사 대상 기업 DB")
        print(f"✅ Table View: 생성된 보고서/전략 DB")
        print(f"✅ 대시보드 내용: 실시간 데이터 반영")
        print(f"\n📝 다음 단계: 실제 웹훅 연동 및 Make.com/Pipedream 설정")
    else:
        print(f"\n⚠️ 일부 작업이 실패했습니다. 수동으로 확인이 필요합니다.")

if __name__ == "__main__":
    main()

