#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한진중공업 실제 뉴스 수집 및 완전한 클리핑 구현
작성일: 2025년 8월 6일
작성자: 서대리 (Lead Developer)
목적: 실제 뉴스 제목 + 내용 + 링크를 포함한 완전한 뉴스 클리핑
"""

import requests
import json
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re

class HanjinNewsCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.keywords = [
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
        
    def get_google_news(self, keyword, max_results=5):
        """Google News에서 실제 뉴스 수집"""
        try:
            # Google News 검색 URL
            search_url = f"https://news.google.com/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
            
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # 뉴스 기사 링크 찾기
            article_links = soup.find_all('a', href=re.compile(r'./articles/'))
            
            for i, link in enumerate(article_links[:max_results]):
                try:
                    # 기사 제목 추출
                    title_element = link.find('h3') or link.find('h4') or link.find('span')
                    if title_element:
                        title = title_element.get_text().strip()
                    else:
                        title = link.get_text().strip()
                    
                    # 기사 URL 구성
                    article_url = "https://news.google.com" + link.get('href')
                    
                    # 언론사 정보 추출
                    source_element = link.find_parent().find('time')
                    source = "Google News"
                    if source_element and source_element.find_parent():
                        source_text = source_element.find_parent().get_text()
                        if "•" in source_text:
                            source = source_text.split("•")[0].strip()
                    
                    # 기사 내용 수집
                    content = self.get_article_content(article_url)
                    
                    articles.append({
                        'title': title,
                        'content': content,
                        'url': article_url,
                        'source': source,
                        'keyword': keyword,
                        'publishedAt': datetime.now().strftime("%Y-%m-%d")
                    })
                    
                    # 요청 간격 조절
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"기사 처리 중 오류: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Google News 수집 중 오류: {e}")
            return []
    
    def get_article_content(self, url):
        """기사 URL에서 실제 내용 추출"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 일반적인 기사 내용 태그들
            content_selectors = [
                'article p',
                '.article-content p',
                '.news-content p',
                '.content p',
                'p'
            ]
            
            content = ""
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    for p in paragraphs[:10]:  # 처음 10개 문단만
                        text = p.get_text().strip()
                        if len(text) > 20:  # 의미있는 텍스트만
                            content += text + "\n\n"
                    break
            
            # 내용이 없으면 제목이라도 반환
            if not content:
                title = soup.find('title')
                if title:
                    content = title.get_text().strip()
            
            return content[:2000]  # 2000자로 제한
            
        except Exception as e:
            print(f"기사 내용 추출 중 오류: {e}")
            return "내용을 불러올 수 없습니다."
    
    def collect_all_news(self):
        """모든 키워드로 뉴스 수집"""
        all_articles = []
        
        for keyword in self.keywords:
            print(f"🔍 '{keyword}' 키워드로 뉴스 수집 중...")
            articles = self.get_google_news(keyword, max_results=3)
            all_articles.extend(articles)
            print(f"✅ {len(articles)}개 기사 수집 완료")
            time.sleep(2)  # 키워드 간 간격
        
        return all_articles
    
    def save_news_data(self, articles, filename="hanjin_enhanced_news_data.json"):
        """수집된 뉴스 데이터 저장"""
        data = {
            "collection_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_articles": len(articles),
            "keywords_used": self.keywords,
            "articles": articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 {len(articles)}개 기사를 {filename}에 저장했습니다.")
        return filename

def main():
    """메인 실행 함수"""
    print("🚀 한진중공업 실제 뉴스 수집 시작...")
    
    collector = HanjinNewsCollector()
    articles = collector.collect_all_news()
    
    if articles:
        filename = collector.save_news_data(articles)
        print(f"✅ 뉴스 수집 완료: {len(articles)}개 기사")
        print(f"📁 저장 위치: {filename}")
        
        # 샘플 출력
        print("\n📰 수집된 뉴스 샘플:")
        for i, article in enumerate(articles[:3]):
            print(f"\n{i+1}. {article['title']}")
            print(f"   언론사: {article['source']}")
            print(f"   키워드: {article['keyword']}")
            print(f"   내용 미리보기: {article['content'][:100]}...")
    else:
        print("❌ 수집된 뉴스가 없습니다.")

if __name__ == "__main__":
    main() 