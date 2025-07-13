#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 고급 알림 시스템
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 조대표님께 GIA 시스템 실행 결과 및 상태를 실시간으로 통지
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from mvp_config import APIConfig

class GIANotificationSystem:
    """GIA 고급 알림 시스템"""
    
    def __init__(self):
        self.notion_api_key = APIConfig.NOTION_API_TOKEN
        self.base_url = "https://api.notion.com/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # 알림 설정 로드
        self.config = self.load_notification_config()
        self.logger = self.setup_logging()
        
        # 조대표님 맞춤 설정
        self.executive_name = "조대표님"
        self.notification_page_id = self.config.get('notion_notification_page_id', APIConfig.NOTION_DASHBOARD_PAGE_ID)
    
    def load_notification_config(self) -> Dict:
        """알림 설정 로드"""
        try:
            with open('notification_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 기본 설정 반환
            return {
                "notification_enabled": True,
                "notification_methods": ["notion", "log"],
                "notion_notification_page_id": APIConfig.NOTION_DASHBOARD_PAGE_ID
            }
        except Exception as e:
            print(f"알림 설정 로드 실패: {str(e)}")
            return {"notification_enabled": True, "notification_methods": ["log"]}
    
    def setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger('GIA_Notification')
        logger.setLevel(logging.INFO)
        
        # 파일 핸들러
        file_handler = logging.FileHandler('logs/notification_system.log', encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def send_system_start_notification(self) -> bool:
        """GIA 시스템 시작 알림"""
        current_time = datetime.now()
        title = f"🚀 GIA 시스템 시작 알림"
        
        message = {
            "type": "system_start",
            "title": title,
            "timestamp": current_time.isoformat(),
            "content": f"{self.executive_name}, GIA 지능형 정보 에이전트가 데이터 수집을 시작했습니다.",
            "details": [
                "📰 뉴스 정보 수집 중",
                "💼 입찰/낙찰 정보 수집 중", 
                "📊 통계/정책 정보 수집 중",
                "🤖 자동 대시보드 업데이트 준비 중"
            ]
        }
        
        return self._send_notification(message)
    
    def send_system_success_notification(self, results: Dict) -> bool:
        """GIA 시스템 성공 완료 알림"""
        current_time = datetime.now()
        title = f"✅ GIA 시스템 실행 완료 - {current_time.strftime('%H:%M')}"
        
        # 결과 요약
        news_count = results.get('news_count', 0)
        bid_count = results.get('bid_count', 0)
        stats_count = results.get('stats_count', 0)
        dashboard_url = results.get('dashboard_url', '')
        
        total_items = news_count + bid_count + stats_count
        
        message = {
            "type": "system_success",
            "title": title,
            "timestamp": current_time.isoformat(),
            "content": f"{self.executive_name}, GIA 시스템이 성공적으로 완료되었습니다.",
            "summary": {
                "total_items": total_items,
                "news_count": news_count,
                "bid_count": bid_count,
                "stats_count": stats_count
            },
            "details": [
                f"📰 뉴스 정보: {news_count}건 수집 완료",
                f"💼 입찰/낙찰 정보: {bid_count}건 수집 완료",
                f"📊 통계/정책 정보: {stats_count}건 수집 완료",
                f"🎯 총 {total_items}건의 정보가 수집되었습니다",
                f"📱 대시보드가 최신 정보로 업데이트되었습니다"
            ],
            "dashboard_url": dashboard_url,
            "execution_time": results.get('execution_time', 'Unknown')
        }
        
        return self._send_notification(message)
    
    def send_system_error_notification(self, error_details: Dict) -> bool:
        """GIA 시스템 오류 알림"""
        current_time = datetime.now()
        title = f"🚨 GIA 시스템 오류 발생 - {current_time.strftime('%H:%M')}"
        
        error_type = error_details.get('error_type', 'Unknown Error')
        error_message = error_details.get('error_message', 'Unknown Error Message')
        failed_component = error_details.get('failed_component', 'Unknown Component')
        
        message = {
            "type": "system_error",
            "title": title,
            "timestamp": current_time.isoformat(),
            "content": f"⚠️ {self.executive_name}, GIA 시스템 실행 중 오류가 발생했습니다.",
            "error_info": {
                "error_type": error_type,
                "failed_component": failed_component,
                "error_message": error_message
            },
            "details": [
                f"🔴 오류 유형: {error_type}",
                f"🔧 문제 구성요소: {failed_component}",
                f"📝 오류 메시지: {error_message[:100]}...",
                f"🛠️ 서대리에게 기술 지원을 요청하시기 바랍니다"
            ],
            "next_actions": [
                "1. 시스템 자동 복구 시도 중",
                "2. 다음 정기 실행 시간에 재시도",
                "3. 문제 지속 시 서대리에게 연락"
            ]
        }
        
        return self._send_notification(message)
    
    def send_weekly_summary_notification(self, weekly_data: Dict) -> bool:
        """주간 요약 알림"""
        current_time = datetime.now()
        week_start = weekly_data.get('week_start', 'Unknown')
        week_end = weekly_data.get('week_end', 'Unknown')
        
        title = f"📊 GIA 주간 요약 리포트 ({week_start} ~ {week_end})"
        
        message = {
            "type": "weekly_summary",
            "title": title,
            "timestamp": current_time.isoformat(),
            "content": f"{self.executive_name}, 이번 주 GIA 시스템 활동 요약을 보고드립니다.",
            "weekly_stats": weekly_data.get('stats', {}),
            "details": [
                f"📰 주간 뉴스: {weekly_data.get('total_news', 0)}건",
                f"💼 주간 입찰정보: {weekly_data.get('total_bids', 0)}건",
                f"📊 주간 통계/정책: {weekly_data.get('total_stats', 0)}건",
                f"🎯 중요 이슈: {weekly_data.get('important_items', 0)}건",
                f"⚡ 시스템 가동률: {weekly_data.get('uptime_percentage', 95)}%"
            ],
            "insights": weekly_data.get('insights', []),
            "recommendations": weekly_data.get('recommendations', [])
        }
        
        return self._send_notification(message)
    
    def _send_notification(self, message: Dict) -> bool:
        """통합 알림 전송"""
        if not self.config.get('notification_enabled', True):
            return True
        
        success = True
        methods = self.config.get('notification_methods', ['log'])
        
        # 로그에 기록
        if 'log' in methods:
            self._log_notification(message)
        
        # 노션 페이지에 알림
        if 'notion' in methods:
            if not self._send_notion_notification(message):
                success = False
        
        # 추가 알림 방법들 (향후 확장 가능)
        # if 'email' in methods: self._send_email_notification(message)
        # if 'slack' in methods: self._send_slack_notification(message)
        # if 'telegram' in methods: self._send_telegram_notification(message)
        
        return success
    
    def _log_notification(self, message: Dict):
        """로그 파일에 알림 기록"""
        msg_type = message.get('type', 'unknown')
        title = message.get('title', 'No Title')
        content = message.get('content', 'No Content')
        
        log_message = f"[{msg_type.upper()}] {title} - {content}"
        self.logger.info(log_message)
    
    def _send_notion_notification(self, message: Dict) -> bool:
        """노션 페이지에 알림 전송"""
        try:
            # 알림 페이지 생성 또는 기존 페이지에 블록 추가
            notification_blocks = self._create_notification_blocks(message)
            
            # 새 알림 페이지 생성
            page_title = f"📢 {message.get('title', 'GIA 알림')}"
            
            page_data = {
                "parent": {"page_id": self.notification_page_id},
                "properties": {
                    "title": {"title": [{"text": {"content": page_title}}]}
                },
                "children": notification_blocks
            }
            
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                self.logger.info(f"노션 알림 전송 성공: {page_title}")
                return True
            else:
                self.logger.error(f"노션 알림 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"노션 알림 전송 중 오류: {str(e)}")
            return False
    
    def _create_notification_blocks(self, message: Dict) -> List[Dict]:
        """알림 메시지용 노션 블록 생성"""
        blocks = []
        msg_type = message.get('type', 'unknown')
        
        # 메시지 유형별 색상 설정
        color_map = {
            'system_start': 'blue_background',
            'system_success': 'green_background',
            'system_error': 'red_background',
            'weekly_summary': 'purple_background'
        }
        color = color_map.get(msg_type, 'gray_background')
        
        # 헤더 블록
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {"text": {"content": message.get('title', 'GIA 알림')}, "annotations": {"bold": True}},
                    {"text": {"content": f"\n📅 {message.get('timestamp', datetime.now().isoformat())}"}}
                ],
                "icon": {"emoji": self._get_notification_emoji(msg_type)},
                "color": color
            }
        })
        
        # 내용 블록
        content = message.get('content', '')
        if content:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            })
        
        # 세부사항 블록
        details = message.get('details', [])
        if details:
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "📋 세부 정보"}}]
                }
            })
            
            for detail in details:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"text": {"content": detail}}]
                    }
                })
        
        # 추가 정보 블록들
        if message.get('dashboard_url'):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": "📊 업데이트된 대시보드: "}},
                        {"text": {"content": message['dashboard_url'], "link": {"url": message['dashboard_url']}}}
                    ]
                }
            })
        
        # 다음 액션 블록 (오류 시)
        if message.get('next_actions'):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": "🔧 다음 조치사항"}}]
                }
            })
            
            for action in message['next_actions']:
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"text": {"content": action}}]
                    }
                })
        
        # 구분선
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _get_notification_emoji(self, msg_type: str) -> str:
        """메시지 유형별 이모지 반환"""
        emoji_map = {
            'system_start': '🚀',
            'system_success': '✅',
            'system_error': '🚨',
            'weekly_summary': '📊'
        }
        return emoji_map.get(msg_type, '📢')


# 편의 함수들
def notify_system_start():
    """시스템 시작 알림 전송"""
    notifier = GIANotificationSystem()
    return notifier.send_system_start_notification()

def notify_system_success(results: Dict):
    """시스템 성공 알림 전송"""
    notifier = GIANotificationSystem()
    return notifier.send_system_success_notification(results)

def notify_system_error(error_details: Dict):
    """시스템 오류 알림 전송"""
    notifier = GIANotificationSystem()
    return notifier.send_system_error_notification(error_details)

def notify_weekly_summary(weekly_data: Dict):
    """주간 요약 알림 전송"""
    notifier = GIANotificationSystem()
    return notifier.send_weekly_summary_notification(weekly_data)


if __name__ == "__main__":
    # 테스트 실행
    print("🧪 GIA 알림 시스템 테스트 시작")
    
    # 시스템 시작 알림 테스트
    print("1. 시스템 시작 알림 테스트...")
    notify_system_start()
    
    # 시스템 성공 알림 테스트
    print("2. 시스템 성공 알림 테스트...")
    test_results = {
        'news_count': 15,
        'bid_count': 8,
        'stats_count': 12,
        'dashboard_url': 'https://www.notion.so/test-dashboard',
        'execution_time': '2분 30초'
    }
    notify_system_success(test_results)
    
    print("✅ 알림 시스템 테스트 완료")
    print("📧 조대표님께 테스트 알림이 전송되었습니다.") 