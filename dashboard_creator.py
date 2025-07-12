#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
조대표님 전용 핵심 정보 대시보드 생성기
작성일: 2025년 1월 12일
작성자: 서대리 (Lead Developer)
목적: 조대표님이 매일 아침 10분에 핵심 정보를 파악할 수 있는 맞춤형 대시보드

주요 기능:
- 오늘의 중요 뉴스 섹션 (자동 우선순위 정렬)
- 주요 낙찰 정보 요약 섹션 (초기 임시 데이터)
- LLM 기반 요약 자리 (핵심 인사이트)
- 빠른 액션 버튼 (읽음 처리, 프로젝트 연결, 중요 표시)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from notion_client import Client
from mvp_config import APIConfig, DashboardConfig

class DashboardCreator:
    """조대표님 전용 대시보드 생성기"""
    
    def __init__(self):
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        self.database_id = APIConfig.NOTION_NEWS_DATABASE_ID
        self.bid_database_id = APIConfig.NOTION_BID_DATABASE_ID
        
    def get_todays_important_news(self, limit: int = 10) -> List[Dict]:
        """오늘의 중요 뉴스 가져오기"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 노션 DB에서 오늘 날짜 뉴스 조회
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "and": [
                        {
                            "property": "날짜",
                            "date": {
                                "equals": today
                            }
                        }
                    ]
                },
                sorts=[
                    {
                        "property": "중요도",
                        "direction": "ascending"  # 중요도 높은 순
                    }
                ]
            )
            
            news_items = []
            for page in response.get('results', [])[:limit]:
                properties = page.get('properties', {})
                
                # 속성 값 추출
                title = self.extract_title(properties.get('제목', {}))
                date = self.extract_date(properties.get('날짜', {}))
                link = self.extract_url(properties.get('링크', {}))
                importance = self.extract_select(properties.get('중요도', {}))
                category = self.extract_multiselect(properties.get('분야', {}))
                summary = self.extract_rich_text(properties.get('주요내용', {}))
                
                news_item = {
                    'id': page['id'],
                    'title': title,
                    'date': date,
                    'link': link,
                    'importance': importance,
                    'category': category,
                    'summary': summary,
                    'importance_score': self.get_importance_score(importance)
                }
                
                news_items.append(news_item)
            
            # 중요도 점수로 정렬
            news_items.sort(key=lambda x: x['importance_score'], reverse=True)
            
            logging.info(f"[DASHBOARD] 오늘의 뉴스 {len(news_items)}건 로드 완료")
            return news_items
            
        except Exception as e:
            logging.error(f"[DASHBOARD] 뉴스 조회 실패: {str(e)}")
            return []
    
    def get_todays_bid_information(self, limit: int = 5) -> List[Dict]:
        """오늘의 입찰/낙찰 정보 가져오기"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 노션 입찰낙찰 공고 DB에서 오늘 수정된 항목 조회
            response = self.notion.databases.query(
                database_id=self.bid_database_id,
                filter={
                    "and": [
                        {
                            "property": "수정일시",
                            "date": {
                                "equals": today
                            }
                        },
                        {
                            "property": "선별여부",
                            "checkbox": {
                                "equals": True
                            }
                        }
                    ]
                },
                sorts=[
                    {
                        "property": "중요도",
                        "direction": "ascending"  # 중요도 높은 순
                    }
                ]
            )
            
            bid_items = []
            for page in response.get('results', [])[:limit]:
                properties = page.get('properties', {})
                
                # 속성 값 추출
                title = self.extract_title(properties.get('제목', {}))
                date = self.extract_date(properties.get('날짜', {}))
                link = self.extract_url(properties.get('링크', {}))
                importance = self.extract_select(properties.get('중요도', {}))
                category = self.extract_multiselect(properties.get('분야', {}))
                bid_type = self.extract_select(properties.get('유형', {}))
                content = self.extract_rich_text(properties.get('주요내용', {}))
                
                bid_item = {
                    'id': page['id'],
                    'title': title,
                    'date': date,
                    'link': link,
                    'importance': importance,
                    'category': category,
                    'type': bid_type,
                    'content': content,
                    'importance_score': self.get_importance_score(importance)
                }
                
                bid_items.append(bid_item)
            
            # 중요도 점수로 정렬
            bid_items.sort(key=lambda x: x['importance_score'], reverse=True)
            
            logging.info(f"[DASHBOARD] 입찰/낙찰 정보 {len(bid_items)}건 로드 완료")
            return bid_items
            
        except Exception as e:
            logging.error(f"[DASHBOARD] 입찰/낙찰 정보 조회 실패: {str(e)}")
            return []
    
    def extract_title(self, title_prop: Dict) -> str:
        """제목 속성에서 텍스트 추출"""
        try:
            return title_prop.get('title', [{}])[0].get('text', {}).get('content', '')
        except:
            return ''
    
    def extract_date(self, date_prop: Dict) -> str:
        """날짜 속성에서 날짜 추출"""
        try:
            return date_prop.get('date', {}).get('start', '')
        except:
            return ''
    
    def extract_url(self, url_prop: Dict) -> str:
        """URL 속성에서 링크 추출"""
        try:
            return url_prop.get('url', '')
        except:
            return ''
    
    def extract_select(self, select_prop: Dict) -> str:
        """Select 속성에서 값 추출"""
        try:
            return select_prop.get('select', {}).get('name', '')
        except:
            return ''
    
    def extract_multiselect(self, multiselect_prop: Dict) -> List[str]:
        """Multi-select 속성에서 값들 추출"""
        try:
            return [item.get('name', '') for item in multiselect_prop.get('multi_select', [])]
        except:
            return []
    
    def extract_rich_text(self, rich_text_prop: Dict) -> str:
        """Rich text 속성에서 텍스트 추출"""
        try:
            texts = rich_text_prop.get('rich_text', [])
            return ''.join([item.get('text', {}).get('content', '') for item in texts])
        except:
            return ''
    
    def get_importance_score(self, importance: str) -> int:
        """중요도 문자열을 점수로 변환"""
        scores = {
            '매우중요': 5,
            '중요': 4,
            '높음': 3,
            '보통': 2,
            '낮음': 1,
            '무시': 0
        }
        return scores.get(importance, 2)
    
    def create_dashboard_page(self, news_items: List[Dict]) -> str:
        """대시보드 페이지 생성"""
        current_time = datetime.now()
        
        # 대시보드 제목
        page_title = f"📊 조대표님 일일 브리핑 - {current_time.strftime('%Y년 %m월 %d일')}"
        
        # 입찰/낙찰 정보 가져오기
        bid_items = self.get_todays_bid_information()
        
        # 페이지 내용 구성
        blocks = []
        
        # 1. 헤더
        blocks.extend(self.create_header_blocks(current_time))
        
        # 2. 중요 뉴스 섹션
        blocks.extend(self.create_news_section_blocks(news_items))
        
        # 3. 입찰공고 및 낙찰정보 섹션
        blocks.extend(self.create_procurement_section_blocks(bid_items))
        
        # 4. LLM 요약 섹션
        blocks.extend(self.create_summary_section_blocks(news_items))
        
        # 5. 액션 버튼 섹션
        blocks.extend(self.create_action_section_blocks())
        
        # 6. 푸터
        blocks.extend(self.create_footer_blocks())
        
        try:
            # 노션 페이지 생성
            response = self.notion.pages.create(
                parent={"page_id": "227a613d-25ff-800c-a97d-e24f6eb521a8"},  # 부모 페이지 ID
                properties={
                    "title": {
                        "title": [{"text": {"content": page_title}}]
                    }
                },
                children=blocks
            )
            
            page_url = response.get('url', '')
            logging.info(f"[DASHBOARD] 대시보드 페이지 생성 완료: {page_url}")
            return page_url
            
        except Exception as e:
            logging.error(f"[DASHBOARD] 페이지 생성 실패: {str(e)}")
            return ""
    
    def create_header_blocks(self, current_time: datetime) -> List[Dict]:
        """헤더 블록 생성"""
        greeting_hour = current_time.hour
        if greeting_hour < 12:
            greeting = "🌅 좋은 아침입니다!"
        elif greeting_hour < 18:
            greeting = "☀️ 좋은 오후입니다!"
        else:
            greeting = "🌙 좋은 저녁입니다!"
        
        return [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": f"{greeting} 조대표님"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"오늘({current_time.strftime('%Y년 %m월 %d일')})의 핵심 정보를 정리해드렸습니다. 📋"}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
    
    def create_news_section_blocks(self, news_items: List[Dict]) -> List[Dict]:
        """중요 뉴스 섹션 블록 생성"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "📰 오늘의 중요 뉴스"}}]
                }
            }
        ]
        
        if not news_items:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "🔍 오늘 수집된 뉴스가 없습니다. 뉴스 수집 시스템을 확인해주세요."}}]
                }
            })
            return blocks
        
        # 중요도별로 그룹화
        very_important = [item for item in news_items if item['importance'] == '매우중요']
        important = [item for item in news_items if item['importance'] in ['중요', '높음']]
        normal = [item for item in news_items if item['importance'] == '보통']
        
        # 매우중요 뉴스
        if very_important:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "🔴 매우 중요"}}]
                }
            })
            
            for item in very_important:
                blocks.extend(self.create_news_item_blocks(item))
        
        # 중요 뉴스
        if important:
            blocks.append({
                "object": "block",
                "type": "heading_3", 
                "heading_3": {
                    "rich_text": [{"text": {"content": "🟠 중요"}}]
                }
            })
            
            for item in important:
                blocks.extend(self.create_news_item_blocks(item))
        
        # 일반 뉴스 (상위 3개만)
        if normal:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "🟢 일반 (주요 3건)"}}]
                }
            })
            
            for item in normal[:3]:
                blocks.extend(self.create_news_item_blocks(item))
        
        return blocks
    
    def create_news_item_blocks(self, news_item: Dict) -> List[Dict]:
        """개별 뉴스 아이템 블록 생성"""
        category_emoji = DashboardConfig.CATEGORY_ICONS.get(
            news_item['category'][0] if news_item['category'] else '', '📰'
        )
        
        title_text = f"{category_emoji} {news_item['title']}"
        
        blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {"content": title_text, "link": {"url": news_item['link']}},
                            "annotations": {"bold": True}
                        }
                    ]
                }
            }
        ]
        
        if news_item['summary']:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": f"💡 {news_item['summary']}"}}]
                }
            })
        
        return blocks
    
    def create_procurement_section_blocks(self, bid_items: List[Dict]) -> List[Dict]:
        """입찰공고 및 낙찰정보 섹션 블록 생성"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2", 
                "heading_2": {
                    "rich_text": [{"text": {"content": "💼 입찰공고 및 낙찰정보"}}]
                }
            }
        ]
        
        if not bid_items:
            blocks.extend([
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"text": {"content": "📋 오늘 새로운 입찰/낙찰 정보가 없습니다."}},
                            {"text": {"content": "\n🔍 시스템이 지속적으로 모니터링하고 있습니다."}}
                        ]
                    }
                }
            ])
            return blocks
        
        # 통계 정보
        type_counts = {}
        category_counts = {}
        
        for item in bid_items:
            bid_type = item.get('type', '관련뉴스')
            type_counts[bid_type] = type_counts.get(bid_type, 0) + 1
            
            for category in item.get('category', []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # 요약 통계
        summary_text = f"📊 총 {len(bid_items)}건 수집 | "
        summary_text += " | ".join([f"{bid_type} {count}건" for bid_type, count in type_counts.items()])
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": summary_text}}]
            }
        })
        
        # 각 입찰/낙찰 정보 블록 생성
        for item in bid_items:
            blocks.extend(self.create_bid_item_blocks(item))
        
        return blocks
    
    def create_bid_item_blocks(self, bid_item: Dict) -> List[Dict]:
        """개별 입찰/낙찰 정보 블록 생성"""
        # 유형별 이모지
        type_emojis = {
            "입찰공고": "📋",
            "낙찰결과": "🎯", 
            "계약소식": "📝",
            "관련뉴스": "📰"
        }
        
        # 중요도별 이모지
        importance_emoji = DashboardConfig.IMPORTANCE_COLORS.get(
            bid_item.get('importance', '보통'), '🟢'
        )
        
        bid_type = bid_item.get('type', '관련뉴스')
        type_emoji = type_emojis.get(bid_type, '📰')
        categories_text = ', '.join(bid_item.get('category', []))
        
        blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"{type_emoji} [{bid_type}] {bid_item.get('title', '')}"}},
                        {"text": {"content": f"\n🏢 {categories_text} | {importance_emoji} {bid_item.get('importance', '보통')} | 📅 {bid_item.get('date', '')}"}}
                    ]
                }
            }
        ]
        
        # 링크가 있는 경우
        if bid_item.get('link'):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": "🔗 "}},
                        {
                            "text": {"content": "원문 보기"},
                            "href": bid_item['link']
                        }
                    ]
                }
            })
        
        # 요약 내용이 있는 경우
        if bid_item.get('content'):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": f"💡 {bid_item['content']}"}}]
                }
            })
        
        return blocks
    
    def create_summary_section_blocks(self, news_items: List[Dict]) -> List[Dict]:
        """LLM 요약 섹션 블록 생성"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "🤖 AI 인사이트 요약"}}]
                }
            }
        ]
        
        if not news_items:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "📊 분석할 뉴스 데이터가 없습니다."}}]
                }
            })
            return blocks
        
        # 카테고리별 요약
        categories = {}
        for item in news_items:
            for cat in item['category']:
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
        
        for category, items in categories.items():
            emoji = DashboardConfig.CATEGORY_ICONS.get(category, '📰')
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"{emoji} {category}: {len(items)}건 수집"}},
                        {"text": {"content": f"\n💡 주요 트렌드: LLM 분석 기능 구현 예정"}}
                    ]
                }
            })
        
        return blocks
    
    def create_action_section_blocks(self) -> List[Dict]:
        """액션 버튼 섹션 블록 생성"""
        return [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "⚡ 빠른 액션"}}]
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"text": {"content": "📖 모든 뉴스 읽음 처리"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"text": {"content": "🔗 프로젝트 연결 검토"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"text": {"content": "⭐ 중요 뉴스 북마크"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"text": {"content": "📞 팀 공유 필요 항목 선별"}}],
                    "checked": False
                }
            }
        ]
    
    def create_footer_blocks(self) -> List[Dict]:
        """푸터 블록 생성"""
        current_time = datetime.now()
        
        return [
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"📅 생성 시간: {current_time.strftime('%Y-%m-%d %H:%M')}"}},
                        {"text": {"content": "\n🤖 GIA MVP1.0 자동화 시스템"}},
                        {"text": {"content": "\n👨‍💻 개발: 서대리 | 📋 기획: 나실장"}}
                    ]
                }
            }
        ]

def main():
    """메인 실행 함수"""
    print("📊 조대표님 전용 대시보드 생성 시작")
    print("=" * 50)
    
    dashboard = DashboardCreator()
    
    # 오늘의 뉴스 가져오기
    news_items = dashboard.get_todays_important_news()
    
    if news_items:
        print(f"✅ 오늘의 뉴스 {len(news_items)}건 로드 완료")
        
        # 카테고리별 통계
        categories = {}
        for item in news_items:
            for cat in item['category']:
                categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 카테고리별 현황:")
        for category, count in categories.items():
            emoji = DashboardConfig.CATEGORY_ICONS.get(category, '📰')
            print(f"  {emoji} {category}: {count}건")
        
    else:
        print("⚠️  오늘 수집된 뉴스가 없습니다.")
    
    # 대시보드 페이지 생성
    dashboard_url = dashboard.create_dashboard_page(news_items)
    
    if dashboard_url:
        print(f"\n🎉 대시보드 생성 완료!")
        print(f"🔗 URL: {dashboard_url}")
        print(f"\n📱 조대표님께서 모바일에서도 편리하게 확인하실 수 있습니다.")
    else:
        print("❌ 대시보드 생성 실패")

if __name__ == "__main__":
    main() 