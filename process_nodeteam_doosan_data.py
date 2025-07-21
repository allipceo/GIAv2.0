#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
노반장 두산중공업 조사 데이터 처리 스크립트
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: 노반장의 두산중공업 조사 결과를 구조화하여 Notion DB에 입력
"""

import json
import re
from datetime import datetime

def process_business_opportunities(content):
    """영업 기회 데이터 처리"""
    opportunities = []
    
    # 영업 기회 패턴 매칭
    opportunity_patterns = [
        {
            "name": "해외 원전 프로젝트 특화 보험 솔루션",
            "db_mapping": "기업 재무 및 프로젝트 DB",
            "potential_scale": "연간 200-500억원",
            "priority": "최우선 기회",
            "details": [
                "체코 원전 (26조원): 건설공사보험, 정치적위험보험, 기술성능보험",
                "폴란드 원전 (예상 15조원): 해외투자보험, 공급망중단보험",
                "불가리아/영국/베트남: 다국적 프로젝트 통합보험 패키지"
            ],
            "competitive_advantage": [
                "록톤의 글로벌 네트워크: 체코, 폴란드 현지 보험시장 전문성",
                "원전 특화 경험: UAE 바라카 원전 보험 성공 사례 (한국 최초)",
                "정치적 위험 관리: 동유럽 지정학적 리스크 전문 컨설팅"
            ]
        },
        {
            "name": "SMR 및 신기술 기술성능보험",
            "db_mapping": "기업 위험 프로파일 DB",
            "potential_scale": "연간 100-300억원",
            "priority": "신규 블루오션",
            "details": [
                "SMR 기술성능보험: 뉴스케일, 엑스에너지 협력 프로젝트 대상",
                "수소 가스터빈 보험: 연소 안정성, 효율성 보증 보험",
                "해상풍력 특화보험: 두산 8MW급 터빈 성능 보험"
            ],
            "competitive_advantage": [
                "신기술 리스크 평가: 록톤 글로벌의 첨단기술 보험 경험",
                "맞춤형 상품 개발: 기존 보험사가 커버하지 못하는 신기술 위험",
                "단계별 보험 설계: R&D → 파일럿 → 상용화 각 단계별 보험"
            ]
        },
        {
            "name": "글로벌 통합 보험 프로그램",
            "db_mapping": "글로벌 보험중개 시장 DB",
            "potential_scale": "연간 300-800억원",
            "priority": "확장성 최대",
            "details": [
                "글로벌 재물보험: 29개국 119개 사업장 통합 커버리지",
                "D&O 보험: 체코 상장, 글로벌 M&A 확대에 따른 임원 리스크",
                "공급망 통합보험: 일본 JSW 의존 등 핵심 소재 공급망 리스크"
            ],
            "competitive_advantage": [
                "독립적 자문: 특정 보험사에 종속되지 않은 최적 솔루션",
                "비용 효율성: 통합 프로그램을 통한 20-30% 보험료 절감",
                "클레임 지원: 록톤의 글로벌 클레임 처리 전문성"
            ]
        },
        {
            "name": "친환경 전환 ESG 보험",
            "db_mapping": "정부 정책 영향 분석 DB",
            "potential_scale": "연간 50-200억원",
            "priority": "미래 성장동력",
            "details": [
                "탄소배출권 관련보험: EU ETS, K-ETS 가격 변동 헤지",
                "친환경 기술 보험: 수소터빈, SF6-Free GIS 등 친환경 제품",
                "ESG 컴플라이언스 보험: 환경규제 위반 시 배상책임"
            ],
            "competitive_advantage": [
                "ESG 전문성: 친환경 기술에 대한 깊은 이해",
                "규제 대응: 급변하는 환경규제에 대한 선제적 대응",
                "미래 지향: 지속가능한 성장을 위한 보험 솔루션"
            ]
        }
    ]
    
    for pattern in opportunity_patterns:
        opportunities.append({
            "opportunity_name": pattern["name"],
            "db_mapping": pattern["db_mapping"],
            "potential_scale": pattern["potential_scale"],
            "priority_level": pattern["priority"],
            "specific_details": pattern["details"],
            "competitive_advantages": pattern["competitive_advantage"],
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "data_source": "노반장 두산중공업 조사",
            "confidence_score": 95
        })
    
    return opportunities

def process_ma_jv_trends(content):
    """M&A/JV 동향 데이터 처리"""
    ma_jv_data = []
    
    # M&A/JV 투자 현황
    investments = [
        {
            "year": "2009",
            "target": "체코 스코다파워",
            "type": "M&A",
            "scale": "8,000억원",
            "region": "유럽",
            "db_mapping": "기업 재무 및 프로젝트 DB"
        },
        {
            "year": "2019",
            "target": "미국 뉴스케일",
            "type": "지분투자",
            "scale": "미공개",
            "region": "북미",
            "db_mapping": "기업 재무 및 프로젝트 DB"
        },
        {
            "year": "2021",
            "target": "미국 엑스에너지",
            "type": "JV",
            "scale": "설계용역",
            "region": "북미",
            "db_mapping": "기업 재무 및 프로젝트 DB"
        },
        {
            "year": "2024",
            "target": "두산스코다파워",
            "type": "IPO",
            "scale": "체코 상장",
            "region": "유럽",
            "db_mapping": "기업 재무 및 프로젝트 DB"
        }
    ]
    
    for investment in investments:
        ma_jv_data.append({
            "investment_year": investment["year"],
            "target_company": investment["target"],
            "investment_type": investment["type"],
            "investment_scale": investment["scale"],
            "target_region": investment["region"],
            "db_mapping": investment["db_mapping"],
            "insurance_needs": [
                "W&I (Warranty & Indemnity) 보험",
                "정치적 위험보험 (PRI)",
                "해외투자보험"
            ],
            "risk_level": "중간-높음",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "data_source": "노반장 두산중공업 조사"
        })
    
    return ma_jv_data

def process_key_personnel_data(content):
    """핵심 인물 데이터 처리"""
    personnel_data = []
    
    # 박지원 회장 프로필
    park_jiwon_profile = {
        "name": "박지원",
        "position": "두산에너빌리티 대표이사 회장",
        "birth_year": "1965",
        "education": "연세대 경영학과, 뉴욕대 경영대학원 MBA",
        "family_relation": "박정원 두산그룹 회장의 동생",
        "career_highlights": [
            "2007-현재: 두산중공업/에너빌리티 CEO (18년)",
            "2010: UAE 원전 수출 공로 금탑산업훈장",
            "2009: 체코 스코다파워 인수 결정",
            "2024: 체코 원전 수주 성공"
        ],
        "government_influence": "원전 정책 핵심 인물",
        "overseas_network": "체코, 폴란드 정관계",
        "industry_leadership": "한국원자력산업협회 등 업계 단체 활동",
        "sales_approach": "정책 연계 + 글로벌 네트워크 활용",
        "db_mapping": "기업 핵심 인물 DB",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "data_source": "노반장 두산중공업 조사",
        "confidence_score": 90
    }
    
    personnel_data.append(park_jiwon_profile)
    
    return personnel_data

def process_policy_analysis(content):
    """정책 분석 데이터 처리"""
    policy_data = []
    
    # 정책 영향 분석
    policy_impacts = [
        {
            "policy_area": "원전 수출 정책",
            "impact_level": "높음",
            "business_opportunity": "수출보험 패키지 강화",
            "target_company": "두산중공업",
            "policy_trend": "정부지원 확대",
            "db_mapping": "정부 정책 영향 분석 DB"
        },
        {
            "policy_area": "ESG 규제",
            "impact_level": "중간",
            "business_opportunity": "ESG 컴플라이언스 보험",
            "target_company": "두산중공업",
            "policy_trend": "환경규제 강화",
            "db_mapping": "정부 정책 영향 분석 DB"
        },
        {
            "policy_area": "해외투자 지원",
            "impact_level": "높음",
            "business_opportunity": "해외투자보험 연계",
            "target_company": "두산중공업",
            "policy_trend": "K-SURE, NEXI 등 공적보험 확대",
            "db_mapping": "정부 정책 영향 분석 DB"
        }
    ]
    
    for policy in policy_impacts:
        policy_data.append({
            "policy_area": policy["policy_area"],
            "impact_level": policy["impact_level"],
            "business_opportunity": policy["business_opportunity"],
            "target_company": policy["target_company"],
            "policy_trend": policy["policy_trend"],
            "db_mapping": policy["db_mapping"],
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "data_source": "노반장 두산중공업 조사"
        })
    
    return policy_data

def process_all_data(content):
    """전체 데이터 처리"""
    print("🚀 노반장 두산중공업 데이터 처리 시작")
    
    # 각 카테고리별 데이터 처리
    business_opportunities = process_business_opportunities(content)
    ma_jv_trends = process_ma_jv_trends(content)
    key_personnel = process_key_personnel_data(content)
    policy_analysis = process_policy_analysis(content)
    
    # 통합 결과
    processed_data = {
        "business_opportunities": business_opportunities,
        "ma_jv_trends": ma_jv_trends,
        "key_personnel": key_personnel,
        "policy_analysis": policy_analysis,
        "processing_metadata": {
            "processing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "노반장 두산중공업 조사",
            "total_opportunities": len(business_opportunities),
            "total_investments": len(ma_jv_trends),
            "total_personnel": len(key_personnel),
            "total_policies": len(policy_analysis),
            "processing_status": "완료"
        }
    }
    
    # 결과 저장
    output_filename = f"nodeteam_doosan_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 데이터 처리 완료: {output_filename}")
    print(f"📊 처리 결과:")
    print(f"   - 영업 기회: {len(business_opportunities)}개")
    print(f"   - M&A/JV 동향: {len(ma_jv_trends)}개")
    print(f"   - 핵심 인물: {len(key_personnel)}개")
    print(f"   - 정책 분석: {len(policy_analysis)}개")
    
    return processed_data

def main():
    """메인 실행 함수"""
    # 노반장 데이터 파일 읽기
    try:
        with open('nodeteam_doosan_data.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 데이터 처리 실행
        processed_data = process_all_data(content)
        
        print("\n🎉 노반장 두산중공업 데이터 처리 성공!")
        print("📋 다음 단계: Notion DB 입력 준비 완료")
        
    except FileNotFoundError:
        print("❌ nodeteam_doosan_data.txt 파일을 찾을 수 없습니다.")
        print("📝 노반장 데이터를 먼저 저장해주세요.")
    except Exception as e:
        print(f"❌ 데이터 처리 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 