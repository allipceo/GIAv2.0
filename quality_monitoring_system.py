"""
품질 모니터링 시스템
- 선택적 DB화 품질 실시간 추적
- 품질 지표 모니터링
- 자동 롤백 시스템
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class QualityMonitor:
    def __init__(self):
        self.quality_metrics = {
            'extraction_accuracy': 0.0,      # 추출 정확도
            'db_classification_accuracy': 0.0, # DB 분류 정확도
            'missing_important_info': 0.0,    # 누락 중요정보
            'unnecessary_extraction': 0.0,    # 불필요 추출
            'processing_efficiency': 0.0,     # 처리 효율성
            'system_error_rate': 0.0          # 시스템 오류율
        }
        
        self.thresholds = {
            'extraction_accuracy': 0.90,      # 목표 90% 이상
            'db_classification_accuracy': 0.85, # 목표 85% 이상
            'missing_important_info': 0.05,   # 목표 5% 이하
            'unnecessary_extraction': 0.10,   # 목표 10% 이하
            'processing_efficiency': 0.25,    # 목표 25-35%
            'system_error_rate': 0.05         # 목표 5% 이하
        }
        
        self.quality_history = []
        self.error_log = []
    
    def calculate_extraction_accuracy(self, extracted_items: List, total_important_items: List) -> float:
        """추출 정확도 계산"""
        if not total_important_items:
            return 1.0
        
        correct_extractions = 0
        for item in extracted_items:
            if any(important in item['content'] for important in total_important_items):
                correct_extractions += 1
        
        return correct_extractions / len(total_important_items) if total_important_items else 0.0
    
    def calculate_db_classification_accuracy(self, db_entries: Dict, manual_verification: Dict) -> float:
        """DB 분류 정확도 계산"""
        if not manual_verification:
            return 1.0
        
        correct_classifications = 0
        total_classifications = 0
        
        for db_name, entries in db_entries.items():
            if db_name in manual_verification:
                for entry in entries:
                    total_classifications += 1
                    if self._is_correctly_classified(entry, manual_verification[db_name]):
                        correct_classifications += 1
        
        return correct_classifications / total_classifications if total_classifications > 0 else 0.0
    
    def _is_correctly_classified(self, entry: Dict, manual_verification: List) -> bool:
        """분류 정확성 판단"""
        for manual_entry in manual_verification:
            if entry.get('위험_유형') == manual_entry.get('위험_유형') or \
               entry.get('재무_정보') == manual_entry.get('재무_정보') or \
               entry.get('인물_정보') == manual_entry.get('인물_정보'):
                return True
        return False
    
    def calculate_missing_important_info(self, extracted_items: List, all_important_items: List) -> float:
        """누락 중요정보 비율 계산"""
        if not all_important_items:
            return 0.0
        
        extracted_content = ' '.join([item['content'] for item in extracted_items])
        missing_count = 0
        
        for important_item in all_important_items:
            if important_item not in extracted_content:
                missing_count += 1
        
        return missing_count / len(all_important_items)
    
    def calculate_unnecessary_extraction(self, extracted_items: List, core_keywords: List) -> float:
        """불필요 추출 비율 계산"""
        if not extracted_items:
            return 0.0
        
        unnecessary_count = 0
        
        for item in extracted_items:
            has_core_keyword = any(keyword in item['content'] for keyword in core_keywords)
            if not has_core_keyword:
                unnecessary_count += 1
        
        return unnecessary_count / len(extracted_items)
    
    def calculate_processing_efficiency(self, db_entries_count: int, total_paragraphs: int) -> float:
        """처리 효율성 계산"""
        if total_paragraphs == 0:
            return 0.0
        
        return db_entries_count / total_paragraphs
    
    def update_quality_metrics(self, processing_result: Dict, manual_verification: Dict = None) -> Dict:
        """품질 지표 업데이트"""
        # 기본 메트릭 계산
        total_paragraphs = processing_result['summary']['전체_문단_수']
        db_entries_count = processing_result['summary']['DB_엔트리_수']
        
        # 추출된 항목들
        extracted_items = []
        for category, items in processing_result['core_data'].items():
            if isinstance(items, list):
                extracted_items.extend(items)
        
        # 핵심 키워드 (보험 관련)
        core_keywords = ['위험', '보험', '매출', '투자', 'CEO', '정책', '프로젝트']
        
        # 품질 지표 계산
        self.quality_metrics['processing_efficiency'] = self.calculate_processing_efficiency(
            db_entries_count, total_paragraphs
        )
        
        self.quality_metrics['unnecessary_extraction'] = self.calculate_unnecessary_extraction(
            extracted_items, core_keywords
        )
        
        # 수동 검증이 있는 경우 정확도 계산
        if manual_verification:
            self.quality_metrics['extraction_accuracy'] = self.calculate_extraction_accuracy(
                extracted_items, manual_verification.get('important_items', [])
            )
            
            self.quality_metrics['db_classification_accuracy'] = self.calculate_db_classification_accuracy(
                processing_result['db_entries'], manual_verification
            )
            
            self.quality_metrics['missing_important_info'] = self.calculate_missing_important_info(
                extracted_items, manual_verification.get('important_items', [])
            )
        
        # 품질 이력 저장
        quality_record = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.quality_metrics.copy(),
            'processing_result': processing_result['summary']
        }
        self.quality_history.append(quality_record)
        
        return self.quality_metrics
    
    def check_quality_thresholds(self) -> Dict:
        """품질 임계값 확인"""
        alerts = {
            'warnings': [],
            'critical': [],
            'recommendations': []
        }
        
        for metric, value in self.quality_metrics.items():
            threshold = self.thresholds.get(metric, 0.0)
            
            if metric in ['extraction_accuracy', 'db_classification_accuracy', 'processing_efficiency']:
                # 높을수록 좋은 지표
                if value < threshold:
                    if value < threshold * 0.8:  # 20% 이상 낮으면 critical
                        alerts['critical'].append(f"{metric}: {value:.1%} (목표: {threshold:.1%})")
                    else:
                        alerts['warnings'].append(f"{metric}: {value:.1%} (목표: {threshold:.1%})")
            
            elif metric in ['missing_important_info', 'unnecessary_extraction', 'system_error_rate']:
                # 낮을수록 좋은 지표
                if value > threshold:
                    if value > threshold * 1.5:  # 50% 이상 높으면 critical
                        alerts['critical'].append(f"{metric}: {value:.1%} (목표: {threshold:.1%})")
                    else:
                        alerts['warnings'].append(f"{metric}: {value:.1%} (목표: {threshold:.1%})")
        
        # 권장사항 생성
        if alerts['critical']:
            alerts['recommendations'].append("즉시 수동 검증 모드로 전환")
            alerts['recommendations'].append("이전 안정 버전으로 롤백 검토")
        
        elif alerts['warnings']:
            alerts['recommendations'].append("노팀장님 검증 강화")
            alerts['recommendations'].append("필터링 규칙 조정 검토")
        
        return alerts
    
    def generate_quality_report(self) -> Dict:
        """품질 보고서 생성"""
        alerts = self.check_quality_thresholds()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'quality_metrics': self.quality_metrics,
            'alerts': alerts,
            'trend_analysis': self._analyze_trends(),
            'recommendations': alerts['recommendations']
        }
        
        return report
    
    def _analyze_trends(self) -> Dict:
        """트렌드 분석"""
        if len(self.quality_history) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_metrics = self.quality_history[-1]['metrics']
        previous_metrics = self.quality_history[-2]['metrics']
        
        trends = {}
        for metric in self.quality_metrics.keys():
            if metric in recent_metrics and metric in previous_metrics:
                change = recent_metrics[metric] - previous_metrics[metric]
                trends[metric] = {
                    'change': change,
                    'direction': 'improving' if change > 0 else 'declining' if change < 0 else 'stable'
                }
        
        return trends
    
    def emergency_rollback_check(self) -> bool:
        """긴급 롤백 필요성 확인"""
        critical_count = len(self.check_quality_thresholds()['critical'])
        return critical_count >= 2  # 2개 이상의 critical 알림이 있으면 롤백
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """오류 로그 기록"""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        self.error_log.append(error_record)
        
        # 오류율 업데이트
        if len(self.quality_history) > 0:
            self.quality_metrics['system_error_rate'] = len(self.error_log) / len(self.quality_history)

# 사용 예시
if __name__ == "__main__":
    monitor = QualityMonitor()
    
    # 가상의 처리 결과
    processing_result = {
        'summary': {
            '전체_문단_수': 20,
            'DB_엔트리_수': 6,
            '추출된_핵심_정보_수': 8
        },
        'core_data': {
            'risk_profile': [
                {'content': '기술적 위험요소가 존재합니다', 'priority_score': 15},
                {'content': '재무적 리스크가 높습니다', 'priority_score': 12}
            ],
            'financial_data': [
                {'content': '500억원 투자 계획', 'priority_score': 18}
            ]
        },
        'db_entries': {
            '기업_위험_프로파일_DB': [
                {'위험_유형': '기술위험', '위험_설명': '기술적 위험요소가 존재합니다'}
            ]
        }
    }
    
    # 품질 지표 업데이트
    metrics = monitor.update_quality_metrics(processing_result)
    
    # 품질 보고서 생성
    report = monitor.generate_quality_report()
    
    print("📊 품질 모니터링 결과:")
    print(json.dumps(report, indent=2, ensure_ascii=False)) 