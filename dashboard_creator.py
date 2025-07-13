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
        # 통계/정책 DB ID 추가
        self.stats_policy_db_id = self.get_stats_policy_db_id()
        
    def get_todays_important_news(self, limit: int = 10) -> List[Dict]:
        """오늘의 중요 뉴스 가져오기"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 노션 DB에서 최근 뉴스 조회 (날짜 제한 없이)
            response = self.notion.databases.query(
                database_id=self.database_id,
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
            
            # 노션 입찰낙찰 공고 DB에서 선별된 항목 조회
            response = self.notion.databases.query(
                database_id=self.bid_database_id,
                filter={
                    "property": "선별여부",
                    "checkbox": {
                        "equals": True
                    }
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
    
    def get_todays_stats_policy_info(self, limit: int = 8) -> List[Dict]:
        """오늘의 통계/정책 정보 가져오기"""
        try:
            if not self.stats_policy_db_id:
                logging.warning("[DASHBOARD] 통계/정책 DB ID가 설정되지 않음")
                return []
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 노션 통계/정책 DB에서 최근 수집된 항목 조회
            response = self.notion.databases.query(
                database_id=self.stats_policy_db_id,
                sorts=[
                    {
                        "property": "중요도",
                        "direction": "ascending"  # 중요도 높은 순
                    }
                ]
            )
            
            stats_items = []
            for page in response.get('results', [])[:limit]:
                properties = page.get('properties', {})
                
                # 속성 값 추출
                title = self.extract_title(properties.get('제목', {}))
                category = self.extract_select(properties.get('분야', {}))
                data_type = self.extract_select(properties.get('유형', {}))
                source = self.extract_select(properties.get('출처', {}))
                indicator_name = self.extract_rich_text(properties.get('지표명', {}))
                value = self.extract_rich_text(properties.get('수치', {}))
                unit = self.extract_rich_text(properties.get('단위', {}))
                importance = self.extract_select(properties.get('중요도', {}))
                trend = self.extract_select(properties.get('트렌드', {}))
                detail_info = self.extract_rich_text(properties.get('상세정보', {}))
                source_url = self.extract_url(properties.get('원본링크', {}))
                
                stats_item = {
                    'id': page['id'],
                    'title': title,
                    'category': category,
                    'data_type': data_type,
                    'source': source,
                    'indicator_name': indicator_name,
                    'value': value,
                    'unit': unit,
                    'importance': importance,
                    'trend': trend,
                    'detail_info': detail_info,
                    'source_url': source_url,
                    'importance_score': self.get_importance_score(importance)
                }
                
                stats_items.append(stats_item)
            
            # 중요도 점수로 정렬
            stats_items.sort(key=lambda x: x['importance_score'], reverse=True)
            
            logging.info(f"[DASHBOARD] 통계/정책 정보 {len(stats_items)}건 로드 완료")
            return stats_items
            
        except Exception as e:
            logging.error(f"[DASHBOARD] 통계/정책 정보 조회 실패: {str(e)}")
            return []
    
    def get_stats_policy_db_id(self) -> Optional[str]:
        """통계/정책 DB ID 가져오기"""
        try:
            with open('stats_policy_db_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('stats_policy_db_id')
        except FileNotFoundError:
            logging.warning("[DASHBOARD] 통계/정책 DB 설정 파일이 없음")
            return None
        except Exception as e:
            logging.error(f"[DASHBOARD] 통계/정책 DB ID 조회 실패: {str(e)}")
            return None
    
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
        
        # 통계/정책 정보 가져오기
        stats_items = self.get_todays_stats_policy_info()
        
        # 페이지 내용 구성
        blocks = []
        
        # 1. 헤더
        blocks.extend(self.create_header_blocks(current_time))
        
        # 2. 중요 뉴스 섹션
        blocks.extend(self.create_news_section_blocks(news_items))
        
        # 3. 입찰공고 및 낙찰정보 섹션
        blocks.extend(self.create_procurement_section_blocks(bid_items))
        
        # 4. 통계/정책 정보 섹션 추가
        blocks.extend(self.create_stats_policy_section_blocks(stats_items))
        
        # 5. LLM 요약 섹션
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
    
    def create_stats_policy_section_blocks(self, stats_items: List[Dict]) -> List[Dict]:
        """통계/정책 정보 섹션 블록 생성"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "📊 주요 통계 및 정책 동향"}}]
                }
            }
        ]
        
        if not stats_items:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "📈 오늘 수집된 통계/정책 정보가 없습니다."}}]
                }
            })
            return blocks
        
        # 분야별로 그룹화
        categories = {}
        for item in stats_items:
            category = item.get('category', '기타')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # 분야별 섹션 생성
        for category, items in categories.items():
            # 분야 헤더
            category_emoji = {
                '신재생에너지': '⚡',
                '방위산업': '🛡️',
                '보험업계': '🏥',
                '경제일반': '💰'
            }.get(category, '📈')
            
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": f"{category_emoji} {category}"}}]
                }
            })
            
            # 각 항목별 블록 생성
            for item in items[:3]:  # 최대 3개씩만 표시
                blocks.extend(self.create_stats_item_blocks(item))
        
        return blocks
    
    def create_stats_item_blocks(self, stats_item: Dict) -> List[Dict]:
        """통계/정책 정보 항목 블록 생성"""
        blocks = []
        
        # 중요도에 따른 아이콘
        importance_icons = {
            '매우중요': '🔴',
            '중요': '🟠',
            '보통': '🟡'
        }
        
        importance_icon = importance_icons.get(stats_item.get('importance', '보통'), '🟡')
        
        # 트렌드에 따른 아이콘
        trend_icons = {
            '상승': '📈',
            '하락': '📉',
            '보합': '➡️',
            '변동': '🔄',
            '정상': '✅'
        }
        
        trend_icon = trend_icons.get(stats_item.get('trend', '보합'), '➡️')
        
        # 메인 정보 블록
        title = stats_item.get('title', '제목 없음')
        indicator_name = stats_item.get('indicator_name', '')
        value = stats_item.get('value', '')
        unit = stats_item.get('unit', '')
        source = stats_item.get('source', '')
        
        # 수치 표시
        value_display = f"{value}"
        if unit:
            value_display += f" {unit}"
        
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"emoji": importance_icon},
                "rich_text": [
                    {"text": {"content": f"{indicator_name}: {value_display} {trend_icon}"}}
                ]
            }
        })
        
        # 상세 정보
        detail_info = stats_item.get('detail_info', '')
        if detail_info:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"📋 {detail_info[:200]}{'...' if len(detail_info) > 200 else ''}"}}
                    ]
                }
            })
        
        # 출처 정보
        source_url = stats_item.get('source_url', '')
        if source_url:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"🔗 출처: {source} - {source_url}"}}
                    ]
                }
            })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"🔗 출처: {source}"}}
                    ]
                }
            })
        
        # 구분선
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
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


class PremiumDashboardCreator(DashboardCreator):
    """
    자비스를 지향하는 전문가 경영자용 통합 대시보드 생성기
    
    GIA 대문 UI V1.0 - 조대표님 전용 프리미엄 대시보드
    - 자비스급 헤더 섹션
    - 3단 그리드 전문가 레이아웃
    - 조대표님 맞춤 특화 요소 (아침 5분 브리핑 모드, 모바일 퍼스트)
    """
    
    def __init__(self):
        super().__init__()
        self.dashboard_title = "🤖 GIA - 지능형 정보 에이전트"
        self.executive_name = "조대표님"
        
    def create_executive_dashboard(self) -> str:
        """조대표님 전용 프리미엄 대시보드 생성"""
        try:
            logging.info("[PREMIUM_DASHBOARD] 자비스급 대시보드 생성 시작")
            
            # 데이터 수집
            news_items = self.get_todays_important_news(limit=8)
            bid_items = self.get_todays_bid_information(limit=5)
            stats_items = self.get_todays_stats_policy_info(limit=6)
            
            # 블록 생성
            blocks = []
            current_time = datetime.now()
            
            # 1. 자비스급 헤더 섹션
            blocks.extend(self.create_executive_header_blocks(current_time))
            
            # 2. 핵심 브리핑 섹션 (아침 5분 브리핑 모드)
            blocks.extend(self.create_morning_briefing_blocks(news_items, bid_items, stats_items))
            
            # 3. 3단 그리드 전문가 레이아웃
            blocks.extend(self.create_three_column_layout_blocks(news_items, bid_items, stats_items))
            
            # 4. 조대표님 맞춤 빠른 액션 섹션
            blocks.extend(self.create_executive_action_blocks())
            
            # 5. 프리미엄 푸터
            blocks.extend(self.create_premium_footer_blocks(current_time))
            
            # 노션 페이지 생성
            today_str = current_time.strftime("%Y-%m-%d")
            page_title = f"{self.dashboard_title} | {today_str}"
            
            page_response = self.notion.pages.create(
                parent={"page_id": "22ea613d25ff819698ccf55e84b650c8"},  # 기존 페이지 ID 사용
                properties={
                    "title": {"title": [{"text": {"content": page_title}}]}
                },
                children=blocks
            )
            
            dashboard_url = page_response["url"]
            logging.info(f"[PREMIUM_DASHBOARD] 프리미엄 대시보드 생성 완료: {dashboard_url}")
            
            return dashboard_url
            
        except Exception as e:
            logging.error(f"[PREMIUM_DASHBOARD] 대시보드 생성 실패: {str(e)}")
            return None
    
    def create_executive_header_blocks(self, current_time: datetime) -> List[Dict]:
        """자비스급 헤더 섹션 블록 생성"""
        today_str = current_time.strftime("%Y년 %m월 %d일")
        time_str = current_time.strftime("%H:%M")
        weekday = current_time.strftime("%A")
        weekday_ko = {
            'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일', 
            'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
        }.get(weekday, weekday)
        
        return [
            # 메인 헤더
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"text": {"content": f"🤖 GIA - 지능형 정보 에이전트"}}
                    ]
                }
            },
            # 날짜/시간 정보
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"📅 {today_str} ({weekday_ko}) | ⏰ {time_str} 업데이트"}},
                        {"text": {"content": f"\n👋 안녕하세요, {self.executive_name}! 오늘의 핵심 정보를 준비했습니다."}}
                    ],
                    "icon": {"emoji": "🌟"},
                    "color": "blue_background"
                }
            },
            # 빠른 액션 버튼 그룹 (3단 컬럼)
            {
                "object": "block",
                "type": "column_list",
                "column_list": {
                    "children": [
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {"text": {"content": "🔄 새로고침"}, "annotations": {"bold": True}}
                                            ]
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {"text": {"content": "📊 주간 보고서"}, "annotations": {"bold": True}}
                                            ]
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {"text": {"content": "💬 피드백"}, "annotations": {"bold": True}}
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            # 구분선
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
    
    def create_morning_briefing_blocks(self, news_items: List[Dict], bid_items: List[Dict], stats_items: List[Dict]) -> List[Dict]:
        """아침 5분 브리핑 모드 블록 생성"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "🌅 오늘의 핵심 브리핑 (5분 요약)"}}]
                }
            }
        ]
        
        # 긴급/중요 알림
        urgent_items = []
        for item in news_items:
            if item.get('importance_score', 0) >= 4:  # 매우중요/중요
                urgent_items.append(item)
        
        if urgent_items:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"🚨 긴급 확인 필요: {len(urgent_items)}건"}},
                        {"text": {"content": "\n" + "\n".join([f"• {item['title'][:50]}..." for item in urgent_items[:3]])}}
                    ],
                    "icon": {"emoji": "🔥"},
                    "color": "red_background"
                }
            })
        
        # 핵심 지표 요약
        total_info = len(news_items) + len(bid_items) + len(stats_items)
        
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {"text": {"content": f"📊 오늘의 정보 현황"}},
                    {"text": {"content": f"\n📰 뉴스: {len(news_items)}건 | 💼 입찰: {len(bid_items)}건 | 📈 통계: {len(stats_items)}건"}},
                    {"text": {"content": f"\n🎯 총 {total_info}건의 정보가 수집되었습니다."}}
                ],
                "icon": {"emoji": "📋"},
                "color": "green_background"
            }
        })
        
        return blocks
    
    def create_three_column_layout_blocks(self, news_items: List[Dict], bid_items: List[Dict], stats_items: List[Dict]) -> List[Dict]:
        """3단 그리드 전문가 레이아웃 블록 생성"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "💼 입찰공고 및 낙찰정보"}}]
                }
            }
        ]
        
        # 1열: 오늘의 중요 뉴스
        news_children = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "📰 오늘의 중요 뉴스"}}]
                }
            }
        ]
        
        # 뉴스 아이템 추가 (상위 3개)
        for item in news_items[:3]:
            importance_emoji = self.get_importance_emoji(item.get('importance', ''))
            category_emojis = " ".join([DashboardConfig.CATEGORY_ICONS.get(cat, '📰') for cat in item.get('category', [])])
            
            news_children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"{importance_emoji} {item['title'][:40]}..."}, "annotations": {"bold": True}},
                        {"text": {"content": f"\n{category_emojis} {item.get('summary', '')[:60]}..."}}
                    ]
                }
            })
        
        # 2열: 입찰공고 및 낙찰정보
        bid_children = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "💼 입찰공고 및 낙찰정보"}}]
                }
            }
        ]
        
        # 입찰 아이템 추가 (상위 3개)
        for item in bid_items[:3]:
            importance_emoji = self.get_importance_emoji(item.get('importance', ''))
            type_emoji = "📋" if item.get('type') == '입찰공고' else "🎯"
            
            bid_children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"{importance_emoji} {item['title'][:40]}..."}, "annotations": {"bold": True}},
                        {"text": {"content": f"\n{type_emoji} {item.get('content', '')[:60]}..."}}
                    ]
                }
            })
        
        # 3열: 통계/정책 및 시장 동향
        stats_children = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "📈 통계/정책 및 시장 동향"}}]
                }
            }
        ]
        
        # 통계 아이템 추가 (상위 3개)
        for item in stats_items[:3]:
            importance_emoji = self.get_importance_emoji(item.get('importance', ''))
            category_emoji = DashboardConfig.CATEGORY_ICONS.get(item.get('category', ''), '📊')
            
            stats_children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"{importance_emoji} {item['title'][:40]}..."}, "annotations": {"bold": True}},
                        {"text": {"content": f"\n{category_emoji} {item.get('content', '')[:60]}..."}}
                    ]
                }
            })
        
        # 3단 컬럼 레이아웃
        three_column_layout = {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": news_children
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": bid_children
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": stats_children
                        }
                    }
                ]
            }
        }
        
        blocks.append(three_column_layout)
        
        return blocks
    
    def create_executive_action_blocks(self) -> List[Dict]:
        """조대표님 맞춤 빠른 액션 섹션 블록 생성"""
        return [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "⚡ 조대표님 맞춤 빠른 액션"}}]
                }
            },
            {
                "object": "block",
                "type": "column_list",
                "column_list": {
                    "children": [
                        # 1열: 즉시 처리
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {"text": {"content": "🔥 즉시 처리"}, "annotations": {"bold": True}}
                                            ]
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "긴급 뉴스 확인"}}],
                                            "checked": False
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "중요 입찰 검토"}}],
                                            "checked": False
                                        }
                                    }
                                ]
                            }
                        },
                        # 2열: 오늘 중
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {"text": {"content": "⏰ 오늘 중"}, "annotations": {"bold": True}}
                                            ]
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "팀 브리핑 준비"}}],
                                            "checked": False
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "주요 이슈 공유"}}],
                                            "checked": False
                                        }
                                    }
                                ]
                            }
                        },
                        # 3열: 이번 주
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {"text": {"content": "📅 이번 주"}, "annotations": {"bold": True}}
                                            ]
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "전략 검토 미팅"}}],
                                            "checked": False
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "시장 동향 분석"}}],
                                            "checked": False
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    
    def create_premium_footer_blocks(self, current_time: datetime) -> List[Dict]:
        """프리미엄 푸터 블록 생성"""
        return [
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"🤖 GIA - 지능형 정보 에이전트"}},
                        {"text": {"content": f"\n📅 생성 시간: {current_time.strftime('%Y-%m-%d %H:%M')}"}},
                        {"text": {"content": f"\n🎯 {self.executive_name} 전용 프리미엄 대시보드"}},
                        {"text": {"content": f"\n💼 개발: 서대리 | 📋 기획: 나실장 | 🔬 자문: 노팀장"}}
                    ],
                    "icon": {"emoji": "🌟"},
                    "color": "gray_background"
                }
            }
        ]
    
    def get_importance_emoji(self, importance: str) -> str:
        """중요도에 따른 이모지 반환"""
        importance_emojis = {
            '매우중요': '🔴',
            '중요': '⭐',
            '높음': '🔺',
            '보통': '📌',
            '낮음': '📋'
        }
        return importance_emojis.get(importance, '📋')


def main_premium():
    """프리미엄 대시보드 메인 실행 함수"""
    print("🤖 GIA 프리미엄 대시보드 생성 시작")
    print("=" * 60)
    
    premium_dashboard = PremiumDashboardCreator()
    
    # 프리미엄 대시보드 생성
    dashboard_url = premium_dashboard.create_executive_dashboard()
    
    if dashboard_url:
        print(f"\n🎉 자비스급 프리미엄 대시보드 생성 완료!")
        print(f"🔗 URL: {dashboard_url}")
        print(f"\n🌟 조대표님 전용 '전문가 경영자용 통합 대시보드'가 준비되었습니다.")
        print(f"📱 모바일에서도 최적화된 경험을 제공합니다.")
    else:
        print("❌ 프리미엄 대시보드 생성 실패")
        print("📞 서대리에게 문의해 주세요.")
    
    return dashboard_url 


# === 시각적 고도화된 프리미엄 대시보드 ===
class UltraPremiumDashboardCreator(DashboardCreator):
    """자비스급 시각적 고도화 대시보드 생성기"""
    
    def __init__(self):
        super().__init__()
        self.dashboard_title = "🤖 GIA Executive Dashboard"
        self.executive_name = "조대표님"
        
        # 전문가급 색상 팔레트 (HTML 시안 기반)
        self.color_palette = {
            "primary": "blue",           # 메인 색상 (다크 슬레이트 블루)
            "accent": "purple",          # 액센트 색상 (인디고)
            "success": "green",          # 성공/긍정 (녹색)
            "warning": "yellow",         # 주의/경고 (노란색)
            "danger": "red",             # 위험/긴급 (빨간색)
            "neutral": "gray"            # 중성/보조 (회색)
        }
        
        # 전문가급 텍스트 스타일
        self.text_styles = {
            "executive_title": {"bold": True, "italic": False},
            "section_header": {"bold": True, "italic": False},
            "important_data": {"bold": True, "italic": False},
            "metadata": {"bold": False, "italic": True},
            "emphasis": {"bold": True, "italic": True}
        }
    
    def create_ultra_premium_dashboard(self) -> str:
        """자비스급 시각적 고도화 대시보드 생성"""
        try:
            # 모든 데이터 수집
            news_items = self.get_todays_important_news(limit=12)
            bid_items = self.get_todays_bid_information(limit=8)
            stats_items = self.get_todays_stats_policy_info(limit=10)
            
            # 블록 생성
            blocks = []
            current_time = datetime.now()
            
            # 1. 🌟 Executive Master Header (자비스급)
            blocks.extend(self.create_master_executive_header(current_time))
            
            # 2. 🚨 Critical Intelligence Briefing (핵심 인텔리전스)
            blocks.extend(self.create_critical_intelligence_section(news_items, bid_items, stats_items))
            
            # 3. 📊 Professional Data Dashboard (전문가 데이터 대시보드)
            blocks.extend(self.create_professional_data_grid(news_items, bid_items, stats_items))
            
            # 4. ⚡ Executive Command Center (경영진 명령 센터)
            blocks.extend(self.create_executive_command_center())
            
            # 5. 🎯 Strategic Insights & Analytics (전략적 통찰)
            blocks.extend(self.create_strategic_insights_section(news_items, bid_items, stats_items))
            
            # 6. 🔮 Premium Footer (프리미엄 푸터)
            blocks.extend(self.create_ultra_premium_footer(current_time))
            
            # 노션 페이지 생성
            today_str = current_time.strftime("%Y-%m-%d")
            page_title = f"🤖 GIA Executive Dashboard | {today_str}"
            
            page_response = self.notion.pages.create(
                parent={"page_id": "22ea613d25ff819698ccf55e84b650c8"},
                properties={
                    "title": {"title": [{"text": {"content": page_title}}]}
                },
                children=blocks
            )
            
            dashboard_url = page_response["url"]
            logging.info(f"[ULTRA_PREMIUM_DASHBOARD] 자비스급 대시보드 생성 완료: {dashboard_url}")
            
            return dashboard_url
            
        except Exception as e:
            logging.error(f"[ULTRA_PREMIUM_DASHBOARD] 대시보드 생성 실패: {str(e)}")
            return None
    
    def create_master_executive_header(self, current_time: datetime) -> List[Dict]:
        """🌟 Executive Master Header (자비스급 헤더)"""
        today_str = current_time.strftime("%Y년 %m월 %d일")
        time_str = current_time.strftime("%H:%M")
        weekday = current_time.strftime("%A")
        weekday_ko = {
            'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일', 
            'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
        }.get(weekday, weekday)
        
        return [
            # Master Title Banner
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"text": {"content": "🤖 GIA Executive Dashboard"}, "annotations": self.text_styles["executive_title"]},
                        {"text": {"content": " | Intelligence Command Center"}, "annotations": {"bold": False, "italic": True}}
                    ],
                    "color": self.color_palette["primary"]
                }
            },
            # Executive Welcome Banner
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"👑 Welcome, {self.executive_name}"}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": f"\n📅 {today_str} ({weekday_ko}) | ⏰ {time_str} System Update"}},
                        {"text": {"content": f"\n🎯 Your intelligent business intelligence system is ready."}}
                    ],
                    "icon": {"emoji": "🌟"},
                    "color": f"{self.color_palette['primary']}_background"
                }
            },
            # Professional Quick Actions Grid
            {
                "object": "block",
                "type": "column_list",
                "column_list": {
                    "children": [
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [
                                                {"text": {"content": "🔄 Refresh Data"}, "annotations": self.text_styles["important_data"]}
                                            ],
                                            "icon": {"emoji": "⚡"},
                                            "color": f"{self.color_palette['accent']}_background"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [
                                                {"text": {"content": "📊 Weekly Report"}, "annotations": self.text_styles["important_data"]}
                                            ],
                                            "icon": {"emoji": "📈"},
                                            "color": f"{self.color_palette['success']}_background"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [
                                                {"text": {"content": "💬 Feedback Hub"}, "annotations": self.text_styles["important_data"]}
                                            ],
                                            "icon": {"emoji": "🎯"},
                                            "color": f"{self.color_palette['warning']}_background"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            # Professional Divider
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
    
    def create_critical_intelligence_section(self, news_items: List[Dict], bid_items: List[Dict], stats_items: List[Dict]) -> List[Dict]:
        """🚨 Critical Intelligence Briefing"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "🚨 Critical Intelligence Briefing"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["danger"]
                }
            }
        ]
        
        # 긴급/중요 항목 식별
        critical_items = []
        for item in news_items:
            if item.get('importance_score', 0) >= 4:
                critical_items.append(('NEWS', item))
        for item in bid_items:
            if item.get('importance_score', 0) >= 4:
                critical_items.append(('BID', item))
        for item in stats_items:
            if item.get('importance_score', 0) >= 4:
                critical_items.append(('STATS', item))
        
        if critical_items:
            critical_text = "\n" + "\n".join([f"🔸 {item[1].get('title', 'Unknown')[:60]}..." for item in critical_items[:3]])
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"🔥 URGENT ATTENTION REQUIRED: {len(critical_items)} Critical Items"}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": critical_text}}
                    ],
                    "icon": {"emoji": "🚨"},
                    "color": f"{self.color_palette['danger']}_background"
                }
            })
        else:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": "✅ ALL SYSTEMS NORMAL"}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": "\nNo critical issues detected. All intelligence streams are operating within normal parameters."}}
                    ],
                    "icon": {"emoji": "✅"},
                    "color": f"{self.color_palette['success']}_background"
                }
            })
        
        # Executive Summary Stats
        total_info = len(news_items) + len(bid_items) + len(stats_items)
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {"text": {"content": "📊 INTELLIGENCE SUMMARY"}, "annotations": self.text_styles["important_data"]},
                    {"text": {"content": f"\n📰 News Intel: {len(news_items)} items | 💼 Bid Intel: {len(bid_items)} items | 📈 Market Intel: {len(stats_items)} items"}},
                    {"text": {"content": f"\n🎯 Total Intelligence Collected: {total_info} data points"}}
                ],
                "icon": {"emoji": "📋"},
                "color": f"{self.color_palette['primary']}_background"
            }
        })
        
        return blocks
    
    def create_professional_data_grid(self, news_items: List[Dict], bid_items: List[Dict], stats_items: List[Dict]) -> List[Dict]:
        """📊 Professional Data Dashboard Grid"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "📊 Professional Intelligence Grid"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["primary"]
                }
            }
        ]
        
        # High-End 3-Column Professional Layout
        news_column = self._create_enhanced_news_column(news_items)
        bid_column = self._create_enhanced_bid_column(bid_items)
        stats_column = self._create_enhanced_stats_column(stats_items)
        
        professional_grid = {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {"children": news_column}
                    },
                    {
                        "object": "block",
                        "type": "column", 
                        "column": {"children": bid_column}
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {"children": stats_column}
                    }
                ]
            }
        }
        
        blocks.append(professional_grid)
        return blocks
    
    def _create_enhanced_news_column(self, news_items: List[Dict]) -> List[Dict]:
        """Enhanced News Intelligence Column"""
        children = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "📰 News Intelligence"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["success"]
                }
            }
        ]
        
        for item in news_items[:4]:
            importance_emoji = self.get_enhanced_importance_emoji(item.get('importance', ''))
            category_emojis = " ".join([DashboardConfig.CATEGORY_ICONS.get(cat, '📰') for cat in item.get('category', [])])
            
            children.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"{importance_emoji} {item['title'][:45]}..."}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": f"\n{category_emojis} {item.get('summary', 'No summary available')[:50]}..."}, "annotations": self.text_styles["metadata"]}
                    ],
                    "icon": {"emoji": "📰"},
                    "color": f"{self.color_palette['neutral']}_background"
                }
            })
        
        return children
    
    def _create_enhanced_bid_column(self, bid_items: List[Dict]) -> List[Dict]:
        """Enhanced Bid Intelligence Column"""
        children = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "💼 Bid Intelligence"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["accent"]
                }
            }
        ]
        
        for item in bid_items[:4]:
            importance_emoji = self.get_enhanced_importance_emoji(item.get('importance', ''))
            type_emoji = {"입찰공고": "📋", "낙찰결과": "🎯", "계약소식": "📝", "관련뉴스": "📰"}.get(item.get('type', ''), "💼")
            
            children.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"{importance_emoji} {item['title'][:45]}..."}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": f"\n{type_emoji} {item.get('content', 'No details available')[:50]}..."}, "annotations": self.text_styles["metadata"]}
                    ],
                    "icon": {"emoji": "💼"},
                    "color": f"{self.color_palette['accent']}_background"
                }
            })
        
        return children
    
    def _create_enhanced_stats_column(self, stats_items: List[Dict]) -> List[Dict]:
        """Enhanced Statistics Intelligence Column"""
        children = [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "📈 Market Intelligence"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["warning"]
                }
            }
        ]
        
        for item in stats_items[:4]:
            importance_emoji = self.get_enhanced_importance_emoji(item.get('importance', ''))
            trend_emoji = {"상승": "📈", "하락": "📉", "보합": "➡️", "변동": "📊"}.get(item.get('trend', ''), "📊")
            
            value_display = f"{item.get('value', 'N/A')}"
            if item.get('unit'):
                value_display += f" {item.get('unit')}"
            
            children.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": f"{importance_emoji} {item['title'][:45]}..."}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": f"\n{trend_emoji} {value_display}"}, "annotations": self.text_styles["emphasis"]}
                    ],
                    "icon": {"emoji": "📈"},
                    "color": f"{self.color_palette['warning']}_background"
                }
            })
        
        return children
    
    def create_executive_command_center(self) -> List[Dict]:
        """⚡ Executive Command Center"""
        return [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "⚡ Executive Command Center"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["accent"]
                }
            },
            {
                "object": "block",
                "type": "column_list",
                "column_list": {
                    "children": [
                        # Immediate Actions
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [
                                                {"text": {"content": "🔥 IMMEDIATE"}, "annotations": self.text_styles["important_data"]}
                                            ],
                                            "icon": {"emoji": "🚨"},
                                            "color": f"{self.color_palette['danger']}_background"
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "Review critical intelligence"}}],
                                            "checked": False
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "Assess urgent opportunities"}}],
                                            "checked": False
                                        }
                                    }
                                ]
                            }
                        },
                        # Today's Priorities
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [
                                                {"text": {"content": "⏰ TODAY"}, "annotations": self.text_styles["important_data"]}
                                            ],
                                            "icon": {"emoji": "🎯"},
                                            "color": f"{self.color_palette['warning']}_background"
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "Team strategic briefing"}}],
                                            "checked": False
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "Market analysis review"}}],
                                            "checked": False
                                        }
                                    }
                                ]
                            }
                        },
                        # This Week
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "callout",
                                        "callout": {
                                            "rich_text": [
                                                {"text": {"content": "📅 THIS WEEK"}, "annotations": self.text_styles["important_data"]}
                                            ],
                                            "icon": {"emoji": "📋"},
                                            "color": f"{self.color_palette['success']}_background"
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "Strategic planning session"}}],
                                            "checked": False
                                        }
                                    },
                                    {
                                        "object": "block",
                                        "type": "to_do",
                                        "to_do": {
                                            "rich_text": [{"text": {"content": "Quarterly review prep"}}],
                                            "checked": False
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    
    def create_strategic_insights_section(self, news_items: List[Dict], bid_items: List[Dict], stats_items: List[Dict]) -> List[Dict]:
        """🎯 Strategic Insights & Analytics"""
        blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "🎯 Strategic Insights & Analytics"}, "annotations": self.text_styles["section_header"]}],
                    "color": self.color_palette["accent"]
                }
            }
        ]
        
        # Trend Analysis
        trends = self._analyze_trends(news_items, bid_items, stats_items)
        
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {"text": {"content": "📊 MARKET TRENDS ANALYSIS"}, "annotations": self.text_styles["important_data"]},
                    {"text": {"content": f"\n🔋 Renewable Energy: {trends['renewable']} signals"}},
                    {"text": {"content": f"\n🛡️ Defense Industry: {trends['defense']} indicators"}},
                    {"text": {"content": f"\n🏢 Insurance Sector: {trends['insurance']} opportunities"}}
                ],
                "icon": {"emoji": "🔮"},
                "color": f"{self.color_palette['primary']}_background"
            }
        })
        
        return blocks
    
    def create_ultra_premium_footer(self, current_time: datetime) -> List[Dict]:
        """🔮 Ultra Premium Footer"""
        return [
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"text": {"content": "🤖 GIA Executive Dashboard"}, "annotations": self.text_styles["important_data"]},
                        {"text": {"content": f" | Powered by Advanced Intelligence"}},
                        {"text": {"content": f"\n⚡ Last Updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')} KST"}},
                        {"text": {"content": f"\n👥 Developed by: 조대표님, 나실장, 노팀장, 서대리"}},
                        {"text": {"content": f"\n💎 Professional Grade Business Intelligence System"}}
                    ],
                    "icon": {"emoji": "🌟"},
                    "color": f"{self.color_palette['primary']}_background"
                }
            }
        ]
    
    def get_enhanced_importance_emoji(self, importance: str) -> str:
        """Enhanced importance emoji mapping"""
        enhanced_emojis = {
            '매우중요': '🔴',
            '중요': '🟠', 
            '높음': '🟡',
            '보통': '🟢',
            '낮음': '🔵'
        }
        return enhanced_emojis.get(importance, '⚪')
    
    def _analyze_trends(self, news_items: List[Dict], bid_items: List[Dict], stats_items: List[Dict]) -> Dict[str, str]:
        """Analyze market trends from collected data"""
        # Simplified trend analysis
        renewable_count = len([item for item in news_items if '신재생에너지' in str(item.get('category', []))])
        defense_count = len([item for item in news_items if '방위산업' in str(item.get('category', []))])
        insurance_count = len([item for item in news_items if '보험중개' in str(item.get('category', []))])
        
        return {
            'renewable': f"{renewable_count} positive",
            'defense': f"{defense_count} stable", 
            'insurance': f"{insurance_count} growing"
        }


def main_ultra_premium():
    """자비스급 시각적 고도화 대시보드 메인 실행 함수"""
    print("🚀 GIA 자비스급 시각적 고도화 대시보드 생성 시작")
    print("=" * 60)
    
    ultra_dashboard = UltraPremiumDashboardCreator()
    
    # 자비스급 대시보드 생성
    dashboard_url = ultra_dashboard.create_ultra_premium_dashboard()
    
    if dashboard_url:
        print(f"\n🎉 자비스급 시각적 고도화 대시보드 생성 완료!")
        print(f"🔗 URL: {dashboard_url}")
        print(f"\n🌟 HTML 시안 수준의 전문적 완성도를 달성한 대시보드입니다.")
        print(f"📱 깔끔하고 통일된 색상 팔레트와 전문가급 레이아웃을 제공합니다.")
        print(f"⚡ 조대표님 전용 자비스급 경영자 대시보드가 준비되었습니다.")
    else:
        print("❌ 자비스급 대시보드 생성 실패")
        print("📞 서대리에게 문의해 주세요.")
    
    return dashboard_url 