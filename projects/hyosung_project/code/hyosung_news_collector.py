#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
효성중공업 전용 뉴스 수집 자동화 스크립트 (Google News RSS 기반)
작성일: 2025년 7월 17일
작성자: 서대리 (Lead Developer)
목적: 효성중공업 관련 뉴스 자동 수집 및 hyosung_news_data.json 저장

협업헌장 GIA V2.0 준수:
- 기존 검증된 시스템 활용: google_news_collector.py 구조 완전 재활용
- 최소 개발 원칙: 키워드만 효성중공업 특화로 변경
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
        logging.FileHandler('hyosung_news_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 효성중공업 관련 키워드 (기업 조사 및 보험 영업 최적화)
KEYWORDS = {
    "회사명": ["효성중공업", "효성", "Hyosung Heavy Industries"],
    "전력기기": ["전력기기", "변압기", "차단기", "초고압변압기", "HVDC", "스마트변전소"],
    "신재생에너지": ["ESS", "에너지저장시스템", "풍력발전", "태양광", "신재생에너지"],
    "해외사업": ["멤피스", "창원", "해외수주", "글로벌", "북미", "중동", "유럽"],
    "건설사업": ["해링턴플레이스", "데이터센터", "클린룸", "EPC", "플랜트"]
}

# Google News RSS 기본 URL (한국어, 한국 지역)
GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"
RSS_PARAMS = "hl=ko&gl=KR&ceid=KR:ko"

# 설정값
MAX_ARTICLES_PER_KEYWORD = 5  # 키워드당 최대 수집 기사 수 (효성중공업 전용으로 증가)
NEWS_DATA_FILE = "../data/hyosung_news_data.json"

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
            # CP949로 인코딩 불가능한 문자들을 비슷한 문자로 대체
            text = text.replace('—', '-')
            text = text.replace('–', '-')
            text = text.replace('"', '"')
            text = text.replace('"', '"')
            text = text.replace(''', "'")
            text = text.replace(''', "'")
            text = text.replace('…', '...')
            
        return text.strip()
    
    except Exception as e:
        logging.error(f"텍스트 인코딩 처리 중 오류 발생: {str(e)}")
        return str(text)[:100]  # 오류 시 앞 100자만 반환

def safe_print(text):
    """안전한 출력 함수 - Windows CP949 인코딩 문제 방지"""
    try:
        safe_text = safe_encode_text(text)
        print(safe_text)
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
    """기사 제목과 카테고리를 바탕으로 중요도 판단 (효성중공업 특화)"""
    high_keywords = ["효성중공업", "대규모", "수주", "투자", "확대", "해외", "신기록", "혁신", "획기적", "최초"]
    medium_keywords = ["효성", "전력기기", "변압기", "ESS", "성장", "개발", "시장", "동향", "멤피스", "창원"]
    
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
    
    for category, keywords in keywords_dict.items():
        safe_print(f"\n=== {category} 카테고리 뉴스 수집 시작 ===")
        
        for keyword in keywords:
            safe_print(f"키워드 '{keyword}' 검색 중...")
            
            # URL 인코딩된 쿼리 생성
            encoded_keyword = quote(keyword)
            search_url = f"{GOOGLE_NEWS_RSS_BASE}?q={encoded_keyword}&{RSS_PARAMS}"
            
            try:
                # RSS 피드 파싱
                feed = feedparser.parse(search_url)
                
                if feed.bozo:
                    logging.warning(f"RSS 피드 파싱 경고: {keyword}")
                
                # 기사 수집
                articles_count = 0
                for entry in feed.entries:
                    if articles_count >= MAX_ARTICLES_PER_KEYWORD:
                        break
                    
                    # 기사 정보 추출
                    title = clean_html_tags(entry.title)
                    link = entry.link
                    description = clean_html_tags(entry.get('description', ''))
                    published = format_korean_date(entry.published_parsed)
                    
                    # 중요도 판단
                    importance = determine_importance(title, category)
                    
                    # 기사 객체 생성
                    article = {
                        "제목": title,
                        "URL": link,
                        "요약": description,
                        "발행일": published,
                        "카테고리": category,
                        "키워드": keyword,
                        "중요도": importance,
                        "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    all_articles.append(article)
                    articles_count += 1
                    
                    safe_print(f"  ✓ [{importance}] {title}")
                
                safe_print(f"키워드 '{keyword}': {articles_count}개 기사 수집")
                
            except Exception as e:
                logging.error(f"키워드 '{keyword}' 수집 중 오류: {str(e)}")
                safe_print(f"  ✗ 오류 발생: {str(e)}")
    
    return all_articles

def save_to_json(articles, filename):
    """수집된 뉴스를 JSON 파일로 저장"""
    try:
        # 기존 데이터 로드 (있는 경우)
        existing_data = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 중복 제거를 위한 기존 제목 세트
        existing_titles = {article.get('제목', '') for article in existing_data}
        
        # 새로운 기사만 추가
        new_articles = []
        for article in articles:
            if article['제목'] not in existing_titles:
                new_articles.append(article)
        
        # 전체 데이터 = 기존 + 새로운
        all_data = existing_data + new_articles
        
        # JSON 파일로 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        safe_print(f"\n✓ 총 {len(all_data)}개 기사 저장 완료 (신규: {len(new_articles)}개)")
        safe_print(f"저장 위치: {filename}")
        
        return len(new_articles)
        
    except Exception as e:
        logging.error(f"JSON 저장 중 오류 발생: {str(e)}")
        safe_print(f"✗ 저장 실패: {str(e)}")
        return 0

def main():
    """메인 실행 함수"""
    safe_print("=" * 60)
    safe_print("🏭 효성중공업 전용 뉴스 수집기 시작")
    safe_print("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # 뉴스 수집 실행
        articles = collect_google_news_rss(KEYWORDS)
        
        # JSON 파일로 저장
        new_count = save_to_json(articles, NEWS_DATA_FILE)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        safe_print("\n" + "=" * 60)
        safe_print("📊 효성중공업 뉴스 수집 완료")
        safe_print("=" * 60)
        safe_print(f"수집 기사 수: {len(articles)}개")
        safe_print(f"신규 기사 수: {new_count}개")
        safe_print(f"소요 시간: {duration.seconds}초")
        safe_print(f"완료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        logging.info(f"효성중공업 뉴스 수집 완료: {len(articles)}개 수집, {new_count}개 신규")
        
    except Exception as e:
        logging.error(f"메인 실행 중 오류 발생: {str(e)}")
        safe_print(f"✗ 프로그램 실행 중 오류: {str(e)}")

if __name__ == "__main__":
    main() 