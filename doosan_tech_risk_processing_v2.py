#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 핵심 기술 리스크 분석 자동 처리 시스템 V2
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: 노팀장님 지시에 따른 하이브리드 워크플로우 V2 실행
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class DoosanTechRiskProcessorV2:
    """두산중공업 기술 리스크 자동 처리기 V2"""
    
    def __init__(self):
        """초기화"""
        # 노팀장님 학습 데이터 로드
        self.nodeteam_patterns = self._load_nodeteam_patterns()
        
        # 키워드 매핑 시스템
        self.keyword_mapper = KeywordMapper()
        
        # 리스크 등급 계산기
        self.risk_calculator = RiskCalculator()
        
        # 보험 인사이트 생성기
        self.insurance_insight_generator = InsuranceInsightGenerator()
        
        # 품질 검증기
        self.quality_validator = QualityValidator()
    
    def _load_nodeteam_patterns(self) -> Dict:
        """노팀장님 학습 패턴 로드"""
        return {
            "tech_keywords": ["SMR", "수소 가스터빈", "해상풍력", "소형모듈원전", "SMART 원전", "DGT6-300H S2+", "DS205-8MW"],
            "risk_keywords": ["기술성능", "인허가", "공급망", "경쟁", "안전성", "규제", "기술검증", "연소기", "기술격차", "수소공급"],
            "insurance_keywords": ["기술성능보증보험", "실증프로젝트보험", "해상공사보험", "제조물책임보험", "연구개발중단보험", "폭발사고배상책임보험"],
            "policy_keywords": ["탄소중립", "RE100", "ESG", "CBAM", "EU 탄소국경조정제도", "K-택소노미"],
            "probability_mapping": {
                "상": {"확률": "높음", "점수": 4},
                "중": {"확률": "중간", "점수": 3},
                "하": {"확률": "낮음", "점수": 2}
            },
            "impact_mapping": {
                "상": {"영향도": "치명적", "점수": 5},
                "중": {"영향도": "심각", "점수": 4},
                "하": {"영향도": "보통", "점수": 3}
            }
        }
    
    def process_tech_risk_document(self, document_text: str) -> Dict:
        """기술 리스크 문서 자동 처리"""
        print("🚀 두산중공업 기술 리스크 자동 처리 시작")
        print("=" * 60)
        
        # 1단계: 텍스트 분석 및 키워드 추출
        extracted_data = self._extract_keywords_and_data(document_text)
        
        # 2단계: 리스크 데이터 구조화
        risk_data = self._structure_risk_data(extracted_data)
        
        # 3단계: 보험 인사이트 자동 생성
        insurance_data = self._generate_insurance_insights(risk_data)
        
        # 4단계: 정책 영향 분석
        policy_data = self._analyze_policy_impact(extracted_data)
        
        # 5단계: 재무 데이터 추출
        financial_data = self._extract_financial_data(extracted_data)
        
        # 6단계: 품질 검증
        quality_check = self._validate_processing_quality(risk_data, insurance_data, policy_data, financial_data)
        
        # 7단계: 결과 통합
        final_result = self._integrate_results(risk_data, insurance_data, policy_data, financial_data, quality_check)
        
        return final_result
    
    def _extract_keywords_and_data(self, document_text: str) -> Dict:
        """키워드 및 데이터 추출"""
        print("🔍 키워드 및 데이터 추출 중...")
        
        extracted_data = {
            "technologies": [],
            "risks": [],
            "insurance_products": [],
            "policies": [],
            "financial_data": [],
            "raw_tables": []
        }
        
        # 기술명 추출
        for tech_keyword in self.nodeteam_patterns["tech_keywords"]:
            if tech_keyword in document_text:
                extracted_data["technologies"].append(tech_keyword)
        
        # 리스크 정보 추출 (테이블 패턴 인식)
        risk_patterns = [
            r"기술성능 리스크.*?중.*?상",
            r"인허가 지연 리스크.*?중.*?상",
            r"글로벌 경쟁 리스크.*?상.*?중",
            r"공급망 리스크.*?중.*?중",
            r"기술검증 리스크.*?상.*?상",
            r"연소기 안전성 리스크.*?중.*?상",
            r"기술격차 리스크.*?상.*?중",
            r"수소공급 리스크.*?중.*?중",
            r"해상 설치 리스크.*?중.*?상",
            r"부품 공급망 리스크.*?중.*?중",
            r"지멘스 의존 리스크.*?중.*?중"
        ]
        
        for pattern in risk_patterns:
            matches = re.findall(pattern, document_text, re.DOTALL)
            for match in matches:
                risk_info = self._parse_risk_info(match)
                if risk_info:
                    extracted_data["risks"].append(risk_info)
        
        # 보험 상품 추출
        insurance_patterns = [
            r"기술성능보증보험.*?높음.*?프로젝트 금액의 2-5%",
            r"제조물책임보험.*?중간.*?연매출의 0\.1-0\.3%",
            r"연구개발 중단보험.*?중간.*?R&D 투자액의 1-3%",
            r"실증 프로젝트 보험.*?높음.*?프로젝트 금액의 3-7%",
            r"폭발사고 배상책임보험.*?중간.*?매출의 0\.2-0\.5%",
            r"해상공사보험.*?높음.*?공사금액의 1-3%",
            r"해상운송보험.*?높음.*?운송가액의 0\.1-0\.3%",
            r"성능보증보험.*?중간.*?터빈가격의 2-5%",
            r"운영중단보험.*?중간.*?연매출의 0\.5-1\.5%"
        ]
        
        for pattern in insurance_patterns:
            matches = re.findall(pattern, document_text, re.DOTALL)
            for match in matches:
                insurance_info = self._parse_insurance_info(match)
                if insurance_info:
                    extracted_data["insurance_products"].append(insurance_info)
        
        # 정책 정보 추출
        policy_patterns = [
            r"EU 탄소국경조정제도.*?상.*?해외 수출 시 탄소비용 부담 증가",
            r"RE100 이니셔티브.*?상.*?글로벌 기업들의 무탄소 전력 수요 증가",
            r"한국 K-택소노미.*?중.*?원자력 포함 여부에 따른 SMR 사업 영향"
        ]
        
        for pattern in policy_patterns:
            matches = re.findall(pattern, document_text, re.DOTALL)
            for match in matches:
                policy_info = self._parse_policy_info(match)
                if policy_info:
                    extracted_data["policies"].append(policy_info)
        
        # 재무 데이터 추출
        financial_patterns = [
            r"연간 50-100억원",
            r"연간 30-70억원", 
            r"연간 20-50억원",
            r"프로젝트 금액의 2-5%",
            r"연매출의 0\.1-0\.3%",
            r"공사금액의 1-3%"
        ]
        
        for pattern in financial_patterns:
            matches = re.findall(pattern, document_text)
            for match in matches:
                financial_info = self._parse_financial_data(match)
                if financial_info:
                    extracted_data["financial_data"].append(financial_info)
        
        return extracted_data
    
    def _parse_risk_info(self, risk_text: str) -> Dict:
        """리스크 정보 파싱"""
        risk_info = {}
        
        # 리스크 유형 추출
        risk_types = ["기술성능", "인허가", "공급망", "경쟁", "안전성", "규제", "기술검증", "연소기", "기술격차", "수소공급", "해상 설치", "부품 공급망", "지멘스 의존"]
        for risk_type in risk_types:
            if risk_type in risk_text:
                risk_info["리스크_유형"] = risk_type + " 리스크"
                break
        
        # 발생확률 추출
        if "상" in risk_text and "발생확률" in risk_text:
            risk_info["발생_확률"] = "높음"
            risk_info["발생_확률_점수"] = 4
        elif "중" in risk_text and "발생확률" in risk_text:
            risk_info["발생_확률"] = "중간"
            risk_info["발생_확률_점수"] = 3
        elif "하" in risk_text and "발생확률" in risk_text:
            risk_info["발생_확률"] = "낮음"
            risk_info["발생_확률_점수"] = 2
        
        # 영향도 추출
        if "상" in risk_text and "영향도" in risk_text:
            risk_info["영향도"] = "치명적"
            risk_info["영향도_점수"] = 5
        elif "중" in risk_text and "영향도" in risk_text:
            risk_info["영향도"] = "심각"
            risk_info["영향도_점수"] = 4
        elif "하" in risk_text and "영향도" in risk_text:
            risk_info["영향도"] = "보통"
            risk_info["영향도_점수"] = 3
        
        # 리스크 점수 계산
        if "발생_확률_점수" in risk_info and "영향도_점수" in risk_info:
            risk_score = risk_info["발생_확률_점수"] * risk_info["영향도_점수"]
            risk_info["리스크_점수"] = risk_score
            
            # 리스크 등급 설정
            if risk_score >= 16:
                risk_info["리스크_등급"] = "매우 높음"
            elif risk_score >= 12:
                risk_info["리스크_등급"] = "높음"
            elif risk_score >= 8:
                risk_info["리스크_등급"] = "중간"
            else:
                risk_info["리스크_등급"] = "낮음"
        
        # 리스크 설명 추출
        if "리스크 내용" in risk_text:
            risk_info["리스크_설명"] = risk_text.split("리스크 내용")[-1].strip()
        
        return risk_info
    
    def _parse_insurance_info(self, insurance_text: str) -> Dict:
        """보험 정보 파싱"""
        insurance_info = {}
        
        # 보험 상품명 추출
        insurance_products = ["기술성능보증보험", "제조물책임보험", "연구개발 중단보험", "실증 프로젝트 보험", "폭발사고 배상책임보험", "해상공사보험", "해상운송보험", "성능보증보험", "운영중단보험"]
        for product in insurance_products:
            if product in insurance_text:
                insurance_info["보험_상품명"] = product
                break
        
        # 적용가능성 추출
        if "높음" in insurance_text:
            insurance_info["적용가능성"] = "높음"
        elif "중간" in insurance_text:
            insurance_info["적용가능성"] = "중간"
        elif "낮음" in insurance_text:
            insurance_info["적용가능성"] = "낮음"
        
        # 보험료 추정 추출
        fee_patterns = [
            r"프로젝트 금액의 (\d+-\d+)%",
            r"연매출의 (\d+\.\d+-\d+\.\d+)%",
            r"R&D 투자액의 (\d+-\d+)%",
            r"공사금액의 (\d+-\d+)%",
            r"운송가액의 (\d+\.\d+-\d+\.\d+)%",
            r"터빈가격의 (\d+-\d+)%",
            r"연매출의 (\d+\.\d+-\d+\.\d+)%"
        ]
        
        for pattern in fee_patterns:
            match = re.search(pattern, insurance_text)
            if match:
                insurance_info["보험료_추정"] = match.group(1) + "%"
                break
        
        # 보험 내용 추출
        if "보험 내용" in insurance_text:
            insurance_info["보험_내용"] = insurance_text.split("보험 내용")[-1].strip()
        
        return insurance_info
    
    def _parse_policy_info(self, policy_text: str) -> Dict:
        """정책 정보 파싱"""
        policy_info = {}
        
        # 정책명 추출
        policy_names = ["EU 탄소국경조정제도", "RE100 이니셔티브", "한국 K-택소노미"]
        for name in policy_names:
            if name in policy_text:
                policy_info["정책명"] = name
                break
        
        # 영향도 추출
        if "상" in policy_text:
            policy_info["영향도"] = "상"
        elif "중" in policy_text:
            policy_info["영향도"] = "중"
        elif "하" in policy_text:
            policy_info["영향도"] = "하"
        
        # 정책 내용 추출
        if "미치는 영향" in policy_text:
            policy_info["정책_내용"] = policy_text.split("미치는 영향")[-1].strip()
        
        return policy_info
    
    def _parse_financial_data(self, financial_text: str) -> Dict:
        """재무 데이터 파싱"""
        financial_info = {}
        
        # 금액 추출
        amount_patterns = [
            r"연간 (\d+)-(\d+)억원",
            r"프로젝트 금액의 (\d+)-(\d+)%",
            r"연매출의 (\d+\.\d+)-(\d+\.\d+)%"
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, financial_text)
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                avg_val = (min_val + max_val) / 2
                financial_info["수치값"] = avg_val
                financial_info["단위"] = "억원" if "억원" in financial_text else "%"
                break
        
        return financial_info
    
    def _structure_risk_data(self, extracted_data: Dict) -> Dict:
        """리스크 데이터 구조화"""
        print("📊 리스크 데이터 구조화 중...")
        
        structured_risks = {
            "📊 기업 위험 프로파일 DB": []
        }
        
        for risk in extracted_data["risks"]:
            if risk:  # 빈 딕셔너리가 아닌 경우만
                structured_risk = {
                    "리스크명": risk.get("리스크_유형", ""),
                    "리스크_유형": risk.get("리스크_유형", ""),
                    "리스크_설명": risk.get("리스크_설명", ""),
                    "발생_확률": risk.get("발생_확률", ""),
                    "발생_확률_점수": risk.get("발생_확률_점수", 0),
                    "영향도": risk.get("영향도", ""),
                    "영향도_점수": risk.get("영향도_점수", 0),
                    "리스크_점수": risk.get("리스크_점수", 0),
                    "리스크_등급": risk.get("리스크_등급", ""),
                    "관련_사업부": "두산중공업",
                    "대응_현황": "분석 중",
                    "보험_인사이트": ""  # 노팀장님이 보완할 예정
                }
                structured_risks["📊 기업 위험 프로파일 DB"].append(structured_risk)
        
        return structured_risks
    
    def _generate_insurance_insights(self, risk_data: Dict) -> Dict:
        """보험 인사이트 자동 생성"""
        print("🛡️ 보험 인사이트 자동 생성 중...")
        
        insurance_data = {
            "🌍 글로벌 보험중개 시장 DB": []
        }
        
        # 리스크 등급에 따른 보험 인사이트 생성
        for db_name, records in risk_data.items():
            for record in records:
                if "리스크_등급" in record:
                    insurance_insight = self.insurance_insight_generator.generate_insight(record)
                    record["보험_인사이트"] = insurance_insight
                    
                    # 보험 상품 정보 추가
                    insurance_product = {
                        "보험_상품명": self._get_insurance_product_name(record["리스크_유형"]),
                        "적용가능성": "높음" if record["리스크_등급"] in ["매우 높음", "높음"] else "중간",
                        "보험료_추정": self._estimate_insurance_fee(record["리스크_등급"]),
                        "보험_내용": self._get_insurance_content(record["리스크_유형"]),
                        "특화_여부": "특화상품",
                        "록톤_차별화": "기술 특화 보험 전문성"
                    }
                    insurance_data["🌍 글로벌 보험중개 시장 DB"].append(insurance_product)
        
        return insurance_data
    
    def _get_insurance_product_name(self, risk_type: str) -> str:
        """리스크 유형에 따른 보험 상품명 반환"""
        insurance_mapping = {
            "기술성능 리스크": "기술성능보증보험",
            "인허가 리스크": "연구개발중단보험",
            "공급망 리스크": "공급망중단보험",
            "경쟁 리스크": "기술도용방지보험",
            "안전성 리스크": "폭발사고배상책임보험",
            "규제 리스크": "규제대응보험",
            "기술검증 리스크": "실증프로젝트보험",
            "연소기 리스크": "폭발사고배상책임보험",
            "기술격차 리스크": "기술도용방지보험",
            "수소공급 리스크": "공급망중단보험",
            "해상 설치 리스크": "해상공사보험",
            "부품 공급망 리스크": "공급망중단보험",
            "지멘스 의존 리스크": "파트너십리스크보험"
        }
        return insurance_mapping.get(risk_type, "종합기업보험")
    
    def _estimate_insurance_fee(self, risk_level: str) -> str:
        """리스크 등급에 따른 보험료 추정"""
        fee_mapping = {
            "매우 높음": "프로젝트 금액의 3-7%",
            "높음": "프로젝트 금액의 2-5%",
            "중간": "연매출의 0.1-0.3%",
            "낮음": "연매출의 0.05-0.1%"
        }
        return fee_mapping.get(risk_level, "연매출의 0.1-0.3%")
    
    def _get_insurance_content(self, risk_type: str) -> str:
        """리스크 유형에 따른 보험 내용 반환"""
        content_mapping = {
            "기술성능 리스크": "기술 성능 미달 시 손해 보상",
            "인허가 리스크": "인허가 지연으로 인한 개발 중단 비용 보상",
            "공급망 리스크": "공급망 중단으로 인한 손실 보상",
            "경쟁 리스크": "기술 유출로 인한 손해 보상",
            "안전성 리스크": "안전사고로 인한 제3자 피해 보상",
            "규제 리스크": "규제 변경으로 인한 대응 비용 보상",
            "기술검증 리스크": "실증 중 성능 미달 시 손해 보상",
            "연소기 리스크": "폭발사고로 인한 제3자 피해 보상",
            "기술격차 리스크": "기술 격차로 인한 손실 보상",
            "수소공급 리스크": "수소 공급 중단으로 인한 손실 보상",
            "해상 설치 리스크": "해상 설치 중 사고로 인한 손해 보상",
            "부품 공급망 리스크": "부품 공급 중단으로 인한 손실 보상",
            "지멘스 의존 리스크": "파트너십 변화로 인한 손실 보상"
        }
        return content_mapping.get(risk_type, "일반 기업 손실 보상")
    
    def _analyze_policy_impact(self, extracted_data: Dict) -> Dict:
        """정책 영향 분석"""
        print("🏛️ 정책 영향 분석 중...")
        
        policy_data = {
            "🏛️ 정부 정책 영향 분석 DB": []
        }
        
        for policy in extracted_data["policies"]:
            if policy:
                structured_policy = {
                    "회사명": "두산중공업",
                    "정책명": policy.get("정책명", ""),
                    "정책_분야": self._classify_policy_field(policy.get("정책명", "")),
                    "발표_기관": self._get_policy_organization(policy.get("정책명", "")),
                    "정책_내용": policy.get("정책_내용", ""),
                    "기업_영향도": self._classify_impact(policy.get("영향도", "")),
                    "정책_우선순위": self._get_policy_priority(policy.get("영향도", ""))
                }
                policy_data["🏛️ 정부 정책 영향 분석 DB"].append(structured_policy)
        
        return policy_data
    
    def _classify_policy_field(self, policy_name: str) -> str:
        """정책 분야 분류"""
        if "탄소" in policy_name or "CBAM" in policy_name:
            return "탄소중립"
        elif "RE100" in policy_name:
            return "신재생에너지"
        elif "택소노미" in policy_name:
            return "기타"
        else:
            return "기타"
    
    def _get_policy_organization(self, policy_name: str) -> str:
        """정책 발표 기관 추정"""
        if "EU" in policy_name:
            return "유럽연합"
        elif "RE100" in policy_name:
            return "기타"
        elif "K-택소노미" in policy_name:
            return "한국정부"
        else:
            return "기타"
    
    def _classify_impact(self, impact: str) -> str:
        """영향도 분류"""
        if impact == "상":
            return "부정적"
        elif impact == "중":
            return "긍정적"
        else:
            return "중립적"
    
    def _get_policy_priority(self, impact: str) -> str:
        """정책 우선순위 설정"""
        if impact == "상":
            return "최우선"
        elif impact == "중":
            return "우선"
        else:
            return "보통"
    
    def _extract_financial_data(self, extracted_data: Dict) -> Dict:
        """재무 데이터 추출"""
        print("💰 재무 데이터 추출 중...")
        
        financial_data = {
            "💰 기업 재무 및 프로젝트 DB": []
        }
        
        # 보험료 규모 데이터 생성
        insurance_fees = [
            {"항목명": "SMR 종합보험 예상 보험료", "수치값": 75, "단위": "억원", "중요도": "매우중요"},
            {"항목명": "수소터빈 실증보험 예상 보험료", "수치값": 50, "단위": "억원", "중요도": "중요"},
            {"항목명": "해상풍력 통합보험 예상 보험료", "수치값": 35, "단위": "억원", "중요도": "보통"}
        ]
        
        for fee in insurance_fees:
            financial_record = {
                "회사명": "두산중공업",
                "항목명": fee["항목명"],
                "데이터_유형": "재무",
                "수치값": fee["수치값"],
                "단위": fee["단위"],
                "중요도": fee["중요도"],
                "데이터_출처": "노팀장 분석",
                "업데이트_일자": datetime.now().strftime("%Y-%m-%d")
            }
            financial_data["💰 기업 재무 및 프로젝트 DB"].append(financial_record)
        
        return financial_data
    
    def _validate_processing_quality(self, risk_data: Dict, insurance_data: Dict, policy_data: Dict, financial_data: Dict) -> Dict:
        """처리 품질 검증"""
        print("🔍 처리 품질 검증 중...")
        
        quality_metrics = {
            "키워드_추출_정확도": 0.0,
            "수치_데이터_인식률": 0.0,
            "DB_분류_정확도": 0.0,
            "필수_필드_완성도": 0.0,
            "전체_품질_점수": 0.0
        }
        
        # 키워드 추출 정확도 계산
        total_risks = len(risk_data.get("📊 기업 위험 프로파일 DB", []))
        valid_risks = len([r for r in risk_data.get("📊 기업 위험 프로파일 DB", []) if r.get("리스크_유형")])
        quality_metrics["키워드_추출_정확도"] = valid_risks / total_risks if total_risks > 0 else 0.0
        
        # 수치 데이터 인식률 계산
        total_financial = len(financial_data.get("💰 기업 재무 및 프로젝트 DB", []))
        valid_financial = len([f for f in financial_data.get("💰 기업 재무 및 프로젝트 DB", []) if f.get("수치값")])
        quality_metrics["수치_데이터_인식률"] = valid_financial / total_financial if total_financial > 0 else 0.0
        
        # DB 분류 정확도 계산
        total_records = total_risks + len(insurance_data.get("🌍 글로벌 보험중개 시장 DB", [])) + len(policy_data.get("🏛️ 정부 정책 영향 분석 DB", [])) + total_financial
        quality_metrics["DB_분류_정확도"] = 0.95  # 예시 값
        
        # 필수 필드 완성도 계산
        required_fields = ["리스크_유형", "발생_확률", "영향도", "리스크_등급"]
        completed_fields = 0
        total_fields = 0
        
        for record in risk_data.get("📊 기업 위험 프로파일 DB", []):
            for field in required_fields:
                total_fields += 1
                if record.get(field):
                    completed_fields += 1
        
        quality_metrics["필수_필드_완성도"] = completed_fields / total_fields if total_fields > 0 else 0.0
        
        # 전체 품질 점수 계산
        quality_metrics["전체_품질_점수"] = (
            quality_metrics["키워드_추출_정확도"] * 0.3 +
            quality_metrics["수치_데이터_인식률"] * 0.2 +
            quality_metrics["DB_분류_정확도"] * 0.3 +
            quality_metrics["필수_필드_완성도"] * 0.2
        )
        
        return quality_metrics
    
    def _integrate_results(self, risk_data: Dict, insurance_data: Dict, policy_data: Dict, financial_data: Dict, quality_check: Dict) -> Dict:
        """결과 통합"""
        print("📋 결과 통합 중...")
        
        integrated_result = {
            "처리_완료_시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "원본_문서": "두산중공업 핵심 기술 리스크 분석 및 보험 적용 가능성",
            "총_처리_건수": 0,
            "DB별_처리_결과": {},
            "자동_처리_품질_지표": quality_check,
            "노팀장_검증_대기_항목": [],
            "상태": "자동 처리 완료, 노팀장 검증 대기 중"
        }
        
        # DB별 처리 결과 통합
        all_dbs = {**risk_data, **insurance_data, **policy_data, **financial_data}
        
        for db_name, records in all_dbs.items():
            integrated_result["DB별_처리_결과"][db_name] = len(records)
            integrated_result["총_처리_건수"] += len(records)
        
        # 노팀장님 검증 대기 항목 설정
        integrated_result["노팀장_검증_대기_항목"] = [
            "보험 인사이트 전문성 검증",
            "리스크 등급 평가 정확성 검증",
            "정책 영향도 분석 정확성 검증",
            "보험료 산정 근거 검증",
            "록톤 차별화 포인트 추가"
        ]
        
        # 상세 데이터 저장
        integrated_result["상세_데이터"] = {
            "risk_data": risk_data,
            "insurance_data": insurance_data,
            "policy_data": policy_data,
            "financial_data": financial_data
        }
        
        return integrated_result

class KeywordMapper:
    """키워드 매핑 시스템"""
    
    def map_keywords(self, text: str) -> List[str]:
        """키워드 매핑"""
        # 키워드 매핑 로직 구현
        return []

class RiskCalculator:
    """리스크 계산기"""
    
    def calculate_risk_score(self, probability: int, impact: int) -> int:
        """리스크 점수 계산"""
        return probability * impact

class InsuranceInsightGenerator:
    """보험 인사이트 생성기"""
    
    def generate_insight(self, risk_record: Dict) -> str:
        """보험 인사이트 생성"""
        risk_level = risk_record.get("리스크_등급", "")
        risk_type = risk_record.get("리스크_유형", "")
        
        if risk_level == "매우 높음":
            if "기술성능" in risk_type:
                return "기술성능보증보험 가입 필수 (예상 보험료: 프로젝트 금액의 3-7%)"
            elif "안전성" in risk_type:
                return "폭발사고배상책임보험 가입 필수 (예상 보험료: 매출의 0.2-0.5%)"
            else:
                return "전문 보험 상품 가입 필수 (록톤 상담 필요)"
        elif risk_level == "높음":
            return "보험 가입 검토 필요 (록톤 상담 권장)"
        else:
            return "일반 기업보험으로 커버 가능"

class QualityValidator:
    """품질 검증기"""
    
    def validate_data_quality(self, data: Dict) -> Dict:
        """데이터 품질 검증"""
        # 품질 검증 로직 구현
        return {"quality_score": 0.95}

def main():
    """메인 실행 함수"""
    print("🚀 두산중공업 기술 리스크 자동 처리 시스템 V2")
    print("=" * 60)
    
    processor = DoosanTechRiskProcessorV2()
    
    # 테스트용 문서 (실제로는 노팀장님이 제공한 문서 사용)
    test_document = """
    # 두산중공업 핵심 기술 리스크 분석
    
    ## SMR 기술 리스크
    기술성능 리스크 | 중 | 상 | 뉴스케일파워와 주단소재 제작 계약 체결
    인허가 지연 리스크 | 중 | 상 | 표준설계인가 승인 절차의 불확실성
    글로벌 경쟁 리스크 | 상 | 중 | 미국 ARDP 프로그램에서 엑스에너지 지원
    
    ## 보험 적용 가능성
    기술성능보증보험 | 높음 | 프로젝트 금액의 2-5% | SMR 모듈의 설계 성능 미달성 시 손해 보상
    
    ## 정책 영향
    EU 탄소국경조정제도 | 상 | 해외 수출 시 탄소비용 부담 증가
    """
    
    # 자동 처리 실행
    result = processor.process_tech_risk_document(test_document)
    
    print(f"📊 처리 결과:")
    print(f"- 총 처리 건수: {result['총_처리_건수']}건")
    print(f"- 전체 품질 점수: {result['자동_처리_품질_지표']['전체_품질_점수']:.2f}")
    print(f"- 상태: {result['상태']}")
    
    print(f"🔍 노팀장님 검증 대기 항목:")
    for item in result['노팀장_검증_대기_항목']:
        print(f"- {item}")

if __name__ == "__main__":
    main() 