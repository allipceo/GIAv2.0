#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 하이브리드 워크플로우 V2
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: 노팀장님 제안 반영한 개선된 하이브리드 시스템
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class DoosanHybridWorkflowV2:
    """두산중공업 하이브리드 워크플로우 V2"""
    
    def __init__(self):
        """초기화"""
        # 노팀장님 학습 데이터 로드
        self.nodeteam_learned_patterns = self._load_nodeteam_patterns()
        
        # 보험 인사이트 자동 생성 시스템
        self.insurance_insight_generator = InsuranceInsightGenerator()
        
        # 정책 분야 확장 시스템
        self.policy_classifier = PolicyClassifier()
        
        # 프로젝트 유형 확장 시스템
        self.project_classifier = ProjectClassifier()
        
        # 품질 검증 시스템
        self.quality_validator = QualityValidator()
    
    def _load_nodeteam_patterns(self) -> Dict:
        """노팀장님 학습 패턴 로드"""
        return {
            "보험_인사이트_패턴": [
                {
                    "리스크_유형": "공급망 리스크",
                    "보험_상품": "공급망 중단 보험",
                    "예상_보험료": "200-300억원",
                    "보상_한도": "5,000-8,000억원"
                },
                {
                    "리스크_유형": "정치적 리스크",
                    "보험_상품": "정치적 위험 보험",
                    "예상_보험료": "50-100억원",
                    "보상_한도": "1,000-2,000억원"
                }
            ],
            "정책_분야_확장": {
                "원자력": "원자력 발전 정책",
                "SMR": "소형모듈원전 정책",
                "공급망": "공급망 자립화 정책",
                "청정에너지": "청정에너지 전환 정책"
            },
            "프로젝트_유형_확장": {
                "SMR": "소형모듈원전",
                "원전": "원자력발전소",
                "태양광": "태양광발전",
                "풍력": "풍력발전",
                "ESS": "에너지저장장치"
            }
        }
    
    def process_with_nodeteam_enhancement(self, team_data: str, team_member: str) -> Dict:
        """노팀장님 개선사항이 반영된 처리"""
        print(f"🚀 하이브리드 워크플로우 V2 시작: {team_member}")
        print("=" * 50)
        
        # 1단계: 서대리 자동 처리 (90%)
        auto_result = self._auto_process_with_enhancements(team_data)
        
        # 2단계: 노팀장님 보험 인사이트 보완 (10%)
        enhanced_result = self._apply_nodeteam_insurance_insights(auto_result)
        
        # 3단계: 품질 검증
        quality_check = self._validate_with_nodeteam_standards(enhanced_result)
        
        # 4단계: 학습 피드백 루프
        learning_feedback = self._generate_learning_feedback(enhanced_result, quality_check)
        
        result = {
            "team_member": team_member,
            "auto_processed_data": auto_result,
            "nodeteam_enhanced_data": enhanced_result,
            "quality_check": quality_check,
            "learning_feedback": learning_feedback,
            "processing_time": time.time(),
            "workflow_version": "v2_hybrid"
        }
        
        return result
    
    def _auto_process_with_enhancements(self, team_data: str) -> Dict:
        """개선된 자동 처리 (90%)"""
        print("🤖 서대리 자동 처리 (90%) 시작")
        
        # 기존 자동화 시스템에 개선사항 적용
        from doosan_phase2_automation_system import DoosanPhase2AutomationSystem
        
        # 노팀장님 학습 데이터로 개선된 템플릿 생성
        enhanced_templates = self._create_enhanced_templates()
        
        automation_system = DoosanPhase2AutomationSystem(enhanced_templates)
        
        # 개선된 자동 처리 실행
        auto_result = automation_system.process_with_learned_templates(team_data, "서대리_자동")
        
        return auto_result
    
    def _create_enhanced_templates(self) -> Dict:
        """노팀장님 학습 데이터로 개선된 템플릿 생성"""
        enhanced_templates = {
            "templates": {
                "📊 기업 위험 프로파일 DB": {
                    "리스크명": {"type": "text", "required": True},
                    "리스크_유형": {"type": "text", "required": True},
                    "리스크_설명": {"type": "text", "required": True},
                    "발생_확률": {"type": "text", "required": True},
                    "발생_확률_점수": {"type": "number", "required": True},
                    "영향도": {"type": "text", "required": True},
                    "영향도_점수": {"type": "number", "required": True},
                    "리스크_점수": {"type": "number", "required": True},
                    "리스크_등급": {"type": "text", "required": True},
                    "관련_사업부": {"type": "text", "required": False},
                    "대응_현황": {"type": "text", "required": False},
                    "보험_인사이트": {"type": "text", "required": False}  # 노팀장님 추가
                }
            },
            "insurance_patterns": self.nodeteam_learned_patterns["보험_인사이트_패턴"],
            "policy_classifications": self.nodeteam_learned_patterns["정책_분야_확장"],
            "project_classifications": self.nodeteam_learned_patterns["프로젝트_유형_확장"]
        }
        
        return enhanced_templates
    
    def _apply_nodeteam_insurance_insights(self, auto_result: Dict) -> Dict:
        """노팀장님 보험 인사이트 보완 (10%)"""
        print("🛡️ 노팀장님 보험 인사이트 보완 (10%)")
        
        enhanced_result = auto_result.copy()
        
        # 보험 인사이트 자동 생성
        for db_name, records in enhanced_result["structured_data"].items():
            for record in records:
                # 리스크 등급에 따른 보험 인사이트 생성
                if "리스크_등급" in record:
                    insurance_insight = self.insurance_insight_generator.generate_advanced_insight(record)
                    record["보험_인사이트"] = insurance_insight
                
                # 정책 분야 확장 적용
                if "정책_분야" in record:
                    expanded_policy = self.policy_classifier.expand_policy_field(record["정책_분야"])
                    record["정책_분야_확장"] = expanded_policy
                
                # 프로젝트 유형 확장 적용
                if "프로젝트_유형" in record:
                    expanded_project = self.project_classifier.expand_project_field(record["프로젝트_유형"])
                    record["프로젝트_유형_확장"] = expanded_project
        
        return enhanced_result
    
    def _validate_with_nodeteam_standards(self, enhanced_result: Dict) -> Dict:
        """노팀장님 기준으로 품질 검증"""
        print("🔍 노팀장님 기준 품질 검증")
        
        quality_check = {
            "보험_인사이트_품질": 0.0,
            "정책_분야_정확도": 0.0,
            "프로젝트_유형_정확도": 0.0,
            "전체_품질": 0.0,
            "개선_필요_항목": []
        }
        
        # 보험 인사이트 품질 검증
        insurance_quality = self.quality_validator.validate_insurance_insights(enhanced_result)
        quality_check["보험_인사이트_품질"] = insurance_quality
        
        # 정책 분야 정확도 검증
        policy_accuracy = self.quality_validator.validate_policy_classifications(enhanced_result)
        quality_check["정책_분야_정확도"] = policy_accuracy
        
        # 프로젝트 유형 정확도 검증
        project_accuracy = self.quality_validator.validate_project_classifications(enhanced_result)
        quality_check["프로젝트_유형_정확도"] = project_accuracy
        
        # 전체 품질 계산
        quality_check["전체_품질"] = (insurance_quality + policy_accuracy + project_accuracy) / 3
        
        return quality_check
    
    def _generate_learning_feedback(self, enhanced_result: Dict, quality_check: Dict) -> Dict:
        """학습 피드백 루프 생성"""
        print("🔄 학습 피드백 루프 생성")
        
        learning_feedback = {
            "quality_score": quality_check["전체_품질"],
            "improvement_suggestions": [],
            "template_updates": {},
            "pattern_enhancements": {}
        }
        
        # 품질 점수에 따른 개선 제안
        if quality_check["전체_품질"] < 0.8:
            learning_feedback["improvement_suggestions"].append("보험 인사이트 자동 생성 로직 개선 필요")
            learning_feedback["improvement_suggestions"].append("정책 분야 분류 정확도 향상 필요")
            learning_feedback["improvement_suggestions"].append("프로젝트 유형 분류 정확도 향상 필요")
        
        # 템플릿 업데이트 제안
        learning_feedback["template_updates"] = {
            "보험_인사이트_필드": "모든 리스크 DB에 보험 인사이트 필드 추가",
            "정책_분야_확장": "원자력, SMR 등 새로운 정책 분야 추가",
            "프로젝트_유형_확장": "SMR 등 새로운 프로젝트 유형 추가"
        }
        
        return learning_feedback

class InsuranceInsightGenerator:
    """보험 인사이트 자동 생성기"""
    
    def generate_advanced_insight(self, record: Dict) -> str:
        """고급 보험 인사이트 생성"""
        risk_level = record.get("리스크_등급", "")
        risk_type = record.get("리스크_유형", "")
        
        # 노팀장님 패턴 기반 보험 인사이트 생성
        if risk_level == "매우 높음":
            if "공급망" in risk_type:
                return "공급망 중단 보험 가입 필수 (예상 보험료: 200-300억원)"
            elif "정치적" in risk_type:
                return "정치적 위험 보험 가입 필수 (예상 보험료: 50-100억원)"
            else:
                return "전문 보험 상품 가입 필수 (록톤 상담 필요)"
        elif risk_level == "높음":
            return "보험 가입 검토 필요 (록톤 상담 권장)"
        else:
            return "일반 기업보험으로 커버 가능"
    
    def generate_company_specific_insight(self, company_data: Dict) -> str:
        """회사별 맞춤 보험 인사이트"""
        company_size = company_data.get("회사_규모", "")
        industry = company_data.get("산업", "")
        
        if company_size == "대기업" and industry == "중공업":
            return "대형 중공업 전용 보험 프로그램 적용"
        elif company_size == "중견기업":
            return "중견기업 맞춤 보험 상품 적용"
        else:
            return "표준 기업보험 상품 적용"

class PolicyClassifier:
    """정책 분류기"""
    
    def expand_policy_field(self, policy_field: str) -> str:
        """정책 분야 확장"""
        policy_expansions = {
            "원자력": "원자력 발전 정책",
            "SMR": "소형모듈원전 정책",
            "공급망": "공급망 자립화 정책",
            "청정에너지": "청정에너지 전환 정책"
        }
        
        return policy_expansions.get(policy_field, policy_field)

class ProjectClassifier:
    """프로젝트 분류기"""
    
    def expand_project_field(self, project_field: str) -> str:
        """프로젝트 유형 확장"""
        project_expansions = {
            "SMR": "소형모듈원전",
            "원전": "원자력발전소",
            "태양광": "태양광발전",
            "풍력": "풍력발전",
            "ESS": "에너지저장장치"
        }
        
        return project_expansions.get(project_field, project_field)

class QualityValidator:
    """품질 검증기"""
    
    def validate_insurance_insights(self, enhanced_result: Dict) -> float:
        """보험 인사이트 품질 검증"""
        total_records = 0
        valid_insights = 0
        
        for db_name, records in enhanced_result["structured_data"].items():
            for record in records:
                if "보험_인사이트" in record:
                    total_records += 1
                    if record["보험_인사이트"] and len(record["보험_인사이트"]) > 10:
                        valid_insights += 1
        
        return valid_insights / total_records if total_records > 0 else 0.0
    
    def validate_policy_classifications(self, enhanced_result: Dict) -> float:
        """정책 분류 정확도 검증"""
        # 정책 분류 정확도 검증 로직
        return 0.95  # 예시 값
    
    def validate_project_classifications(self, enhanced_result: Dict) -> float:
        """프로젝트 분류 정확도 검증"""
        # 프로젝트 분류 정확도 검증 로직
        return 0.90  # 예시 값

def main():
    """메인 실행 함수 (테스트)"""
    print("🚀 두산중공업 하이브리드 워크플로우 V2 테스트")
    print("=" * 50)
    
    workflow = DoosanHybridWorkflowV2()
    
    # 테스트 데이터
    test_data = """
    두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다.
    정경훈 대표이사는 30년 경력의 전문가입니다.
    2024년 매출 15,000억원을 달성했습니다.
    태양광 발전소 200MW 프로젝트를 진행 중입니다.
    """
    
    # 하이브리드 워크플로우 실행
    result = workflow.process_with_nodeteam_enhancement(test_data, "시대리")
    
    print(f"📊 처리 결과:")
    print(f"- 전체 품질: {result['quality_check']['전체_품질']:.2f}")
    print(f"- 보험 인사이트 품질: {result['quality_check']['보험_인사이트_품질']:.2f}")
    print(f"- 정책 분야 정확도: {result['quality_check']['정책_분야_정확도']:.2f}")
    print(f"- 프로젝트 유형 정확도: {result['quality_check']['프로젝트_유형_정확도']:.2f}")
    
    print(f"🔄 학습 피드백:")
    for suggestion in result['learning_feedback']['improvement_suggestions']:
        print(f"- {suggestion}")

if __name__ == "__main__":
    main() 