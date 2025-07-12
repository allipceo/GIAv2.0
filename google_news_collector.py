#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News RSS 피드 기반 뉴스 수집 자동화 스크립트
작성일: 2025년 7월 12일
작성자: 서대리 (Lead Developer)
목적: 조대표님 관심 키워드 뉴스 자동 수집 및 news_data.json 저장

협업헌장 GIA V2.0 준수:
- Notion 기능 극대화: 기존 한글 필드명 완벽 호환
- 최소 개발 원칙: RSS 피드, 파싱, JSON 저장에 집중
- 인코딩 안전성: Windows CP949 환경 완전 호환
"""

import feedparser
import json
import logging
import os
import re
import sys
from datetime import datetime
from urllib.parse import quote

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
        logging.FileHandler('google_news_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 조대표님 관심 키워드 (주력 영업 필드 최적화)
KEYWORDS = {
    "방위산업": ["방위산업", "국방", "K-방산", "군수산업"],
    "신재생에너지": ["신재생에너지", "태양광", "풍력", "ESS"],
    "보험중개": ["보험중개", "보험대리점", "보험영업", "보험상품"]
}

# Google News RSS 기본 URL (한국어, 한국 지역)
GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"
RSS_PARAMS = "hl=ko&gl=KR&ceid=KR:ko"

# 설정값
MAX_ARTICLES_PER_KEYWORD = 3  # 키워드당 최대 수집 기사 수
NEWS_DATA_FILE = "news_data.json"

def safe_encode_text(text):
    """
    인코딩 안전성을 보장하는 텍스트 처리 함수
    모든 특수문자, 이모지, 외국어를 안전하게 처리
    """
    if not text:
        return ""
    
    try:
        # 1단계: 문자열로 변환
        text = str(text)
        
        # 2단계: UTF-8로 인코딩 후 에러 문자 제거
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 3단계: CP949에서 문제가 되는 문자들 제거/대체
        # 이모지 제거 (U+1F000-U+1F9FF 범위)
        text = re.sub(r'[\U0001F000-\U0001F9FF]', '', text)
        
        # 기타 특수 유니코드 문자 제거
        text = re.sub(r'[\u2000-\u206F\u2E00-\u2E7F\u3000-\u303F]', '', text)
        
        # 제어 문자 제거
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        # 4단계: CP949 호환성 테스트
        try:
            text.encode('cp949')
        except UnicodeEncodeError:
            # CP949로 인코딩할 수 없는 문자가 있으면 ASCII 안전 문자로만 구성
            text = text.encode('ascii', errors='ignore').decode('ascii')
        
        return text.strip()
        
    except Exception as e:
        logging.warning(f"[ENCODING] 텍스트 처리 실패, 기본값 반환: {str(e)}")
        return "텍스트 처리 오류"

def safe_print(message):
    """
    인코딩 안전한 출력 함수
    """
    try:
        safe_message = safe_encode_text(message)
        print(safe_message)
    except Exception as e:
        print(f"[PRINT_ERROR] 출력 오류: {str(e)}")

def clean_html_tags(text):
    """HTML 태그 및 특수문자 제거"""
    if not text:
        return ""
    
    # 안전한 텍스트로 변환
    text = safe_encode_text(text)
    
    # HTML 태그 제거
    clean_text = re.sub(r'<[^>]+>', '', text)
    # 연속된 공백 정리
    clean_text = re.sub(r'\s+', ' ', clean_text)
    # 앞뒤 공백 제거
    return clean_text.strip()

def format_korean_date(date_string):
    """RSS 피드의 날짜를 한국 형식으로 변환"""
    try:
        # feedparser가 파싱한 날짜 구조체 처리
        if hasattr(date_string, 'tm_year'):
            dt = datetime(*date_string[:6])
        else:
            # 문자열인 경우 파싱 시도
            dt = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")
        
        return dt.strftime("%Y-%m-%d")
    except:
        # 파싱 실패 시 오늘 날짜 반환
        return datetime.now().strftime("%Y-%m-%d")

def determine_importance(title, category):
    """기사 제목과 카테고리를 바탕으로 중요도 판단"""
    high_keywords = ["신기록", "혁신", "획기적", "최초", "대규모", "정책", "발표"]
    medium_keywords = ["확대", "증가", "성장", "개발", "시장", "동향"]
    
    title_lower = title.lower()
    
    # 고중요도 키워드 포함 시
    if any(keyword in title for keyword in high_keywords):
        return "높음"
    # 중간중요도 키워드 포함 시
    elif any(keyword in title for keyword in medium_keywords):
        return "중간"
    else:
        return "보통"

def collect_google_news_rss(keywords_dict):
    """Google News RSS 피드에서 뉴스 수집"""
    all_articles = []
    
    for category, keyword_list in keywords_dict.items():
        logging.info(f"[NEWS] {category} 카테고리 뉴스 수집 시작")
        
        for keyword in keyword_list:
            try:
                # Google News RSS URL 구성
                encoded_keyword = quote(keyword)
                rss_url = f"{GOOGLE_NEWS_RSS_BASE}?q={encoded_keyword}&{RSS_PARAMS}"
                
                logging.info(f"[SEARCH] 키워드 '{keyword}' 검색 중...")
                
                # RSS 피드 파싱
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    logging.warning(f"[WARNING] RSS 피드 파싱 경고: {keyword}")
                
                # 기사 수집 (최대 개수 제한)
                articles_collected = 0
                for entry in feed.entries:
                    if articles_collected >= MAX_ARTICLES_PER_KEYWORD:
                        break
                    
                    # Notion DB 형식에 맞춰 데이터 구성 (인코딩 안전 처리)
                    article = {
                        "제목": safe_encode_text(clean_html_tags(entry.title)),
                        "URL": safe_encode_text(entry.link),
                        "발행일": format_korean_date(entry.published_parsed if hasattr(entry, 'published_parsed') else entry.published),
                        "요약": "자동 수집된 뉴스",  # 초기 플레이스홀더
                        "태그": [safe_encode_text(category)],  # 수집 카테고리를 태그로 사용
                        "중요도": determine_importance(safe_encode_text(entry.title), category),
                        "요약 품질 평가": "보통"  # 초기 기본값
                    }
                    
                    all_articles.append(article)
                    articles_collected += 1
                
                logging.info(f"[SUCCESS] '{keyword}' 키워드: {articles_collected}건 수집 완료")
                
            except Exception as e:
                logging.error(f"[ERROR] '{keyword}' 수집 실패: {str(e)}")
                continue
    
    logging.info(f"[COMPLETE] 전체 수집 완료: 총 {len(all_articles)}건")
    return all_articles

def load_existing_news(file_path):
    """기존 news_data.json 파일 로드"""
    if not os.path.exists(file_path):
        logging.info(f"[INFO] {file_path} 파일이 없어 새로 생성합니다.")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"[INFO] 기존 뉴스 {len(data)}건 로드 완료")
        return data
    except Exception as e:
        logging.error(f"[ERROR] 기존 파일 로드 실패: {str(e)}")
        return []

def get_existing_urls(news_list):
    """기존 뉴스의 URL 목록 추출"""
    return {news.get('URL', '') for news in news_list}

def avoid_duplicates(new_articles, existing_news):
    """중복 URL 제거"""
    existing_urls = get_existing_urls(existing_news)
    unique_articles = []
    
    for article in new_articles:
        if article['URL'] not in existing_urls:
            unique_articles.append(article)
        else:
            logging.info(f"[DUPLICATE] 중복 제거: {article['제목']}")
    
    logging.info(f"[INFO] 중복 제거 후: {len(unique_articles)}건")
    return unique_articles

def save_news_data(news_list, file_path):
    """뉴스 데이터를 JSON 파일로 저장"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        logging.info(f"[SAVE] {file_path}에 {len(news_list)}건 저장 완료")
        return True
    except Exception as e:
        logging.error(f"[ERROR] 파일 저장 실패: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    logging.info("[START] Google News 수집 시작")
    logging.info(f"[INFO] 수집 키워드: {list(KEYWORDS.keys())}")
    
    try:
        # 1. 새 뉴스 수집
        new_articles = collect_google_news_rss(KEYWORDS)
        
        if not new_articles:
            logging.warning("[WARNING] 수집된 뉴스가 없습니다.")
            return
        
        # 2. 기존 뉴스 로드
        existing_news = load_existing_news(NEWS_DATA_FILE)
        
        # 3. 중복 제거
        unique_articles = avoid_duplicates(new_articles, existing_news)
        
        if not unique_articles:
            logging.info("[INFO] 새로운 뉴스가 없습니다. (모두 중복)")
            return
        
        # 4. 기존 뉴스와 합치기
        updated_news = existing_news + unique_articles
        
        # 5. 저장
        if save_news_data(updated_news, NEWS_DATA_FILE):
            logging.info(f"[SUCCESS] 성공: 새 뉴스 {len(unique_articles)}건 추가")
            logging.info(f"[INFO] 전체 뉴스: {len(updated_news)}건")
            
            # 수집된 뉴스 요약 출력 (인코딩 안전)
            safe_print("\n" + "="*50)
            safe_print("[NEWS] Google News 수집 결과")
            safe_print("="*50)
            for i, article in enumerate(unique_articles, 1):
                safe_print(f"{i}. [{article['태그'][0]}] {article['제목']}")
                safe_print(f"   [DATE] {article['발행일']} | [URL] {article['URL'][:50]}...")
                safe_print(f"   [PRIORITY] 중요도: {article['중요도']}")
                safe_print("")
            safe_print(f"[SUCCESS] 총 {len(unique_articles)}건의 새 뉴스가 news_data.json에 추가되었습니다!")
        else:
            logging.error("[ERROR] 저장 실패")
            
    except Exception as e:
        logging.error(f"[ERROR] 실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main() 