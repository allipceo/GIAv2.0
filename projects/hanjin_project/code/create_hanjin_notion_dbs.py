#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 심층 조사를 위한 노션 DB 생성 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업 프로젝트 Phase 0 노션 DB 생성 및 스키마 적용
"""

import requests
import json
import time
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"  # 검증된 노션 API 토큰
PARENT_PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"  # GIA_작업장 1단계

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_notion_database(db_name, properties, icon="🏢"):
    """
    노션 데이터베이스 생성
    """
    url = "https://api.notion.com/v1/databases"
    
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": PARENT_PAGE_ID
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": db_name
                }
            }
        ],
        "properties": properties,
        "icon": {
            "type": "emoji",
            "emoji": icon
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        db_id = result["id"]
        db_url = result["url"]
        
        print(f"✅ {db_name} 생성 완료!")
        print(f"   - DB ID: {db_id}")
        print(f"   - URL: {db_url}")
        
        return db_id, db_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ {db_name} 생성 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def create_risk_profile_db():
    """
    1. 기업 위험 프로파일 DB 생성 (리스크 매트릭스 메인)
    """
    print("\n🎯 1. 기업 위험 프로파일 DB 생성 중...")
    
    properties = {
        "리스크명": {
            "title": {}
        },
        "리스크 유형": {
            "select": {
                "options": [
                    {"name": "운영 리스크", "color": "red"},
                    {"name": "기술 리스크", "color": "orange"},
                    {"name": "법률 리스크", "color": "yellow"},
                    {"name": "재무 리스크", "color": "green"},
                    {"name": "사이버 리스크", "color": "blue"},
                    {"name": "환경 리스크", "color": "purple"}
                ]
            }
        },
        "리스크 설명": {
            "rich_text": {}
        },
        "발생 확률": {
            "select": {
                "options": [
                    {"name": "높음", "color": "red"},
                    {"name": "중간", "color": "yellow"},
                    {"name": "낮음", "color": "green"}
                ]
            }
        },
        "발생 확률 점수": {
            "number": {
                "format": "number"
            }
        },
        "영향도": {
            "select": {
                "options": [
                    {"name": "치명적", "color": "red"},
                    {"name": "심각", "color": "orange"},
                    {"name": "보통", "color": "yellow"},
                    {"name": "경미", "color": "green"}
                ]
            }
        },
        "영향도 점수": {
            "number": {
                "format": "number"
            }
        },
        "리스크 점수": {
            "formula": {
                "expression": "prop(\"발생 확률 점수\") * prop(\"영향도 점수\")"
            }
        },
        "리스크 등급": {
            "select": {
                "options": [
                    {"name": "매우 높음", "color": "red"},
                    {"name": "높음", "color": "orange"},
                    {"name": "보통", "color": "yellow"},
                    {"name": "낮음", "color": "green"},
                    {"name": "매우 낮음", "color": "blue"}
                ]
            }
        },
        "관련 사업부": {
            "multi_select": {
                "options": [
                    {"name": "중공업", "color": "red"},
                    {"name": "첨단소재", "color": "orange"},
                    {"name": "화학", "color": "yellow"},
                    {"name": "TNS", "color": "green"},
                    {"name": "전체", "color": "blue"}
                ]
            }
        },
        "대응 현황": {
            "select": {
                "options": [
                    {"name": "대응 완료", "color": "green"},
                    {"name": "대응 진행중", "color": "yellow"},
                    {"name": "대응 계획", "color": "orange"},
                    {"name": "미대응", "color": "red"}
                ]
            }
        },
        "최종 업데이트": {
            "last_edited_time": {}
        },
        "담당자": {
            "people": {}
        }
    }
    
    return create_notion_database("기업 위험 프로파일 DB", properties, "⚠️")

def create_financial_project_db():
    """
    2. 기업 재무 및 프로젝트 DB 생성
    """
    print("\n🎯 2. 기업 재무 및 프로젝트 DB 생성 중...")
    
    properties = {
        "항목명": {
            "title": {}
        },
        "데이터 유형": {
            "select": {
                "options": [
                    {"name": "재무", "color": "green"},
                    {"name": "프로젝트", "color": "blue"},
                    {"name": "IR", "color": "orange"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "수치값": {
            "number": {
                "format": "number"
            }
        },
        "단위": {
            "select": {
                "options": [
                    {"name": "억원", "color": "green"},
                    {"name": "조원", "color": "blue"},
                    {"name": "USD", "color": "orange"},
                    {"name": "%", "color": "yellow"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "기준일": {
            "date": {}
        },
        "전분기 대비": {
            "number": {
                "format": "percent"
            }
        },
        "전년 동기 대비": {
            "number": {
                "format": "percent"
            }
        },
        "사업 부문": {
            "multi_select": {
                "options": [
                    {"name": "중공업", "color": "red"},
                    {"name": "첨단소재", "color": "orange"},
                    {"name": "화학", "color": "yellow"},
                    {"name": "TNS", "color": "green"}
                ]
            }
        },
        "지역": {
            "select": {
                "options": [
                    {"name": "국내", "color": "blue"},
                    {"name": "해외", "color": "red"},
                    {"name": "아시아", "color": "yellow"},
                    {"name": "유럽", "color": "green"},
                    {"name": "미주", "color": "orange"}
                ]
            }
        },
        "중요도": {
            "select": {
                "options": [
                    {"name": "매우중요", "color": "red"},
                    {"name": "중요", "color": "orange"},
                    {"name": "보통", "color": "yellow"},
                    {"name": "참고", "color": "green"}
                ]
            }
        },
        "데이터 소스": {
            "url": {}
        },
        "수집일시": {
            "created_time": {}
        }
    }
    
    return create_notion_database("기업 재무 및 프로젝트 DB", properties, "💰")

def create_renewable_energy_db():
    """
    3. 신재생에너지 프로젝트 DB 생성
    """
    print("\n🎯 3. 신재생에너지 프로젝트 DB 생성 중...")
    
    properties = {
        "프로젝트명": {
            "title": {}
        },
        "프로젝트 유형": {
            "select": {
                "options": [
                    {"name": "태양광", "color": "yellow"},
                    {"name": "풍력", "color": "blue"},
                    {"name": "ESS", "color": "green"},
                    {"name": "수소", "color": "purple"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "프로젝트 규모": {
            "number": {
                "format": "number"
            }
        },
        "단위": {
            "select": {
                "options": [
                    {"name": "MW", "color": "blue"},
                    {"name": "MWh", "color": "green"},
                    {"name": "억원", "color": "red"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "지역": {
            "select": {
                "options": [
                    {"name": "국내", "color": "blue"},
                    {"name": "미국", "color": "red"},
                    {"name": "유럽", "color": "green"},
                    {"name": "아시아", "color": "yellow"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "진행 상태": {
            "select": {
                "options": [
                    {"name": "완료", "color": "green"},
                    {"name": "진행중", "color": "yellow"},
                    {"name": "계획", "color": "orange"},
                    {"name": "중단", "color": "red"}
                ]
            }
        },
        "시작일": {
            "date": {}
        },
        "완료일": {
            "date": {}
        },
        "한진중공업 역할": {
            "multi_select": {
                "options": [
                    {"name": "변압기", "color": "blue"},
                    {"name": "인버터", "color": "green"},
                    {"name": "ESS", "color": "yellow"},
                    {"name": "건설", "color": "orange"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "계약 금액": {
            "number": {
                "format": "number"
            }
        },
        "리스크 등급": {
            "select": {
                "options": [
                    {"name": "높음", "color": "red"},
                    {"name": "보통", "color": "yellow"},
                    {"name": "낮음", "color": "green"}
                ]
            }
        },
        "관련 정책": {
            "rich_text": {}
        },
        "데이터 소스": {
            "url": {}
        }
    }
    
    return create_notion_database("신재생에너지 프로젝트 DB", properties, "🌱")

def create_key_persons_db():
    """
    4. 핵심 인물 DB 생성
    """
    print("\n🎯 4. 핵심 인물 DB 생성 중...")
    
    properties = {
        "인물명": {
            "title": {}
        },
        "직책": {
            "select": {
                "options": [
                    {"name": "대표이사", "color": "red"},
                    {"name": "사장", "color": "orange"},
                    {"name": "부사장", "color": "yellow"},
                    {"name": "상무", "color": "green"},
                    {"name": "이사", "color": "blue"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "소속 부문": {
            "select": {
                "options": [
                    {"name": "중공업", "color": "red"},
                    {"name": "첨단소재", "color": "orange"},
                    {"name": "화학", "color": "yellow"},
                    {"name": "TNS", "color": "green"},
                    {"name": "지주회사", "color": "blue"}
                ]
            }
        },
        "담당 영역": {
            "multi_select": {
                "options": [
                    {"name": "경영총괄", "color": "red"},
                    {"name": "기술개발", "color": "blue"},
                    {"name": "영업", "color": "green"},
                    {"name": "재무", "color": "orange"},
                    {"name": "해외사업", "color": "purple"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "경력": {
            "rich_text": {}
        },
        "학력": {
            "rich_text": {}
        },
        "주요 성과": {
            "rich_text": {}
        },
        "연락처": {
            "email": {}
        },
        "중요도": {
            "select": {
                "options": [
                    {"name": "매우중요", "color": "red"},
                    {"name": "중요", "color": "orange"},
                    {"name": "보통", "color": "yellow"},
                    {"name": "참고", "color": "green"}
                ]
            }
        },
        "최종 업데이트": {
            "last_edited_time": {}
        }
    }
    
    return create_notion_database("핵심 인물 DB", properties, "👥")

def create_government_policy_db():
    """
    5. 정부 정책 DB 생성
    """
    print("\n🎯 5. 정부 정책 DB 생성 중...")
    
    properties = {
        "정책명": {
            "title": {}
        },
        "정책 분야": {
            "select": {
                "options": [
                    {"name": "신재생에너지", "color": "green"},
                    {"name": "수소", "color": "blue"},
                    {"name": "데이터센터", "color": "purple"},
                    {"name": "전력망", "color": "orange"},
                    {"name": "탄소중립", "color": "red"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "발표 기관": {
            "select": {
                "options": [
                    {"name": "산업통상자원부", "color": "blue"},
                    {"name": "기획재정부", "color": "green"},
                    {"name": "과학기술정보통신부", "color": "orange"},
                    {"name": "환경부", "color": "red"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "발표일": {
            "date": {}
        },
        "시행일": {
            "date": {}
        },
        "정책 내용": {
            "rich_text": {}
        },
        "한진중공업 영향": {
            "select": {
                "options": [
                    {"name": "매우 긍정", "color": "green"},
                    {"name": "긍정", "color": "yellow"},
                    {"name": "중립", "color": "gray"},
                    {"name": "부정", "color": "orange"},
                    {"name": "매우 부정", "color": "red"}
                ]
            }
        },
        "관련 사업부": {
            "multi_select": {
                "options": [
                    {"name": "중공업", "color": "red"},
                    {"name": "첨단소재", "color": "orange"},
                    {"name": "화학", "color": "yellow"},
                    {"name": "TNS", "color": "green"},
                    {"name": "전체", "color": "blue"}
                ]
            }
        },
        "예산 규모": {
            "number": {
                "format": "number"
            }
        },
        "정책 우선순위": {
            "select": {
                "options": [
                    {"name": "최우선", "color": "red"},
                    {"name": "우선", "color": "orange"},
                    {"name": "보통", "color": "yellow"},
                    {"name": "참고", "color": "green"}
                ]
            }
        },
        "관련 링크": {
            "url": {}
        },
        "수집일시": {
            "created_time": {}
        }
    }
    
    return create_notion_database("정부 정책 DB", properties, "🏛️")

def create_insurance_market_db():
    """
    6. 글로벌 보험중개 시장 DB 생성
    """
    print("\n🎯 6. 글로벌 보험중개 시장 DB 생성 중...")
    
    properties = {
        "회사명": {
            "title": {}
        },
        "회사 유형": {
            "select": {
                "options": [
                    {"name": "글로벌 보험중개사", "color": "blue"},
                    {"name": "국내 보험사", "color": "green"},
                    {"name": "해외 보험사", "color": "orange"},
                    {"name": "재보험사", "color": "red"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "본사 위치": {
            "select": {
                "options": [
                    {"name": "미국", "color": "red"},
                    {"name": "영국", "color": "blue"},
                    {"name": "독일", "color": "yellow"},
                    {"name": "일본", "color": "green"},
                    {"name": "한국", "color": "orange"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "연매출": {
            "number": {
                "format": "number"
            }
        },
        "직원 수": {
            "number": {
                "format": "number"
            }
        },
        "주요 서비스": {
            "multi_select": {
                "options": [
                    {"name": "기업보험", "color": "blue"},
                    {"name": "재보험", "color": "green"},
                    {"name": "컨설팅", "color": "orange"},
                    {"name": "리스크관리", "color": "red"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "한진중공업 경쟁력": {
            "select": {
                "options": [
                    {"name": "매우 우위", "color": "green"},
                    {"name": "우위", "color": "yellow"},
                    {"name": "동등", "color": "gray"},
                    {"name": "열세", "color": "orange"},
                    {"name": "매우 열세", "color": "red"}
                ]
            }
        },
        "주요 고객": {
            "rich_text": {}
        },
        "특화 영역": {
            "multi_select": {
                "options": [
                    {"name": "전력", "color": "blue"},
                    {"name": "건설", "color": "orange"},
                    {"name": "제조", "color": "green"},
                    {"name": "IT", "color": "purple"},
                    {"name": "기타", "color": "gray"}
                ]
            }
        },
        "록톤과의 관계": {
            "select": {
                "options": [
                    {"name": "파트너", "color": "green"},
                    {"name": "경쟁사", "color": "red"},
                    {"name": "잠재고객", "color": "yellow"},
                    {"name": "무관", "color": "gray"}
                ]
            }
        },
        "분석 메모": {
            "rich_text": {}
        },
        "데이터 소스": {
            "url": {}
        },
        "수집일시": {
            "created_time": {}
        }
    }
    
    return create_notion_database("글로벌 보험중개 시장 DB", properties, "🌍")

def main():
    """
    메인 실행 함수
    """
    print("="*80)
    print("🚀 한진중공업 프로젝트 Phase 0: 노션 DB 생성 시작")
    print("="*80)
    
    start_time = time.time()
    
    # 생성된 DB 정보 저장
    created_dbs = {}
    
    # 1. 기업 위험 프로파일 DB 생성
    db_id, db_url = create_risk_profile_db()
    if db_id:
        created_dbs["기업 위험 프로파일 DB"] = {"id": db_id, "url": db_url}
    
    # 2. 기업 재무 및 프로젝트 DB 생성
    db_id, db_url = create_financial_project_db()
    if db_id:
        created_dbs["기업 재무 및 프로젝트 DB"] = {"id": db_id, "url": db_url}
    
    # 3. 신재생에너지 프로젝트 DB 생성
    db_id, db_url = create_renewable_energy_db()
    if db_id:
        created_dbs["신재생에너지 프로젝트 DB"] = {"id": db_id, "url": db_url}
    
    # 4. 핵심 인물 DB 생성
    db_id, db_url = create_key_persons_db()
    if db_id:
        created_dbs["핵심 인물 DB"] = {"id": db_id, "url": db_url}
    
    # 5. 정부 정책 DB 생성
    db_id, db_url = create_government_policy_db()
    if db_id:
        created_dbs["정부 정책 DB"] = {"id": db_id, "url": db_url}
    
    # 6. 글로벌 보험중개 시장 DB 생성
    db_id, db_url = create_insurance_market_db()
    if db_id:
        created_dbs["글로벌 보험중개 시장 DB"] = {"id": db_id, "url": db_url}
    
    # 완료 보고
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "="*80)
    print("🎉 2-16단계 완료 보고")
    print("="*80)
    
    print(f"⏱️ 총 실행 시간: {execution_time:.2f}초")
    print(f"✅ 생성된 DB 수: {len(created_dbs)}/6개")
    
    print("\n📋 생성된 DB 목록:")
    for db_name, db_info in created_dbs.items():
        print(f"  - {db_name}")
        print(f"    • ID: {db_info['id']}")
        print(f"    • URL: {db_info['url']}")
    
    # 결과를 JSON 파일로 저장
    result_file = f"../data/hanjin_dbs_created_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(created_dbs, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과 파일 저장: {result_file}")
    print("🎯 2-16단계 완료!")
    
    return created_dbs

if __name__ == "__main__":
    result = main() 