#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DART API 연동 모듈 - 효성중공업 조사용
"""
DART API 연동 모듈 - 효성중공업 조사용
작성일: 2025년 7월 12일
작성자: 서대리 (Lead Developer)
목적: 효성중공업 DART API 연동 및 데이터 수집

협업헌장 GIA V2.0 준수:
- Notion 기능 극대화: 기존 한글 필드명 완벽 호환
- 최소 개발 원칙: DART API 연동에 집중
- 인코딩 안전성: Windows CP949 환경 완전 호환
"""

import os
DART_API_KEY = os.getenv('DART_API_KEY', 'API키_설정_필요')
HYOSUNG_CODE = "298040"  # 효성중공업 종목코드

def test_dart_connection():
    print("DART API 연결 테스트 시작")
    # TODO: DART API 키 설정 필요
    print(f"DART API 키: {DART_API_KEY}")
    print(f"효성중공업 종목코드: {HYOSUNG_CODE}")
    print("연결 테스트 준비 완료")
    result = get_company_info()
    save_result = save_to_notion()
    return True

def get_company_info():
    print(f"효성중공업(298040) 정보 조회 준비")
    # TODO: 실제 DART API 호출 예정
    print("기업 정보 조회 함수 준비 완료")
    return {"company_name": "효성중공업", "code": "298040"}

def save_to_notion():
    print("노션 DB 연동 준비")
    # TODO: 노션 API 연동 예정
    print("데이터 저장 함수 준비 완료")
    return True

def analyze_datacenter_policy(policy_data, hyosung_projects):
    """
    데이터센터 투자 정책 분석 및 효성중공업 수주 기회 예측
    
    Args:
        policy_data (dict): 정부 데이터센터 투자 정책 데이터
        hyosung_projects (dict): 효성중공업 현재 프로젝트 현황
    
    Returns:
        dict: 분석 결과
    """
    print("데이터센터 투자 정책 분석 시작")
    print(f"정책 데이터: {policy_data['total_investment']}")
    print(f"효성 프로젝트 수: {len(hyosung_projects['us_projects'])}")
    
    # 더미 분석 로직
    business_opportunities = {
        "단기_기회": "초고압 변압기 수요 증가",
        "중기_기회": "ESS 설비 확대",
        "장기_기회": "AI 데이터센터 전용 설비"
    }
    
    insurance_demand = {
        "계약이행보증": "연간 500억원 예상",
        "기술보증": "연간 200억원 예상",
        "배상책임보험": "연간 100억원 예상"
    }
    
    risk_assessment = {
        "기술_리스크": "중간",
        "납기_리스크": "높음",
        "경쟁_리스크": "중간"
    }
    
    result = {
        "business_opportunities": business_opportunities,
        "insurance_demand_forecast": insurance_demand,
        "risk_assessment": risk_assessment
    }
    
    print("분석 완료:")
    print(f"- 수주 기회: {len(business_opportunities)}개 식별")
    print(f"- 보험 수요: {len(insurance_demand)}개 항목 예측")
    print(f"- 리스크 평가: {len(risk_assessment)}개 요소 분석")
    
    return result

def create_dummy_data():
    """더미 데이터 생성"""
    policy_data = {
        "total_investment": "100조원",
        "key_locations": ["광주", "울산", "세종", "충북"],
        "tech_requirements": ["초고압 변압기", "GIS", "ESS"],
        "support_measures": ["세액공제", "정책금융", "규제완화"]
    }
    
    hyosung_projects = {
        "us_projects": [
            {"name": "초고압 GIS 수출", "value": "2600억원"},
            {"name": "멤피스 초고압변압기", "value": "1.2억USD"}
        ],
        "domestic_renewable": [
            {"name": "밀양 부북 ESS", "capacity": "336MW"},
            {"name": "창녕 재생에너지", "capacity": "100MW"}
        ],
        "capabilities": ["초고압 변압기", "GIS", "ESS"]
    }
    
    return policy_data, hyosung_projects

def prepare_financial_data_structure():
    """
    시대리로부터 받을 효성중공업 재무 데이터의 예상 구조 정의
    
    Returns:
        dict: 예상 재무 데이터 구조
    """
    print("효성중공업 재무 데이터 구조 준비 중...")
    
    # 예상 재무 데이터 구조 정의
    expected_structure = {
        "company_name": "효성중공업",
        "company_code": "298040",
        "years": ["2019", "2020", "2021", "2022", "2023"],
        "financial_metrics": {
            "revenue": {
                "name": "매출액",
                "unit": "억원",
                "expected_format": "연도별 배열"
            },
            "operating_profit": {
                "name": "영업이익", 
                "unit": "억원",
                "expected_format": "연도별 배열"
            },
            "net_income": {
                "name": "당기순이익",
                "unit": "억원", 
                "expected_format": "연도별 배열"
            },
            "total_assets": {
                "name": "총자산",
                "unit": "억원",
                "expected_format": "연도별 배열"
            },
            "debt_ratio": {
                "name": "부채비율",
                "unit": "%",
                "expected_format": "연도별 배열"
            }
        },
        "data_format": "CSV 또는 JSON",
        "period": "2019-2023 연간 데이터"
    }
    
    print("예상 재무 데이터 구조:")
    print(f"- 회사명: {expected_structure['company_name']}")
    print(f"- 종목코드: {expected_structure['company_code']}")
    print(f"- 분석 기간: {expected_structure['period']}")
    print(f"- 주요 지표 수: {len(expected_structure['financial_metrics'])}개")
    
    for key, metric in expected_structure['financial_metrics'].items():
        print(f"  • {metric['name']} ({metric['unit']})")
    
    print("재무 데이터 수신 준비 완료")
    return expected_structure

def preprocess_financial_data(raw_data):
    """
    시계열 분석을 위한 효성중공업 재무 데이터 전처리
    
    Args:
        raw_data (dict): 시대리가 제공한 원시 재무 데이터
        
    Returns:
        dict: 전처리된 시계열 분석 적합 데이터
        
    전처리 작업:
    - 날짜 형식 통일 (YYYY 형태)
    - 결측치 처리 (평균값 또는 이전값 사용)
    - 숫자 형식 통일 (억원 단위 통일)
    - 데이터 유효성 검증
    """
    print("시계열 분석용 재무 데이터 전처리 시작...")
    
    # 1. 날짜 형식 통일 (YYYY 형태)
    def normalize_year_format(year_data):
        """연도 데이터를 YYYY 형태로 통일"""
        normalized_years = []
        for year in year_data:
            if isinstance(year, str):
                # "2019년", "2019-01-01" 등을 "2019"로 변환
                year_clean = year.replace("년", "").split("-")[0]
                normalized_years.append(year_clean)
            else:
                normalized_years.append(str(year))
        return normalized_years
    
    # 2. 결측치 처리 함수
    def handle_missing_values(data_list):
        """결측치를 이전값 또는 평균값으로 대체"""
        processed_data = []
        for i, value in enumerate(data_list):
            if value is None or value == "" or value == "N/A":
                if i > 0:
                    # 이전값 사용
                    processed_data.append(processed_data[i-1])
                else:
                    # 첫 번째 값이 결측치면 0으로 설정
                    processed_data.append(0)
            else:
                processed_data.append(value)
        return processed_data
    
    # 3. 숫자 형식 통일 (억원 단위)
    def normalize_financial_values(values):
        """재무 데이터를 억원 단위로 통일"""
        normalized = []
        for value in values:
            if isinstance(value, str):
                # "1,000억원", "500억" 등을 숫자로 변환
                value_clean = value.replace(",", "").replace("억원", "").replace("억", "")
                try:
                    normalized.append(float(value_clean))
                except:
                    normalized.append(0)
            else:
                normalized.append(float(value) if value is not None else 0)
        return normalized
    
    # 4. 데이터 유효성 검증
    def validate_data(data):
        """데이터 유효성 검증"""
        issues = []
        
        # 연도 수와 데이터 수 일치 여부 확인
        expected_years = 5  # 2019-2023
        for metric_name, metric_data in data.items():
            if metric_name != "years" and isinstance(metric_data, list):
                if len(metric_data) != expected_years:
                    issues.append(f"{metric_name}: 데이터 수 불일치 (예상: {expected_years}, 실제: {len(metric_data)})")
        
        # 음수 값 확인 (부채비율 제외)
        for metric_name, metric_data in data.items():
            if metric_name not in ["years", "debt_ratio"] and isinstance(metric_data, list):
                for i, value in enumerate(metric_data):
                    if value < 0:
                        issues.append(f"{metric_name}: {data['years'][i]}년 음수 값 ({value})")
        
        return issues
    
    # 전처리 실행
    print("1. 날짜 형식 통일 처리...")
    processed_data = {
        "company_name": raw_data.get("company_name", "효성중공업"),
        "company_code": raw_data.get("company_code", "298040"),
        "years": normalize_year_format(raw_data.get("years", ["2019", "2020", "2021", "2022", "2023"]))
    }
    
    print("2. 재무 지표 전처리...")
    financial_metrics = ["revenue", "operating_profit", "net_income", "total_assets", "debt_ratio"]
    
    for metric in financial_metrics:
        if metric in raw_data:
            print(f"   - {metric} 처리 중...")
            # 결측치 처리
            cleaned_data = handle_missing_values(raw_data[metric])
            # 숫자 형식 통일
            normalized_data = normalize_financial_values(cleaned_data)
            processed_data[metric] = normalized_data
        else:
            print(f"   - {metric} 데이터 없음 (기본값 설정)")
            processed_data[metric] = [0] * len(processed_data["years"])
    
    print("3. 데이터 유효성 검증...")
    validation_issues = validate_data(processed_data)
    
    if validation_issues:
        print("   ⚠️  검증 이슈 발견:")
        for issue in validation_issues:
            print(f"   - {issue}")
    else:
        print("   ✅ 데이터 유효성 검증 완료")
    
    print("시계열 분석용 데이터 전처리 완료")
    return processed_data

def create_dummy_financial_data():
    """
    전처리 테스트용 더미 재무 데이터 생성
    (다양한 문제 상황 포함: 결측치, 문자열 형태, 쉼표 포함 등)
    """
    dummy_data = {
        "company_name": "효성중공업",
        "company_code": "298040",
        "years": ["2019년", "2020", "2021-01-01", "2022", "2023년"],
        "revenue": ["15,000억원", "14,500억", None, "16,200억원", "17,800억"],
        "operating_profit": [1200, 1150, "N/A", "1,300억", "1,450억원"],
        "net_income": ["800억", "750억원", "", "900억", "1,100억"],
        "total_assets": ["50,000억", "52,000억원", "51,500억", "55,000억", "58,000억원"],
        "debt_ratio": [45.5, 47.2, 44.8, 43.1, 41.5]
    }
    
    return dummy_data

def forecast_financial_trends(preprocessed_data):
    """
    효성중공업 재무 및 사업 성장 궤적 예측 모델
    
    Args:
        preprocessed_data (dict): 전처리된 재무 데이터 (2019-2023)
        
    Returns:
        dict: 향후 3-5년 예측 결과 (2024-2028)
        
    예측 모델: 단순 선형 회귀 + 이동평균 조합
    - 단순 선형 회귀: 과거 5년 트렌드 기반 예측
    - 이동평균: 최근 3년 평균 기반 안정성 확보
    - 효성중공업 특성: 인프라 장비 제조업체로 안정적 성장 패턴 고려
    """
    print("효성중공업 재무 예측 모델 시작...")
    print("선택된 예측 모델: 단순 선형 회귀 + 이동평균 조합")
    
    # 예측 대상 연도 설정
    forecast_years = ["2024", "2025", "2026", "2027", "2028"]
    
    def calculate_linear_trend(data_values):
        """단순 선형 회귀를 통한 트렌드 계산"""
        n = len(data_values)
        x_values = list(range(n))  # 0, 1, 2, 3, 4
        
        # 선형 회귀 계수 계산 (y = ax + b)
        sum_x = sum(x_values)
        sum_y = sum(data_values)
        sum_xy = sum(x * y for x, y in zip(x_values, data_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # 기울기 (a) 계산
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        # 절편 (b) 계산
        intercept = (sum_y - slope * sum_x) / n
        
        return slope, intercept
    
    def calculate_moving_average(data_values, window=3):
        """이동평균 계산 (최근 3년 기준)"""
        recent_values = data_values[-window:]
        return sum(recent_values) / len(recent_values)
    
    def predict_with_confidence(data_values, years_ahead=5):
        """예측값과 신뢰도 계산"""
        # 선형 회귀 트렌드
        slope, intercept = calculate_linear_trend(data_values)
        
        # 이동평균 기준값
        moving_avg = calculate_moving_average(data_values)
        
        predictions = []
        confidences = []
        growth_rates = []
        
        for i in range(years_ahead):
            # 선형 회귀 예측값
            linear_pred = slope * (len(data_values) + i) + intercept
            
            # 이동평균 조정 (가중치: 선형 70%, 이동평균 30%)
            adjusted_pred = linear_pred * 0.7 + moving_avg * 0.3
            
            # 음수 예측값 방지
            if adjusted_pred < 0:
                adjusted_pred = data_values[-1] * 0.9
            
            predictions.append(round(adjusted_pred, 1))
            
            # 신뢰도 계산 (트렌드 일관성 기반)
            trend_consistency = abs(slope) / (sum(abs(data_values[i] - data_values[i-1]) for i in range(1, len(data_values))) / len(data_values))
            confidence = min(85, max(60, 75 + trend_consistency * 10))  # 60-85% 범위
            confidences.append(round(confidence, 1))
            
            # 성장률 계산
            if i == 0:
                growth_rate = (adjusted_pred - data_values[-1]) / data_values[-1] * 100
            else:
                growth_rate = (adjusted_pred - predictions[i-1]) / predictions[i-1] * 100
            growth_rates.append(round(growth_rate, 2))
        
        return predictions, confidences, growth_rates
    
    # 주요 지표별 예측 실행
    print("\n주요 재무 지표별 예측 실행:")
    
    forecast_results = {
        "company_name": preprocessed_data["company_name"],
        "company_code": preprocessed_data["company_code"],
        "forecast_years": forecast_years,
        "model_type": "단순 선형 회귀 + 이동평균",
        "predictions": {}
    }
    
    # 매출액 예측
    print("1. 매출액 예측...")
    revenue_pred, revenue_conf, revenue_growth = predict_with_confidence(preprocessed_data["revenue"])
    forecast_results["predictions"]["revenue"] = {
        "name": "매출액",
        "unit": "억원",
        "forecasted_values": revenue_pred,
        "confidence_levels": revenue_conf,
        "growth_rates": revenue_growth
    }
    
    # 영업이익 예측
    print("2. 영업이익 예측...")
    op_pred, op_conf, op_growth = predict_with_confidence(preprocessed_data["operating_profit"])
    forecast_results["predictions"]["operating_profit"] = {
        "name": "영업이익",
        "unit": "억원",
        "forecasted_values": op_pred,
        "confidence_levels": op_conf,
        "growth_rates": op_growth
    }
    
    # 당기순이익 예측
    print("3. 당기순이익 예측...")
    net_pred, net_conf, net_growth = predict_with_confidence(preprocessed_data["net_income"])
    forecast_results["predictions"]["net_income"] = {
        "name": "당기순이익",
        "unit": "억원",
        "forecasted_values": net_pred,
        "confidence_levels": net_conf,
        "growth_rates": net_growth
    }
    
    # 모델 선택 근거 및 특성 설명
    forecast_results["model_rationale"] = {
        "선택_근거": "효성중공업은 인프라 장비 제조업체로 안정적 성장 패턴을 보임",
        "모델_장점": [
            "단순하고 해석 가능한 예측 결과",
            "과거 트렌드와 최근 안정성 모두 고려",
            "인프라 업계 특성에 적합한 보수적 접근"
        ],
        "모델_단점": [
            "급격한 시장 변화 반영 제한",
            "외부 요인 (정책, 경기변동) 미반영",
            "복잡한 비선형 패턴 감지 불가"
        ]
    }
    
    print("재무 예측 모델 완료")
    return forecast_results

if __name__ == "__main__":
    # 기존 테스트
    test_dart_connection()
    
    print("\n" + "="*50)
    print("데이터센터 정책 분석 모듈 테스트")
    print("="*50)
    
    # 더미 데이터 생성
    policy_data, hyosung_projects = create_dummy_data()
    
    # 분석 함수 실행
    analysis_result = analyze_datacenter_policy(policy_data, hyosung_projects)
    
    print("\n분석 결과 요약:")
    print(f"수주 기회: {list(analysis_result['business_opportunities'].keys())}")
    print(f"보험 수요: {list(analysis_result['insurance_demand_forecast'].keys())}")
    print(f"리스크 평가: {list(analysis_result['risk_assessment'].keys())}")
    
    print("\n더미 테스트 완료!")
    
    print("\n" + "="*50)
    print("2-8단계: 재무 데이터 구조 준비")
    print("="*50)
    
    # 재무 데이터 구조 준비
    financial_structure = prepare_financial_data_structure()
    
    print("\n2-8단계 완료 보고")
    print("효성중공업 재무 데이터 수신 준비 완료!") 
    
    print("\n" + "="*50)
    print("2-9단계: 재무 데이터 전처리 함수 구현 및 테스트")
    print("="*50)
    
    # 더미 재무 데이터 생성
    dummy_raw_data = create_dummy_financial_data()
    print("생성된 더미 재무 데이터:")
    print(f"- 연도: {dummy_raw_data['years']}")
    print(f"- 매출액: {dummy_raw_data['revenue']}")
    print(f"- 영업이익: {dummy_raw_data['operating_profit']}")
    print(f"- 당기순이익: {dummy_raw_data['net_income']}")
    print(f"- 총자산: {dummy_raw_data['total_assets']}")
    print(f"- 부채비율: {dummy_raw_data['debt_ratio']}")
    
    # 전처리 실행
    preprocessed_data = preprocess_financial_data(dummy_raw_data)
    
    print("\n전처리된 데이터 구조:")
    print(f"- 연도: {preprocessed_data['years']}")
    print(f"- 매출액: {preprocessed_data['revenue']}")
    print(f"- 영업이익: {preprocessed_data['operating_profit']}")
    print(f"- 당기순이익: {preprocessed_data['net_income']}")
    print(f"- 총자산: {preprocessed_data['total_assets']}")
    print(f"- 부채비율: {preprocessed_data['debt_ratio']}")
    
    print("\n2-9단계 완료 보고")
    print("시계열 분석용 데이터 전처리 함수 구현 완료!") 
    
    print("\n" + "="*50)
    print("2-10단계: 재무 데이터 예측 모델 구현 및 테스트")
    print("="*50)
    
    # 예측 모델 실행
    forecast_result = forecast_financial_trends(preprocessed_data)
    
    print("\n예측 결과 요약:")
    print(f"회사명: {forecast_result['company_name']}")
    print(f"종목코드: {forecast_result['company_code']}")
    print(f"예측 기간: {forecast_result['forecast_years']}")
    print(f"모델 유형: {forecast_result['model_type']}")
    
    for metric_name, metric_data in forecast_result['predictions'].items():
        print(f"\n{metric_data['name']} 예측 결과:")
        print(f"  예측값: {metric_data['forecasted_values']}")
        print(f"  신뢰도: {metric_data['confidence_levels']}%")
        print(f"  성장률: {metric_data['growth_rates']}%")
    
    print("\n모델 특성:")
    print(f"선택 근거: {forecast_result['model_rationale']['선택_근거']}")
    print("모델 장점:")
    for advantage in forecast_result['model_rationale']['모델_장점']:
        print(f"  - {advantage}")
    print("모델 단점:")
    for disadvantage in forecast_result['model_rationale']['모델_단점']:
        print(f"  - {disadvantage}")
    
    print("\n2-10단계 완료 보고")
    print("효성중공업 재무 예측 모델 구현 완료!") 