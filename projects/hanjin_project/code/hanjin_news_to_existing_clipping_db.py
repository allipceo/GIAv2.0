#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 뉴스를 기존 뉴스 클리핑 DB에 업로드하는 스크립트
작성일: 2025년 8월 6일
작성자: 서대리 (Lead Developer)
목적: 조대표님 지시에 따라 기존 뉴스 클리핑 DB 활용
"""

import json
import requests
from datetime import datetime
import time

# 노션 API 설정
NOTION_TOKEN = "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"
CLIPPING_DB_ID = "22aa613d25ff80888257c652d865f85a"  # 기존 뉴스 클리핑 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def load_hanjin_news_data(filename="../data/hanjin_real_news_data.json"):
    """한진중공업 뉴스 데이터 로드"""
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
    url = f"https://api.notion.com/v1/databases/{CLIPPING_DB_ID}/query"
    
    try:
        response = requests.post(url, headers=HEADERS)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        existing_titles = []
        
        for result in results:
            properties = result.get('properties', {})
            title_prop = properties.get('제목', {})
            if title_prop.get('title'):
                title = title_prop['title'][0]['text']['content']
                existing_titles.append(title)
        
        return existing_titles
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 기존 뉴스 조회 실패: {e}")
        return []

def upload_hanjin_news_to_clipping_db(article):
    """한진중공업 뉴스를 기존 클리핑 DB에 업로드"""
    url = "https://api.notion.com/v1/pages"
    
    # 제목에서 중복 제거
    title = article.get('title', '')
    if not title:
        return False
    
    # 날짜 처리
    published_at = article.get('publishedAt', datetime.now().strftime("%Y-%m-%d"))
    if isinstance(published_at, str):
        try:
            # ISO 형식으로 변환
            date_obj = datetime.strptime(published_at, "%Y-%m-%d")
            iso_date = date_obj.isoformat()
        except:
            iso_date = datetime.now().isoformat()
    else:
        iso_date = datetime.now().isoformat()
    
    # 키워드 정보
    keyword = article.get('keyword', '한진중공업')
    
    payload = {
        "parent": {
            "database_id": CLIPPING_DB_ID
        },
        "properties": {
            "제목": {
                "title": [
                    {
                        "text": {
                            "content": title[:200]  # 제목 길이 제한
                        }
                    }
                ]
            },
            "링크": {
                "url": article.get('url', '')
            },
            "날짜": {
                "date": {
                    "start": iso_date
                }
            },
            "분야": {
                "multi_select": [
                    {
                        "name": keyword
                    }
                ]
            },
            "출처": {
                "rich_text": [
                    {
                        "text": {
                            "content": article.get('source', 'Google News')
                        }
                    }
                ]
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
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 업로드 실패: {title[:50]}... - {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 한진중공업 뉴스를 기존 클리핑 DB에 업로드 시작...")
    
    # 1. 한진중공업 뉴스 데이터 로드
    articles = load_hanjin_news_data()
    if not articles:
        print("❌ 업로드할 뉴스 데이터가 없습니다.")
        print("💡 먼저 hanjin_real_news_collector.py를 실행하여 뉴스를 수집하세요.")
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
        if upload_hanjin_news_to_clipping_db(article):
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
        print(f"\n🎉 한진중공업 뉴스가 기존 클리핑 DB에 업로드되었습니다!")
        print(f"📱 노션에서 기존 뉴스 클리핑 DB를 확인하세요.")
        print(f"🔍 '분야' 필터에서 '한진중공업'을 선택하면 한진중공업 뉴스만 볼 수 있습니다.")

if __name__ == "__main__":
    main() 