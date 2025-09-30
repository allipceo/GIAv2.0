#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
생성된 보고서/전략 DB 생성 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 과업지시서 V1.2에 따른 핵심 DB 구축 - 보고서/전략 DB만 생성
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = ""
PARENT_PAGE_ID = "227a613d-25ff-800c-a97d-e24f6eb521a8"  # 조대표님 워크스페이스 페이지 ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

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
    print("🚀 생성된 보고서/전략 DB 생성 시작...")
    print("=" * 50)
    
    # 생성된 보고서/전략 DB 생성
    report_db_id = create_report_database()
    
    if report_db_id:
        print(f"\n🎉 생성된 보고서/전략 DB 생성 완료!")
        print(f"📋 DB ID: {report_db_id}")
        print(f"\n📝 다음 단계: 2단계 대시보드 페이지 UI/UX 프로토타입 구현")
    else:
        print(f"\n❌ 생성된 보고서/전략 DB 생성 실패.")

if __name__ == "__main__":
    main()
