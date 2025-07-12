#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 API 기반 뉴스 수집 자동화 스크립트
작성일: 2025년 1월 12일
작성자: 서대리 (Lead Developer)
목적: 조대표님 관심 키워드 중심 네이버 뉴스 수집 및 LLM 연동

주요 개선사항:
- Google News RSS → 네이버 뉴스 API 전환
- LLM 기반 자동 분류 및 요약
- 조대표님 맞춤 키워드 체계 적용
"""

import json
import logging
import os
import re
import requests
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from mvp_config import APIConfig, BusinessKeywords, ProcessingConfig, QualityConfig

# Windows 인코딩 문제 방지
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/naver_news_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class NaverNewsCollector:
    """네이버 뉴스 API 기반 뉴스 수집기"""
    
    def __init__(self):
        self.client_id = APIConfig.NAVER_NEWS_CLIENT_ID
        self.client_secret = APIConfig.NAVER_NEWS_CLIENT_SECRET
        self.api_url = ProcessingConfig.NAVER_NEWS_API_URL
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        # 수집된 뉴스 저장
        self.collected_news = []
        
    def safe_encode_text(self, text: str) -> str:
        """인코딩 안전성 보장 텍스트 처리"""
        if not text:
            return ""
        
        try:
            # UTF-8 안전 처리
            text = str(text).encode('utf-8', errors='ignore').decode('utf-8')
            
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            
            # 특수 문자 정리
            text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)  # HTML 엔티티
            text = re.sub(r'\s+', ' ', text)              # 연속 공백
            
            return text.strip()
            
        except Exception as e:
            logging.warning(f"[ENCODING] 텍스트 처리 실패: {str(e)}")
            return "텍스트 처리 오류"
    
    def search_news_by_keyword(self, keyword: str, display: int = None) -> List[Dict]:
        """키워드로 네이버 뉴스 검색"""
        display = display or ProcessingConfig.NEWS_DISPLAY_COUNT
        
        params = {
            'query': keyword,
            'display': min(display, 100),  # 네이버 API 최대 100개
            'start': 1,
            'sort': ProcessingConfig.NEWS_SORT_OPTION
        }
        
        try:
            response = requests.get(self.api_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('items', []):
                article = {
                    'title': self.safe_encode_text(item.get('title', '')),
                    'link': item.get('link', ''),
                    'description': self.safe_encode_text(item.get('description', '')),
                    'pubDate': item.get('pubDate', ''),
                    'keyword': keyword
                }
                
                # 품질 필터링
                if self.is_quality_article(article):
                    articles.append(article)
            
            logging.info(f"[SEARCH] '{keyword}' 키워드: {len(articles)}건 수집")
            return articles
            
        except requests.exceptions.RequestException as e:
            logging.error(f"[ERROR] '{keyword}' 검색 실패: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"[ERROR] '{keyword}' 처리 중 오류: {str(e)}")
            return []
    
    def is_quality_article(self, article: Dict) -> bool:
        """기사 품질 검사"""
        title = article.get('title', '')
        description = article.get('description', '')
        
        # 최소 길이 검사
        if len(title) < QualityConfig.MIN_TITLE_LENGTH:
            return False
        
        if len(description) < QualityConfig.MIN_CONTENT_LENGTH:
            return False
        
        # 제외 키워드 검사
        content = f"{title} {description}".lower()
        for exclude_word in QualityConfig.EXCLUDE_KEYWORDS:
            if exclude_word in content:
                return False
        
        return True
    
    def parse_naver_date(self, date_string: str) -> str:
        """네이버 뉴스 날짜 형식을 표준 형식으로 변환"""
        try:
            # 네이버 API 날짜 형식: "Mon, 11 Dec 2023 10:30:00 +0900"
            dt = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d")
        except:
            # 파싱 실패 시 오늘 날짜
            return datetime.now().strftime("%Y-%m-%d")
    
    def collect_all_categories(self) -> List[Dict]:
        """모든 카테고리별 뉴스 수집"""
        all_articles = []
        categories = BusinessKeywords.get_all_categories()
        
        logging.info(f"[START] {len(categories)}개 카테고리 뉴스 수집 시작")
        
        for category, keywords in categories.items():
            logging.info(f"[CATEGORY] {category} 수집 중...")
            
            category_articles = []
            for keyword in keywords:
                articles = self.search_news_by_keyword(
                    keyword, 
                    ProcessingConfig.MAX_ARTICLES_PER_KEYWORD
                )
                
                # 카테고리 정보 추가
                for article in articles:
                    article['category'] = category
                    article['formatted_date'] = self.parse_naver_date(article['pubDate'])
                
                category_articles.extend(articles)
            
            # 카테고리별 중복 제거 및 최신순 정렬
            unique_articles = self.remove_duplicates(category_articles)
            unique_articles.sort(key=lambda x: x['pubDate'], reverse=True)
            
            # 카테고리별 최대 10개로 제한
            selected_articles = unique_articles[:10]
            all_articles.extend(selected_articles)
            
            logging.info(f"[CATEGORY] {category}: {len(selected_articles)}건 선별 완료")
        
        logging.info(f"[COMPLETE] 전체 수집 완료: {len(all_articles)}건")
        return all_articles
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """중복 기사 제거 (제목 기준)"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article['title'].lower().strip()
            if title not in seen_titles and len(title) > 5:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles
    
    def format_for_notion(self, articles: List[Dict]) -> List[Dict]:
        """노션 DB 형식으로 데이터 변환"""
        formatted_articles = []
        
        for article in articles:
            notion_article = {
                "제목": article['title'],
                "URL": article['link'],
                "발행일": article['formatted_date'],
                "요약": article['description'][:200] + "..." if len(article['description']) > 200 else article['description'],
                "태그": [article['category']],
                "중요도": "보통",  # LLM에서 나중에 판단
                "요약 품질 평가": "보통",
                "출처": "네이버 뉴스",
                "키워드": article['keyword']
            }
            formatted_articles.append(notion_article)
        
        return formatted_articles
    
    def save_to_json(self, articles: List[Dict], filename: str = "naver_news_data.json"):
        """수집된 뉴스를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            logging.info(f"[SAVE] {filename}에 {len(articles)}건 저장 완료")
            return True
            
        except Exception as e:
            logging.error(f"[ERROR] 파일 저장 실패: {str(e)}")
            return False

def main():
    """메인 실행 함수"""
    print("🚀 네이버 뉴스 수집 시작 (MVP1.0)")
    print("=" * 50)
    
    # 수집기 초기화
    collector = NaverNewsCollector()
    
    # API 키 확인
    if collector.client_id == "YOUR_NAVER_NEWS_CLIENT_ID":
        print("❌ 네이버 뉴스 API 키가 설정되지 않았습니다.")
        print("mvp_config.py에서 API 키를 설정해주세요.")
        return
    
    # 뉴스 수집
    articles = collector.collect_all_categories()
    
    if not articles:
        print("❌ 수집된 뉴스가 없습니다.")
        return
    
    # 노션 형식으로 변환
    notion_articles = collector.format_for_notion(articles)
    
    # JSON 파일로 저장
    if collector.save_to_json(notion_articles):
        print(f"✅ 네이버 뉴스 {len(notion_articles)}건 수집 완료")
        print(f"📁 저장 파일: naver_news_data.json")
        
        # 카테고리별 통계
        categories = {}
        for article in notion_articles:
            category = article['태그'][0]
            categories[category] = categories.get(category, 0) + 1
        
        print("\n📊 카테고리별 수집 현황:")
        for category, count in categories.items():
            emoji = "🛡️" if "방위" in category else "🔋" if "에너지" in category else "🏢"
            print(f"  {emoji} {category}: {count}건")
    else:
        print("❌ 파일 저장 실패")

if __name__ == "__main__":
    main() 