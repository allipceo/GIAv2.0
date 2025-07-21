#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 하이브리드 워크플로우 시스템
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 서대리 직접 처리 + 노팀장 선택적 관여의 최적화된 워크플로우
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class ProcessingStage(Enum):
    """처리 단계 열거형"""
    INITIAL = "initial"
    DIRECT_PROCESSING = "direct_processing"
    QUALITY_CHECK = "quality_check"
    NODETEAM_REVIEW = "nodeteam_review"
    FINAL_INPUT = "final_input"
    COMPLETED = "completed"

class QualityLevel(Enum):
    """품질 수준 열거형"""
    EXCELLENT = "excellent"  # 95% 이상
    GOOD = "good"           # 80-95%
    NEEDS_REVIEW = "needs_review"  # 60-80%
    REQUIRES_NODETEAM = "requires_nodeteam"  # 60% 미만

class DoosanHybridWorkflow:
    """두산중공업 하이브리드 워크플로우 클래스"""
    
    def __init__(self):
        """초기화"""
        self.current_stage = ProcessingStage.INITIAL
        self.quality_thresholds = {
            "classification_accuracy": 0.85,  # 85% 이상
            "data_completeness": 0.90,       # 90% 이상
            "insurance_insight_score": 0.70   # 70% 이상
        }
        self.processing_log = []
        
        # 안전성 관리자 임포트
        from doosan_safety_manager import DoosanSafetyManager
        self.safety_manager = DoosanSafetyManager()
        
        # 사용자 친화적 처리기 임포트
        from doosan_user_friendly_processor import DoosanUserFriendlyProcessor
        self.user_processor = DoosanUserFriendlyProcessor()
    
    def process_team_data(self, team_data: str, team_member: str) -> Dict:
        """팀원 데이터 처리 (하이브리드 워크플로우)"""
        print(f"🔄 하이브리드 워크플로우 시작: {team_member}")
        print("=" * 50)
        
        # 1단계: 서대리 직접 처리
        direct_result = self._direct_processing(team_data, team_member)
        
        # 2단계: 품질 평가
        quality_assessment = self._assess_quality(direct_result)
        
        # 3단계: 워크플로우 결정
        workflow_decision = self._determine_workflow(quality_assessment, direct_result)
        
        # 4단계: 결정된 워크플로우 실행
        final_result = self._execute_workflow(workflow_decision, direct_result)
        
        return final_result
    
    def _direct_processing(self, team_data: str, team_member: str) -> Dict:
        """서대리 직접 처리"""
        print("📝 1단계: 서대리 직접 처리 시작")
        
        self.current_stage = ProcessingStage.DIRECT_PROCESSING
        
        # 안전성 백업 생성
        backup_id = self.safety_manager.create_backup("팀원데이터", {"team_member": team_member, "data": team_data})
        
        # 사용자 친화적 처리
        processing_result = self.user_processor.simple_text_input(team_data)
        
        # 텍스트 처리기 임포트 및 실행
        from doosan_text_processor import DoosanTextProcessor
        text_processor = DoosanTextProcessor()
        structured_data = text_processor.process_markdown_text(team_data)
        
        result = {
            "team_member": team_member,
            "backup_id": backup_id,
            "processing_result": processing_result,
            "structured_data": structured_data,
            "processing_time": time.time(),
            "stage": self.current_stage.value
        }
        
        self.processing_log.append({
            "timestamp": datetime.now().isoformat(),
            "stage": "direct_processing",
            "team_member": team_member,
            "backup_id": backup_id,
            "success": True
        })
        
        print("✅ 서대리 직접 처리 완료")
        return result
    
    def _assess_quality(self, direct_result: Dict) -> Dict:
        """품질 평가"""
        print("🔍 2단계: 품질 평가 시작")
        
        self.current_stage = ProcessingStage.QUALITY_CHECK
        
        processing_result = direct_result["processing_result"]
        structured_data = direct_result["structured_data"]
        
        # 분류 정확도 평가
        classification_accuracy = self._calculate_classification_accuracy(processing_result)
        
        # 데이터 완성도 평가
        data_completeness = self._calculate_data_completeness(structured_data)
        
        # 보험 인사이트 점수 평가
        insurance_insight_score = self._calculate_insurance_insight_score(structured_data)
        
        quality_assessment = {
            "classification_accuracy": classification_accuracy,
            "data_completeness": data_completeness,
            "insurance_insight_score": insurance_insight_score,
            "overall_quality": (classification_accuracy + data_completeness + insurance_insight_score) / 3,
            "quality_level": self._determine_quality_level(classification_accuracy, data_completeness, insurance_insight_score)
        }
        
        print(f"📊 품질 평가 결과: {quality_assessment['quality_level'].value}")
        return quality_assessment
    
    def _calculate_classification_accuracy(self, processing_result: Dict) -> float:
        """분류 정확도 계산"""
        feedback = processing_result["feedback"]
        total_lines = feedback["총텍스트라인"]
        classified_lines = feedback["분류된라인"]
        
        if total_lines == 0:
            return 0.0
        
        return classified_lines / total_lines
    
    def _calculate_data_completeness(self, structured_data: Dict) -> float:
        """데이터 완성도 계산"""
        total_records = sum(len(data) for data in structured_data.values())
        complete_records = 0
        
        for db_name, records in structured_data.items():
            for record in records:
                # 필수 필드가 있는지 확인
                if self._has_required_fields(record, db_name):
                    complete_records += 1
        
        if total_records == 0:
            return 0.0
        
        return complete_records / total_records
    
    def _calculate_insurance_insight_score(self, structured_data: Dict) -> float:
        """보험 인사이트 점수 계산"""
        insurance_keywords = ['보험', '리스크', '위험', '중개', '영업', '기회']
        total_records = sum(len(data) for data in structured_data.values())
        insurance_records = 0
        
        for db_name, records in structured_data.items():
            for record in records:
                # 보험 관련 키워드가 있는지 확인
                if self._has_insurance_keywords(record, insurance_keywords):
                    insurance_records += 1
        
        if total_records == 0:
            return 0.0
        
        return insurance_records / total_records
    
    def _has_required_fields(self, record: Dict, db_name: str) -> bool:
        """필수 필드 확인"""
        required_fields = {
            "📊 기업 위험 프로파일 DB": ["위험요소명"],
            "💰 기업 재무 및 프로젝트 DB": ["프로젝트명"],
            "🔋 신재생에너지 프로젝트 DB": ["프로젝트명"],
            "👥 기업 핵심 인물 DB": ["이름"],
            "🏛️ 정부 정책 영향 분석 DB": ["정책명"],
            "🌍 글로벌 보험중개 시장 DB": ["시장명"]
        }
        
        if db_name not in required_fields:
            return True
        
        required = required_fields[db_name]
        return any(field in record for field in required)
    
    def _has_insurance_keywords(self, record: Dict, keywords: List[str]) -> bool:
        """보험 관련 키워드 확인"""
        record_text = str(record).lower()
        return any(keyword in record_text for keyword in keywords)
    
    def _determine_quality_level(self, classification_accuracy: float, data_completeness: float, insurance_insight_score: float) -> QualityLevel:
        """품질 수준 결정"""
        overall_score = (classification_accuracy + data_completeness + insurance_insight_score) / 3
        
        if overall_score >= 0.95:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.80:
            return QualityLevel.GOOD
        elif overall_score >= 0.60:
            return QualityLevel.NEEDS_REVIEW
        else:
            return QualityLevel.REQUIRES_NODETEAM
    
    def _determine_workflow(self, quality_assessment: Dict, direct_result: Dict) -> Dict:
        """워크플로우 결정"""
        print("🎯 3단계: 워크플로우 결정")
        
        quality_level = quality_assessment["quality_level"]
        
        if quality_level == QualityLevel.EXCELLENT:
            workflow = "direct_to_final"
            reason = "품질이 우수하여 서대리 직접 최종 입력"
        elif quality_level == QualityLevel.GOOD:
            workflow = "direct_to_final"
            reason = "품질이 양호하여 서대리 직접 최종 입력"
        elif quality_level == QualityLevel.NEEDS_REVIEW:
            workflow = "nodeteam_review"
            reason = "품질 검토가 필요하여 노팀장님 검토 요청"
        else:  # REQUIRES_NODETEAM
            workflow = "nodeteam_review"
            reason = "품질이 낮아 노팀장님 검토 필수"
        
        workflow_decision = {
            "workflow": workflow,
            "reason": reason,
            "quality_level": quality_level.value,
            "quality_scores": quality_assessment
        }
        
        print(f"📋 워크플로우 결정: {workflow} - {reason}")
        return workflow_decision
    
    def _execute_workflow(self, workflow_decision: Dict, direct_result: Dict) -> Dict:
        """결정된 워크플로우 실행"""
        print("⚡ 4단계: 워크플로우 실행")
        
        workflow = workflow_decision["workflow"]
        
        if workflow == "direct_to_final":
            return self._execute_direct_to_final(direct_result)
        elif workflow == "nodeteam_review":
            return self._execute_nodeteam_review(direct_result, workflow_decision)
        else:
            raise ValueError(f"알 수 없는 워크플로우: {workflow}")
    
    def _execute_direct_to_final(self, direct_result: Dict) -> Dict:
        """직접 최종 입력 실행"""
        print("🚀 직접 최종 입력 실행")
        
        self.current_stage = ProcessingStage.FINAL_INPUT
        
        # 통합 처리기 임포트 및 실행
        from doosan_integrated_processor import DoosanIntegratedProcessor
        integrated_processor = DoosanIntegratedProcessor()
        
        # 구조화된 데이터를 텍스트로 변환
        structured_data = direct_result["structured_data"]
        combined_text = self._convert_structured_to_text(structured_data)
        
        # 노션 DB 입력
        input_results = integrated_processor.process_text_and_input(combined_text)
        
        # 최종 검증
        validation_result = self.safety_manager.validate_final_result(input_results)
        
        result = {
            "workflow": "direct_to_final",
            "input_results": input_results,
            "validation_result": validation_result,
            "processing_time": time.time(),
            "stage": self.current_stage.value
        }
        
        self.current_stage = ProcessingStage.COMPLETED
        
        print("✅ 직접 최종 입력 완료")
        return result
    
    def _execute_nodeteam_review(self, direct_result: Dict, workflow_decision: Dict) -> Dict:
        """노팀장님 검토 실행"""
        print("👨‍💼 노팀장님 검토 요청")
        
        self.current_stage = ProcessingStage.NODETEAM_REVIEW
        
        # 노팀장님 검토 요청 데이터 준비
        review_request = {
            "original_data": direct_result,
            "quality_assessment": workflow_decision["quality_scores"],
            "review_reason": workflow_decision["reason"],
            "request_timestamp": datetime.now().isoformat()
        }
        
        # 노팀장님 검토 요청 파일 생성
        review_file = f"nodeteam_review_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review_request, f, ensure_ascii=False, indent=2)
        
        result = {
            "workflow": "nodeteam_review",
            "review_request_file": review_file,
            "quality_assessment": workflow_decision["quality_scores"],
            "review_reason": workflow_decision["reason"],
            "status": "waiting_for_nodeteam_review",
            "stage": self.current_stage.value
        }
        
        print(f"📋 노팀장님 검토 요청 파일 생성: {review_file}")
        return result
    
    def _convert_structured_to_text(self, structured_data: Dict) -> str:
        """구조화된 데이터를 텍스트로 변환"""
        text_parts = []
        
        for db_name, records in structured_data.items():
            if records:
                text_parts.append(f"## {db_name}")
                for record in records:
                    if isinstance(record, dict):
                        for key, value in record.items():
                            text_parts.append(f"- {key}: {value}")
                    else:
                        text_parts.append(f"- {record}")
                text_parts.append("")
        
        return "\n".join(text_parts)
    
    def get_workflow_report(self) -> Dict:
        """워크플로우 보고서 생성"""
        report = {
            "current_stage": self.current_stage.value,
            "total_processing_steps": len(self.processing_log),
            "processing_log": self.processing_log,
            "quality_thresholds": self.quality_thresholds
        }
        
        return report

def main():
    """메인 실행 함수 (테스트)"""
    print("🔄 두산중공업 하이브리드 워크플로우 테스트")
    print("=" * 50)
    
    workflow = DoosanHybridWorkflow()
    
    # 테스트 데이터
    test_data = """
    두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다.
    정경훈 대표이사는 30년 경력의 전문가입니다.
    2024년 매출 15,000억원을 달성했습니다.
    태양광 발전소 200MW 프로젝트를 진행 중입니다.
    """
    
    # 워크플로우 실행
    result = workflow.process_team_data(test_data, "시대리")
    
    print(f"\n📊 최종 결과:")
    print(f"- 워크플로우: {result.get('workflow', 'unknown')}")
    print(f"- 처리 단계: {result.get('stage', 'unknown')}")
    
    if 'input_results' in result:
        print(f"- 입력 결과: {len(result['input_results'])}개 DB")
    
    if 'review_request_file' in result:
        print(f"- 검토 요청: {result['review_request_file']}")
    
    # 워크플로우 보고서
    report = workflow.get_workflow_report()
    print(f"\n📋 워크플로우 보고서:")
    print(f"- 현재 단계: {report['current_stage']}")
    print(f"- 총 처리 단계: {report['total_processing_steps']}")

if __name__ == "__main__":
    main() 