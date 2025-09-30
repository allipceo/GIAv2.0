#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 관련 뉴스만 선별하여 기존 뉴스 클리핑 DB에 업로드하는 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 조대표님 지시에 따라 한진중공업 뉴스를 올바른 클리핑 DB에 업로드
"""

import json
import requests
from datetime import datetime
import time

# 노션 API 설정
NOTION_TOKEN = ""
CLIPPING_DB_ID = "22aa613d25ff80888257c652d865f85a"  # 기존 뉴스 클리핑 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def load_hanjin_news():
    """한진중공업 관련 뉴스만 선별"""
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
        
        # 한진중공업 관련 키워드로 필터링
        hanjin_keywords = ["한진중공업", "한진", "HJ중공업", "한진중공", "한진칼"]
        hanjin_news = []
        
        for news in all_news:
            title = news.get("제목", "").lower()
            if any(keyword.lower() in title for keyword in hanjin_keywords):
                hanjin_news.append(news)
        
        print(f"[INFO] 한진중공업 관련 뉴스 {len(hanjin_news)}건 선별 완료")
        return hanjin_news
        
    except Exception as e:
        print(f"[ERROR] 뉴스 로드 실패: {e}")
        return []

def upload_hanjin_news(article):
    """한진중공업 뉴스를 클리핑 DB에 업로드"""
    url = "https://api.notion.com/v1/pages"
    
    # 제목 처리
    title = article.get('제목', '')
    if not title:
        return False
    
    # 날짜 처리
    published_at = article.get('발행일', datetime.now().strftime("%Y-%m-%d"))
    try:
        date_obj = datetime.strptime(published_at, "%Y-%m-%d")
        iso_date = date_obj.isoformat()
    except:
        iso_date = datetime.now().isoformat()
    
    # 태그 처리
    tag = article.get('태그', ['한진중공업'])[0] if article.get('태그') else '한진중공업'
    
    payload = {
        "parent": {
            "database_id": CLIPPING_DB_ID
        },
        "properties": {
            "제목": {
                "title": [{"text": {"content": title[:200]}}]
            },
            "링크": {
                "url": article.get('URL', '')
            },
            "날짜": {
                "date": {"start": iso_date}
            },
            "분야": {
                "multi_select": [{"name": tag}]
            },
            "출처": {
                "rich_text": [{"text": {"content": "Google News"}}]
            },
            "중요도": {
                "select": {"name": article.get('중요도', '보통')}
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print(f"✅ 업로드 성공: {title[:50]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 업로드 실패: {title[:50]}... - {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 한진중공업 뉴스를 기존 클리핑 DB에 업로드 시작...")
    
    # 1. 한진중공업 뉴스 선별
    hanjin_news = load_hanjin_news()
    if not hanjin_news:
        print("❌ 한진중공업 관련 뉴스가 없습니다.")
        return
    
    print(f"📰 {len(hanjin_news)}개 한진중공업 기사를 업로드합니다.")
    
    # 2. 업로드 실행
    success_count = 0
    error_count = 0
    
    for article in hanjin_news:
        if upload_hanjin_news(article):
            success_count += 1
        else:
            error_count += 1
        
        # 요청 간격 조절
        time.sleep(1)
    
    # 3. 결과 출력
    print(f"\n📊 업로드 완료:")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"📝 총 처리: {len(hanjin_news)}개")
    
    if success_count > 0:
        print(f"\n🎉 한진중공업 뉴스가 기존 클리핑 DB에 업로드되었습니다!")
        print(f"📱 노션에서 기존 뉴스 클리핑 DB를 확인하세요.")
        print(f"🔍 '분야' 필터에서 '한진중공업'을 선택하면 한진중공업 뉴스만 볼 수 있습니다.")

if __name__ == "__main__":
    main()
