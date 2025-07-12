#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA MVP1.0 통합 자동화 시스템 (Google News 연동)
작성일: 2025년 1월 12일
수정일: 2025년 1월 12일 (Google News 연동 변경)
작성자: 서대리 (Lead Developer)
목적: 구글 뉴스 수집 → LLM 처리 → 노션 업로드 → 대시보드 생성 전체 파이프라인 자동화

워크플로우:
1. 구글 뉴스 RSS로 키워드별 뉴스 수집
2. Gemini LLM으로 분류/요약/중요도 판단
3. 노션 DB에 자동 업로드
4. 조대표님 전용 대시보드 생성
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List

# 로컬 모듈 임포트
from mvp_config import APIConfig, get_config_summary, validate_config
from google_news_collector import collect_google_news_rss, KEYWORDS, safe_encode_text
from llm_processor import LLMProcessor
from dashboard_creator import DashboardCreator
from notion_client import Client

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mvp1_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MVP1AutomationPipeline:
    """MVP1.0 전체 자동화 파이프라인 (Google News 연동)"""
    
    def __init__(self):
        self.llm_processor = LLMProcessor()
        self.dashboard_creator = DashboardCreator()
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        
        # 실행 통계
        self.stats = {
            'start_time': datetime.now(),
            'collected_articles': 0,
            'processed_articles': 0,
            'uploaded_articles': 0,
            'dashboard_created': False,
            'errors': []
        }
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = ['logs', 'data', 'backup']
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logging.info(f"[SETUP] {directory} 디렉토리 생성")
    
    def step1_collect_google_news(self) -> List[Dict]:
        """1단계: 구글 뉴스 수집"""
        logging.info("=" * 60)
        logging.info("🔥 1단계: 구글 뉴스 수집 시작")
        logging.info("=" * 60)
        
        try:
            # 구글 뉴스 수집
            articles = collect_google_news_rss(KEYWORDS)
            
            if not articles:
                raise Exception("수집된 뉴스가 없습니다.")
            
            # 임시 파일로 저장 (백업용)
            backup_filename = f"backup/collected_google_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            self.stats['collected_articles'] = len(articles)
            logging.info(f"✅ 1단계 완료: {len(articles)}건 수집")
            
            return articles
            
        except Exception as e:
            error_msg = f"1단계 실패: {str(e)}"
            self.stats['errors'].append(error_msg)
            logging.error(f"❌ {error_msg}")
            return []
    
    def step2_process_with_llm(self, articles: List[Dict]) -> List[Dict]:
        """2단계: LLM 처리 (분류/요약/중요도)"""
        logging.info("=" * 60)
        logging.info("🤖 2단계: LLM 처리 시작")
        logging.info("=" * 60)
        
        try:
            if not articles:
                raise Exception("처리할 기사가 없습니다.")
            
            # 구글 뉴스 데이터를 LLM 처리에 적합한 형태로 변환
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    '제목': article.get('제목', ''),
                    '요약': article.get('요약', ''),
                    '발행일': article.get('발행일', ''),
                    'URL': article.get('URL', ''),
                    '출처': 'Google News',
                    '태그': article.get('태그', []),
                    '중요도': article.get('중요도', '보통'),
                    '요약 품질 평가': article.get('요약 품질 평가', '보통')
                }
                formatted_articles.append(formatted_article)
            
            # LLM 배치 처리
            processed_articles = self.llm_processor.process_articles_batch(formatted_articles)
            
            # 처리 결과 리포트
            report = self.llm_processor.generate_processing_report(processed_articles)
            logging.info(report)
            
            # 처리된 데이터 저장
            processed_filename = f"data/processed_google_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(processed_filename, 'w', encoding='utf-8') as f:
                json.dump(processed_articles, f, ensure_ascii=False, indent=2)
            
            self.stats['processed_articles'] = len(processed_articles)
            logging.info(f"✅ 2단계 완료: {len(processed_articles)}건 처리")
            
            return processed_articles
            
        except Exception as e:
            error_msg = f"2단계 실패: {str(e)}"
            self.stats['errors'].append(error_msg)
            logging.error(f"❌ {error_msg}")
            return articles  # 원본 반환
    
    def step3_upload_to_notion(self, articles: List[Dict]) -> bool:
        """3단계: 노션 DB 업로드"""
        logging.info("=" * 60)
        logging.info("📊 3단계: 노션 DB 업로드 시작")
        logging.info("=" * 60)
        
        try:
            if not articles:
                raise Exception("업로드할 기사가 없습니다.")
            
            success_count = 0
            error_count = 0
            
            for article in articles:
                try:
                    # 날짜 형식 변환
                    iso_date = datetime.strptime(article["발행일"], "%Y-%m-%d").isoformat()
                    
                    # 안전한 텍스트 처리
                    safe_title = safe_encode_text(str(article["제목"]))
                    safe_url = safe_encode_text(str(article["URL"]))
                    safe_summary = safe_encode_text(str(article.get("요약", "")))
                    safe_tags = [safe_encode_text(str(tag)) for tag in article.get("태그", [])]
                    safe_importance = safe_encode_text(str(article.get("중요도", "보통")))
                    safe_source = safe_encode_text(str(article.get("출처", "Google News")))
                    
                    # 노션 페이지 생성
                    response = self.notion.pages.create(
                        parent={"database_id": APIConfig.NOTION_NEWS_DATABASE_ID},
                        properties={
                            "제목": {
                                "title": [{"text": {"content": safe_title}}]
                            },
                            "링크": {
                                "url": safe_url
                            },
                            "날짜": {
                                "date": {"start": iso_date}
                            },
                            "분야": {
                                "multi_select": [{"name": tag} for tag in safe_tags if tag]
                            },
                            "출처": {
                                "rich_text": [{"text": {"content": safe_source}}]
                            },
                            "중요도": {
                                "select": {"name": safe_importance}
                            },
                            "주요내용": {
                                "rich_text": [{"text": {"content": safe_summary}}]
                            }
                        }
                    )
                    
                    success_count += 1
                    
                    # 진행 상황 로깅 (10건마다)
                    if success_count % 10 == 0:
                        logging.info(f"[UPLOAD] {success_count}건 업로드 완료...")
                
                except Exception as e:
                    error_count += 1
                    logging.error(f"[UPLOAD] 실패: {article.get('제목', '')[:30]}... - {str(e)}")
            
            self.stats['uploaded_articles'] = success_count
            
            if success_count > 0:
                logging.info(f"✅ 3단계 완료: {success_count}건 업로드, {error_count}건 실패")
                return True
            else:
                logging.error("❌ 3단계 실패: 업로드된 기사 없음")
                return False
                
        except Exception as e:
            error_msg = f"3단계 실패: {str(e)}"
            self.stats['errors'].append(error_msg)
            logging.error(f"❌ {error_msg}")
            return False
    
    def step4_create_dashboard(self) -> str:
        """4단계: 대시보드 생성"""
        logging.info("=" * 60)
        logging.info("📊 4단계: 대시보드 생성 시작")
        logging.info("=" * 60)
        
        try:
            # 대시보드 생성
            dashboard_url = self.dashboard_creator.create_dashboard_page(
                self.dashboard_creator.get_todays_important_news()
            )
            
            if dashboard_url:
                self.stats['dashboard_created'] = True
                logging.info(f"✅ 4단계 완료: 대시보드 생성 완료")
                return dashboard_url
            else:
                logging.error("❌ 4단계 실패: 대시보드 생성 실패")
                return ""
                
        except Exception as e:
            error_msg = f"4단계 실패: {str(e)}"
            self.stats['errors'].append(error_msg)
            logging.error(f"❌ {error_msg}")
            return ""
    
    def generate_final_report(self, dashboard_url: str = "") -> str:
        """최종 실행 보고서 생성"""
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']
        
        report = f"""
🎯 GIA MVP1.0 자동화 실행 완료 보고서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 실행 시간: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%H:%M:%S')}
⏱️ 소요 시간: {duration.seconds//60}분 {duration.seconds%60}초

📊 처리 결과:
┌─────────────────────────────────────────────────────┐
│ 🔥 구글 뉴스 수집      │ {self.stats['collected_articles']:>3}건 │
│ 🤖 LLM 처리           │ {self.stats['processed_articles']:>3}건 │
│ 📊 노션 업로드         │ {self.stats['uploaded_articles']:>3}건 │
│ 🎨 대시보드 생성       │ {'완료' if self.stats['dashboard_created'] else '실패':>3}  │
└─────────────────────────────────────────────────────┘

🎨 대시보드 URL: {dashboard_url if dashboard_url else '생성 실패'}

{"❌ 오류 발생:" if self.stats['errors'] else "✅ 성공적으로 완료"}
{chr(10).join(self.stats['errors']) if self.stats['errors'] else "모든 단계가 성공적으로 완료되었습니다."}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
    
    def run_full_pipeline(self) -> bool:
        """전체 파이프라인 실행"""
        logging.info("🚀 GIA MVP1.0 자동화 파이프라인 시작")
        logging.info(f"📋 설정 정보: {get_config_summary()}")
        
        try:
            # 디렉토리 확인
            self.ensure_directories()
            
            # 1단계: 구글 뉴스 수집
            articles = self.step1_collect_google_news()
            if not articles:
                logging.error("❌ 파이프라인 중단: 수집된 뉴스가 없음")
                return False
            
            # 2단계: LLM 처리
            processed_articles = self.step2_process_with_llm(articles)
            
            # 3단계: 노션 업로드
            upload_success = self.step3_upload_to_notion(processed_articles)
            if not upload_success:
                logging.warning("⚠️ 노션 업로드 실패, 대시보드 생성 계속 진행")
            
            # 4단계: 대시보드 생성
            dashboard_url = self.step4_create_dashboard()
            
            # 최종 보고서 생성
            final_report = self.generate_final_report(dashboard_url)
            logging.info(final_report)
            
            # 성공 여부 판단
            success = (
                self.stats['collected_articles'] > 0 and
                self.stats['processed_articles'] > 0 and
                (self.stats['uploaded_articles'] > 0 or self.stats['dashboard_created'])
            )
            
            if success:
                logging.info("🎉 GIA MVP1.0 자동화 파이프라인 성공 완료!")
                return True
            else:
                logging.error("❌ GIA MVP1.0 자동화 파이프라인 실패")
                return False
                
        except Exception as e:
            logging.error(f"❌ 파이프라인 실행 중 치명적 오류: {str(e)}")
            return False

def main():
    """메인 실행 함수"""
    try:
        # 설정 검증
        if not validate_config():
            logging.error("❌ 설정 검증 실패, 실행 중단")
            return False
        
        # 파이프라인 실행
        pipeline = MVP1AutomationPipeline()
        success = pipeline.run_full_pipeline()
        
        if success:
            logging.info("🎉 프로그램 정상 종료")
        else:
            logging.error("❌ 프로그램 오류 종료")
        
        return success
        
    except KeyboardInterrupt:
        logging.info("⏹️ 사용자에 의해 중단됨")
        return False
    except Exception as e:
        logging.error(f"❌ 치명적 오류: {str(e)}")
        return False

if __name__ == "__main__":
    main() 