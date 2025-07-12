#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
입찰/낙찰 뉴스 전용 수집기
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 신재생에너지 및 방산산업 분야의 입찰/낙찰 정보 구글 뉴스 클리핑

주요 기능:
- 카테고리별 입찰/낙찰 키워드 조합 검색
- 분야별 5개씩 총 10개 선별 로직
- 새로운 입찰낙찰 공고 DB 형식으로 변환
"""

import feedparser
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import quote
from typing import Dict, List

# 로컬 모듈 임포트
from mvp_config import (
    APIConfig, BusinessKeywords, ProcessingConfig, QualityConfig, 
    BidDatabaseFields
)
from google_news_collector import safe_encode_text, clean_html_tags, format_korean_date

# Windows 인코딩 문제 완전 방지 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bid_news_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Google News RSS 기본 URL (한국어, 한국 지역)
GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"
RSS_PARAMS = "hl=ko&gl=KR&ceid=KR:ko"

class BidNewsCollector:
    """입찰/낙찰 뉴스 전용 수집기"""
    
    def __init__(self):
        self.collected_articles = []
        
    def determine_bid_type(self, title: str, description: str) -> str:
        """기사 내용을 바탕으로 입찰/낙찰 유형 판단"""
        content = f"{title} {description}".lower()
        
        # 유형별 키워드 매핑
        type_keywords = {
            "입찰공고": ["입찰공고", "사업자 모집", "공개입찰", "지명입찰", "경쟁입찰", "제안서", "참가신청"],
            "낙찰결과": ["낙찰", "선정", "계약자", "수주", "업체 선정", "최종 선택", "계약 체결"],
            "계약소식": ["계약 체결", "계약 서명", "MOU", "협약", "파트너십", "업무협약"],
            "관련뉴스": ["발표", "계획", "추진", "검토", "예정", "동향"]
        }
        
        # 점수 기반 판단
        scores = {}
        for bid_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[bid_type] = score
        
        # 가장 높은 점수의 유형 반환
        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else "관련뉴스"
    
    def determine_bid_importance(self, title: str, description: str, bid_type: str) -> str:
        """입찰/낙찰 뉴스의 중요도 판단"""
        content = f"{title} {description}".lower()
        
        # 고중요도 키워드
        high_keywords = ["대규모", "수백억", "수천억", "조원", "국가", "정부", "공공", "메가"]
        
        # 중간중요도 키워드
        medium_keywords = ["계약", "선정", "낙찰", "입찰", "공고", "발주"]
        
        # 유형별 가중치
        type_weights = {
            "낙찰결과": 1.5,
            "입찰공고": 1.2,
            "계약소식": 1.3,
            "관련뉴스": 1.0
        }
        
        # 기본 점수 계산
        score = 0
        score += sum(2 for keyword in high_keywords if keyword in content)
        score += sum(1 for keyword in medium_keywords if keyword in content)
        
        # 유형별 가중치 적용
        score *= type_weights.get(bid_type, 1.0)
        
        # 점수에 따른 중요도 결정
        if score >= 4:
            return "매우중요"
        elif score >= 2:
            return "높음"
        elif score >= 1:
            return "보통"
        else:
            return "낮음"
    
    def search_bid_news_by_keywords(self, category: str, keyword_combinations: List[str]) -> List[Dict]:
        """카테고리별 입찰/낙찰 키워드 조합으로 뉴스 검색"""
        articles = []
        
        logging.info(f"[BID_SEARCH] {category} 카테고리 입찰/낙찰 뉴스 검색 시작")
        
        for keyword_combo in keyword_combinations:
            try:
                # Google News RSS URL 구성
                encoded_keyword = quote(keyword_combo)
                rss_url = f"{GOOGLE_NEWS_RSS_BASE}?q={encoded_keyword}&{RSS_PARAMS}"
                
                logging.info(f"[BID_SEARCH] 키워드 '{keyword_combo}' 검색 중...")
                
                # RSS 피드 파싱
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    logging.warning(f"[BID_WARNING] RSS 피드 파싱 경고: {keyword_combo}")
                
                # 기사 수집 (최대 3개로 제한)
                articles_collected = 0
                for entry in feed.entries:
                    if articles_collected >= 3:  # 키워드당 최대 3개
                        break
                    
                    title = safe_encode_text(clean_html_tags(entry.title))
                    description = safe_encode_text(clean_html_tags(entry.description if hasattr(entry, 'description') else ''))
                    
                    # 입찰/낙찰 관련성 검사
                    if self.is_bid_related(title, description):
                        # 입찰낙찰 공고 DB 형식에 맞춰 데이터 구성
                        article = {
                            "제목": title,
                            "링크": safe_encode_text(entry.link),
                            "날짜": format_korean_date(entry.published_parsed if hasattr(entry, 'published_parsed') else entry.published),
                            "출처": "Google News",
                            "분야": [category],
                            "유형": self.determine_bid_type(title, description),
                            "주요내용": description[:200] if description else title,  # 초기 요약
                            "중요도": self.determine_bid_importance(title, description, self.determine_bid_type(title, description)),
                            "선별여부": False,  # 초기값
                            "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "관련 프로젝트": "",  # 빈 값
                            "_keyword": keyword_combo,  # 내부 추적용
                            "_score": self.calculate_relevance_score(title, description, category)
                        }
                        
                        articles.append(article)
                        articles_collected += 1
                
                logging.info(f"[BID_SUCCESS] '{keyword_combo}' 키워드: {articles_collected}건 수집")
                
                # API 호출 간격 (Rate limit 방지)
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"[BID_ERROR] '{keyword_combo}' 수집 실패: {str(e)}")
                continue
        
        logging.info(f"[BID_COMPLETE] {category} 카테고리: 총 {len(articles)}건 수집")
        return articles
    
    def is_bid_related(self, title: str, description: str) -> bool:
        """입찰/낙찰 관련성 검사"""
        content = f"{title} {description}".lower()
        
        # 입찰/낙찰 관련 키워드
        bid_keywords = ["입찰", "낙찰", "공고", "계약", "조달", "수주", "선정", "발주"]
        
        # 최소 1개 이상의 입찰/낙찰 키워드 포함 여부
        return any(keyword in content for keyword in bid_keywords)
    
    def calculate_relevance_score(self, title: str, description: str, category: str) -> float:
        """입찰/낙찰 뉴스의 관련성 점수 계산"""
        content = f"{title} {description}".lower()
        score = 0.0
        
        # 카테고리별 키워드 점수
        category_keywords = BusinessKeywords.get_all_categories().get(category, [])
        for keyword in category_keywords:
            if keyword.lower() in content:
                score += 2.0
        
        # 입찰/낙찰 키워드 점수
        bid_keywords = BusinessKeywords.BID_KEYWORDS
        for keyword in bid_keywords:
            if keyword.lower() in content:
                score += 1.5
        
        # 중요도 키워드 점수
        importance_keywords = ["대규모", "수백억", "수천억", "국가", "정부"]
        for keyword in importance_keywords:
            if keyword in content:
                score += 1.0
        
        return score
    
    def select_top_articles_by_category(self, articles: List[Dict], category: str, count: int = 5) -> List[Dict]:
        """카테고리별 상위 기사 선별"""
        category_articles = [article for article in articles if category in article.get("분야", [])]
        
        # 관련성 점수로 정렬
        category_articles.sort(key=lambda x: x.get("_score", 0), reverse=True)
        
        # 상위 N개 선별
        selected = category_articles[:count]
        
        # 선별 여부 마킹
        for article in selected:
            article["선별여부"] = True
        
        logging.info(f"[BID_SELECT] {category}: {len(selected)}건 선별 (총 {len(category_articles)}건 중)")
        
        return selected
    
    def collect_bid_news_all_categories(self) -> List[Dict]:
        """모든 카테고리의 입찰/낙찰 뉴스 수집"""
        all_articles = []
        target_categories = ["신재생에너지", "방위산업"]  # 보험중개는 제외
        
        logging.info(f"[BID_START] 입찰/낙찰 뉴스 수집 시작")
        
        for category in target_categories:
            # 카테고리별 입찰/낙찰 키워드 조합 생성
            keyword_combinations = BusinessKeywords.get_bid_keywords_for_category(category)
            
            # 키워드 조합으로 뉴스 검색
            category_articles = self.search_bid_news_by_keywords(category, keyword_combinations)
            
            all_articles.extend(category_articles)
        
        # 중복 제거 (URL 기준)
        unique_articles = self.remove_duplicates(all_articles)
        
        # 카테고리별 상위 5개씩 선별
        selected_articles = []
        for category in target_categories:
            top_articles = self.select_top_articles_by_category(
                unique_articles, category, ProcessingConfig.BID_ARTICLES_PER_CATEGORY
            )
            selected_articles.extend(top_articles)
        
        logging.info(f"[BID_FINAL] 최종 선별: {len(selected_articles)}건 (목표: {ProcessingConfig.BID_TOTAL_TARGET}건)")
        
        return selected_articles
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """중복 기사 제거 (URL 기준)"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('링크', '')
            if url not in seen_urls and url:
                seen_urls.add(url)
                unique_articles.append(article)
        
        logging.info(f"[BID_DEDUP] 중복 제거: {len(articles)}건 → {len(unique_articles)}건")
        return unique_articles
    
    def save_to_json(self, articles: List[Dict], filename: str = "bid_news_data.json"):
        """입찰/낙찰 뉴스 데이터를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            logging.info(f"[BID_SAVE] {filename}에 {len(articles)}건 저장 완료")
            return True
        except Exception as e:
            logging.error(f"[BID_ERROR] 파일 저장 실패: {str(e)}")
            return False

def main():
    """메인 실행 함수"""
    logging.info("[BID_MAIN] 입찰/낙찰 뉴스 수집 시작")
    
    try:
        # 입찰/낙찰 뉴스 수집기 초기화
        collector = BidNewsCollector()
        
        # 모든 카테고리 입찰/낙찰 뉴스 수집
        selected_articles = collector.collect_bid_news_all_categories()
        
        if not selected_articles:
            logging.warning("[BID_WARNING] 수집된 입찰/낙찰 뉴스가 없습니다.")
            return
        
        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/bid_news_{timestamp}.json"
        
        if collector.save_to_json(selected_articles, filename):
            logging.info(f"[BID_SUCCESS] 입찰/낙찰 뉴스 수집 완료: {len(selected_articles)}건")
            
            # 수집 결과 요약 출력
            logging.info("\n" + "="*60)
            logging.info("[BID_SUMMARY] 입찰/낙찰 뉴스 수집 결과")
            logging.info("="*60)
            
            for i, article in enumerate(selected_articles, 1):
                logging.info(f"{i}. [{article['분야'][0]}][{article['유형']}] {article['제목']}")
                logging.info(f"   중요도: {article['중요도']} | 날짜: {article['날짜']}")
                logging.info("")
            
            logging.info(f"[BID_FINAL] 총 {len(selected_articles)}건의 입찰/낙찰 뉴스가 수집되었습니다!")
        else:
            logging.error("[BID_ERROR] 저장 실패")
            
    except Exception as e:
        logging.error(f"[BID_ERROR] 실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main() 