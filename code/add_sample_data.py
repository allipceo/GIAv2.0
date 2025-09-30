#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 프로젝트 샘플 데이터 생성 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 과업지시서 V1.2에 따른 3단계 자동화 워크플로우 연동 - 샘플 데이터 생성
"""

import requests
import json
from datetime import datetime, timedelta

# 노션 API 설정
NOTION_TOKEN = ""
COMPANY_DB_ID = "253a613d-25ff-819b-acfe-fa0547939de1"  # 조사 대상 기업 DB
REPORT_DB_ID = "253a613d-25ff-8161-b357-e6b56237fc0d"   # 생성된 보고서/전략 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_company_data():
    """조사 대상 기업 DB에 샘플 데이터 추가"""
    url = "https://api.notion.com/v1/pages"
    
    # 샘플 기업 데이터
    companies = [
        {
            "name": "한진중공업",
            "status": "Phase 1 - 심화 조사",
            "progress": 60,
            "assignee": "서대리",
            "phase3_check": False,
            "execution_status": "대기중",
            "execution_time": None,
            "execution_result": "",
            "created_date": datetime.now() - timedelta(days=5),
            "last_modified": datetime.now() - timedelta(days=1),
            "remarks": "해외 원전 사업 진출 검토 중"
        },
        {
            "name": "효성중공업",
            "status": "Phase 0 - 기초 조사",
            "progress": 30,
            "assignee": "서대리",
            "phase3_check": False,
            "execution_status": "실행중",
            "execution_time": datetime.now() - timedelta(hours=2),
            "execution_result": "데이터 수집 진행 중",
            "created_date": datetime.now() - timedelta(days=3),
            "last_modified": datetime.now(),
            "remarks": "신재생 에너지 기술 보험 검토"
        },
        {
            "name": "두산에너빌리티",
            "status": "Phase 2 - 분석 완료",
            "progress": 100,
            "assignee": "나실장",
            "phase3_check": True,
            "execution_status": "완료",
            "execution_time": datetime.now() - timedelta(days=1),
            "execution_result": "해외 원전 특화 보험 제안서 완성",
            "created_date": datetime.now() - timedelta(days=10),
            "last_modified": datetime.now() - timedelta(days=1),
            "remarks": "해외 원전 특화 보험 제안 완료"
        }
    ]
    
    success_count = 0
    
    for company in companies:
        payload = {
            "parent": {
                "database_id": COMPANY_DB_ID
            },
            "properties": {
                "기업명": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": company["name"]
                            }
                        }
                    ]
                },
                "조사 상태": {
                    "select": {
                        "name": company["status"]
                    }
                },
                "진행률": {
                    "number": company["progress"]
                },
                "담당자": {
                    "select": {
                        "name": company["assignee"]
                    }
                },
                "Phase 3 분석 실행": {
                    "checkbox": company["phase3_check"]
                },
                "실행 상태": {
                    "select": {
                        "name": company["execution_status"]
                    }
                },
                "실행 일시": {
                    "date": {
                        "start": company["execution_time"].isoformat() if company["execution_time"] else None
                    }
                },
                "실행 결과": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": company["execution_result"]
                            }
                        }
                    ]
                },
                "생성일": {
                    "date": {
                        "start": company["created_date"].isoformat()
                    }
                },
                "최종 수정일": {
                    "date": {
                        "start": company["last_modified"].isoformat()
                    }
                },
                "비고": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": company["remarks"]
                            }
                        }
                    ]
                }
            }
        }
        
        try:
            response = requests.post(url, headers=HEADERS, json=payload)
            response.raise_for_status()
            success_count += 1
            print(f"✅ {company['name']} 데이터 추가 성공")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {company['name']} 데이터 추가 실패: {e}")
    
    return success_count

def add_report_data():
    """생성된 보고서/전략 DB에 샘플 데이터 추가"""
    url = "https://api.notion.com/v1/pages"
    
    # 샘플 보고서 데이터
    reports = [
        {
            "name": "두산에너빌리티 해외 원전 특화 보험 제안서",
            "related_company": "두산에너빌리티",
            "created_time": datetime.now() - timedelta(days=1),
            "summary": "해외 원전 사업의 특수성을 고려한 맞춤형 보험 제안서",
            "type": "전략 제안서",
            "author": "나실장",
            "status": "승인됨",
            "version": 1.0,
            "created_date": datetime.now() - timedelta(days=2),
            "last_modified": datetime.now() - timedelta(days=1)
        },
        {
            "name": "효성중공업 신재생 에너지 기술 보험 분석 보고서",
            "related_company": "효성중공업",
            "created_time": datetime.now() - timedelta(hours=3),
            "summary": "신재생 에너지 기술의 리스크 분석 및 보험 적용 방안",
            "type": "기초 조사 보고서",
            "author": "서대리",
            "status": "작성중",
            "version": 0.5,
            "created_date": datetime.now() - timedelta(days=1),
            "last_modified": datetime.now() - timedelta(hours=3)
        },
        {
            "name": "한진중공업 해외 사업 진출 리스크 분석",
            "related_company": "한진중공업",
            "created_time": datetime.now() - timedelta(days=2),
            "summary": "해외 원전 사업 진출 시 예상되는 리스크 및 대응 방안",
            "type": "리스크 분석",
            "author": "노팀장",
            "status": "검토중",
            "version": 1.2,
            "created_date": datetime.now() - timedelta(days=3),
            "last_modified": datetime.now() - timedelta(days=2)
        }
    ]
    
    success_count = 0
    
    for report in reports:
        payload = {
            "parent": {
                "database_id": REPORT_DB_ID
            },
            "properties": {
                "보고서명": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": report["name"]
                            }
                        }
                    ]
                },
                "관련 기업": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": report["related_company"]
                            }
                        }
                    ]
                },
                "생성 일시": {
                    "date": {
                        "start": report["created_time"].isoformat()
                    }
                },
                "핵심 요약": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": report["summary"]
                            }
                        }
                    ]
                },
                "보고서 유형": {
                    "select": {
                        "name": report["type"]
                    }
                },
                "작성자": {
                    "select": {
                        "name": report["author"]
                    }
                },
                "상태": {
                    "select": {
                        "name": report["status"]
                    }
                },
                "버전": {
                    "number": report["version"]
                },
                "생성일": {
                    "date": {
                        "start": report["created_date"].isoformat()
                    }
                },
                "최종 수정일": {
                    "date": {
                        "start": report["last_modified"].isoformat()
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, headers=HEADERS, json=payload)
            response.raise_for_status()
            success_count += 1
            print(f"✅ {report['name']} 데이터 추가 성공")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {report['name']} 데이터 추가 실패: {e}")
    
    return success_count

def main():
    """메인 실행 함수"""
    print("🚀 3단계: 자동화 워크플로우 연동 - 샘플 데이터 생성 시작...")
    print("=" * 70)
    
    # 1. 조사 대상 기업 DB에 샘플 데이터 추가
    print("📋 3-1. 조사 대상 기업 DB에 샘플 데이터 추가 중...")
    company_success = add_company_data()
    print(f"✅ 기업 데이터 {company_success}개 추가 완료")
    
    # 2. 생성된 보고서/전략 DB에 샘플 데이터 추가
    print("\n📋 3-2. 생성된 보고서/전략 DB에 샘플 데이터 추가 중...")
    report_success = add_report_data()
    print(f"✅ 보고서 데이터 {report_success}개 추가 완료")
    
    print(f"\n🎉 3단계 샘플 데이터 생성 완료!")
    print(f"📊 총 {company_success + report_success}개의 샘플 데이터가 추가되었습니다.")
    print(f"\n📝 다음 단계: 대시보드에서 실제 데이터 확인 및 자동화 워크플로우 테스트")

if __name__ == "__main__":
    main()
