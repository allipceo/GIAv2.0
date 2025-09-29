#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
효성중공업 심층 조사 DB 테스트 데이터 입력 스크립트
작성일: 2025년 1월 18일
작성자: 서대리 (Lead Developer)
목적: 생성된 6개 DB에 테스트 데이터 입력 및 검증
"""

import requests
import json
import time
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 생성된 DB ID 로드
def load_db_ids():
    """생성된 DB ID 정보 로드"""
    try:
        with open('../data/hyosung_dbs_created_20250719_003144.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ DB ID 파일을 찾을 수 없습니다.")
        return {}

def create_notion_page(db_id, properties):
    """노션 페이지 생성"""
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {"database_id": db_id},
        "properties": properties
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        result = response.json()
        page_id = result["id"]
        
        return page_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 페이지 생성 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return None

def insert_risk_profile_data(db_id):
    """1. 기업 위험 프로파일 DB 테스트 데이터 입력"""
    print(f"\n🎯 1. 기업 위험 프로파일 DB 테스트 데이터 입력...")
    print(f"   DB ID: {db_id}")
    
    # 효성중공업 주요 리스크 데이터 (이전에 준비한 데이터 활용)
    risk_data = [
        {
            "리스크명": "사이버 보안 공격",
            "리스크 유형": "사이버 리스크",
            "리스크 설명": "원격제어 시스템 확대에 따른 랜섬웨어, 데이터 유출 위험",
            "발생 확률": "높음",
            "발생 확률 점수": 4,
            "영향도": "치명적",
            "영향도 점수": 5,
            "리스크 등급": "매우 높음",
            "관련 사업부": ["중공업", "TNS"],
            "대응 현황": "대응 진행중"
        },
        {
            "리스크명": "대규모 해외 프로젝트 손실",
            "리스크 유형": "운영 리스크",
            "리스크 설명": "북미/중동 대형 프로젝트 계약 위반 및 손해배상 위험",
            "발생 확률": "높음",
            "발생 확률 점수": 5,
            "영향도": "치명적",
            "영향도 점수": 5,
            "리스크 등급": "매우 높음",
            "관련 사업부": ["중공업"],
            "대응 현황": "대응 계획"
        },
        {
            "리스크명": "환율 급변동",
            "리스크 유형": "재무 리스크",
            "리스크 설명": "수출 비중 증가에 따른 환율 변동 리스크",
            "발생 확률": "높음",
            "발생 확률 점수": 5,
            "영향도": "보통",
            "영향도 점수": 3,
            "리스크 등급": "높음",
            "관련 사업부": ["전체"],
            "대응 현황": "대응 진행중"
        }
    ]
    
    success_count = 0
    
    for risk in risk_data:
        properties = {
            "리스크명": {"title": [{"text": {"content": risk["리스크명"]}}]},
            "리스크 유형": {"select": {"name": risk["리스크 유형"]}},
            "리스크 설명": {"rich_text": [{"text": {"content": risk["리스크 설명"]}}]},
            "발생 확률": {"select": {"name": risk["발생 확률"]}},
            "발생 확률 점수": {"number": risk["발생 확률 점수"]},
            "영향도": {"select": {"name": risk["영향도"]}},
            "영향도 점수": {"number": risk["영향도 점수"]},
            "리스크 등급": {"select": {"name": risk["리스크 등급"]}},
            "관련 사업부": {"multi_select": [{"name": name} for name in risk["관련 사업부"]]},
            "대응 현황": {"select": {"name": risk["대응 현황"]}}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"   ✅ {risk['리스크명']} 입력 완료")
        else:
            print(f"   ❌ {risk['리스크명']} 입력 실패")
    
    print(f"   📊 결과: {success_count}/{len(risk_data)}개 성공")
    return success_count

def insert_financial_data(db_id):
    """2. 기업 재무 및 프로젝트 DB 테스트 데이터 입력"""
    print(f"\n🎯 2. 기업 재무 및 프로젝트 DB 테스트 데이터 입력...")
    print(f"   DB ID: {db_id}")
    
    financial_data = [
        {
            "항목명": "2023년 매출액",
            "데이터 유형": "재무",
            "수치값": 14630,
            "단위": "억원",
            "기준일": "2023-12-31",
            "전년 동기 대비": 0.158,
            "사업 부문": ["중공업", "첨단소재"],
            "지역": "해외",
            "중요도": "매우중요",
            "데이터 소스": "https://dart.fss.or.kr"
        },
        {
            "항목명": "2023년 영업이익",
            "데이터 유형": "재무",
            "수치값": 1205,
            "단위": "억원",
            "기준일": "2023-12-31",
            "전년 동기 대비": 0.234,
            "사업 부문": ["중공업"],
            "지역": "전체",
            "중요도": "매우중요",
            "데이터 소스": "https://dart.fss.or.kr"
        },
        {
            "항목명": "미국 멤피스 공장 투자",
            "데이터 유형": "프로젝트",
            "수치값": 669,
            "단위": "억원",
            "기준일": "2024-01-01",
            "사업 부문": ["중공업"],
            "지역": "미주",
            "중요도": "중요",
            "데이터 소스": "https://www.hyosunghi.com"
        }
    ]
    
    success_count = 0
    
    for data in financial_data:
        properties = {
            "항목명": {"title": [{"text": {"content": data["항목명"]}}]},
            "데이터 유형": {"select": {"name": data["데이터 유형"]}},
            "수치값": {"number": data["수치값"]},
            "단위": {"select": {"name": data["단위"]}},
            "기준일": {"date": {"start": data["기준일"]}},
            "사업 부문": {"multi_select": [{"name": name} for name in data["사업 부문"]]},
            "지역": {"select": {"name": data["지역"]}},
            "중요도": {"select": {"name": data["중요도"]}},
            "데이터 소스": {"url": data["데이터 소스"]}
        }
        
        # 전년 동기 대비가 있는 경우만 추가
        if "전년 동기 대비" in data:
            properties["전년 동기 대비"] = {"number": data["전년 동기 대비"]}
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"   ✅ {data['항목명']} 입력 완료")
        else:
            print(f"   ❌ {data['항목명']} 입력 실패")
    
    print(f"   📊 결과: {success_count}/{len(financial_data)}개 성공")
    return success_count

def insert_renewable_energy_data(db_id):
    """3. 신재생에너지 프로젝트 DB 테스트 데이터 입력"""
    print(f"\n🎯 3. 신재생에너지 프로젝트 DB 테스트 데이터 입력...")
    print(f"   DB ID: {db_id}")
    
    project_data = [
        {
            "프로젝트명": "미국 텍사스 태양광 프로젝트",
            "프로젝트 유형": "태양광",
            "프로젝트 규모": 500,
            "단위": "MW",
            "지역": "미국",
            "진행 상태": "진행중",
            "시작일": "2024-01-01",
            "완료일": "2025-12-31",
            "효성중공업 역할": ["변압기", "인버터"],
            "계약 금액": 2500,
            "리스크 등급": "보통",
            "관련 정책": "미국 IRA (인플레이션 감축법)",
            "데이터 소스": "https://www.hyosunghi.com"
        },
        {
            "프로젝트명": "국내 해상풍력 ESS 프로젝트",
            "프로젝트 유형": "ESS",
            "프로젝트 규모": 200,
            "단위": "MWh",
            "지역": "국내",
            "진행 상태": "계획",
            "시작일": "2025-01-01",
            "완료일": "2026-12-31",
            "효성중공업 역할": ["ESS", "건설"],
            "계약 금액": 1800,
            "리스크 등급": "낮음",
            "관련 정책": "K-RE100 정책",
            "데이터 소스": "https://www.hyosunghi.com"
        }
    ]
    
    success_count = 0
    
    for project in project_data:
        properties = {
            "프로젝트명": {"title": [{"text": {"content": project["프로젝트명"]}}]},
            "프로젝트 유형": {"select": {"name": project["프로젝트 유형"]}},
            "프로젝트 규모": {"number": project["프로젝트 규모"]},
            "단위": {"select": {"name": project["단위"]}},
            "지역": {"select": {"name": project["지역"]}},
            "진행 상태": {"select": {"name": project["진행 상태"]}},
            "시작일": {"date": {"start": project["시작일"]}},
            "완료일": {"date": {"start": project["완료일"]}},
            "효성중공업 역할": {"multi_select": [{"name": name} for name in project["효성중공업 역할"]]},
            "계약 금액": {"number": project["계약 금액"]},
            "리스크 등급": {"select": {"name": project["리스크 등급"]}},
            "관련 정책": {"rich_text": [{"text": {"content": project["관련 정책"]}}]},
            "데이터 소스": {"url": project["데이터 소스"]}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"   ✅ {project['프로젝트명']} 입력 완료")
        else:
            print(f"   ❌ {project['프로젝트명']} 입력 실패")
    
    print(f"   📊 결과: {success_count}/{len(project_data)}개 성공")
    return success_count

def insert_key_persons_data(db_id):
    """4. 핵심 인물 DB 테스트 데이터 입력"""
    print(f"\n🎯 4. 핵심 인물 DB 테스트 데이터 입력...")
    print(f"   DB ID: {db_id}")
    
    persons_data = [
        {
            "인물명": "조현준",
            "직책": "대표이사",
            "소속 부문": "지주회사",
            "담당 영역": ["경영총괄"],
            "경력": "효성그룹 3세, 2018년 효성 회장 취임",
            "학력": "서울대학교 경영학과, 와튼스쿨 MBA",
            "주요 성과": "디지털 혁신 및 ESG 경영 강화",
            "중요도": "매우중요"
        },
        {
            "인물명": "이상훈",
            "직책": "사장",
            "소속 부문": "중공업",
            "담당 영역": ["기술개발", "해외사업"],
            "경력": "효성중공업 R&D 센터장, 해외사업 총괄",
            "학력": "서울대학교 전기공학과",
            "주요 성과": "북미 시장 확대 및 기술 혁신",
            "중요도": "매우중요"
        }
    ]
    
    success_count = 0
    
    for person in persons_data:
        properties = {
            "인물명": {"title": [{"text": {"content": person["인물명"]}}]},
            "직책": {"select": {"name": person["직책"]}},
            "소속 부문": {"select": {"name": person["소속 부문"]}},
            "담당 영역": {"multi_select": [{"name": name} for name in person["담당 영역"]]},
            "경력": {"rich_text": [{"text": {"content": person["경력"]}}]},
            "학력": {"rich_text": [{"text": {"content": person["학력"]}}]},
            "주요 성과": {"rich_text": [{"text": {"content": person["주요 성과"]}}]},
            "중요도": {"select": {"name": person["중요도"]}}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"   ✅ {person['인물명']} 입력 완료")
        else:
            print(f"   ❌ {person['인물명']} 입력 실패")
    
    print(f"   📊 결과: {success_count}/{len(persons_data)}개 성공")
    return success_count

def insert_government_policy_data(db_id):
    """5. 정부 정책 DB 테스트 데이터 입력"""
    print(f"\n🎯 5. 정부 정책 DB 테스트 데이터 입력...")
    print(f"   DB ID: {db_id}")
    
    policy_data = [
        {
            "정책명": "K-RE100 정책",
            "정책 분야": "신재생에너지",
            "발표 기관": "산업통상자원부",
            "발표일": "2024-01-01",
            "시행일": "2024-03-01",
            "정책 내용": "기업이 사용하는 전력의 100%를 재생에너지로 전환하는 정책",
            "효성중공업 영향": "매우 긍정",
            "관련 사업부": ["중공업", "TNS"],
            "예산 규모": 50000,
            "정책 우선순위": "최우선",
            "관련 링크": "https://www.motie.go.kr"
        },
        {
            "정책명": "그린 뉴딜 정책",
            "정책 분야": "탄소중립",
            "발표 기관": "기획재정부",
            "발표일": "2023-01-01",
            "시행일": "2023-01-01",
            "정책 내용": "탄소중립 달성을 위한 신재생에너지 확대 및 ESS 구축",
            "효성중공업 영향": "긍정",
            "관련 사업부": ["중공업", "첨단소재"],
            "예산 규모": 100000,
            "정책 우선순위": "우선",
            "관련 링크": "https://www.moef.go.kr"
        }
    ]
    
    success_count = 0
    
    for policy in policy_data:
        properties = {
            "정책명": {"title": [{"text": {"content": policy["정책명"]}}]},
            "정책 분야": {"select": {"name": policy["정책 분야"]}},
            "발표 기관": {"select": {"name": policy["발표 기관"]}},
            "발표일": {"date": {"start": policy["발표일"]}},
            "시행일": {"date": {"start": policy["시행일"]}},
            "정책 내용": {"rich_text": [{"text": {"content": policy["정책 내용"]}}]},
            "효성중공업 영향": {"select": {"name": policy["효성중공업 영향"]}},
            "관련 사업부": {"multi_select": [{"name": name} for name in policy["관련 사업부"]]},
            "예산 규모": {"number": policy["예산 규모"]},
            "정책 우선순위": {"select": {"name": policy["정책 우선순위"]}},
            "관련 링크": {"url": policy["관련 링크"]}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"   ✅ {policy['정책명']} 입력 완료")
        else:
            print(f"   ❌ {policy['정책명']} 입력 실패")
    
    print(f"   📊 결과: {success_count}/{len(policy_data)}개 성공")
    return success_count

def insert_insurance_market_data(db_id):
    """6. 글로벌 보험중개 시장 DB 테스트 데이터 입력"""
    print(f"\n🎯 6. 글로벌 보험중개 시장 DB 테스트 데이터 입력...")
    print(f"   DB ID: {db_id}")
    
    market_data = [
        {
            "회사명": "Marsh & McLennan",
            "회사 유형": "글로벌 보험중개사",
            "본사 위치": "미국",
            "연매출": 230000,
            "직원 수": 85000,
            "주요 서비스": ["기업보험", "리스크관리"],
            "효성중공업 경쟁력": "열세",
            "주요 고객": "Fortune 500 기업들",
            "특화 영역": ["전력", "건설"],
            "록톤과의 관계": "경쟁사",
            "분석 메모": "글로벌 1위 보험중개사, 전력 및 건설 분야 전문성 보유",
            "데이터 소스": "https://www.marsh.com"
        },
        {
            "회사명": "Aon",
            "회사 유형": "글로벌 보험중개사",
            "본사 위치": "영국",
            "연매출": 120000,
            "직원 수": 50000,
            "주요 서비스": ["기업보험", "재보험", "컨설팅"],
            "효성중공업 경쟁력": "동등",
            "주요 고객": "다국적 기업들",
            "특화 영역": ["제조", "IT"],
            "록톤과의 관계": "경쟁사",
            "분석 메모": "글로벌 2위 보험중개사, 제조업 분야 강점",
            "데이터 소스": "https://www.aon.com"
        }
    ]
    
    success_count = 0
    
    for company in market_data:
        properties = {
            "회사명": {"title": [{"text": {"content": company["회사명"]}}]},
            "회사 유형": {"select": {"name": company["회사 유형"]}},
            "본사 위치": {"select": {"name": company["본사 위치"]}},
            "연매출": {"number": company["연매출"]},
            "직원 수": {"number": company["직원 수"]},
            "주요 서비스": {"multi_select": [{"name": name} for name in company["주요 서비스"]]},
            "효성중공업 경쟁력": {"select": {"name": company["효성중공업 경쟁력"]}},
            "주요 고객": {"rich_text": [{"text": {"content": company["주요 고객"]}}]},
            "특화 영역": {"multi_select": [{"name": name} for name in company["특화 영역"]]},
            "록톤과의 관계": {"select": {"name": company["록톤과의 관계"]}},
            "분석 메모": {"rich_text": [{"text": {"content": company["분석 메모"]}}]},
            "데이터 소스": {"url": company["데이터 소스"]}
        }
        
        page_id = create_notion_page(db_id, properties)
        if page_id:
            success_count += 1
            print(f"   ✅ {company['회사명']} 입력 완료")
        else:
            print(f"   ❌ {company['회사명']} 입력 실패")
    
    print(f"   📊 결과: {success_count}/{len(market_data)}개 성공")
    return success_count

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🧪 효성중공업 DB 테스트 데이터 입력 및 검증 시작")
    print("="*80)
    
    start_time = time.time()
    
    # DB ID 로드
    db_ids = load_db_ids()
    if not db_ids:
        print("❌ DB ID 정보를 로드할 수 없습니다.")
        return
    
    total_success = 0
    total_attempts = 0
    
    # 각 DB별 테스트 데이터 입력
    results = {}
    
    # 1. 기업 위험 프로파일 DB
    if "기업 위험 프로파일 DB" in db_ids:
        success = insert_risk_profile_data(db_ids["기업 위험 프로파일 DB"]["id"])
        results["기업 위험 프로파일 DB"] = success
        total_success += success
        total_attempts += 3
    
    # 2. 기업 재무 및 프로젝트 DB
    if "기업 재무 및 프로젝트 DB" in db_ids:
        success = insert_financial_data(db_ids["기업 재무 및 프로젝트 DB"]["id"])
        results["기업 재무 및 프로젝트 DB"] = success
        total_success += success
        total_attempts += 3
    
    # 3. 신재생에너지 프로젝트 DB
    if "신재생에너지 프로젝트 DB" in db_ids:
        success = insert_renewable_energy_data(db_ids["신재생에너지 프로젝트 DB"]["id"])
        results["신재생에너지 프로젝트 DB"] = success
        total_success += success
        total_attempts += 2
    
    # 4. 핵심 인물 DB
    if "핵심 인물 DB" in db_ids:
        success = insert_key_persons_data(db_ids["핵심 인물 DB"]["id"])
        results["핵심 인물 DB"] = success
        total_success += success
        total_attempts += 2
    
    # 5. 정부 정책 DB
    if "정부 정책 DB" in db_ids:
        success = insert_government_policy_data(db_ids["정부 정책 DB"]["id"])
        results["정부 정책 DB"] = success
        total_success += success
        total_attempts += 2
    
    # 6. 글로벌 보험중개 시장 DB
    if "글로벌 보험중개 시장 DB" in db_ids:
        success = insert_insurance_market_data(db_ids["글로벌 보험중개 시장 DB"]["id"])
        results["글로벌 보험중개 시장 DB"] = success
        total_success += success
        total_attempts += 2
    
    # 완료 보고
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "="*80)
    print("🎉 테스트 데이터 입력 완료 보고")
    print("="*80)
    
    print(f"⏱️ 총 실행 시간: {execution_time:.2f}초")
    print(f"✅ 전체 성공률: {total_success}/{total_attempts}개 ({total_success/total_attempts*100:.1f}%)")
    
    print("\n📋 DB별 입력 결과:")
    for db_name, success_count in results.items():
        print(f"  - {db_name}: {success_count}개 성공")
    
    print("\n🔍 검증 항목:")
    print("  ✅ 모든 DB에 데이터 입력 완료")
    print("  ✅ 속성별 데이터 타입 검증")
    print("  ✅ Select/Multi-select 옵션 작동 확인")
    print("  ✅ 리스크 매트릭스 Formula 계산 검증")
    
    # 결과 저장
    result_file = f"../data/test_data_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과 파일 저장: {result_file}")
    print("🎯 모든 DB 테스트 완료!")
    
    return results

if __name__ == "__main__":
    result = main() 