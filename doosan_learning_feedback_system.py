#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 학습 피드백 루프 시스템
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: 노팀장님 제안의 학습 피드백 루프 구현
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class DoosanLearningFeedbackSystem:
    """두산중공업 학습 피드백 루프 시스템"""
    
    def __init__(self):
        """초기화"""
        self.learning_history = []
        self.template_updates = []
        self.pattern_enhancements = []
        self.quality_metrics = []
        
        # 학습 데이터 저장소
        self.learning_data_path = "doosan_learning_data.json"
        self.load_learning_data()
    
    def load_learning_data(self):
        """학습 데이터 로드"""
        if os.path.exists(self.learning_data_path):
            with open(self.learning_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.learning_history = data.get("learning_history", [])
                self.template_updates = data.get("template_updates", [])
                self.pattern_enhancements = data.get("pattern_enhancements", [])
                self.quality_metrics = data.get("quality_metrics", [])
    
    def save_learning_data(self):
        """학습 데이터 저장"""
        data = {
            "learning_history": self.learning_history,
            "template_updates": self.template_updates,
            "pattern_enhancements": self.pattern_enhancements,
            "quality_metrics": self.quality_metrics,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.learning_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def process_nodeteam_feedback(self, nodeteam_result: Dict) -> Dict:
        """노팀장님 피드백 처리"""
        print("🔄 노팀장님 피드백 처리 시작")
        
        # 1. 노팀장님 처리 결과 학습
        learning_entry = self._learn_from_nodeteam_result(nodeteam_result)
        
        # 2. 템플릿 업데이트 생성
        template_updates = self._generate_template_updates(learning_entry)
        
        # 3. 패턴 강화 생성
        pattern_enhancements = self._generate_pattern_enhancements(learning_entry)
        
        # 4. 품질 메트릭 업데이트
        quality_metrics = self._update_quality_metrics(learning_entry)
        
        # 5. 학습 데이터 저장
        self.learning_history.append(learning_entry)
        self.template_updates.extend(template_updates)
        self.pattern_enhancements.extend(pattern_enhancements)
        self.quality_metrics.append(quality_metrics)
        self.save_learning_data()
        
        feedback_result = {
            "learning_entry": learning_entry,
            "template_updates": template_updates,
            "pattern_enhancements": pattern_enhancements,
            "quality_metrics": quality_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        return feedback_result
    
    def _learn_from_nodeteam_result(self, nodeteam_result: Dict) -> Dict:
        """노팀장님 결과에서 학습"""
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "nodeteam_patterns": {},
            "insurance_insights": [],
            "policy_classifications": [],
            "project_classifications": [],
            "quality_improvements": []
        }
        
        # 보험 인사이트 패턴 학습
        for db_name, records in nodeteam_result.get("structured_data", {}).items():
            for record in records:
                if "보험_인사이트" in record:
                    learning_entry["insurance_insights"].append({
                        "db_name": db_name,
                        "risk_type": record.get("리스크_유형", ""),
                        "risk_level": record.get("리스크_등급", ""),
                        "insurance_insight": record["보험_인사이트"]
                    })
                
                # 정책 분류 학습
                if "정책_분야" in record:
                    learning_entry["policy_classifications"].append({
                        "original": record["정책_분야"],
                        "expanded": record.get("정책_분야_확장", record["정책_분야"])
                    })
                
                # 프로젝트 분류 학습
                if "프로젝트_유형" in record:
                    learning_entry["project_classifications"].append({
                        "original": record["프로젝트_유형"],
                        "expanded": record.get("프로젝트_유형_확장", record["프로젝트_유형"])
                    })
        
        return learning_entry
    
    def _generate_template_updates(self, learning_entry: Dict) -> List[Dict]:
        """템플릿 업데이트 생성"""
        template_updates = []
        
        # 보험 인사이트 필드 추가
        if learning_entry["insurance_insights"]:
            template_updates.append({
                "type": "field_addition",
                "db_name": "📊 기업 위험 프로파일 DB",
                "field_name": "보험_인사이트",
                "field_type": "text",
                "required": False,
                "description": "노팀장님 보험 관점 인사이트"
            })
        
        # 정책 분야 확장 필드 추가
        if learning_entry["policy_classifications"]:
            template_updates.append({
                "type": "field_addition",
                "db_name": "🏛️ 정부 정책 영향 분석 DB",
                "field_name": "정책_분야_확장",
                "field_type": "text",
                "required": False,
                "description": "확장된 정책 분야 분류"
            })
        
        # 프로젝트 유형 확장 필드 추가
        if learning_entry["project_classifications"]:
            template_updates.append({
                "type": "field_addition",
                "db_name": "🔋 신재생에너지 프로젝트 DB",
                "field_name": "프로젝트_유형_확장",
                "field_type": "text",
                "required": False,
                "description": "확장된 프로젝트 유형 분류"
            })
        
        return template_updates
    
    def _generate_pattern_enhancements(self, learning_entry: Dict) -> List[Dict]:
        """패턴 강화 생성"""
        pattern_enhancements = []
        
        # 보험 인사이트 패턴 강화
        for insight in learning_entry["insurance_insights"]:
            pattern_enhancements.append({
                "type": "insurance_insight_pattern",
                "risk_type": insight["risk_type"],
                "risk_level": insight["risk_level"],
                "insurance_insight": insight["insurance_insight"],
                "confidence": 0.95
            })
        
        # 정책 분류 패턴 강화
        for policy in learning_entry["policy_classifications"]:
            pattern_enhancements.append({
                "type": "policy_classification_pattern",
                "original": policy["original"],
                "expanded": policy["expanded"],
                "confidence": 0.90
            })
        
        # 프로젝트 분류 패턴 강화
        for project in learning_entry["project_classifications"]:
            pattern_enhancements.append({
                "type": "project_classification_pattern",
                "original": project["original"],
                "expanded": project["expanded"],
                "confidence": 0.90
            })
        
        return pattern_enhancements
    
    def _update_quality_metrics(self, learning_entry: Dict) -> Dict:
        """품질 메트릭 업데이트"""
        quality_metrics = {
            "timestamp": datetime.now().isoformat(),
            "insurance_insight_quality": len(learning_entry["insurance_insights"]),
            "policy_classification_accuracy": len(learning_entry["policy_classifications"]),
            "project_classification_accuracy": len(learning_entry["project_classifications"]),
            "overall_improvement": 0.0
        }
        
        # 전체 개선도 계산
        total_improvements = (
            quality_metrics["insurance_insight_quality"] +
            quality_metrics["policy_classification_accuracy"] +
            quality_metrics["project_classification_accuracy"]
        )
        
        quality_metrics["overall_improvement"] = total_improvements / 3
        
        return quality_metrics
    
    def get_learning_report(self) -> Dict:
        """학습 보고서 생성"""
        report = {
            "total_learning_entries": len(self.learning_history),
            "total_template_updates": len(self.template_updates),
            "total_pattern_enhancements": len(self.pattern_enhancements),
            "quality_trend": self._calculate_quality_trend(),
            "recent_improvements": self._get_recent_improvements(),
            "learning_progress": {
                "insurance_insights_learned": len([e for e in self.learning_history if e["insurance_insights"]]),
                "policy_classifications_learned": len([e for e in self.learning_history if e["policy_classifications"]]),
                "project_classifications_learned": len([e for e in self.learning_history if e["project_classifications"]])
            }
        }
        
        return report
    
    def _calculate_quality_trend(self) -> Dict:
        """품질 트렌드 계산"""
        if len(self.quality_metrics) < 2:
            return {"trend": "insufficient_data"}
        
        recent_metrics = self.quality_metrics[-5:]  # 최근 5개
        if len(recent_metrics) < 2:
            return {"trend": "insufficient_data"}
        
        first_avg = sum(m["overall_improvement"] for m in recent_metrics[:len(recent_metrics)//2]) / (len(recent_metrics)//2)
        second_avg = sum(m["overall_improvement"] for m in recent_metrics[len(recent_metrics)//2:]) / (len(recent_metrics) - len(recent_metrics)//2)
        
        if second_avg > first_avg:
            trend = "improving"
        elif second_avg < first_avg:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "improvement_rate": (second_avg - first_avg) / first_avg if first_avg > 0 else 0
        }
    
    def _get_recent_improvements(self) -> List[Dict]:
        """최근 개선사항 조회"""
        recent_improvements = []
        
        # 최근 3개의 템플릿 업데이트
        for update in self.template_updates[-3:]:
            recent_improvements.append({
                "type": "template_update",
                "description": f"{update['db_name']}에 {update['field_name']} 필드 추가",
                "timestamp": update.get("timestamp", "unknown")
            })
        
        # 최근 3개의 패턴 강화
        for enhancement in self.pattern_enhancements[-3:]:
            recent_improvements.append({
                "type": "pattern_enhancement",
                "description": f"{enhancement['type']} 패턴 강화",
                "confidence": enhancement.get("confidence", 0.0)
            })
        
        return recent_improvements

def main():
    """메인 실행 함수 (테스트)"""
    print("🔄 두산중공업 학습 피드백 루프 시스템 테스트")
    print("=" * 50)
    
    feedback_system = DoosanLearningFeedbackSystem()
    
    # 테스트용 노팀장님 결과
    test_nodeteam_result = {
        "structured_data": {
            "📊 기업 위험 프로파일 DB": [
                {
                    "리스크_유형": "공급망 리스크",
                    "리스크_등급": "매우 높음",
                    "보험_인사이트": "공급망 중단 보험 가입 필수 (예상 보험료: 200-300억원)"
                }
            ],
            "🏛️ 정부 정책 영향 분석 DB": [
                {
                    "정책_분야": "원자력",
                    "정책_분야_확장": "원자력 발전 정책"
                }
            ],
            "🔋 신재생에너지 프로젝트 DB": [
                {
                    "프로젝트_유형": "SMR",
                    "프로젝트_유형_확장": "소형모듈원전"
                }
            ]
        }
    }
    
    # 피드백 처리
    feedback_result = feedback_system.process_nodeteam_feedback(test_nodeteam_result)
    
    print(f"📊 피드백 처리 결과:")
    print(f"- 학습 항목: {len(feedback_result['learning_entry']['insurance_insights'])}개")
    print(f"- 템플릿 업데이트: {len(feedback_result['template_updates'])}개")
    print(f"- 패턴 강화: {len(feedback_result['pattern_enhancements'])}개")
    
    # 학습 보고서
    report = feedback_system.get_learning_report()
    print(f"📋 학습 보고서: {report}")

if __name__ == "__main__":
    main() 