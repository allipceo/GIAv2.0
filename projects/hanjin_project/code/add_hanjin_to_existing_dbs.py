#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 6개 정보 DB에 한진중공업 항목 추가 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업 프로젝트 Phase 0 - 기존 DB에 한진중공업 항목 추가
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = ""  # 검증된 노션 API 토큰

# 기존 6개 정보 DB ID
DB_IDS = {
    "기업위험 프로파일 DB": "234a613d25ff815a96b5e321b62b08a1",
    "기업재무 및 프로젝트 DB": "234a613d25ff81aba93ae4cb8f36c920",
    "신재생에너지 프로젝트 DB": "234a613d25ff81b5a9a3f01a46bdaab8",
    "핵심인물 DB": "234a613d25ff81f08d29f5ccc2d15e6e",
    "정부정책 DB": "234a613d25ff81d393addb6970db66a8",
    "글로벌보험중개 시장 DB": "234a613d25ff818fb525d84d366e5adf"
}

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_hanjin_to_risk_profile_db():
    """기업위험 프로파일 DB에 한진중공업 항목 추가"""
    print("\n🎯 기업위험 프로파일 DB에 한진중공업 항목 추가 중...")
    
    url = "https://api.notion.com/v1/pages"
    db_id = DB_IDS["기업위험 프로파일 DB"]
    
    payload = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "리스크명": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 - 기본 리스크 프로파일"
                        }
                    }
                ]
            },
            "리스크 유형": {
                "select": {
                    "name": "운영 리스크"
                }
            },
            "리스크 설명": {
                "rich_text": [
                    {
                        "text": {
                            "content": "한진중공업의 기본 리스크 프로파일을 분석하기 위한 초기 항목입니다."
                        }
                    }
                ]
            },
            "발생 확률": {
                "select": {
                    "name": "중간"
                }
            },
            "영향도": {
                "select": {
                    "name": "보통"
                }
            },
            "관련 사업부": {
                "multi_select": [
                    {
                        "name": "중공업"
                    }
                ]
            },
            "대응 현황": {
                "select": {
                    "name": "대응 계획"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 기업위험 프로파일 DB에 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 기업위험 프로파일 DB 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def add_hanjin_to_financial_db():
    """기업재무 및 프로젝트 DB에 한진중공업 항목 추가"""
    print("\n🎯 기업재무 및 프로젝트 DB에 한진중공업 항목 추가 중...")
    
    url = "https://api.notion.com/v1/pages"
    db_id = DB_IDS["기업재무 및 프로젝트 DB"]
    
    payload = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "항목명": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 - 2024년 매출"
                        }
                    }
                ]
            },
            "데이터 유형": {
                "select": {
                    "name": "재무"
                }
            },
            "수치값": {
                "number": 11648  # 1조 1,648억원
            },
            "단위": {
                "select": {
                    "name": "억원"
                }
            },
            "기준일": {
                "date": {
                    "start": "2024-12-31"
                }
            },
            "사업 부문": {
                "multi_select": [
                    {
                        "name": "중공업"
                    }
                ]
            },
            "중요도": {
                "select": {
                    "name": "매우중요"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 기업재무 및 프로젝트 DB에 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 기업재무 및 프로젝트 DB 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def add_hanjin_to_renewable_energy_db():
    """신재생에너지 프로젝트 DB에 한진중공업 항목 추가"""
    print("\n🎯 신재생에너지 프로젝트 DB에 한진중공업 항목 추가 중...")
    
    url = "https://api.notion.com/v1/pages"
    db_id = DB_IDS["신재생에너지 프로젝트 DB"]
    
    payload = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "프로젝트명": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 - 신재생에너지 프로젝트 모니터링"
                        }
                    }
                ]
            },
            "프로젝트 유형": {
                "select": {
                    "name": "기타"
                }
            },
            "지역": {
                "select": {
                    "name": "국내"
                }
            },
            "진행 상태": {
                "select": {
                    "name": "계획"
                }
            },
            "기업 역할": {
                "multi_select": [
                    {
                        "name": "기타"
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 신재생에너지 프로젝트 DB에 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 신재생에너지 프로젝트 DB 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def add_hanjin_to_key_persons_db():
    """핵심인물 DB에 한진중공업 항목 추가"""
    print("\n🎯 핵심인물 DB에 한진중공업 항목 추가 중...")
    
    url = "https://api.notion.com/v1/pages"
    db_id = DB_IDS["핵심인물 DB"]
    
    payload = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "인물명": {
                "title": [
                    {
                        "text": {
                            "content": "조원국"
                        }
                    }
                ]
            },
            "직책": {
                "select": {
                    "name": "대표이사"
                }
            },
            "소속 부문": {
                "select": {
                    "name": "중공업"
                }
            },
            "담당 영역": {
                "multi_select": [
                    {
                        "name": "경영총괄"
                    }
                ]
            },
            "중요도": {
                "select": {
                    "name": "매우중요"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 핵심인물 DB에 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 핵심인물 DB 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def add_hanjin_to_government_policy_db():
    """정부정책 DB에 한진중공업 항목 추가"""
    print("\n🎯 정부정책 DB에 한진중공업 항목 추가 중...")
    
    url = "https://api.notion.com/v1/pages"
    db_id = DB_IDS["정부정책 DB"]
    
    payload = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "정책명": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 관련 정책 모니터링"
                        }
                    }
                ]
            },
            "정책 분야": {
                "select": {
                    "name": "신재생에너지"
                }
            },
            "발표 기관": {
                "select": {
                    "name": "산업통상자원부"
                }
            },
            "기업 영향": {
                "select": {
                    "name": "중립"
                }
            },
            "관련 사업부": {
                "multi_select": [
                    {
                        "name": "중공업"
                    }
                ]
            },
            "정책 우선순위": {
                "select": {
                    "name": "보통"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 정부정책 DB에 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 정부정책 DB 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def add_hanjin_to_insurance_market_db():
    """글로벌보험중개 시장 DB에 한진중공업 항목 추가"""
    print("\n🎯 글로벌보험중개 시장 DB에 한진중공업 항목 추가 중...")
    
    url = "https://api.notion.com/v1/pages"
    db_id = DB_IDS["글로벌보험중개 시장 DB"]
    
    payload = {
        "parent": {
            "database_id": db_id
        },
        "properties": {
            "회사명": {
                "title": [
                    {
                        "text": {
                            "content": "한진중공업 (HJ중공업)"
                        }
                    }
                ]
            },
            "회사 유형": {
                "select": {
                    "name": "기타"
                }
            },
            "본사 위치": {
                "select": {
                    "name": "한국"
                }
            },
            "기업 경쟁력": {
                "select": {
                    "name": "동등"
                }
            },
            "록톤과의 관계": {
                "select": {
                    "name": "잠재고객"
                }
            },
            "특화 영역": {
                "multi_select": [
                    {
                        "name": "전력"
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 글로벌보험중개 시장 DB에 한진중공업 항목 추가 완료!")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return page_id, page_url
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 글로벌보험중개 시장 DB 항목 추가 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None, None

def main():
    """
    메인 실행 함수
    """
    print("="*80)
    print("🚀 한진중공업 프로젝트 Phase 0: 기존 DB에 한진중공업 항목 추가")
    print("="*80)
    
    # 생성된 항목 정보 저장
    created_items = {}
    
    # 1. 기업위험 프로파일 DB에 항목 추가
    page_id, page_url = add_hanjin_to_risk_profile_db()
    if page_id:
        created_items["기업위험 프로파일 DB"] = {"id": page_id, "url": page_url}
    
    # 2. 기업재무 및 프로젝트 DB에 항목 추가
    page_id, page_url = add_hanjin_to_financial_db()
    if page_id:
        created_items["기업재무 및 프로젝트 DB"] = {"id": page_id, "url": page_url}
    
    # 3. 신재생에너지 프로젝트 DB에 항목 추가
    page_id, page_url = add_hanjin_to_renewable_energy_db()
    if page_id:
        created_items["신재생에너지 프로젝트 DB"] = {"id": page_id, "url": page_url}
    
    # 4. 핵심인물 DB에 항목 추가
    page_id, page_url = add_hanjin_to_key_persons_db()
    if page_id:
        created_items["핵심인물 DB"] = {"id": page_id, "url": page_url}
    
    # 5. 정부정책 DB에 항목 추가
    page_id, page_url = add_hanjin_to_government_policy_db()
    if page_id:
        created_items["정부정책 DB"] = {"id": page_id, "url": page_url}
    
    # 6. 글로벌보험중개 시장 DB에 항목 추가
    page_id, page_url = add_hanjin_to_insurance_market_db()
    if page_id:
        created_items["글로벌보험중개 시장 DB"] = {"id": page_id, "url": page_url}
    
    # 완료 보고
    print("\n" + "="*80)
    print("🎉 한진중공업 항목 추가 완료 보고")
    print("="*80)
    
    print(f"✅ 추가된 항목 수: {len(created_items)}/6개")
    
    print("\n📋 추가된 항목 목록:")
    for db_name, item_info in created_items.items():
        print(f"  - {db_name}")
        print(f"    • ID: {item_info['id']}")
        print(f"    • URL: {item_info['url']}")
    
    # 결과를 JSON 파일로 저장
    result_file = f"../data/hanjin_items_added_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(created_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과 파일 저장: {result_file}")
    print("🎯 한진중공업 항목 추가 완료!")
    
    return created_items

if __name__ == "__main__":
    main() 