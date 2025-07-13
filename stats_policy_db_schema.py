"""
통계/정책 정보 DB 스키마 설계
- 조대표님의 비즈니스 도메인에 맞는 통계/정책 정보 구조
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class StatsPolicyDatabaseFields:
    """통계/정책 DB 필드 정의"""
    
    # 기본 정보
    title: str  # 통계/정책명
    category: str  # 분야 (신재생에너지, 방위산업, 보험업계, 경제일반)
    data_type: str  # 유형 (통계, 정책, 지표, 보고서)
    source: str  # 출처 (전력거래소, 금융감독원, 한국에너지공단 등)
    
    # 데이터 세부정보
    indicator_name: str  # 지표명
    value: str  # 수치/값
    unit: str  # 단위
    reference_period: str  # 기준기간 (2024년 상반기, 2024.06 등)
    
    # 중요도 및 분류
    importance_level: str  # 중요도 (매우중요, 중요, 보통)
    business_relevance: str  # 사업연관성 (직접연관, 간접연관, 참고용)
    trend_analysis: str  # 트렌드 분석 (상승, 하락, 보합, 변동)
    
    # 링크 및 첨부
    source_url: str  # 원본 링크
    detail_info: str  # 상세정보/요약
    attached_files: Optional[str]  # 첨부파일 링크
    
    # 메타데이터
    collection_date: datetime  # 수집일시
    publish_date: str  # 발표일자
    next_update: Optional[str]  # 다음 업데이트 예정일
    
    # 관련 프로젝트
    related_projects: Optional[str]  # 관련 프로젝트

# 주요 통계/정책 카테고리 정의
STATS_CATEGORIES = {
    "신재생에너지": [
        "태양광발전량",
        "풍력발전량", 
        "수소연료전지",
        "REC 거래가격",
        "신재생에너지 보급률",
        "전력계통연계용량",
        "에너지저장장치(ESS)",
        "그린뉴딜 정책"
    ],
    "방위산업": [
        "방산업체 수출실적",
        "국방예산 현황",
        "방위산업 매출",
        "무기체계 도입계획",
        "방산업체 현황",
        "국제공동개발",
        "방산수출 지원정책"
    ],
    "보험업계": [
        "보험료 수입",
        "보험금 지급",
        "자동차보험 통계",
        "생명보험 가입률", 
        "손해보험 실적",
        "보험사기 현황",
        "보험업계 정책",
        "금융감독 동향"
    ],
    "경제일반": [
        "GDP 성장률",
        "금리 동향",
        "환율 변동",
        "소비자물가지수",
        "수출입 통계",
        "주가지수",
        "기업투자 동향"
    ]
}

# 데이터 소스별 접근 정보
DATA_SOURCES = {
    "전력거래소": {
        "base_url": "https://new.kpx.or.kr",
        "api_available": True,
        "data_types": ["전력통계", "REC거래", "발전실적", "전력수급"]
    },
    "금융감독원": {
        "base_url": "https://www.fss.or.kr",
        "api_available": True,
        "data_types": ["금융통계", "보험통계", "연금통계", "보험사기통계"]
    },
    "한국에너지공단": {
        "base_url": "https://www.energy.or.kr",
        "api_available": True,
        "data_types": ["신재생에너지통계", "에너지효율", "온실가스통계"]
    },
    "e-나라지표": {
        "base_url": "https://www.index.go.kr",
        "api_available": True,
        "data_types": ["국가승인통계", "에너지통계", "경제통계"]
    },
    "방위사업청": {
        "base_url": "https://dapa.go.kr",
        "api_available": False,
        "data_types": ["입찰공고", "방위사업통계", "방산업체현황"]
    },
    "공공데이터포털": {
        "base_url": "https://www.data.go.kr",
        "api_available": True,
        "data_types": ["정부통계", "공공데이터API", "오픈데이터"]
    }
}

# 중요도 판정 기준
IMPORTANCE_CRITERIA = {
    "매우중요": [
        "조대표님 사업에 직접적 영향",
        "투자 의사결정에 핵심 지표",
        "정부 정책 변화 신호"
    ],
    "중요": [
        "업계 전반 동향 파악",
        "경쟁사 분석 관련",
        "시장 트렌드 지표"
    ],
    "보통": [
        "일반적 경제 동향",
        "참고용 통계",
        "배경 정보"
    ]
}

def get_field_mapping():
    """노션 DB 필드 매핑 정보 반환"""
    return {
        "제목": "title",
        "분야": "category", 
        "유형": "data_type",
        "출처": "source",
        "지표명": "indicator_name",
        "수치": "value",
        "단위": "unit",
        "기준기간": "reference_period",
        "중요도": "importance_level",
        "사업연관성": "business_relevance",
        "트렌드": "trend_analysis",
        "원본링크": "source_url",
        "상세정보": "detail_info",
        "첨부파일": "attached_files",
        "수집일시": "collection_date",
        "발표일자": "publish_date",
        "다음업데이트": "next_update",
        "관련프로젝트": "related_projects"
    } 