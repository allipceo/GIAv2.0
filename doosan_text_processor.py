#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 서술형 텍스트 처리 스크립트
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 서술형 마크다운/텍스트를 구조화된 데이터로 변환하여 노션 DB에 입력
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

class DoosanTextProcessor:
    """두산중공업 서술형 텍스트 처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.processed_data = {
            "📊 기업 위험 프로파일 DB": [],
            "💰 기업 재무 및 프로젝트 DB": [],
            "🔋 신재생에너지 프로젝트 DB": [],
            "👥 기업 핵심 인물 DB": [],
            "🏛️ 정부 정책 영향 분석 DB": [],
            "🌍 글로벌 보험중개 시장 DB": []
        }
        
        # 키워드 매핑 규칙
        self.keyword_mapping = {
            "📊 기업 위험 프로파일 DB": {
                "keywords": ["리스크", "위험", "위협", "취약점", "문제점", "불안요소"],
                "risk_types": {
                    "재무": ["재무", "금융", "환율", "환리스크", "투자", "자금"],
                    "운영": ["운영", "생산", "공정", "품질", "안전"],
                    "전략": ["전략", "시장", "경쟁", "기술", "혁신"],
                    "규제": ["규제", "법규", "정책", "환경", "ESG"],
                    "사이버": ["사이버", "보안", "해킹", "데이터", "정보"]
                }
            },
            "💰 기업 재무 및 프로젝트 DB": {
                "keywords": ["매출", "수익", "투자", "자금", "재무", "프로젝트", "사업"],
                "data_types": {
                    "재무": ["매출", "수익", "이익", "자산", "부채", "자본"],
                    "프로젝트": ["프로젝트", "사업", "투자", "계약", "개발"]
                }
            },
            "🔋 신재생에너지 프로젝트 DB": {
                "keywords": ["태양광", "풍력", "신재생", "에너지", "ESS", "수소", "바이오"],
                "project_types": {
                    "태양광": ["태양광", "솔라", "PV"],
                    "풍력": ["풍력", "윈드", "터빈"],
                    "ESS": ["ESS", "에너지저장", "배터리"],
                    "수소": ["수소", "하이드로젠", "연료전지"],
                    "바이오": ["바이오", "바이오매스", "생물"]
                }
            },
            "👥 기업 핵심 인물 DB": {
                "keywords": ["대표", "사장", "이사", "임원", "경영진", "CEO", "CFO"],
                "positions": {
                    "대표이사": ["대표이사", "CEO", "최고경영자"],
                    "사장": ["사장", "부사장", "전무"],
                    "이사": ["이사", "상무", "이사회"],
                    "팀장": ["팀장", "부장", "과장", "대리"]
                }
            },
            "🏛️ 정부 정책 영향 분석 DB": {
                "keywords": ["정책", "법규", "규제", "정부", "국가", "지원", "보조"],
                "policy_areas": {
                    "신재생에너지": ["신재생", "에너지", "태양광", "풍력"],
                    "탄소중립": ["탄소", "기후", "환경", "ESG"],
                    "제조업": ["제조", "산업", "공장", "생산"],
                    "무역": ["무역", "수출", "수입", "관세"],
                    "금융": ["금융", "은행", "투자", "자금"]
                }
            },
            "🌍 글로벌 보험중개 시장 DB": {
                "keywords": ["보험", "중개", "브로커", "리스크", "보장", "글로벌"],
                "company_types": {
                    "글로벌 보험중개사": ["글로벌", "해외", "국제", "다국적"],
                    "국내 보험중개사": ["국내", "한국", "로컬"],
                    "기타": ["기타", "특수", "전문"]
                }
            }
        }
    
    def process_markdown_text(self, text: str) -> Dict:
        """마크다운 텍스트 처리"""
        print("📝 서술형 마크다운 텍스트 분석 시작...")
        
        # 텍스트를 섹션별로 분리
        sections = self._split_text_into_sections(text)
        
        # 각 섹션 분석
        for section_title, section_content in sections.items():
            self._analyze_section(section_title, section_content)
        
        return self.processed_data
    
    def _split_text_into_sections(self, text: str) -> Dict:
        """텍스트를 섹션별로 분리"""
        sections = {}
        current_section = "기본"
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            # 헤더 라인 감지
            if line.startswith('#'):
                # 이전 섹션 저장
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # 새 섹션 시작
                current_section = line.strip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # 마지막 섹션 저장
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _analyze_section(self, section_title: str, section_content: str):
        """섹션 내용 분석"""
        print(f"🔍 섹션 분석: {section_title}")
        
        # 각 DB별 키워드 매칭
        for db_name, mapping_info in self.keyword_mapping.items():
            keywords = mapping_info["keywords"]
            
            # 키워드 매칭 확인
            matched_keywords = [kw for kw in keywords if kw in section_content]
            
            if matched_keywords:
                print(f"✅ {db_name} 매칭: {matched_keywords}")
                self._extract_structured_data(db_name, section_title, section_content, mapping_info)
    
    def _extract_structured_data(self, db_name: str, section_title: str, content: str, mapping_info: Dict):
        """구조화된 데이터 추출"""
        
        if db_name == "📊 기업 위험 프로파일 DB":
            self._extract_risk_data(section_title, content, mapping_info)
        elif db_name == "💰 기업 재무 및 프로젝트 DB":
            self._extract_financial_data(section_title, content, mapping_info)
        elif db_name == "🔋 신재생에너지 프로젝트 DB":
            self._extract_renewable_energy_data(section_title, content, mapping_info)
        elif db_name == "👥 기업 핵심 인물 DB":
            self._extract_personnel_data(section_title, content, mapping_info)
        elif db_name == "🏛️ 정부 정책 영향 분석 DB":
            self._extract_policy_data(section_title, content, mapping_info)
        elif db_name == "🌍 글로벌 보험중개 시장 DB":
            self._extract_insurance_data(section_title, content, mapping_info)
    
    def _extract_risk_data(self, section_title: str, content: str, mapping_info: Dict):
        """위험 프로파일 데이터 추출"""
        # 리스크 관련 문장 찾기
        risk_sentences = re.findall(r'[^.]*(?:리스크|위험|위협|취약점)[^.]*\.', content)
        
        for sentence in risk_sentences:
            risk_data = {
                "리스크명": self._extract_risk_name(sentence),
                "리스크 유형": self._classify_risk_type(sentence, mapping_info["risk_types"]),
                "발생 확률": self._extract_probability(sentence),
                "영향도": self._extract_impact(sentence),
                "리스크 등급": self._calculate_risk_grade(sentence),
                "대응 현황": "대응 계획",  # 기본값
                "리스크 설명": sentence.strip(),
                "관련 사업부": "중공업",  # 기본값
                "발생 확률 점수": self._probability_to_score(sentence),
                "영향도 점수": self._impact_to_score(sentence)
            }
            
            self.processed_data["📊 기업 위험 프로파일 DB"].append(risk_data)
    
    def _extract_financial_data(self, section_title: str, content: str, mapping_info: Dict):
        """재무 및 프로젝트 데이터 추출"""
        # 금액 관련 정보 찾기
        amount_patterns = [
            r'(\d+(?:,\d+)*)\s*(억원|만원|원|달러|유로)',
            r'매출\s*(\d+(?:,\d+)*)',
            r'수익\s*(\d+(?:,\d+)*)',
            r'투자\s*(\d+(?:,\d+)*)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    amount, unit = match
                else:
                    amount = match
                    unit = "억원"
                
                financial_data = {
                    "항목명": f"{section_title} 관련 {unit}",
                    "데이터 유형": "재무",
                    "수치값": float(amount.replace(',', '')),
                    "단위": unit,
                    "기준일": datetime.now().strftime('%Y-%m-%d'),
                    "사업 부문": "중공업",
                    "지역": "국내",
                    "중요도": "중요",
                    "설명": f"{section_title} 관련 {amount}{unit} 데이터"
                }
                
                self.processed_data["💰 기업 재무 및 프로젝트 DB"].append(financial_data)
    
    def _extract_renewable_energy_data(self, section_title: str, content: str, mapping_info: Dict):
        """신재생에너지 프로젝트 데이터 추출"""
        # 프로젝트 관련 키워드 찾기
        project_keywords = ["프로젝트", "사업", "발전소", "플랜트"]
        
        for keyword in project_keywords:
            if keyword in content:
                # 용량 정보 찾기
                capacity_match = re.search(r'(\d+)\s*(MW|MWh)', content)
                capacity = capacity_match.group(1) if capacity_match else "100"
                unit = capacity_match.group(2) if capacity_match else "MW"
                
                project_data = {
                    "프로젝트명": f"두산 {section_title} 프로젝트",
                    "프로젝트 유형": self._classify_project_type(content, mapping_info["project_types"]),
                    "프로젝트 규모": float(capacity),
                    "단위": unit,
                    "지역": "국내",
                    "진행 상태": "계획",
                    "시작일": datetime.now().strftime('%Y-%m-%d'),
                    "두산중공업 역할": "건설",
                    "계약 금액": 0,
                    "리스크 등급": "보통",
                    "프로젝트 설명": f"{section_title} 관련 {capacity}{unit} 프로젝트"
                }
                
                self.processed_data["🔋 신재생에너지 프로젝트 DB"].append(project_data)
    
    def _extract_personnel_data(self, section_title: str, content: str, mapping_info: Dict):
        """핵심 인물 데이터 추출"""
        # 인물 관련 키워드 찾기
        person_keywords = ["대표", "사장", "이사", "CEO", "CFO", "CTO"]
        
        for keyword in person_keywords:
            if keyword in content:
                # 이름 추출 시도
                name_match = re.search(r'([가-힣]{2,4})\s*(?:대표|사장|이사)', content)
                name = name_match.group(1) if name_match else "미상"
                
                personnel_data = {
                    "인물명": name,
                    "직책": self._classify_position(keyword, mapping_info["positions"]),
                    "소속 부문": "지주회사",
                    "담당 영역": "경영총괄",
                    "경력": "20년",
                    "중요도": "매우중요",
                    "주요 성과": f"{section_title} 관련 경영진",
                    "연락처": "미상"
                }
                
                self.processed_data["👥 기업 핵심 인물 DB"].append(personnel_data)
    
    def _extract_policy_data(self, section_title: str, content: str, mapping_info: Dict):
        """정부 정책 데이터 추출"""
        # 정책 관련 키워드 찾기
        policy_keywords = ["정책", "법규", "규제", "지원", "보조"]
        
        for keyword in policy_keywords:
            if keyword in content:
                policy_data = {
                    "정책명": f"{section_title} 관련 정책",
                    "정책 분야": self._classify_policy_area(content, mapping_info["policy_areas"]),
                    "발표 기관": "산업통상자원부",
                    "발표일": datetime.now().strftime('%Y-%m-%d'),
                    "시행일": datetime.now().strftime('%Y-%m-%d'),
                    "정책 내용": content[:200] + "..." if len(content) > 200 else content,
                    "두산중공업 영향": "중립",
                    "관련 사업부": "중공업",
                    "정책 우선순위": "보통",
                    "예산 규모": 0
                }
                
                self.processed_data["🏛️ 정부 정책 영향 분석 DB"].append(policy_data)
    
    def _extract_insurance_data(self, section_title: str, content: str, mapping_info: Dict):
        """보험중개 시장 데이터 추출"""
        # 보험 관련 키워드 찾기
        insurance_keywords = ["보험", "중개", "브로커", "보장"]
        
        for keyword in insurance_keywords:
            if keyword in content:
                insurance_data = {
                    "회사명": f"{section_title} 관련 보험사",
                    "회사 유형": "국내 보험중개사",
                    "본사 위치": "한국",
                    "연매출": 0,
                    "직원 수": 0,
                    "주요 서비스": "기업보험",
                    "두산중공업 경쟁력": "동등",
                    "특화 영역": "제조",
                    "록톤과의 관계": "중립",
                    "회사 설명": f"{section_title} 관련 보험중개 서비스"
                }
                
                self.processed_data["🌍 글로벌 보험중개 시장 DB"].append(insurance_data)
    
    # 헬퍼 메서드들
    def _extract_risk_name(self, sentence: str) -> str:
        """리스크명 추출"""
        risk_keywords = ["리스크", "위험", "위협", "취약점"]
        for keyword in risk_keywords:
            if keyword in sentence:
                # 키워드 앞뒤 문맥에서 리스크명 추출
                parts = sentence.split(keyword)
                if len(parts) > 1:
                    return f"{parts[0].strip()} {keyword}"
        return "미분류 리스크"
    
    def _classify_risk_type(self, sentence: str, risk_types: Dict) -> str:
        """리스크 유형 분류"""
        for risk_type, keywords in risk_types.items():
            for keyword in keywords:
                if keyword in sentence:
                    return risk_type
        return "기타"
    
    def _extract_probability(self, sentence: str) -> str:
        """발생 확률 추출"""
        if "높음" in sentence:
            return "높음"
        elif "낮음" in sentence:
            return "낮음"
        else:
            return "보통"
    
    def _extract_impact(self, sentence: str) -> str:
        """영향도 추출"""
        if "치명적" in sentence or "매우 높음" in sentence:
            return "치명적"
        elif "높음" in sentence:
            return "높음"
        elif "낮음" in sentence:
            return "낮음"
        else:
            return "보통"
    
    def _calculate_risk_grade(self, sentence: str) -> str:
        """리스크 등급 계산"""
        probability = self._extract_probability(sentence)
        impact = self._extract_impact(sentence)
        
        if probability == "높음" and impact in ["높음", "치명적"]:
            return "높음"
        elif probability == "낮음" and impact == "낮음":
            return "낮음"
        else:
            return "보통"
    
    def _probability_to_score(self, sentence: str) -> int:
        """확률을 점수로 변환"""
        probability = self._extract_probability(sentence)
        if probability == "높음":
            return 4
        elif probability == "낮음":
            return 2
        else:
            return 3
    
    def _impact_to_score(self, sentence: str) -> int:
        """영향도를 점수로 변환"""
        impact = self._extract_impact(sentence)
        if impact == "치명적":
            return 5
        elif impact == "높음":
            return 4
        elif impact == "낮음":
            return 2
        else:
            return 3
    
    def _classify_project_type(self, content: str, project_types: Dict) -> str:
        """프로젝트 유형 분류"""
        for project_type, keywords in project_types.items():
            for keyword in keywords:
                if keyword in content:
                    return project_type
        return "기타"
    
    def _classify_position(self, keyword: str, positions: Dict) -> str:
        """직책 분류"""
        for position, keywords in positions.items():
            if keyword in keywords:
                return position
        return "기타"
    
    def _classify_policy_area(self, content: str, policy_areas: Dict) -> str:
        """정책 분야 분류"""
        for area, keywords in policy_areas.items():
            for keyword in keywords:
                if keyword in content:
                    return area
        return "기타"
    
    def generate_processing_report(self) -> str:
        """처리 결과 보고서 생성"""
        report = f"""
# 두산중공업 서술형 텍스트 처리 결과 보고서
생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

## 📊 처리 결과
"""
        
        total_extracted = 0
        
        for db_name, data_list in self.processed_data.items():
            report += f"""
### {db_name}
- 추출된 레코드: {len(data_list)}개
"""
            
            if data_list:
                report += "\n추출된 데이터 예시:\n"
                for i, data in enumerate(data_list[:3], 1):  # 처음 3개만 표시
                    report += f"{i}. {list(data.items())[0][1]}\n"
            
            total_extracted += len(data_list)
        
        report += f"""
## 🎯 최종 결과
- 총 추출된 레코드: {total_extracted}개
- 처리된 DB: {len([db for db, data in self.processed_data.items() if data])}개
"""
        
        return report

def main():
    """메인 실행 함수"""
    print("📝 두산중공업 서술형 텍스트 처리 시작")
    print("=" * 50)
    
    processor = DoosanTextProcessor()
    
    # 예시 서술형 텍스트 (실제로는 팀원들이 제공한 텍스트 사용)
    sample_text = """
# 두산중공업 해외 프로젝트 현황

## 리스크 분석
두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다. 특히 미국 달러화 변동으로 인한 손실 위험이 높은 상황입니다.

## 재무 현황
2024년 매출 15,000억원을 달성했으며, 해외 프로젝트 비중이 60%를 차지합니다.

## 신재생에너지 프로젝트
태양광 발전소 200MW 프로젝트를 진행 중이며, ESS 사업도 확장하고 있습니다.

## 경영진
정경훈 대표이사가 경영을 총괄하고 있으며, 30년 경력의 전문가입니다.

## 정부 정책 영향
신재생에너지 지원 정책으로 인해 태양광 사업이 확대되고 있습니다.

## 보험 시장
글로벌 보험중개사들과 협력하여 해외 프로젝트 리스크를 관리하고 있습니다.
"""
    
    # 텍스트 처리
    processed_data = processor.process_markdown_text(sample_text)
    
    # 결과 보고서 생성
    report = processor.generate_processing_report()
    print(report)
    
    # 처리된 데이터를 JSON으로 저장
    with open('doosan_processed_data.json', 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 두산중공업 서술형 텍스트 처리 완료")

if __name__ == "__main__":
    main() 