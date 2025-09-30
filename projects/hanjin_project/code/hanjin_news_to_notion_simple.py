#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 실제 뉴스 제목 업로드 (기존 DB 구조 유지)
작성일: 2025년 8월 6일
작성자: 서대리 (Lead Developer)
목적: 실제 뉴스 제목으로 업로드하여 클리핑 의미 개선
"""

import json
import requests
from datetime import datetime
import time

# 노션 API 설정
NOTION_TOKEN = ""
NEWS_DB_ID = "234a613d25ff81aba93ae4cb8f36c920"  # 기업재무 및 프로젝트 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def load_enhanced_news_data(filename="../data/hanjin_real_news_data.json"):
    """향상된 뉴스 데이터 로드"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('articles', [])
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {filename}")
        return []
    except json.JSONDecodeError:
        print(f"❌ JSON 파일 형식 오류: {filename}")
        return []

def get_existing_news_titles():
    """기존 뉴스 제목 조회 (중복 방지)"""
    url = f"https://api.notion.com/v1/databases/{NEWS_DB_ID}/query"
    
    try:
        response = requests.post(url, headers=HEADERS)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        existing_titles = []
        
        for result in results:
            properties = result.get('properties', {})
            title_prop = properties.get('항목명', {})
            if title_prop.get('title'):
                title = title_prop['title'][0]['text']['content']
                existing_titles.append(title)
        
        return existing_titles
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 기존 뉴스 조회 실패: {e}")
        return []

def upload_news_with_real_title(article):
    """실제 뉴스 제목으로 업로드 (기존 DB 구조 유지)"""
    url = "https://api.notion.com/v1/pages"
    
    # 제목에서 중복 제거
    title = article.get('title', '')
    if not title:
        return False
    
    # 언론사 정보
    source = article.get('source', 'Google News')
    
    # 키워드 정보
    keyword = article.get('keyword', '한진중공업')
    
    payload = {
        "parent": {
            "database_id": NEWS_DB_ID
        },
        "properties": {
            "항목명": {
                "title": [
                    {
                        "text": {
                            "content": title[:200]  # 제목 길이 제한
                        }
                    }
                ]
            },
            "데이터 유형": {
                "select": {
                    "name": "뉴스"
                }
            },
            "사업 부문": {
                "select": {
                    "name": "중공업"
                }
            },
            "수치값": {
                "number": 1  # 뉴스 항목이므로 1로 설정
            },
            "단위": {
                "select": {
                    "name": "건"
                }
            },
            "기준일": {
                "date": {
                    "start": article.get('publishedAt', datetime.now().strftime("%Y-%m-%d"))
                }
            },
            "수집일시": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "중요도": {
                "select": {
                    "name": "보통"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        print(f"✅ 업로드 성공: {title[:50]}...")
        print(f"   📰 언론사: {source}")
        print(f"   🔍 키워드: {keyword}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 업로드 실패: {title[:30]}... - {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 한진중공업 실제 뉴스 제목 업로드 시작...")
    
    # 1. 향상된 뉴스 데이터 로드
    articles = load_enhanced_news_data()
    if not articles:
        print("❌ 업로드할 뉴스 데이터가 없습니다.")
        return
    
    print(f"📰 {len(articles)}개 기사를 업로드합니다.")
    
    # 2. 기존 뉴스 제목 조회 (중복 방지)
    existing_titles = get_existing_news_titles()
    print(f"📋 기존 뉴스 {len(existing_titles)}개 확인됨")
    
    # 3. 새로운 뉴스만 업로드
    success_count = 0
    duplicate_count = 0
    
    for article in articles:
        title = article.get('title', '')
        
        # 중복 체크
        if title in existing_titles:
            print(f"⏭️ 중복 건너뛰기: {title[:50]}...")
            duplicate_count += 1
            continue
        
        # 업로드 실행
        if upload_news_with_real_title(article):
            success_count += 1
            existing_titles.append(title)  # 중복 목록에 추가
        
        # 요청 간격 조절
        time.sleep(1)
    
    # 4. 결과 출력
    print(f"\n📊 업로드 완료:")
    print(f"✅ 성공: {success_count}개")
    print(f"⏭️ 중복: {duplicate_count}개")
    print(f"📝 총 처리: {len(articles)}개")
    
    if success_count > 0:
        print(f"\n🎉 실제 뉴스 제목으로 업로드되었습니다!")
        print(f"📱 노션에서 '기업재무 및 프로젝트 DB'를 확인하세요.")
        print(f"🔍 '데이터 유형' 필터에서 '뉴스'를 선택하면 뉴스만 볼 수 있습니다.")
        print(f"💡 이제 항목명에 실제 뉴스 제목이 표시됩니다!")

if __name__ == "__main__":
    main() 