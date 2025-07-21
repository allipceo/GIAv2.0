"""
강화된 선택적 데이터베이스화 시스템
- 팀원별 맞춤 처리 강화
- 더 정교한 필터링 시스템
- 안전성과 효율성 균형
"""

import json
import re
from typing import Dict, List, Tuple
from datetime import datetime

class EnhancedSelectiveExtractor:
    def __init__(self):
        # 팀원별 핵심 키워드 정의
        self.team_keywords = {
            '시대리': {
                'primary': ['수치', '통계', '비율', '증감률', '매출', '투자', '규모'],
                'secondary': ['데이터', '분석', '추이', '전망', '예측'],
                'exclude': ['일반적', '대부분', '전반적', '상세한', '자세한']
            },
            '채팀장': {
                'primary': ['정책', '규제', '법령', '정부발표', '지원사업', '리스크'],
                'secondary': ['분석', '전망', '영향', '트렌드', '시장'],
                'exclude': ['개요', '소개', '개념', '정의', '배경']
            },
            '고과장': {
                'primary': ['기술', '특허', 'R&D', '스펙', '성능', '위험'],
                'secondary': ['개발', '연구', '혁신', '특화', '차별화'],
                'exclude': ['일반적', '표준', '기본', '상세한', '자세한']
            },
            '마주임': {
                'primary': ['차트', '그래프', '비교표', '수치', '비율'],
                'secondary': ['시각화', '표', '도표', '분석', '결과'],
                'exclude': ['설명', '해석', '분석', '상세한', '자세한']
            }
        }
        
        # 보험 관련 핵심 키워드
        self.insurance_keywords = {
            'risk': ['위험', '리스크', '사고', '손실', '보험', '배상'],
            'financial': ['매출', '수익', '자본', '투자', '재무', '보험료'],
            'personnel': ['CEO', '대표', '이사', '책임자', '인물', '영업'],
            'policy': ['정책', '규제', '법령', '인허가', '정부', '지원'],
            'project': ['프로젝트', '사업', '계획', '투자', '시설', '보험']
        }
    
    def identify_team_member(self, text: str) -> str:
        """팀원 식별"""
        team_indicators = {
            '시대리': ['perplexity', '데이터', '수치', '통계'],
            '채팀장': ['chatgpt', '분석', '정책', '전망'],
            '고과장': ['copilot', '기술', 'R&D', '특허'],
            '마주임': ['차트', '그래프', '시각화', '표']
        }
        
        scores = {team: 0 for team in team_indicators}
        for team, indicators in team_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text.lower():
                    scores[team] += 1
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else '기타'
    
    def calculate_priority_score(self, text: str, team_member: str) -> int:
        """우선순위 점수 계산"""
        score = 0
        
        # 팀원별 키워드 점수
        if team_member in self.team_keywords:
            team_keywords = self.team_keywords[team_member]
            
            # Primary 키워드 (높은 가중치)
            for keyword in team_keywords['primary']:
                if keyword in text:
                    score += 10
            
            # Secondary 키워드 (중간 가중치)
            for keyword in team_keywords['secondary']:
                if keyword in text:
                    score += 5
            
            # Exclude 키워드 (감점)
            for keyword in team_keywords['exclude']:
                if keyword in text:
                    score -= 5
        
        # 보험 관련성 점수
        for category, keywords in self.insurance_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    score += 15
                    break
        
        # 수치 데이터 포함 여부
        if re.search(r'\d+[억만]?원|\d+%|\d+\.\d+', text):
            score += 10
        
        return max(0, score)  # 음수 방지
    
    def extract_core_info(self, text: str, team_member: str = None) -> Dict:
        """핵심 정보 선별 추출"""
        if not team_member:
            team_member = self.identify_team_member(text)
        
        core_data = {
            'risk_profile': [],
            'financial_data': [],
            'key_personnel': [],
            'policy_impact': [],
            'project_info': [],
            'team_member': team_member
        }
        
        # 문단별 분석
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                priority_score = self.calculate_priority_score(para, team_member)
                
                if priority_score >= 10:  # 최소 기준점
                    category = self._classify_content(para)
                    if category:
                        core_data[category].append({
                            'content': para.strip(),
                            'priority_score': priority_score,
                            'team_member': team_member
                        })
        
        return core_data
    
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
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def create_db_entries(self, core_data: Dict) -> Dict:
        """DB 엔트리 생성"""
        db_entries = {
            '기업_위험_프로파일_DB': [],
            '기업_재무_및_프로젝트_DB': [],
            '기업_핵심_인물_DB': [],
            '정부_정책_영향_분석_DB': [],
            '글로벌_보험중개_시장_DB': []
        }
        
        # 위험 프로파일
        for item in core_data['risk_profile']:
            db_entries['기업_위험_프로파일_DB'].append({
                '위험_유형': self._extract_risk_type(item['content']),
                '위험_설명': item['content'][:200],
                '보험_관련성': '높음',
                '우선순위_점수': item['priority_score'],
                '팀원': item['team_member'],
                '추출_일시': datetime.now().isoformat()
            })
        
        # 재무 데이터
        for item in core_data['financial_data']:
            db_entries['기업_재무_및_프로젝트_DB'].append({
                '재무_정보': item['content'][:200],
                '보험료_산정_관련': '있음',
                '우선순위_점수': item['priority_score'],
                '팀원': item['team_member'],
                '추출_일시': datetime.now().isoformat()
            })
        
        # 핵심 인물
        for item in core_data['key_personnel']:
            db_entries['기업_핵심_인물_DB'].append({
                '인물_정보': item['content'][:200],
                '영업_기회': '있음',
                '우선순위_점수': item['priority_score'],
                '팀원': item['team_member'],
                '추출_일시': datetime.now().isoformat()
            })
        
        return db_entries
    
    def _extract_risk_type(self, text: str) -> str:
        """위험 유형 추출"""
        risk_types = ['기술위험', '재무위험', '규제위험', '운영위험', '시장위험']
        for risk_type in risk_types:
            if risk_type in text:
                return risk_type
        return '기타위험'
    
    def process_report(self, report_text: str, team_member: str = None) -> Dict:
        """보고서 처리 (선택적 DB화)"""
        print(f"🔍 핵심 정보 선별 중... (팀원: {team_member or '자동식별'})")
        
        # 팀원 식별
        if not team_member:
            team_member = self.identify_team_member(report_text)
        
        # 핵심 정보만 추출
        core_data = self.extract_core_info(report_text, team_member)
        
        # DB 엔트리 생성
        db_entries = self.create_db_entries(core_data)
        
        # 처리 결과 요약
        total_paragraphs = len([p for p in report_text.split('\n\n') if p.strip()])
        extracted_items = sum(len(v) for v in core_data.values() if isinstance(v, list))
        db_entries_count = sum(len(v) for v in db_entries.values())
        
        summary = {
            '전체_문단_수': total_paragraphs,
            '추출된_핵심_정보_수': extracted_items,
            'DB_엔트리_수': db_entries_count,
            '처리_효율성': f"{db_entries_count / total_paragraphs * 100:.1f}%" if total_paragraphs > 0 else "0%",
            '팀원': team_member,
            '처리_일시': datetime.now().isoformat()
        }
        
        return {
            'summary': summary,
            'db_entries': db_entries,
            'core_data': core_data
        }

# 사용 예시
if __name__ == "__main__":
    extractor = EnhancedSelectiveExtractor()
    
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