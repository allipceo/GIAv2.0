"""
채팀장(ChatGPT) 조사 자료 처리 시스템
- 노팀장님 지시에 따른 선택적 데이터베이스화 전략 V3.0 적용
- 채팀장 스타일 자동 인식 (분석 중심)
- 우선순위 점수 계산 및 유연한 DB 매핑
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

class ChatTeamProcessor:
    def __init__(self):
        self.team_member = "채팀장"
        self.processing_timestamp = datetime.now().isoformat()
        
        # 채팀장 스타일 특성 (노팀장님 지시 반영)
        self.chat_team_style = {
            "특징": "분석 중심 (ChatGPT)",
            "강점": ["정책 분석", "시장 전망", "리스크 요인"],
            "우선_DB": ["정부 정책 DB", "기업 위험 프로파일 DB"],
            "키워드": ["정책", "분석", "전망", "리스크", "시장"]
        }
        
        # 우선순위 점수 계산 키워드
        self.priority_keywords = {
            '핵심_키워드': ["위험", "리스크", "보험", "정책", "분석", "전망"],
            '분석_키워드': ["시장", "경쟁", "기회", "전략", "예측"],
            '보험_키워드': ["보험료", "보상", "배상", "손해", "클레임"]
        }
    
    def identify_chat_team_style(self, text: str) -> Dict:
        """채팀장 스타일 자동 인식"""
        style_indicators = {
            '분석_중심': ['분석', '전망', '예측', '시장', '트렌드'],
            '정책_중심': ['정책', '규제', '법령', '정부', '지원'],
            '리스크_중심': ['리스크', '위험', '요인', '영향', '대응'],
            'ChatGPT_특성': ['상세한', '구체적', '체계적', '논리적', '종합적']
        }
        
        scores = {category: 0 for category in style_indicators}
        
        for category, indicators in style_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    scores[category] += 1
        
        # 채팀장 스타일 확률 계산
        total_indicators = sum(len(indicators) for indicators in style_indicators.values())
        style_probability = sum(scores.values()) / total_indicators if total_indicators > 0 else 0
        
        return {
            'team_member': self.team_member,
            'style_probability': style_probability,
            'detected_characteristics': scores,
            'processing_mode': '분석 중심' if style_probability > 0.3 else '일반'
        }
    
    def calculate_priority_score(self, content: str) -> Dict:
        """우선순위 점수 계산 (노팀장님 지시 반영)"""
        score = 0
        score_breakdown = {}
        
        # 핵심 키워드 (각 10점)
        core_keywords_found = []
        for keyword in self.priority_keywords['핵심_키워드']:
            if keyword in content:
                score += 10
                core_keywords_found.append(keyword)
        
        score_breakdown['핵심_키워드_점수'] = len(core_keywords_found) * 10
        score_breakdown['핵심_키워드_발견'] = core_keywords_found
        
        # 분석 키워드 (각 5점)
        analysis_keywords_found = []
        for keyword in self.priority_keywords['분석_키워드']:
            if keyword in content:
                score += 5
                analysis_keywords_found.append(keyword)
        
        score_breakdown['분석_키워드_점수'] = len(analysis_keywords_found) * 5
        score_breakdown['분석_키워드_발견'] = analysis_keywords_found
        
        # 보험 관련성 (15점)
        insurance_keywords_found = []
        for keyword in self.priority_keywords['보험_키워드']:
            if keyword in content:
                score += 15
                insurance_keywords_found.append(keyword)
        
        score_breakdown['보험_관련성_점수'] = len(insurance_keywords_found) * 15
        score_breakdown['보험_키워드_발견'] = insurance_keywords_found
        
        # 추가 보너스 점수
        bonus_score = 0
        bonus_reasons = []
        
        # 정형화된 표 형태 보너스
        if re.search(r'\|.*\|.*\|', content):
            bonus_score += 20
            bonus_reasons.append("정형화된 표 형태")
        
        # 수치 데이터 풍부 보너스
        if re.search(r'\d+[억만]?원|\d+%|\d+\.\d+', content):
            bonus_score += 15
            bonus_reasons.append("수치 데이터 풍부")
        
        # 보험 직결 내용 보너스
        if any(word in content for word in ['보험', '보증', '책임', '배상']):
            bonus_score += 25
            bonus_reasons.append("보험 직결 내용")
        
        score += bonus_score
        score_breakdown['보너스_점수'] = bonus_score
        score_breakdown['보너스_이유'] = bonus_reasons
        
        return {
            'total_score': score,
            'breakdown': score_breakdown,
            'processing_mode': self._determine_processing_mode(score)
        }
    
    def _determine_processing_mode(self, score: int) -> str:
        """처리 모드 결정 (노팀장님 지시 반영)"""
        if score >= 30:
            return "완전 구조화 (90-100% DB화)"
        elif score >= 20:
            return "선별 구조화 (60-80% DB화)"
        elif score >= 10:
            return "핵심 추출 (30-50% DB화)"
        else:
            return "보관 모드 (5-15% DB화)"
    
    def extract_core_info(self, content: str, priority_score: int) -> Dict:
        """핵심 정보 선별 추출"""
        core_data = {
            'government_policy': [],
            'risk_profile': [],
            'financial_data': [],
            'key_personnel': [],
            'global_insurance': []
        }
        
        # 문단별 분석
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                para_score = self.calculate_priority_score(para)['total_score']
                
                # 우선순위 점수에 따른 선별
                if self._should_extract_paragraph(para_score, priority_score):
                    category = self._classify_content(para)
                    if category:
                        core_data[category].append({
                            'content': para.strip(),
                            'priority_score': para_score,
                            'team_member': self.team_member
                        })
        
        return core_data
    
    def _should_extract_paragraph(self, para_score: int, overall_score: int) -> bool:
        """문단 추출 여부 판단"""
        if overall_score >= 30:  # 고품질 정보
            return para_score >= 5
        elif overall_score >= 20:  # 양질 정보
            return para_score >= 10
        elif overall_score >= 10:  # 일반 정보
            return para_score >= 15
        else:  # 저품질 정보
            return para_score >= 20
    
    def _classify_content(self, text: str) -> str:
        """내용 분류"""
        classification_keywords = {
            'government_policy': ['정책', '규제', '법령', '정부', '지원', '발표'],
            'risk_profile': ['위험', '리스크', '요인', '영향', '대응'],
            'financial_data': ['매출', '수익', '투자', '재무', '보험료'],
            'key_personnel': ['CEO', '대표', '이사', '책임자', '인물'],
            'global_insurance': ['보험', '보증', '책임', '배상', '클레임']
        }
        
        scores = {category: 0 for category in classification_keywords}
        
        for category, keywords in classification_keywords.items():
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
            '정부_정책_영향_분석_DB': [],
            '기업_위험_프로파일_DB': [],
            '기업_재무_및_프로젝트_DB': [],
            '기업_핵심_인물_DB': [],
            '글로벌_보험중개_시장_DB': []
        }
        
        # 정부 정책
        for item in core_data['government_policy']:
            db_entries['정부_정책_영향_분석_DB'].append({
                '정책_정보': item['content'][:200],
                '정책_영향도': '높음',
                '우선순위_점수': item['priority_score'],
                '팀원': item['team_member'],
                '추출_일시': datetime.now().isoformat()
            })
        
        # 위험 프로파일
        for item in core_data['risk_profile']:
            db_entries['기업_위험_프로파일_DB'].append({
                '위험_정보': item['content'][:200],
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
        
        return db_entries
    
    def process_chat_team_data(self, content: str) -> Dict:
        """채팀장 자료 처리 (노팀장님 지시에 따른 완전 자동화)"""
        print(f"🔍 {self.team_member}님 자료 처리 시작...")
        
        # Step 1: 채팀장 스타일 자동 인식
        style_analysis = self.identify_chat_team_style(content)
        print(f"✅ 스타일 인식 완료: {style_analysis['processing_mode']}")
        
        # Step 2: 우선순위 점수 계산
        priority_analysis = self.calculate_priority_score(content)
        print(f"✅ 우선순위 점수: {priority_analysis['total_score']}점")
        print(f"✅ 처리 모드: {priority_analysis['processing_mode']}")
        
        # Step 3: 핵심 정보 선별 추출
        core_data = self.extract_core_info(content, priority_analysis['total_score'])
        
        # Step 4: DB 엔트리 생성
        db_entries = self.create_db_entries(core_data)
        
        # Step 5: 처리 결과 요약
        total_paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        extracted_items = sum(len(v) for v in core_data.values())
        db_entries_count = sum(len(v) for v in db_entries.values())
        
        summary = {
            '처리_일시': self.processing_timestamp,
            '팀원': self.team_member,
            '스타일_분석': style_analysis,
            '우선순위_분석': priority_analysis,
            '전체_문단_수': total_paragraphs,
            '추출된_핵심_정보_수': extracted_items,
            'DB_엔트리_수': db_entries_count,
            '처리_효율성': f"{db_entries_count / total_paragraphs * 100:.1f}%" if total_paragraphs > 0 else "0%"
        }
        
        return {
            'summary': summary,
            'db_entries': db_entries,
            'core_data': core_data
        }

# 사용 예시
if __name__ == "__main__":
    processor = ChatTeamProcessor()
    
    # 테스트용 채팀장 자료 (가상)
    test_content = """
    이재명 정부의 신재생에너지 확대 정책이 시장에 미치는 영향 분석
    
    정부는 2030년까지 재생에너지 비중을 30%로 확대하는 정책을 발표했습니다.
    이는 기업들의 신재생에너지 투자를 촉진할 것으로 예상됩니다.
    
    시장 전망:
    - ESS 설비 보험 수요 40-60% 증가 예상
    - 수소 프로젝트 보험 수요 50-70% 증가 예상
    - 환경책임보험 수요 30-40% 증가 예상
    
    리스크 요인:
    - 정책 변화에 따른 규제 리스크
    - 기술 발전에 따른 경쟁 리스크
    - 시장 변화에 따른 수요 리스크
    """
    
    result = processor.process_chat_team_data(test_content)
    print("📊 채팀장 자료 처리 완료:")
    print(json.dumps(result['summary'], indent=2, ensure_ascii=False)) 