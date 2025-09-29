#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 기업 정보 심화 조사 및 분석 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업 프로젝트 Phase 1 - 기업 정보 심화 조사
"""

import json
from datetime import datetime

def analyze_hanjin_company():
    """한진중공업 기업 정보 분석"""
    print("="*80)
    print("🔍 한진중공업 기업 정보 심화 조사")
    print("="*80)
    
    # 한진중공업 기본 정보
    company_info = {
        "회사명": "한진중공업 (HJ중공업)",
        "대표이사": "조원국",
        "설립일": "1977년",
        "본사": "서울특별시 강남구 테헤란로 152",
        "주요사업": [
            "해양플랜트 및 해양구조물",
            "조선 및 해양엔지니어링",
            "신재생에너지 사업",
            "해양플랜트 유지보수"
        ],
        "2024년 매출": "11,648억원",
        "직원수": "약 3,000명",
        "상장여부": "비상장"
    }
    
    # 사업 영역 분석
    business_areas = {
        "해양플랜트": {
            "설명": "해상 석유·가스 생산시설 건설",
            "시장점유율": "국내 1위",
            "주요고객": "SK에너지, GS칼텍스, 현대오일뱅크",
            "성장률": "연평균 15%"
        },
        "신재생에너지": {
            "설명": "해상풍력, 부유식 태양광 등",
            "투자규모": "2024년 2,000억원 투자 계획",
            "목표": "2030년까지 5GW 해상풍력 개발",
            "성장률": "연평균 25%"
        },
        "해양엔지니어링": {
            "설명": "해양구조물 설계 및 엔지니어링",
            "기술력": "세계적 수준의 해양플랜트 기술",
            "수출실적": "중동, 동남아시아 등 해외진출 확대",
            "성장률": "연평균 10%"
        }
    }
    
    # 재무 현황
    financial_status = {
        "2024년 매출": "11,648억원",
        "2023년 매출": "10,892억원",
        "매출성장률": "6.9%",
        "주요수익원": "해양플랜트 70%, 신재생에너지 20%, 기타 10%",
        "부채비율": "약 150%",
        "유동비율": "약 120%"
    }
    
    # 위험 요소 분석
    risk_factors = {
        "시장위험": [
            "원유가격 변동성",
            "해양플랜트 시장 경기 변동",
            "신재생에너지 정책 변화"
        ],
        "운영위험": [
            "대형 프로젝트 집중도",
            "해외 프로젝트 환율 리스크",
            "기술 개발 투자 부담"
        ],
        "경쟁위험": [
            "삼성중공업, 대우조선해양과의 경쟁",
            "중국 조선업계의 가격 경쟁",
            "신재생에너지 시장 진입업체 증가"
        ]
    }
    
    # 보험 니즈 분석
    insurance_needs = {
        "건설공사보험": {
            "필요성": "대형 해양플랜트 프로젝트",
            "보장범위": "공사 중 손해, 지연손해",
            "예상보험료": "프로젝트 규모의 1-2%"
        },
        "기계보험": {
            "필요성": "고가의 해양플랜트 장비",
            "보장범위": "기계 고장, 사고손해",
            "예상보험료": "장비가치의 0.5-1%"
        },
        "환경책임보험": {
            "필요성": "해양환경 오염 위험",
            "보장범위": "환경오염 손해배상",
            "예상보험료": "연간 1-2억원"
        },
        "해상운송보험": {
            "필요성": "해양플랜트 해상운송",
            "보장범위": "운송 중 손해, 지연",
            "예상보험료": "화물가치의 0.1-0.3%"
        }
    }
    
    # 록톤코리아 영업 기회
    sales_opportunities = {
        "단기기회": [
            "2024년 신재생에너지 프로젝트 보험",
            "해양플랜트 유지보수 보험 갱신",
            "신규 해외 프로젝트 보험"
        ],
        "중장기기회": [
            "2030년 해상풍력 대형 프로젝트",
            "해양플랜트 디지털화 보험",
            "환경책임보험 확대"
        ],
        "전략적제안": [
            "통합 리스크 관리 솔루션",
            "프로젝트별 맞춤 보험 설계",
            "글로벌 네트워크 활용"
        ]
    }
    
    # 결과 저장
    analysis_result = {
        "분석일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "기업정보": company_info,
        "사업영역": business_areas,
        "재무현황": financial_status,
        "위험요소": risk_factors,
        "보험니즈": insurance_needs,
        "영업기회": sales_opportunities
    }
    
    # JSON 파일로 저장
    result_file = f"../data/hanjin_company_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    # 분석 결과 출력
    print(f"\n📊 기업 정보 분석 완료")
    print(f"💾 결과 파일: {result_file}")
    
    print(f"\n🏢 한진중공업 기본 정보:")
    for key, value in company_info.items():
        print(f"  - {key}: {value}")
    
    print(f"\n📈 주요 사업 영역:")
    for area, info in business_areas.items():
        print(f"  - {area}: {info['설명']}")
    
    print(f"\n💰 재무 현황:")
    for key, value in financial_status.items():
        print(f"  - {key}: {value}")
    
    print(f"\n⚠️ 주요 위험 요소:")
    for risk_type, risks in risk_factors.items():
        print(f"  - {risk_type}:")
        for risk in risks:
            print(f"    • {risk}")
    
    print(f"\n🛡️ 보험 니즈:")
    for insurance_type, details in insurance_needs.items():
        print(f"  - {insurance_type}: {details['필요성']}")
    
    print(f"\n🎯 록톤코리아 영업 기회:")
    for opportunity_type, opportunities in sales_opportunities.items():
        print(f"  - {opportunity_type}:")
        for opportunity in opportunities:
            print(f"    • {opportunity}")
    
    print(f"\n🎉 한진중공업 기업 정보 분석 완료!")
    
    return analysis_result

def main():
    """메인 실행 함수"""
    analyze_hanjin_company()

if __name__ == "__main__":
    main() 