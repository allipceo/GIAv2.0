#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
입찰/낙찰 뉴스 노션 DB 업로드 모듈
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 처리된 입찰/낙찰 뉴스를 새로운 '입찰낙찰 공고 DB'에 업로드

주요 기능:
- 입찰낙찰 공고 DB 필드 매핑
- 다중 선택/선택 필드 정확한 처리
- 중복 체크 및 업로드 안전성
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from notion_client import Client

# 로컬 모듈 임포트
from mvp_config import APIConfig, BidDatabaseFields

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bid_notion_uploader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BidNotionUploader:
    """입찰/낙찰 뉴스 노션 DB 업로드 전용 클래스"""
    
    def __init__(self):
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        self.database_id = APIConfig.NOTION_BID_DATABASE_ID
        self.uploaded_count = 0
        self.failed_count = 0
        
    def map_categories_to_db_options(self, categories: List[str]) -> List[Dict]:
        """수집 시 카테고리를 실제 DB 옵션으로 매핑"""
        db_options = []
        
        for category in categories:
            if category in BidDatabaseFields.CATEGORY_MAPPING:
                # 매핑된 DB 옵션들 중 첫 번째 옵션 사용
                mapped_options = BidDatabaseFields.CATEGORY_MAPPING[category]
                # 신재생에너지의 경우 "신재생에너지" 옵션 사용
                if category == "신재생에너지":
                    db_options.append({"name": "신재생에너지"})
                elif category == "방위산업":
                    db_options.append({"name": "방산개발"})  # 기본값으로 방산개발 사용
                elif category == "보험중개":
                    db_options.append({"name": "보험입찰"})  # 기본값으로 보험입찰 사용
            elif category in BidDatabaseFields.CATEGORY_OPTIONS:
                # 이미 DB 옵션인 경우 그대로 사용
                db_options.append({"name": category})
        
        return db_options
        
    def create_notion_page_properties(self, article: Dict) -> Dict:
        """입찰낙찰 공고 DB 필드에 맞는 노션 페이지 속성 생성"""
        
        # 날짜 형식 변환
        def format_date_for_notion(date_str: str) -> str:
            """다양한 날짜 형식을 노션 형식으로 변환"""
            try:
                # 이미 YYYY-MM-DD 형식인 경우
                if len(date_str) == 10 and date_str.count('-') == 2:
                    return date_str
                
                # 다른 형식 처리
                from datetime import datetime
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                return parsed_date.strftime('%Y-%m-%d')
            except:
                # 파싱 실패 시 오늘 날짜 반환
                return datetime.now().strftime('%Y-%m-%d')
        
        # 기본 속성 구성
        properties = {
            # 제목 (Title)
            BidDatabaseFields.TITLE: {
                "title": [
                    {
                        "text": {
                            "content": article.get('제목', '')[:100]  # 제목 길이 제한
                        }
                    }
                ]
            },
            
            # 날짜 (Date)
            BidDatabaseFields.DATE: {
                "date": {
                    "start": format_date_for_notion(article.get('날짜', ''))
                }
            },
            
            # 링크 (URL)
            BidDatabaseFields.LINK: {
                "url": article.get('링크', '')
            },
            
            # 출처 (Text)
            BidDatabaseFields.SOURCE: {
                "rich_text": [
                    {
                        "text": {
                            "content": article.get('출처', 'Google News')
                        }
                    }
                ]
            },
            
            # 분야 (Multi-select) - 매핑을 통해 실제 DB 옵션으로 변환
            BidDatabaseFields.CATEGORY: {
                "multi_select": self.map_categories_to_db_options(article.get('분야', []))
            },
            
            # 유형 (Select)
            BidDatabaseFields.TYPE: {
                "select": {
                    "name": article.get('유형', '관련뉴스')
                }
            },
            
            # 주요내용 (Text)
            BidDatabaseFields.CONTENT: {
                "rich_text": [
                    {
                        "text": {
                            "content": article.get('주요내용', '')[:2000]  # 내용 길이 제한
                        }
                    }
                ]
            },
            
            # 중요도 (Select)
            BidDatabaseFields.IMPORTANCE: {
                "select": {
                    "name": article.get('중요도', '보통')
                }
            },
            
            # 선별여부 (Checkbox)
            BidDatabaseFields.SELECTED: {
                "checkbox": article.get('선별여부', False)
            },
            
            # 수정일시 (Date)
            BidDatabaseFields.MODIFIED_TIME: {
                "date": {
                    "start": format_date_for_notion(article.get('수정일시', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                }
            }
            
            # 관련 프로젝트는 관계형 필드이므로 일단 제외
            # 추후 프로젝트 DB 연동 시 추가 가능
        }
        
        return properties
    
    def check_duplicate_by_url(self, url: str) -> bool:
        """URL로 중복 페이지 확인"""
        try:
            filter_query = {
                "property": BidDatabaseFields.LINK,
                "url": {
                    "equals": url
                }
            }
            
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter=filter_query
            )
            
            return len(response.get('results', [])) > 0
            
        except Exception as e:
            logging.error(f"[BID_UPLOAD] 중복 체크 실패: {str(e)}")
            return False
    
    def upload_single_article(self, article: Dict) -> bool:
        """단일 입찰/낙찰 기사 업로드"""
        try:
            # 중복 체크
            url = article.get('링크', '')
            if url and self.check_duplicate_by_url(url):
                logging.info(f"[BID_UPLOAD] 중복 건너뛰기: {article.get('제목', '')[:30]}...")
                return True
            
            # 노션 페이지 속성 생성
            properties = self.create_notion_page_properties(article)
            
            # 페이지 생성
            response = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            if response.get('id'):
                logging.info(f"[BID_UPLOAD] 성공: {article.get('제목', '')[:30]}...")
                self.uploaded_count += 1
                return True
            else:
                logging.error(f"[BID_UPLOAD] 응답 오류: {article.get('제목', '')[:30]}...")
                self.failed_count += 1
                return False
                
        except Exception as e:
            logging.error(f"[BID_UPLOAD] 업로드 실패: {str(e)}")
            self.failed_count += 1
            return False
    
    def upload_bid_articles_batch(self, articles: List[Dict], batch_size: int = 5) -> Tuple[int, int]:
        """입찰/낙찰 기사들 배치 업로드"""
        total = len(articles)
        
        logging.info(f"[BID_UPLOAD] {total}건 입찰/낙찰 기사 업로드 시작")
        
        for i in range(0, total, batch_size):
            batch = articles[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total - 1) // batch_size + 1
            
            logging.info(f"[BID_UPLOAD] 배치 {batch_num}/{total_batches} 처리 중...")
            
            for article in batch:
                self.upload_single_article(article)
                
                # API 호출 간격 (Rate limit 방지)
                time.sleep(1)
            
            # 배치 진행 상황 출력
            if i + batch_size < total:
                logging.info(f"[BID_UPLOAD] {min(i + batch_size, total)}건 처리 완료...")
                time.sleep(2)  # 배치 간 대기
        
        logging.info(f"[BID_UPLOAD] 전체 업로드 완료: 성공 {self.uploaded_count}건, 실패 {self.failed_count}건")
        return self.uploaded_count, self.failed_count
    
    def generate_upload_report(self, articles: List[Dict]) -> str:
        """업로드 결과 리포트 생성"""
        total = len(articles)
        success_rate = (self.uploaded_count / total * 100) if total > 0 else 0
        
        # 유형별 업로드 현황
        type_counts = {}
        for bid_type in BidDatabaseFields.TYPE_OPTIONS:
            count = len([a for a in articles if a.get('유형') == bid_type])
            type_counts[bid_type] = count
        
        # 분야별 업로드 현황
        category_counts = {}
        for category in BidDatabaseFields.CATEGORY_OPTIONS:
            count = len([a for a in articles if category in a.get('분야', [])])
            category_counts[category] = count
        
        report = f"""
📊 입찰/낙찰 뉴스 노션 DB 업로드 결과 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 전체 처리: {total}건
✅ 업로드 성공: {self.uploaded_count}건
❌ 업로드 실패: {self.failed_count}건
📊 성공률: {success_rate:.1f}%

🗂️ 타겟 DB: 입찰낙찰 공고 DB
🆔 DB ID: {self.database_id}

🏷️ 유형별 업로드:
  📋 입찰공고: {type_counts.get('입찰공고', 0)}건
  🎯 낙찰결과: {type_counts.get('낙찰결과', 0)}건
  📝 계약소식: {type_counts.get('계약소식', 0)}건
  📰 관련뉴스: {type_counts.get('관련뉴스', 0)}건

🏢 분야별 업로드:
  🔋 신재생에너지: {category_counts.get('신재생에너지', 0)}건
  🛡️ 방위산업: {category_counts.get('방위산업', 0)}건

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report

def main():
    """메인 실행 함수"""
    logging.info("[BID_UPLOAD] 입찰/낙찰 뉴스 노션 DB 업로드 시작")
    
    try:
        # 최근 처리된 입찰/낙찰 데이터 로드
        import os
        import glob
        
        # data 폴더에서 가장 최근 processed_bid_news 파일 찾기
        processed_files = glob.glob("data/processed_bid_news_*.json")
        if not processed_files:
            # 처리되지 않은 원본 파일 찾기
            bid_files = glob.glob("data/bid_news_*.json")
            if not bid_files:
                logging.error("[BID_UPLOAD] 업로드할 입찰/낙찰 데이터 파일이 없습니다.")
                return
            latest_file = max(bid_files, key=os.path.getctime)
        else:
            latest_file = max(processed_files, key=os.path.getctime)
        
        logging.info(f"[BID_UPLOAD] 파일 로드: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        if not articles:
            logging.warning("[BID_UPLOAD] 업로드할 기사가 없습니다.")
            return
        
        # 업로더 초기화
        uploader = BidNotionUploader()
        
        # 배치 업로드 실행
        success_count, failed_count = uploader.upload_bid_articles_batch(articles)
        
        # 결과 리포트
        report = uploader.generate_upload_report(articles)
        logging.info(report)
        
        if success_count > 0:
            logging.info(f"[BID_UPLOAD] ✅ 업로드 완료: {success_count}건 성공")
            logging.info(f"[BID_UPLOAD] 📊 노션 DB URL: https://www.notion.so/{APIConfig.NOTION_BID_DATABASE_ID}")
        else:
            logging.warning("[BID_UPLOAD] ⚠️ 업로드된 기사가 없습니다.")
            
    except Exception as e:
        logging.error(f"[BID_UPLOAD] 실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main() 