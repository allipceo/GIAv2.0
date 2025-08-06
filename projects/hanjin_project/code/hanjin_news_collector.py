#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 뉴스 수집 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업 프로젝트 Phase 1 - 뉴스 수집 및 분석
"""

import requests
import json
import time
from datetime import datetime
from urllib.parse import quote_plus

# 설정값
MAX_ARTICLES_PER_KEYWORD = 5  # 키워드당 최대 수집 기사 수
NEWS_DATA_FILE = "../data/hanjin_news_data.json"

# 한진중공업 관련 키워드
KEYWORDS = [
    "한진중공업",
    "HJ중공업", 
    "한진중공업 조원국",
    "한진중공업 매출",
    "한진중공업 프로젝트",
    "한진중공업 신재생에너지",
    "한진중공업 해양플랜트",
    "한진중공업 보험",
    "한진중공업 리스크"
]

def safe_encode_text(text):
    """텍스트를 안전하게 인코딩"""
    if text is None:
        return ""
    return str(text).strip()

def collect_news_for_keyword(keyword):
    """특정 키워드로 뉴스 수집"""
    print(f"🔍 키워드 '{keyword}' 뉴스 수집 중...")
    
    # Google News API 호출 (실제로는 뉴스 API 사용)
    articles = []
    
    # 임시로 더미 데이터 생성 (실제 API 연동 시 교체)
    for i in range(MAX_ARTICLES_PER_KEYWORD):
        article = {
            "title": f"한진중공업 관련 뉴스 {i+1} - {keyword}",
            "description": f"한진중공업의 {keyword} 관련 최신 동향을 다룬 기사입니다.",
            "url": f"https://example.com/hanjin-news-{i+1}",
            "publishedAt": datetime.now().strftime("%Y-%m-%d"),
            "source": "뉴스 소스",
            "keyword": keyword
        }
        articles.append(article)
    
    print(f"✅ '{keyword}' 키워드로 {len(articles)}개 기사 수집 완료")
    return articles

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🚀 한진중공업 프로젝트 Phase 1: 뉴스 수집 시작")
    print("="*80)
    
    all_articles = []
    
    # 각 키워드별로 뉴스 수집
    for keyword in KEYWORDS:
        articles = collect_news_for_keyword(keyword)
        all_articles.extend(articles)
        time.sleep(1)  # API 호출 간격 조절
    
    # 결과 저장
    news_data = {
        "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_articles": len(all_articles),
        "keywords_used": KEYWORDS,
        "articles": all_articles
    }
    
    with open(NEWS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 뉴스 데이터 저장: {NEWS_DATA_FILE}")
    print(f"📊 총 {len(all_articles)}개 기사 수집 완료")
    print("🎯 한진중공업 뉴스 수집 완료!")

if __name__ == "__main__":
    main() 