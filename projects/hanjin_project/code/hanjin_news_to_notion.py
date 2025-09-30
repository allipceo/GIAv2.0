#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 뉴스를 노션 DB에 업로드하는 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 한진중공업 프로젝트 Phase 1 - 뉴스 데이터 노션 업로드
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = ""  # 검증된 노션 API 토큰
NEWS_DB_ID = "234a613d25ff81aba93ae4cb8f36c920"  # 기업재무 및 프로젝트 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def load_news_data(filename):
    """뉴스 데이터 로드"""
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

def get_existing_news():
    """기존 뉴스 항목 조회"""
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

def upload_news_to_notion(article):
    """뉴스를 노션 DB에 업로드"""
    url = "https://api.notion.com/v1/pages"
    
    # 제목에서 중복 제거
    title = article.get('title', '')
    if not title:
        return False
    
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
            "사업 부문": {
                "multi_select": [
                    {
                        "name": "중공업"
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
        
        result = response.json()
        page_id = result["id"]
        page_url = result["url"]
        
        print(f"✅ 뉴스 업로드 완료: {title[:50]}...")
        print(f"   - Page ID: {page_id}")
        print(f"   - URL: {page_url}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 뉴스 업로드 실패: {title[:50]}...")
        print(f"   - 오류: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - 응답 내용: {e.response.text}")
        return False

def main():
    """메인 실행 함수"""
    print("="*80)
    print("🚀 한진중공업 프로젝트 Phase 1: 뉴스 노션 업로드")
    print("="*80)
    
    # 뉴스 데이터 로드
    news_list = load_news_data('../data/hanjin_news_data.json')
    if not news_list:
        print("❌ 뉴스 데이터를 로드할 수 없습니다.")
        return
    
    print(f"📊 로드된 뉴스 수: {len(news_list)}개")
    
    # 기존 뉴스 조회
    existing = get_existing_news()
    print(f"📋 기존 뉴스 수: {len(existing)}개")
    
    # 중복 제거 후 업로드
    count = 0
    for article in news_list:
        title = article.get('title', '')
        if title and title not in existing:
            if upload_news_to_notion(article):
                count += 1
    
    print(f"\n🎉 업로드 완료: {count}개 뉴스")
    print("🎯 한진중공업 뉴스 노션 업로드 완료!")

if __name__ == "__main__":
    main() 