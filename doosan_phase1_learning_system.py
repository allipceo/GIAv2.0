#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 Phase 1 학습 시스템
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 노팀장님 처리 결과를 학습하여 자동화 로직 개선
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class DoosanPhase1LearningSystem:
    """두산중공업 Phase 1 학습 시스템"""
    
    def __init__(self):
        """초기화"""
        self.learning_data = []
        self.templates = {
            "📊 기업 위험 프로파일 DB": {},
            "💰 기업 재무 및 프로젝트 DB": {},
            "🔋 신재생에너지 프로젝트 DB": {},
            "👥 기업 핵심 인물 DB": {},
            "🏛️ 정부 정책 영향 분석 DB": {},
            "🌍 글로벌 보험중개 시장 DB": {}
        }
        self.insurance_insights = []
        self.relational_patterns = []
        
    def learn_from_nodeteam_processing(self, original_text: str, nodeteam_result: Dict) -> Dict:
        """노팀장님 처리 결과 학습"""
        print("🧠 노팀장님 처리 결과 학습 시작")
        print("=" * 50)
        
        # 학습 데이터 저장
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_text": original_text,
            "nodeteam_result": nodeteam_result,
            "learning_insights": {}
        }
        
        # 1. 보험 인사이트 패턴 학습
        insurance_patterns = self._extract_insurance_patterns(nodeteam_result)
        learning_entry["learning_insights"]["insurance_patterns"] = insurance_patterns
        
        # 2. 관계형 연결 패턴 학습
        relational_patterns = self._extract_relational_patterns(nodeteam_result)
        learning_entry["learning_insights"]["relational_patterns"] = relational_patterns
        
        # 3. 템플릿 패턴 학습
        template_patterns = self._extract_template_patterns(nodeteam_result)
        learning_entry["learning_insights"]["template_patterns"] = template_patterns
        
        # 4. 키워드 매핑 학습
        keyword_mappings = self._extract_keyword_mappings(original_text, nodeteam_result)
        learning_entry["learning_insights"]["keyword_mappings"] = keyword_mappings
        
        # 학습 데이터에 추가
        self.learning_data.append(learning_entry)
        
        # 템플릿 업데이트
        self._update_templates(learning_entry)
        
        print("✅ 노팀장님 처리 결과 학습 완료")
        return learning_entry
    
    def _extract_insurance_patterns(self, nodeteam_result: Dict) -> List[Dict]:
        """보험 인사이트 패턴 추출"""
        insurance_patterns = []
        
        # 보험 관련 키워드 패턴 추출
        insurance_keywords = [
            '보험', '리스크', '위험', '중개', '영업', '기회', '상품', '가입', '보장',
            '환율', '원자재', '프로젝트', '계약', '책임', '배상', '보상'
        ]
        
        for db_name, records in nodeteam_result.items():
            for record in records:
                if isinstance(record, dict):
                    for key, value in record.items():
                        if any(keyword in str(value) for keyword in insurance_keywords):
                            pattern = {
                                "db_name": db_name,
                                "field": key,
                                "value": value,
                                "insurance_keywords": [kw for kw in insurance_keywords if kw in str(value)]
                            }
                            insurance_patterns.append(pattern)
        
        return insurance_patterns
    
    def _extract_relational_patterns(self, nodeteam_result: Dict) -> List[Dict]:
        """관계형 연결 패턴 추출"""
        relational_patterns = []
        
        # 회사 정보와의 관계 패턴 추출
        company_relation_patterns = [
            '회사명', '기업명', '법인명', '대표이사', '설립일'
        ]
        
        for db_name, records in nodeteam_result.items():
            for record in records:
                if isinstance(record, dict):
                    # 회사 정보와의 관계 확인
                    company_relations = []
                    for key, value in record.items():
                        if any(pattern in str(value) for pattern in company_relation_patterns):
                            company_relations.append({
                                "field": key,
                                "value": value,
                                "relation_type": "company_info"
                            })
                    
                    if company_relations:
                        pattern = {
                            "db_name": db_name,
                            "record": record,
                            "company_relations": company_relations
                        }
                        relational_patterns.append(pattern)
        
        return relational_patterns
    
    def _extract_template_patterns(self, nodeteam_result: Dict) -> Dict:
        """템플릿 패턴 추출"""
        template_patterns = {}
        
        for db_name, records in nodeteam_result.items():
            if records:
                # 첫 번째 레코드를 템플릿으로 사용
                template = records[0] if isinstance(records[0], dict) else {}
                
                # 필드 타입 분석
                field_types = {}
                for key, value in template.items():
                    if isinstance(value, str):
                        if any(char.isdigit() for char in value):
                            field_types[key] = "number_or_text"
                        else:
                            field_types[key] = "text"
                    elif isinstance(value, (int, float)):
                        field_types[key] = "number"
                    elif isinstance(value, list):
                        field_types[key] = "multi_select"
                    else:
                        field_types[key] = "unknown"
                
                template_patterns[db_name] = {
                    "template": template,
                    "field_types": field_types,
                    "required_fields": list(template.keys())
                }
        
        return template_patterns
    
    def _extract_keyword_mappings(self, original_text: str, nodeteam_result: Dict) -> Dict:
        """키워드 매핑 추출"""
        keyword_mappings = {}
        
        # 원본 텍스트에서 키워드 추출
        original_keywords = self._extract_keywords_from_text(original_text)
        
        # 노팀장님 결과에서 키워드 추출
        result_keywords = self._extract_keywords_from_result(nodeteam_result)
        
        # 키워드 매핑 생성
        for original_keyword in original_keywords:
            for result_keyword in result_keywords:
                similarity = self._calculate_keyword_similarity(original_keyword, result_keyword)
                if similarity > 0.7:  # 70% 이상 유사
                    if original_keyword not in keyword_mappings:
                        keyword_mappings[original_keyword] = []
                    keyword_mappings[original_keyword].append({
                        "result_keyword": result_keyword,
                        "similarity": similarity
                    })
        
        return keyword_mappings
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 한글 키워드 추출
        korean_keywords = re.findall(r'[가-힣]+', text)
        
        # 영문 키워드 추출
        english_keywords = re.findall(r'\b[A-Za-z]+\b', text)
        
        # 숫자 포함 키워드 추출
        number_keywords = re.findall(r'[가-힣]*\d+[가-힣]*', text)
        
        all_keywords = korean_keywords + english_keywords + number_keywords
        return list(set(all_keywords))
    
    def _extract_keywords_from_result(self, result: Dict) -> List[str]:
        """결과에서 키워드 추출"""
        keywords = []
        
        for db_name, records in result.items():
            for record in records:
                if isinstance(record, dict):
                    for key, value in record.items():
                        keywords.extend(self._extract_keywords_from_text(str(value)))
        
        return list(set(keywords))
    
    def _calculate_keyword_similarity(self, keyword1: str, keyword2: str) -> float:
        """키워드 유사도 계산"""
        if keyword1 == keyword2:
            return 1.0
        
        # 부분 문자열 포함 여부
        if keyword1 in keyword2 or keyword2 in keyword1:
            return 0.8
        
        # 문자 유사도 계산
        from difflib import SequenceMatcher
        return SequenceMatcher(None, keyword1, keyword2).ratio()
    
    def _update_templates(self, learning_entry: Dict):
        """템플릿 업데이트"""
        template_patterns = learning_entry["learning_insights"]["template_patterns"]
        
        for db_name, pattern in template_patterns.items():
            if db_name in self.templates:
                # 기존 템플릿과 병합
                existing_template = self.templates[db_name]
                
                # 새로운 필드 추가
                for field, field_type in pattern["field_types"].items():
                    if field not in existing_template:
                        existing_template[field] = {
                            "type": field_type,
                            "required": field in pattern["required_fields"],
                            "learned_from": learning_entry["timestamp"]
                        }
        
        # 보험 인사이트 패턴 저장
        self.insurance_insights.extend(learning_entry["learning_insights"]["insurance_patterns"])
        
        # 관계형 패턴 저장
        self.relational_patterns.extend(learning_entry["learning_insights"]["relational_patterns"])
    
    def generate_improved_processor(self) -> Dict:
        """개선된 처리기 생성"""
        print("🔧 개선된 처리기 생성")
        
        improved_processor = {
            "templates": self.templates,
            "insurance_patterns": self.insurance_insights,
            "relational_patterns": self.relational_patterns,
            "keyword_mappings": {},
            "learning_summary": {
                "total_learning_entries": len(self.learning_data),
                "total_insurance_patterns": len(self.insurance_insights),
                "total_relational_patterns": len(self.relational_patterns),
                "db_templates": {db: len(template) for db, template in self.templates.items()}
            }
        }
        
        # 키워드 매핑 통합
        for entry in self.learning_data:
            keyword_mappings = entry["learning_insights"]["keyword_mappings"]
            for original_keyword, mappings in keyword_mappings.items():
                if original_keyword not in improved_processor["keyword_mappings"]:
                    improved_processor["keyword_mappings"][original_keyword] = []
                improved_processor["keyword_mappings"][original_keyword].extend(mappings)
        
        return improved_processor
    
    def save_learning_data(self, filename: str = None):
        """학습 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"doosan_phase1_learning_{timestamp}.json"
        
        learning_summary = {
            "learning_data": self.learning_data,
            "templates": self.templates,
            "insurance_insights": self.insurance_insights,
            "relational_patterns": self.relational_patterns,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(learning_summary, f, ensure_ascii=False, indent=2)
        
        print(f"💾 학습 데이터 저장 완료: {filename}")
    
    def get_learning_report(self) -> Dict:
        """학습 보고서 생성"""
        report = {
            "total_learning_entries": len(self.learning_data),
            "total_insurance_patterns": len(self.insurance_insights),
            "total_relational_patterns": len(self.relational_patterns),
            "db_templates": {db: len(template) for db, template in self.templates.items()},
            "learning_progress": {
                "phase1_complete": len(self.learning_data) >= 3,  # 3개 이상 학습 시 Phase 1 완료
                "templates_ready": all(len(template) > 0 for template in self.templates.values()),
                "insurance_insights_ready": len(self.insurance_insights) > 0,
                "relational_patterns_ready": len(self.relational_patterns) > 0
            }
        }
        
        return report

def main():
    """메인 실행 함수 (테스트)"""
    print("🧠 두산중공업 Phase 1 학습 시스템 테스트")
    print("=" * 50)
    
    learning_system = DoosanPhase1LearningSystem()
    
    # 테스트 데이터 (노팀장님 처리 결과 시뮬레이션)
    original_text = """
    두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다.
    정경훈 대표이사는 30년 경력의 전문가입니다.
    2024년 매출 15,000억원을 달성했습니다.
    태양광 발전소 200MW 프로젝트를 진행 중입니다.
    """
    
    nodeteam_result = {
        "📊 기업 위험 프로파일 DB": [
            {
                "위험요소명": "환율 리스크",
                "위험유형": "재무위험",
                "위험도": "높음",
                "설명": "해외 프로젝트로 인한 환율 변동 리스크",
                "보험연계": "환율 리스크 보험 가입 검토 필요"
            }
        ],
        "👥 기업 핵심 인물 DB": [
            {
                "이름": "정경훈",
                "직책": "대표이사",
                "경력": "30년",
                "전문분야": "중공업 경영",
                "보험연계": "경영진 책임보험 가입 필요"
            }
        ]
    }
    
    # 학습 실행
    learning_result = learning_system.learn_from_nodeteam_processing(original_text, nodeteam_result)
    
    print(f"학습된 보험 패턴: {len(learning_result['learning_insights']['insurance_patterns'])}개")
    print(f"학습된 관계형 패턴: {len(learning_result['learning_insights']['relational_patterns'])}개")
    print(f"학습된 템플릿 패턴: {len(learning_result['learning_insights']['template_patterns'])}개")
    
    # 개선된 처리기 생성
    improved_processor = learning_system.generate_improved_processor()
    print(f"개선된 처리기 생성 완료")
    
    # 학습 보고서
    report = learning_system.get_learning_report()
    print(f"학습 진행률: {report['learning_progress']}")

if __name__ == "__main__":
    main() 