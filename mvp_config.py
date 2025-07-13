#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA MVP1.0 설정 관리 모듈
작성일: 2025년 1월 12일
작성자: 서대리 (Lead Developer)
목적: 구글 뉴스, LLM, 노션 연동 및 조대표님 맞춤 설정
"""

import os
from typing import Dict, List

# === API 설정 ===
class APIConfig:
    """API 키 및 연동 설정"""
    # 노션 API (기존 설정 유지)
    NOTION_API_TOKEN = "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"
    NOTION_NEWS_DATABASE_ID = "22aa613d25ff80888257c652d865f85a"
    NOTION_BID_DATABASE_ID = "22ea613d25ff80b59beff3ddc38ad068"  # 새로운 입찰낙찰 공고 DB
    NOTION_DASHBOARD_PAGE_ID = "227a613d-25ff-800c-a97d-e24f6eb521a8"
    
    # 조대표님 기존 DB ID들 (나실장 지시에 따라 기존 DB 사용)
    NOTION_PROJECT_DATABASE_ID = "228a613d25ff818d9bbac1b53e19dcbd"  # 기존 프로젝트 DB
    NOTION_TASK_DATABASE_ID = "228a613d25ff814e9153fa459f1392ef"     # 기존 태스크 DB (URL에서 추출한 실제 DB ID)
    NOTION_TODO_DATABASE_ID = "228a613d25ff813dbb4ef3d3d984d186"     # 기존 TODO DB (URL에서 추출한 실제 DB ID)
    
    # 구글 뉴스 연동 (웹 스크래핑 방식)
    GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss"
    GOOGLE_NEWS_SEARCH_URL = "https://news.google.com/search"
    
    # LLM API (Gemini)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDLMjWJP6fn43tNPykS_ylpjdorZZyICJ8")
    LLM_API_KEY = GEMINI_API_KEY  # 호환성을 위한 별칭
    LLM_MODEL_NAME = "gemini-2.0-flash-exp"

# === 조대표님 맞춤 키워드 설정 ===
class BusinessKeywords:
    """조대표님 주력 영업 분야별 키워드"""
    
    DEFENSE = [
        "방위산업", "국방", "K-방산", "군수산업", "방산수출",
        "한국항공우주산업", "KAI", "LIG넥스원", "한화시스템"
    ]
    
    RENEWABLE_ENERGY = [
        "신재생에너지", "태양광", "풍력", "ESS", "배터리저장장치",
        "해상풍력", "육상풍력", "BESS", "에너지저장시스템"
    ]
    
    INSURANCE = [
        "보험중개", "보험대리점", "보험영업", "보험상품", "보험정책",
        "손해보험", "생명보험", "보험수수료", "보험플랫폼"
    ]
    
    # 입찰/낙찰 관련 키워드
    BID_KEYWORDS = [
        "입찰", "낙찰", "공고", "계약", "조달", "사업자 모집", "수주",
        "공개입찰", "지명입찰", "경쟁입찰", "계약 체결", "업체 선정"
    ]
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, List[str]]:
        """모든 카테고리별 키워드 반환"""
        return {
            "방위산업": cls.DEFENSE,
            "신재생에너지": cls.RENEWABLE_ENERGY,
            "보험중개": cls.INSURANCE
        }
    
    @classmethod
    def get_bid_keywords_for_category(cls, category: str) -> List[str]:
        """특정 카테고리의 입찰/낙찰 키워드 조합 반환"""
        base_keywords = cls.get_all_categories().get(category, [])
        bid_combinations = []
        
        # 카테고리별 키워드와 입찰 키워드 조합
        for base_keyword in base_keywords[:3]:  # 상위 3개 키워드만 사용
            for bid_keyword in cls.BID_KEYWORDS[:5]:  # 상위 5개 입찰 키워드만 사용
                bid_combinations.append(f"{base_keyword} {bid_keyword}")
        
        return bid_combinations

# === 대시보드 설정 ===
class DashboardConfig:
    """조대표님 전용 대시보드 설정"""
    
    # 일일 루틴 최적화
    MORNING_BRIEFING_HOUR = 9    # 오전 9시 핵심 브리핑
    EVENING_SUMMARY_HOUR = 18    # 오후 6시 정리
    
    # 모바일 최적화
    MOBILE_OPTIMIZED = True
    MAX_TITLE_LENGTH = 50        # 모바일에서 읽기 좋은 제목 길이
    
    # 중요도별 색상 코딩
    IMPORTANCE_COLORS = {
        "매우중요": "🔴",
        "중요": "🟠", 
        "높음": "🟡",
        "보통": "🟢",
        "낮음": "⚪"
    }
    
    # 카테고리별 이모지
    CATEGORY_ICONS = {
        "방위산업": "🛡️",
        "신재생에너지": "🔋",
        "보험중개": "🏢"
    }

# === 수집 및 처리 설정 ===
class ProcessingConfig:
    """뉴스 수집 및 LLM 처리 설정"""
    
    # 수집 설정
    COLLECTION_INTERVAL_SECONDS = 3600  # 1시간마다
    MAX_ARTICLES_PER_KEYWORD = 5        # 키워드당 최대 수집 기사
    
    # LLM 처리 설정
    IMPORTANCE_THRESHOLD = 0.8          # 중요도 판단 임계값
    SUMMARY_MAX_LENGTH = 200            # 요약 최대 길이
    
    # 구글 뉴스 설정
    GOOGLE_NEWS_MAX_RESULTS = 20        # 구글 뉴스 최대 결과 수
    GOOGLE_NEWS_LANG = "ko"             # 언어 설정 (한국어)
    GOOGLE_NEWS_COUNTRY = "KR"          # 국가 설정 (대한민국)
    
    # 입찰/낙찰 관련 설정
    BID_ARTICLES_PER_CATEGORY = 5       # 카테고리별 입찰/낙찰 기사 수 (신재생에너지 5개, 방산산업 5개)
    BID_TOTAL_TARGET = 10               # 총 입찰/낙찰 기사 목표 수

# === 품질 관리 설정 ===
class QualityConfig:
    """데이터 품질 관리 및 검증 설정"""
    
    # 중복 제거 설정
    DUPLICATE_CHECK_DAYS = 7            # 7일 이내 중복 체크
    
    # 필터링 키워드 (제외할 내용)
    EXCLUDE_KEYWORDS = [
        "광고", "홍보", "이벤트", "할인", "쿠폰"
    ]
    
    # 최소 품질 기준
    MIN_TITLE_LENGTH = 10               # 최소 제목 길이
    MIN_CONTENT_LENGTH = 50             # 최소 내용 길이

# === 로깅 설정 ===
class LogConfig:
    """로깅 및 모니터링 설정"""
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    # 로그 파일 경로
    LOG_FILES = {
        "google_news": "logs/google_news_collector.log",
        "llm_processing": "logs/llm_processing.log", 
        "notion_upload": "logs/notion_upload.log",
        "dashboard": "logs/dashboard.log",
        "bid_processing": "logs/bid_processing.log"
    }

# === 입찰/낙찰 DB 필드 매핑 ===
class BidDatabaseFields:
    """입찰낙찰 공고 DB 필드 매핑 (실제 노션 DB 스키마 기준)"""
    
    # 필드명 매핑
    TITLE = "제목"
    DATE = "날짜"
    LINK = "링크"
    SOURCE = "출처"
    CATEGORY = "분야"              # 다중 선택
    TYPE = "유형"                  # 선택: 입찰공고, 낙찰결과, 계약소식, 관련뉴스
    CONTENT = "주요내용"
    IMPORTANCE = "중요도"          # 선택: 매우중요, 중요, 보통, 낮음, 무시
    SELECTED = "선별여부"          # 체크박스
    MODIFIED_TIME = "수정일시"     # 실제 DB에는 "수집일시"가 아닌 "수정일시"
    RELATED_PROJECT = "관련프로젝트"  # 공백 없음
    
    # 유형 옵션 (실제 DB 기준)
    TYPE_OPTIONS = ["입찰공고", "낙찰결과", "계약소식", "관련뉴스"]
    
    # 분야 옵션 (실제 DB 기준)
    CATEGORY_OPTIONS = ["재보험입찰", "보험입찰", "방산개발", "육상풍력", "ESS", "해상풍력", "방산수출", "신재생에너지"]
    
    # 중요도 옵션 (실제 DB 기준)
    IMPORTANCE_OPTIONS = ["매우중요", "중요", "보통", "낮음", "무시"]
    
    # 카테고리 매핑 (수집 시 사용하는 카테고리 → 실제 DB 옵션)
    CATEGORY_MAPPING = {
        "신재생에너지": ["신재생에너지", "육상풍력", "해상풍력", "ESS"],
        "방위산업": ["방산개발", "방산수출"],
        "보험중개": ["보험입찰", "재보험입찰"]
    }

# === 설정 검증 함수 ===
def validate_config() -> bool:
    """설정값 유효성 검증"""
    try:
        # API 키 존재 여부 확인
        if APIConfig.LLM_API_KEY == "YOUR_GEMINI_API_KEY":
            print("⚠️  경고: Gemini API 키가 설정되지 않았습니다.")
            return False
        
        # 노션 정보 확인
        if not APIConfig.NOTION_API_TOKEN:
            print("⚠️  경고: 노션 API 토큰이 설정되지 않았습니다.")
            return False
            
        if not APIConfig.NOTION_NEWS_DATABASE_ID:
            print("⚠️  경고: 노션 뉴스 데이터베이스 ID가 설정되지 않았습니다.")
            return False
        
        print("✅ 설정 검증 완료")
        return True
        
    except Exception as e:
        print(f"❌ 설정 검증 실패: {e}")
        return False

def get_config_summary() -> str:
    """현재 설정 요약 반환"""
    return f"""
📋 GIA MVP1.0 설정 요약
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 타겟 키워드: {len(BusinessKeywords.DEFENSE + BusinessKeywords.RENEWABLE_ENERGY + BusinessKeywords.INSURANCE)}개
📰 뉴스 소스: 구글 뉴스 (RSS/웹 스크래핑)
📊 대시보드: 조대표님 맞춤 ({DashboardConfig.MORNING_BRIEFING_HOUR}시 브리핑, {DashboardConfig.EVENING_SUMMARY_HOUR}시 정리)
🔄 수집 주기: {ProcessingConfig.COLLECTION_INTERVAL_SECONDS//60}분마다
🤖 LLM 모델: {APIConfig.LLM_MODEL_NAME}
📱 모바일 최적화: {'활성화' if DashboardConfig.MOBILE_OPTIMIZED else '비활성화'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

if __name__ == "__main__":
    print(get_config_summary())
    validate_config() 