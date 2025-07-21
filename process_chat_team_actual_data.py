"""
채팀장님 실제 조사 자료 처리 시스템
- 마크다운 테이블 데이터 분석
- 노션 DB 매핑 및 구조화
- 채팀장 스타일 자동 인식
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

class ChatTeamActualDataProcessor:
    def __init__(self):
        self.team_member = "채팀장"
        self.processing_timestamp = datetime.now().isoformat()
        
        # 채팀장 스타일 특성
        self.chat_team_style = {
            "특징": "분석 중심 (ChatGPT)",
            "강점": ["정책 분석", "시장 전망", "리스크 요인"],
            "우선_DB": ["정부 정책 DB", "기업 위험 프로파일 DB"],
            "키워드": ["정책", "분석", "전망", "리스크", "시장"]
        }
    
    def parse_markdown_table(self, table_text: str) -> List[Dict]:
        """마크다운 테이블 파싱"""
        lines = table_text.strip().split('\n')
        if len(lines) < 3:  # 헤더 + 구분선 + 데이터 최소 3줄
            return []
        
        # 헤더 추출
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]
        
        # 데이터 행 파싱
        data_rows = []
        for line in lines[2:]:  # 헤더와 구분선 제외
            if line.strip() and '|' in line:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) == len(headers):
                    row_data = {}
                    for i, header in enumerate(headers):
                        row_data[header] = cells[i]
                    data_rows.append(row_data)
        
        return data_rows
    
    def process_core_business_data(self, table_data: List[Dict]) -> Dict:
        """핵심 사업부문 DB 처리"""
        processed_data = []
        
        for row in table_data:
            processed_row = {
                '사업부문': row.get('사업부문', ''),
                '지역': row.get('지역', ''),
                '조사기간': row.get('조사기간', ''),
                '시장규모': row.get('시장규모(USD)', ''),
                '연평균성장률': row.get('연평균성장률(CAGR)', ''),
                '주요_경쟁사': row.get('주요 경쟁사', ''),
                '데이터_확인일': row.get('데이터 확인일', ''),
                '팀원': self.team_member,
                '처리_일시': self.processing_timestamp,
                '우선순위_점수': self._calculate_business_priority_score(row)
            }
            processed_data.append(processed_row)
        
        return {
            'DB명': '핵심_사업부문_DB',
            '처리_건수': len(processed_data),
            '데이터': processed_data
        }
    
    def process_renewable_project_data(self, table_data: List[Dict]) -> Dict:
        """신재생 프로젝트 DB 처리"""
        processed_data = []
        
        for row in table_data:
            processed_row = {
                '프로젝트명': row.get('프로젝트명', ''),
                '기술유형': row.get('기술유형', ''),
                '용량': row.get('용량(MW)', ''),
                '참여형태': row.get('참여형태', ''),
                '참여지분율': row.get('참여지분율(%)', ''),
                '착공연도': row.get('착공연도', ''),
                '준공연도': row.get('준공연도', ''),
                'PF_대출기관': row.get('PF 대출기관', ''),
                '데이터_확인일': row.get('데이터 확인일', ''),
                '팀원': self.team_member,
                '처리_일시': self.processing_timestamp,
                '우선순위_점수': self._calculate_project_priority_score(row)
            }
            processed_data.append(processed_row)
        
        return {
            'DB명': '신재생_프로젝트_DB',
            '처리_건수': len(processed_data),
            '데이터': processed_data
        }
    
    def process_spc_case_data(self, table_data: List[Dict]) -> Dict:
        """SPC 사례 DB 처리"""
        processed_data = []
        
        for row in table_data:
            processed_row = {
                'SPC명': row.get('SPC명', ''),
                'PF_총액': row.get('PF 총액', ''),
                '참여_지분율': row.get('참여 지분율(%)', ''),
                '대주단': row.get('대주단(리스트)', ''),
                '보험_가입_현황': row.get('보험 가입 현황', ''),
                '공사_개시일': row.get('공사 개시일', ''),
                '준공_운영_개시일': row.get('준공/운영 개시일', ''),
                '데이터_확인일': row.get('데이터 확인일', ''),
                '팀원': self.team_member,
                '처리_일시': self.processing_timestamp,
                '우선순위_점수': self._calculate_spc_priority_score(row)
            }
            processed_data.append(processed_row)
        
        return {
            'DB명': 'SPC_사례_DB',
            '처리_건수': len(processed_data),
            '데이터': processed_data
        }
    
    def _calculate_business_priority_score(self, row: Dict) -> int:
        """사업부문 우선순위 점수 계산"""
        score = 0
        
        # 시장 규모 기반 점수
        market_size = row.get('시장규모(USD)', '')
        if '조원' in market_size or '억 달러' in market_size or '억 유로' in market_size:
            score += 20
        
        # 성장률 기반 점수
        growth_rate = row.get('연평균성장률(CAGR)', '')
        if growth_rate and float(growth_rate.replace('%', '')) > 4:
            score += 15
        
        # 경쟁사 수 기반 점수
        competitors = row.get('주요 경쟁사', '')
        if competitors and len(competitors.split(',')) >= 3:
            score += 10
        
        return score
    
    def _calculate_project_priority_score(self, row: Dict) -> int:
        """프로젝트 우선순위 점수 계산"""
        score = 0
        
        # 용량 기반 점수
        capacity = row.get('용량(MW)', '')
        if capacity and int(capacity) >= 100:
            score += 20
        elif capacity and int(capacity) >= 50:
            score += 15
        
        # 참여 형태 기반 점수
        participation = row.get('참여형태', '')
        if 'EPC' in participation:
            score += 15
        if '장비공급' in participation:
            score += 10
        
        # 지분율 기반 점수
        share = row.get('참여지분율(%)', '')
        if share and int(share) >= 20:
            score += 10
        
        return score
    
    def _calculate_spc_priority_score(self, row: Dict) -> int:
        """SPC 우선순위 점수 계산"""
        score = 0
        
        # PF 총액 기반 점수
        pf_amount = row.get('PF 총액', '')
        if '조원' in pf_amount or 'M USD' in pf_amount:
            score += 20
        
        # 보험 가입 현황 기반 점수
        insurance = row.get('보험 가입 현황', '')
        if insurance and ('CPI' in insurance or 'EAR' in insurance or 'CAR' in insurance):
            score += 15
        
        # 지분율 기반 점수
        share = row.get('참여 지분율(%)', '')
        if share and int(share) >= 20:
            score += 10
        
        return score
    
    def process_all_data(self, markdown_content: str) -> Dict:
        """전체 데이터 처리"""
        print(f"🔍 {self.team_member}님 실제 자료 처리 시작...")
        
        # 마크다운 테이블 파싱
        tables = self._extract_tables_from_markdown(markdown_content)
        
        results = {}
        
        # 핵심 사업부문 DB 처리
        if '핵심 사업부문 DB' in tables:
            business_data = self.parse_markdown_table(tables['핵심 사업부문 DB'])
            results['핵심_사업부문_DB'] = self.process_core_business_data(business_data)
        
        # 신재생 프로젝트 DB 처리
        if '신재생 프로젝트 DB' in tables:
            project_data = self.parse_markdown_table(tables['신재생 프로젝트 DB'])
            results['신재생_프로젝트_DB'] = self.process_renewable_project_data(project_data)
        
        # SPC 사례 DB 처리
        if 'SPC 사례 DB' in tables:
            spc_data = self.parse_markdown_table(tables['SPC 사례 DB'])
            results['SPC_사례_DB'] = self.process_spc_case_data(spc_data)
        
        # 처리 결과 요약
        total_entries = sum(result['처리_건수'] for result in results.values())
        
        summary = {
            '처리_일시': self.processing_timestamp,
            '팀원': self.team_member,
            '총_처리_건수': total_entries,
            'DB별_처리_건수': {name: result['처리_건수'] for name, result in results.items()},
            '처리_모드': '완전 구조화',
            '우선순위_점수': 85  # 채팀장 자료 특성상 높은 점수
        }
        
        return {
            'summary': summary,
            'results': results
        }
    
    def _extract_tables_from_markdown(self, content: str) -> Dict:
        """마크다운에서 테이블 추출"""
        tables = {}
        
        # 섹션별로 분리
        sections = content.split('---')
        
        for section in sections:
            if '핵심 사업부문 DB' in section:
                # 테이블 부분 추출
                table_start = section.find('```markdown')
                table_end = section.find('```', table_start + 10)
                if table_start != -1 and table_end != -1:
                    table_content = section[table_start + 10:table_end]
                    tables['핵심 사업부문 DB'] = table_content
            
            elif '신재생 프로젝트 DB' in section:
                table_start = section.find('```markdown')
                table_end = section.find('```', table_start + 10)
                if table_start != -1 and table_end != -1:
                    table_content = section[table_start + 10:table_end]
                    tables['신재생 프로젝트 DB'] = table_content
            
            elif 'SPC 사례 DB' in section:
                table_start = section.find('```markdown')
                table_end = section.find('```', table_start + 10)
                if table_start != -1 and table_end != -1:
                    table_content = section[table_start + 10:table_end]
                    tables['SPC 사례 DB'] = table_content
        
        return tables

# 사용 예시
if __name__ == "__main__":
    processor = ChatTeamActualDataProcessor()
    
    # 채팀장님 실제 자료 (가상)
    test_content = """
    ## 1. 핵심 사업부문 DB
    
    ```markdown
    | 사업부문       | 지역       | 조사기간     | 시장규모(USD)      | 연평균성장률(CAGR) | 주요 경쟁사                                      | 데이터 확인일 |
    |---------------|-----------|-------------|--------------------|--------------------|--------------------------------------------------|--------------|
    | 원자력         | 한국      | 2020–2025   | 12조원             | 3.5%               | GE, Mitsubishi, Toshiba                          | 2025‑07‑19   |
    ```
    """
    
    result = processor.process_all_data(test_content)
    print("📊 채팀장님 실제 자료 처리 완료:")
    print(json.dumps(result['summary'], indent=2, ensure_ascii=False)) 