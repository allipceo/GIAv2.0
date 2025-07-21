#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 Phase 2 자동화 가속 시스템
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 확립된 템플릿으로 대량 자동 처리
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class DoosanPhase2AutomationSystem:
    """두산중공업 Phase 2 자동화 가속 시스템"""
    
    def __init__(self, learned_templates: Dict):
        """초기화"""
        self.templates = learned_templates.get("templates", {})
        self.insurance_patterns = learned_templates.get("insurance_patterns", [])
        self.relational_patterns = learned_templates.get("relational_patterns", [])
        self.keyword_mappings = learned_templates.get("keyword_mappings", {})
        
        # 안전성 관리자 임포트
        from doosan_safety_manager import DoosanSafetyManager
        self.safety_manager = DoosanSafetyManager()
        
        # 사용자 친화적 처리기 임포트
        from doosan_user_friendly_processor import DoosanUserFriendlyProcessor
        self.user_processor = DoosanUserFriendlyProcessor()
    
    def process_with_learned_templates(self, team_data: str, team_member: str) -> Dict:
        """학습된 템플릿으로 처리"""
        print(f"🚀 Phase 2 자동화 처리 시작: {team_member}")
        print("=" * 50)
        
        # 1단계: 템플릿 기반 구조화
        structured_data = self._structure_with_templates(team_data)
        
        # 2단계: 보험 인사이트 자동 적용
        enhanced_data = self._apply_insurance_insights(structured_data)
        
        # 3단계: 관계형 연결 자동 설정
        relational_data = self._apply_relational_patterns(enhanced_data)
        
        # 4단계: 품질 검증
        quality_check = self._validate_with_templates(relational_data)
        
        # 5단계: 노팀장님 검토 필요성 판단
        review_decision = self._determine_review_necessity(quality_check, relational_data)
        
        result = {
            "team_member": team_member,
            "structured_data": relational_data,
            "quality_check": quality_check,
            "review_decision": review_decision,
            "processing_time": time.time(),
            "phase": "phase2_automation"
        }
        
        return result
    
    def _structure_with_templates(self, team_data: str) -> Dict:
        """템플릿 기반 구조화"""
        print("📋 템플릿 기반 구조화 시작")
        
        structured_data = {
            "📊 기업 위험 프로파일 DB": [],
            "💰 기업 재무 및 프로젝트 DB": [],
            "🔋 신재생에너지 프로젝트 DB": [],
            "👥 기업 핵심 인물 DB": [],
            "🏛️ 정부 정책 영향 분석 DB": [],
            "🌍 글로벌 보험중개 시장 DB": []
        }
        
        # 텍스트를 라인별로 분리
        lines = team_data.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 각 DB별 템플릿에 맞게 분류
            for db_name, template in self.templates.items():
                if self._matches_template(line, template):
                    structured_record = self._create_structured_record(line, template)
                    structured_data[db_name].append(structured_record)
                    break
        
        return structured_data
    
    def _matches_template(self, line: str, template: Dict) -> bool:
        """템플릿 매칭 확인"""
        # 템플릿의 키워드가 라인에 포함되는지 확인
        template_keywords = []
        for field in template.keys():
            if isinstance(field, str):
                template_keywords.extend(field.split())
        
        line_lower = line.lower()
        matches = sum(1 for keyword in template_keywords if keyword.lower() in line_lower)
        
        # 50% 이상의 키워드가 매칭되면 해당 템플릿으로 분류
        return matches >= len(template_keywords) * 0.5
    
    def _create_structured_record(self, line: str, template: Dict) -> Dict:
        """구조화된 레코드 생성"""
        record = {}
        
        # 템플릿의 각 필드에 대해 값 추출
        for field, field_info in template.items():
            if isinstance(field_info, dict):
                field_type = field_info.get("type", "text")
                required = field_info.get("required", False)
                
                # 필드 타입에 따른 값 추출
                value = self._extract_field_value(line, field, field_type)
                
                if value or required:
                    record[field] = value
        
        # 원본 텍스트 추가
        record["원본텍스트"] = line
        
        return record
    
    def _extract_field_value(self, line: str, field: str, field_type: str) -> Any:
        """필드 값 추출"""
        line_lower = line.lower()
        field_lower = field.lower()
        
        # 필드명이 라인에 포함되는 경우
        if field_lower in line_lower:
            # 필드명 다음의 값을 추출
            field_index = line_lower.find(field_lower)
            value_start = field_index + len(field_lower)
            
            # 구분자 찾기 (콜론, 공백 등)
            separators = [':', ' ', '-', '=']
            for sep in separators:
                if line[value_start:].startswith(sep):
                    value_start += len(sep)
                    break
            
            # 값의 끝 찾기 (다음 필드명이나 줄 끝)
            value_end = len(line)
            for next_field in self.templates.keys():
                if isinstance(next_field, str):
                    next_field_lower = next_field.lower()
                    next_index = line_lower.find(next_field_lower, value_start)
                    if next_index != -1:
                        value_end = min(value_end, next_index)
            
            value = line[value_start:value_end].strip()
            
            # 필드 타입에 따른 변환
            if field_type == "number" and value:
                try:
                    return float(value.replace(',', ''))
                except ValueError:
                    return value
            elif field_type == "multi_select" and value:
                return [item.strip() for item in value.split(',')]
            else:
                return value
        
        return None
    
    def _apply_insurance_insights(self, structured_data: Dict) -> Dict:
        """보험 인사이트 자동 적용"""
        print("🛡️ 보험 인사이트 자동 적용")
        
        enhanced_data = structured_data.copy()
        
        for db_name, records in enhanced_data.items():
            for record in records:
                # 보험 패턴 매칭
                insurance_insight = self._find_insurance_insight(record, db_name)
                if insurance_insight:
                    record["보험연계"] = insurance_insight
        
        return enhanced_data
    
    def _find_insurance_insight(self, record: Dict, db_name: str) -> Optional[str]:
        """보험 인사이트 찾기"""
        for pattern in self.insurance_patterns:
            if pattern["db_name"] == db_name:
                # 레코드의 값과 패턴의 값 비교
                for field, value in record.items():
                    if field == pattern["field"] and str(value) == str(pattern["value"]):
                        return pattern.get("보험연계", "보험 가입 검토 필요")
        
        # 기본 보험 인사이트 생성
        return self._generate_default_insurance_insight(record, db_name)
    
    def _generate_default_insurance_insight(self, record: Dict, db_name: str) -> str:
        """기본 보험 인사이트 생성"""
        insurance_insights = {
            "📊 기업 위험 프로파일 DB": "위험 관리 보험 가입 검토 필요",
            "💰 기업 재무 및 프로젝트 DB": "프로젝트 보험 가입 검토 필요",
            "🔋 신재생에너지 프로젝트 DB": "에너지 프로젝트 보험 가입 검토 필요",
            "👥 기업 핵심 인물 DB": "경영진 책임보험 가입 검토 필요",
            "🏛️ 정부 정책 영향 분석 DB": "정책 변화 대응 보험 가입 검토 필요",
            "🌍 글로벌 보험중개 시장 DB": "글로벌 보험 중개 기회 검토 필요"
        }
        
        return insurance_insights.get(db_name, "보험 가입 검토 필요")
    
    def _apply_relational_patterns(self, enhanced_data: Dict) -> Dict:
        """관계형 연결 패턴 적용"""
        print("🔗 관계형 연결 패턴 적용")
        
        relational_data = enhanced_data.copy()
        
        # 회사 정보와의 관계 설정
        for db_name, records in relational_data.items():
            for record in records:
                # 회사 정보 관계 추가
                record["회사관계"] = "두산중공업"
                
                # 관계형 패턴 적용
                for pattern in self.relational_patterns:
                    if pattern["db_name"] == db_name:
                        for relation in pattern.get("company_relations", []):
                            if relation["field"] in record:
                                record[f"{relation['field']}_관계"] = relation["relation_type"]
        
        return relational_data
    
    def _validate_with_templates(self, relational_data: Dict) -> Dict:
        """템플릿 기반 품질 검증"""
        print("🔍 템플릿 기반 품질 검증")
        
        quality_check = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "db_quality": {},
            "overall_quality": 0.0
        }
        
        for db_name, records in relational_data.items():
            template = self.templates.get(db_name, {})
            db_quality = {
                "total": len(records),
                "valid": 0,
                "invalid": 0,
                "quality_rate": 0.0
            }
            
            for record in records:
                quality_check["total_records"] += 1
                
                # 템플릿 기반 검증
                if self._validate_record_with_template(record, template):
                    db_quality["valid"] += 1
                    quality_check["valid_records"] += 1
                else:
                    db_quality["invalid"] += 1
                    quality_check["invalid_records"] += 1
            
            # DB별 품질률 계산
            if db_quality["total"] > 0:
                db_quality["quality_rate"] = db_quality["valid"] / db_quality["total"]
            
            quality_check["db_quality"][db_name] = db_quality
        
        # 전체 품질률 계산
        if quality_check["total_records"] > 0:
            quality_check["overall_quality"] = quality_check["valid_records"] / quality_check["total_records"]
        
        return quality_check
    
    def _validate_record_with_template(self, record: Dict, template: Dict) -> bool:
        """템플릿 기반 레코드 검증"""
        if not template:
            return True
        
        # 필수 필드 확인
        required_fields = [field for field, info in template.items() 
                          if isinstance(info, dict) and info.get("required", False)]
        
        for required_field in required_fields:
            if required_field not in record or not record[required_field]:
                return False
        
        # 필드 타입 확인
        for field, info in template.items():
            if isinstance(info, dict) and field in record:
                field_type = info.get("type", "text")
                value = record[field]
                
                if field_type == "number" and value:
                    try:
                        float(str(value).replace(',', ''))
                    except ValueError:
                        return False
        
        return True
    
    def _determine_review_necessity(self, quality_check: Dict, relational_data: Dict) -> Dict:
        """노팀장님 검토 필요성 판단"""
        overall_quality = quality_check["overall_quality"]
        
        if overall_quality >= 0.95:
            review_decision = {
                "needs_review": False,
                "reason": "품질이 우수하여 서대리 직접 처리",
                "quality_level": "excellent"
            }
        elif overall_quality >= 0.80:
            review_decision = {
                "needs_review": False,
                "reason": "품질이 양호하여 서대리 직접 처리",
                "quality_level": "good"
            }
        elif overall_quality >= 0.60:
            review_decision = {
                "needs_review": True,
                "reason": "품질 검토가 필요하여 노팀장님 검토 요청",
                "quality_level": "needs_review"
            }
        else:
            review_decision = {
                "needs_review": True,
                "reason": "품질이 낮아 노팀장님 검토 필수",
                "quality_level": "requires_nodeteam"
            }
        
        return review_decision
    
    def get_automation_report(self) -> Dict:
        """자동화 보고서 생성"""
        report = {
            "phase": "phase2_automation",
            "templates_loaded": len(self.templates),
            "insurance_patterns_loaded": len(self.insurance_patterns),
            "relational_patterns_loaded": len(self.relational_patterns),
            "keyword_mappings_loaded": len(self.keyword_mappings)
        }
        
        return report

def main():
    """메인 실행 함수 (테스트)"""
    print("🚀 두산중공업 Phase 2 자동화 시스템 테스트")
    print("=" * 50)
    
    # 학습된 템플릿 (Phase 1에서 학습된 데이터)
    learned_templates = {
        "templates": {
            "📊 기업 위험 프로파일 DB": {
                "위험요소명": {"type": "text", "required": True},
                "위험유형": {"type": "text", "required": True},
                "위험도": {"type": "text", "required": True},
                "보험연계": {"type": "text", "required": False}
            },
            "👥 기업 핵심 인물 DB": {
                "이름": {"type": "text", "required": True},
                "직책": {"type": "text", "required": True},
                "경력": {"type": "text", "required": False},
                "보험연계": {"type": "text", "required": False}
            }
        },
        "insurance_patterns": [
            {
                "db_name": "📊 기업 위험 프로파일 DB",
                "field": "위험요소명",
                "value": "환율 리스크",
                "보험연계": "환율 리스크 보험 가입 검토 필요"
            }
        ],
        "relational_patterns": [],
        "keyword_mappings": {}
    }
    
    automation_system = DoosanPhase2AutomationSystem(learned_templates)
    
    # 테스트 데이터
    test_data = """
    두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다.
    정경훈 대표이사는 30년 경력의 전문가입니다.
    2024년 매출 15,000억원을 달성했습니다.
    태양광 발전소 200MW 프로젝트를 진행 중입니다.
    """
    
    # Phase 2 자동화 처리
    result = automation_system.process_with_learned_templates(test_data, "시대리")
    
    print(f"📊 처리 결과:")
    print(f"- 품질 수준: {result['review_decision']['quality_level']}")
    print(f"- 검토 필요: {result['review_decision']['needs_review']}")
    print(f"- 검토 사유: {result['review_decision']['reason']}")
    
    # 자동화 보고서
    report = automation_system.get_automation_report()
    print(f"📋 자동화 보고서: {report}")

if __name__ == "__main__":
    main() 