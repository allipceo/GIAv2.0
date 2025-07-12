#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 트리거 기반 뉴스 자동화 실행 시스템
작성일: 2025년 1월 12일
목적: Notion에서 특정 액션 시 자동으로 뉴스 수집 실행

사용법:
1. Notion에 "뉴스 수집 실행" 페이지 생성
2. 해당 페이지의 체크박스를 체크하면 자동 실행
3. 백그라운드에서 이 스크립트가 모니터링
"""

import time
import subprocess
import sys
import logging
from datetime import datetime
from notion_client import Client

# 설정
NOTION_TOKEN = "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"
TRIGGER_DATABASE_ID = "22aa613d25ff80888257c652d865f85a"  # 트리거용 DB ID
CHECK_INTERVAL = 30  # 30초마다 체크

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notion_trigger.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class NotionTriggerWatcher:
    def __init__(self):
        self.notion = Client(auth=NOTION_TOKEN)
        self.last_check_time = datetime.now()
        
    def check_trigger_status(self):
        """Notion DB에서 트리거 상태 확인"""
        try:
            # 트리거 페이지 조회 (최근 생성된 페이지부터)
            response = self.notion.databases.query(
                database_id=TRIGGER_DATABASE_ID,
                sorts=[
                    {
                        "timestamp": "created_time",
                        "direction": "descending"
                    }
                ],
                page_size=5
            )
            
            for page in response["results"]:
                # 페이지 제목에 "뉴스 수집 실행" 포함 여부 확인
                title_property = page["properties"].get("제목", {})
                if title_property.get("title"):
                    title = title_property["title"][0]["text"]["content"]
                    
                    if "뉴스 수집 실행" in title:
                        # 체크박스 상태 확인
                        checkbox_property = page["properties"].get("실행", {})
                        if checkbox_property.get("checkbox") == True:
                            # 페이지 생성 시간이 마지막 체크 이후인지 확인
                            created_time = datetime.fromisoformat(
                                page["created_time"].replace("Z", "+00:00")
                            )
                            
                            if created_time > self.last_check_time:
                                logging.info(f"🎯 트리거 감지: {title}")
                                return page["id"]
            
            return None
            
        except Exception as e:
            logging.error(f"❌ 트리거 확인 중 오류: {str(e)}")
            return None
    
    def execute_news_automation(self):
        """뉴스 자동화 스크립트 실행"""
        try:
            logging.info("🚀 뉴스 자동화 실행 시작...")
            
            result = subprocess.run(
                [sys.executable, "run_news_automation.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                logging.info("✅ 뉴스 자동화 성공 완료")
                return True, "성공"
            else:
                logging.error(f"❌ 뉴스 자동화 실패: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logging.error(f"❌ 실행 중 오류: {str(e)}")
            return False, str(e)
    
    def update_trigger_page(self, page_id, success, message):
        """트리거 페이지에 실행 결과 업데이트"""
        try:
            # 실행 결과를 페이지에 기록
            status = "✅ 성공" if success else "❌ 실패"
            result_text = f"{status} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{message}"
            
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "실행": {"checkbox": False},  # 체크박스 해제
                    "결과": {
                        "rich_text": [{"text": {"content": result_text}}]
                    }
                }
            )
            logging.info("📝 실행 결과 업데이트 완료")
            
        except Exception as e:
            logging.error(f"❌ 결과 업데이트 실패: {str(e)}")
    
    def run_watcher(self):
        """트리거 감시 루프 실행"""
        logging.info("👁️ Notion 트리거 감시 시작...")
        logging.info(f"⏱️ 체크 간격: {CHECK_INTERVAL}초")
        
        while True:
            try:
                # 트리거 상태 확인
                triggered_page_id = self.check_trigger_status()
                
                if triggered_page_id:
                    # 뉴스 자동화 실행
                    success, message = self.execute_news_automation()
                    
                    # 결과를 Notion에 업데이트
                    self.update_trigger_page(triggered_page_id, success, message)
                    
                    # 마지막 체크 시간 업데이트
                    self.last_check_time = datetime.now()
                
                # 대기
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logging.info("⏹️ 사용자에 의해 중단됨")
                break
            except Exception as e:
                logging.error(f"❌ 감시 루프 오류: {str(e)}")
                time.sleep(CHECK_INTERVAL)

def main():
    """메인 실행 함수"""
    print("🎯 Notion 트리거 기반 뉴스 자동화 시스템")
    print("=" * 50)
    print("📋 사용법:")
    print("1. Notion에서 '뉴스 수집 실행' 페이지 생성")
    print("2. '실행' 체크박스를 체크")
    print("3. 자동으로 뉴스 수집이 실행됩니다")
    print("=" * 50)
    
    watcher = NotionTriggerWatcher()
    watcher.run_watcher()

if __name__ == "__main__":
    main() 