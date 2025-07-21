"""
선택적 데이터베이스화 시스템
- 핵심 정보만 선별하여 DB화
- 불필요한 정보는 제외하여 시스템 안정성 확보
"""

import json
import re
from typing import Dict, List, Tuple

class SelectiveDBExtractor:
    def __init__(self):
        # 핵심 키워드 정의 (보험 관련)
        self.insurance_keywords = {
            'risk': ['위험', '리스크', '사고', '손실', '보험'],
            'financial': ['매출', '수익', '자본', '투자', '재무'],
            'personnel': ['CEO', '대표', '이사', '책임자', '인물'],
            'policy': ['정책', '규제', '법령', '인허가', '정부'],
            'project': ['프로젝트', '사업', '계획', '투자', '시설']
        }
        
        # 제외할 키워드 (일반적 설명)
        self.exclude_keywords = [
            '일반적으로', '대부분의', '전반적으로', '상세한', '자세한',
            '배경', '개요', '소개', '개념', '정의'
        ]
    
    def extract_core_info(self, text: str) -> Dict:
        """핵심 정보만 선별 추출"""
        core_data = {
            'risk_profile': [],
            'financial_data': [],
            'key_personnel': [],
            'policy_impact': [],
            'project_info': []
        }
        
        # 문단별 분석
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if self._is_core_info(para):
                category = self._classify_content(para)
                if category:
                    core_data[category].append(para.strip())
        
        return core_data
    
    def _is_core_info(self, text: str) -> bool:
        """핵심 정보인지 판단"""
        # 제외 키워드가 포함된 경우 제외
        for exclude_word in self.exclude_keywords:
            if exclude_word in text:
                return False
        
        # 핵심 키워드가 포함된 경우 포함
        for category, keywords in self.insurance_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return True
        
        return False
    
    def _classify_content(self, text: str) -> str:
        """내용 분류"""
        scores = {
            'risk_profile': 0,
            'financial_data': 0,
            'key_personnel': 0,
            'policy_impact': 0,
            'project_info': 0
        }
        
        for category, keywords in self.insurance_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        # 가장 높은 점수의 카테고리 반환
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def create_db_entries(self, core_data: Dict) -> Dict:
        """DB 엔트리 생성 (핵심 정보만)"""
        db_entries = {
            '기업_위험_프로파일_DB': [],
            '기업_재무_및_프로젝트_DB': [],
            '기업_핵심_인물_DB': [],
            '정부_정책_영향_분석_DB': [],
            '글로벌_보험중개_시장_DB': []
        }
        
        # 위험 프로파일
        for risk_info in core_data['risk_profile']:
            db_entries['기업_위험_프로파일_DB'].append({
                '위험_유형': self._extract_risk_type(risk_info),
                '위험_설명': risk_info[:200],
                '보험_관련성': '높음'
            })
        
        # 재무 데이터
        for financial_info in core_data['financial_data']:
            db_entries['기업_재무_및_프로젝트_DB'].append({
                '재무_정보': financial_info[:200],
                '보험료_산정_관련': '있음'
            })
        
        # 핵심 인물
        for personnel_info in core_data['key_personnel']:
            db_entries['기업_핵심_인물_DB'].append({
                '인물_정보': personnel_info[:200],
                '영업_기회': '있음'
            })
        
        return db_entries
    
    def _extract_risk_type(self, text: str) -> str:
        """위험 유형 추출"""
        risk_types = ['기술위험', '재무위험', '규제위험', '운영위험']
        for risk_type in risk_types:
            if risk_type in text:
                return risk_type
        return '기타위험'
    
    def process_report(self, report_text: str) -> Dict:
        """보고서 처리 (선택적 DB화)"""
        print("🔍 핵심 정보 선별 중...")
        
        # 핵심 정보만 추출
        core_data = self.extract_core_info(report_text)
        
        # DB 엔트리 생성
        db_entries = self.create_db_entries(core_data)
        
        # 처리 결과 요약
        summary = {
            '전체_문단_수': len(report_text.split('\n\n')),
            '추출된_핵심_정보_수': sum(len(v) for v in core_data.values()),
            'DB_엔트리_수': sum(len(v) for v in db_entries.values()),
            '처리_효율성': f"{sum(len(v) for v in db_entries.values()) / len(report_text.split('\n\n')) * 100:.1f}%"
        }
        
        return {
            'summary': summary,
            'db_entries': db_entries,
            'core_data': core_data
        }

# 사용 예시
if __name__ == "__main__":
    extractor = SelectiveDBExtractor()
    
    # 테스트용 보고서
    test_report = """
    두산에너빌리티는 한국의 대표적인 에너지 기업입니다.
    
    현재 SMR(소형모듈원자로) 사업에 500억원을 투자하고 있으며, 
    기술적 위험요소가 존재합니다.
    
    CEO 김영식 대표는 원자력 전문가로서 
    정부의 원전 정책에 큰 영향을 받고 있습니다.
    
    일반적으로 원자력 사업은 복잡한 규제 환경을 가지고 있으며,
    대부분의 프로젝트에서 지연이 발생합니다.
    """
    
    result = extractor.process_report(test_report)
    print("📊 처리 결과:")
    print(json.dumps(result['summary'], indent=2, ensure_ascii=False)) 