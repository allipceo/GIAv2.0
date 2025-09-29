#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조사 대상 기업 DB 생성 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 과업지시서 V1.2에 따른 핵심 DB 구축 - 1단계
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"
PARENT_PAGE_ID = "227a613d-25ff-800c-a97d-e24f6eb521a8"  # 조대표님 워크스페이스 페이지 ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_company_database():
    """조사 대상 기업 DB 생성"""
    url = "https://api.notion.com/v1/databases"
    
    # 설계도 V2.0에 따른 속성 정의
    properties = {
        "기업명": {
            "title": {}
        },
        "조사 상태": {
            "select": {
                "options": [
                    {"name": "Phase 0 - 기초 조사", "color": "blue"},
                    {"name": "Phase 1 - 심화 조사", "color": "yellow"},
                    {"name": "Phase 2 - 분석 완료", "color": "green"},
                    {"name": "Phase 3 - 전략 수립", "color": "purple"},
                    {"name": "완료", "color": "gray"}
                ]
            }
        },
        "진행률": {
            "number": {
                "format": "percent"
            }
        },
        "담당자": {
            "select": {
                "options": [
                    {"name": "나실장", "color": "blue"},
                    {"name": "노팀장", "color": "yellow"},
                    {"name": "서대리", "color": "green"}
                ]
            }
        },
        "Phase 3 분석 실행": {
            "checkbox": {}
        },
        "실행 상태": {
            "select": {
                "options": [
                    {"name": "대기중", "color": "gray"},
                    {"name": "실행중", "color": "yellow"},
                    {"name": "완료", "color": "green"},
                    {"name": "오류", "color": "red"}
                ]
            }
        },
        "실행 일시": {
            "date": {}
        },
        "실행 결과": {
            "rich_text": {}
        },
        "생성일": {
            "date": {}
        },
        "최종 수정일": {
            "date": {}
        },
        "비고": {
            "rich_text": {}
        }
    }
    
    payload = {
        "parent": {
            "page_id": PARENT_PAGE_ID
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "조사 대상 기업"
                }
            }
        ],
        "properties": properties,
        "description": [
            {
                "type": "text",
                "text": {
                    "content": "GIA 프로젝트 조사 대상 기업 관리 DB"
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        database_id = result["id"]
        
        print(f"✅ 조사 대상 기업 DB 생성 성공!")
        print(f"📋 DB ID: {database_id}")
        print(f"📋 DB URL: {result.get('url', 'N/A')}")
        
        # DB ID를 파일에 저장
        with open('company_database_id.txt', 'w') as f:
            f.write(database_id)
        
        return database_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ DB 생성 실패: {e}")
        return None

def create_report_database():
    """생성된 보고서/전략 DB 생성"""
    url = "https://api.notion.com/v1/databases"
    
    # 설계도 V2.0에 따른 속성 정의
    properties = {
        "보고서명": {
            "title": {}
        },
        "관련 기업": {
            "rich_text": {}  # 임시로 rich_text로 변경, 나중에 relation으로 업데이트
        },
        "생성 일시": {
            "date": {}
        },
        "핵심 요약": {
            "rich_text": {}
        },
        "보고서 유형": {
            "select": {
                "options": [
                    {"name": "기초 조사 보고서", "color": "blue"},
                    {"name": "심화 분석 보고서", "color": "yellow"},
                    {"name": "전략 제안서", "color": "green"},
                    {"name": "리스크 분석", "color": "red"},
                    {"name": "영업 전략", "color": "purple"}
                ]
            }
        },
        "작성자": {
            "select": {
                "options": [
                    {"name": "나실장", "color": "blue"},
                    {"name": "노팀장", "color": "yellow"},
                    {"name": "서대리", "color": "green"}
                ]
            }
        },
        "상태": {
            "select": {
                "options": [
                    {"name": "작성중", "color": "yellow"},
                    {"name": "검토중", "color": "blue"},
                    {"name": "완료", "color": "green"},
                    {"name": "승인됨", "color": "purple"}
                ]
            }
        },
        "버전": {
            "number": {
                "format": "number"
            }
        },
        "생성일": {
            "date": {}
        },
        "최종 수정일": {
            "date": {}
        }
    }
    
    payload = {
        "parent": {
            "page_id": PARENT_PAGE_ID
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "생성된 보고서/전략"
                }
            }
        ],
        "properties": properties,
        "description": [
            {
                "type": "text",
                "text": {
                    "content": "GIA 프로젝트에서 생성된 보고서 및 전략 관리 DB"
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        database_id = result["id"]
        
        print(f"✅ 생성된 보고서/전략 DB 생성 성공!")
        print(f"📋 DB ID: {database_id}")
        print(f"📋 DB URL: {result.get('url', 'N/A')}")
        
        # DB ID를 파일에 저장
        with open('report_database_id.txt', 'w') as f:
            f.write(database_id)
        
        return database_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ DB 생성 실패: {e}")
        return None

def main():
    """메인 실행 함수"""
    print("🚀 1단계: 핵심 DB 구축 시작...")
    print("=" * 50)
    
    # 1. 조사 대상 기업 DB 생성
    print("📋 1-1. 조사 대상 기업 DB 생성 중...")
    company_db_id = create_company_database()
    
    if not company_db_id:
        print("❌ 조사 대상 기업 DB 생성 실패. 중단합니다.")
        return
    
    # 2. 생성된 보고서/전략 DB 생성
    print("\n📋 1-2. 생성된 보고서/전략 DB 생성 중...")
    report_db_id = create_report_database()
    
    if not report_db_id:
        print("❌ 생성된 보고서/전략 DB 생성 실패. 중단합니다.")
        return
    
    # 3. 관계형 연결 설정
    print("\n🔗 1-3. 관계형 연결 설정 중...")
    # TODO: 두 DB 간의 관계형 연결 설정
    
    print("\n🎉 1단계 핵심 DB 구축 완료!")
    print("=" * 50)
    print(f"✅ 조사 대상 기업 DB: {company_db_id}")
    print(f"✅ 생성된 보고서/전략 DB: {report_db_id}")
    print("\n📝 다음 단계: 2단계 대시보드 페이지 UI/UX 프로토타입 구현")

if __name__ == "__main__":
    main()
