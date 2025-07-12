#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
입찰/낙찰 뉴스 통합 자동화 시스템
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 입찰/낙찰 뉴스 수집부터 대시보드 생성까지 전체 파이프라인 통합 실행

워크플로우:
1. 입찰/낙찰 뉴스 수집 (구글 뉴스 클리핑)
2. LLM 기반 분류/요약 처리  
3. 노션 입찰낙찰 공고 DB 업로드
4. 대시보드 업데이트 (입찰/낙찰 정보 포함)
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List

# 로컬 모듈 임포트
from bid_news_collector import BidNewsCollector
from bid_llm_processor import BidLLMProcessor
from bid_notion_uploader import BidNotionUploader
from dashboard_creator import DashboardCreator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bid_integrated_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BidIntegratedAutomation:
    """입찰/낙찰 뉴스 통합 자동화 시스템"""
    
    def __init__(self):
        self.collector = BidNewsCollector()
        self.processor = BidLLMProcessor()
        self.uploader = BidNotionUploader()
        self.dashboard = DashboardCreator()
        
        # 실행 통계
        self.stats = {
            'start_time': None,
            'end_time': None,
            'collected_count': 0,
            'processed_count': 0,
            'uploaded_count': 0,
            'dashboard_created': False
        }
    
    def run_full_pipeline(self) -> Dict:
        """전체 파이프라인 실행"""
        self.stats['start_time'] = datetime.now()
        
        logging.info("🚀 입찰/낙찰 뉴스 통합 자동화 시스템 시작")
        logging.info("=" * 60)
        
        try:
            # 1단계: 입찰/낙찰 뉴스 수집
            logging.info("📊 1단계: 입찰/낙찰 뉴스 수집 시작")
            collected_articles = self.collector.collect_bid_news_all_categories()
            self.stats['collected_count'] = len(collected_articles)
            
            if not collected_articles:
                logging.warning("⚠️ 수집된 입찰/낙찰 뉴스가 없습니다. 파이프라인을 종료합니다.")
                return self.generate_final_report()
            
            logging.info(f"✅ 1단계 완료: {len(collected_articles)}건 수집")
            
            # 2단계: LLM 처리
            logging.info("🤖 2단계: LLM 기반 분류/요약 처리 시작")
            processed_articles = self.processor.process_bid_articles_batch(collected_articles)
            self.stats['processed_count'] = len(processed_articles)
            
            logging.info(f"✅ 2단계 완료: {len(processed_articles)}건 처리")
            
            # 3단계: 노션 DB 업로드
            logging.info("📤 3단계: 노션 입찰낙찰 공고 DB 업로드 시작")
            uploaded_count, failed_count = self.uploader.upload_bid_articles_batch(processed_articles)
            self.stats['uploaded_count'] = uploaded_count
            
            logging.info(f"✅ 3단계 완료: {uploaded_count}건 업로드 성공, {failed_count}건 실패")
            
            # 4단계: 대시보드 생성
            logging.info("📊 4단계: 대시보드 업데이트 시작")
            news_items = self.dashboard.get_todays_important_news()  # 기존 뉴스
            dashboard_url = self.dashboard.create_dashboard_page(news_items)
            
            if dashboard_url:
                self.stats['dashboard_created'] = True
                logging.info(f"✅ 4단계 완료: 대시보드 생성 완료")
                logging.info(f"🔗 대시보드 URL: {dashboard_url}")
            else:
                logging.error("❌ 4단계 실패: 대시보드 생성 실패")
            
            # 최종 결과
            self.stats['end_time'] = datetime.now()
            return self.generate_final_report()
            
        except Exception as e:
            logging.error(f"❌ 파이프라인 실행 중 오류 발생: {str(e)}")
            self.stats['end_time'] = datetime.now()
            return self.generate_final_report()
    
    def generate_final_report(self) -> Dict:
        """최종 실행 결과 리포트 생성"""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
        
        report = {
            'execution_time': {
                'start': self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['start_time'] else None,
                'end': self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['end_time'] else None,
                'duration': str(duration) if duration else None
            },
            'results': {
                'collected': self.stats['collected_count'],
                'processed': self.stats['processed_count'],
                'uploaded': self.stats['uploaded_count'],
                'dashboard_created': self.stats['dashboard_created']
            },
            'success_rate': {
                'collection_to_processing': (self.stats['processed_count'] / max(self.stats['collected_count'], 1)) * 100,
                'processing_to_upload': (self.stats['uploaded_count'] / max(self.stats['processed_count'], 1)) * 100,
                'overall_success': self.stats['dashboard_created']
            }
        }
        
        # 콘솔 출력
        self.print_final_report(report)
        
        # 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"logs/bid_automation_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logging.info(f"📄 실행 리포트 저장: {report_file}")
        except Exception as e:
            logging.error(f"❌ 리포트 저장 실패: {str(e)}")
        
        return report
    
    def print_final_report(self, report: Dict):
        """콘솔에 최종 리포트 출력"""
        print("\n" + "="*60)
        print("🎯 입찰/낙찰 뉴스 통합 자동화 최종 결과")
        print("="*60)
        
        execution = report['execution_time']
        results = report['results']
        success_rates = report['success_rate']
        
        print(f"📅 실행 시간: {execution['start']} ~ {execution['end']}")
        print(f"⏱️ 소요 시간: {execution['duration']}")
        print("")
        
        print("📊 처리 결과:")
        print(f"  🔍 수집: {results['collected']}건")
        print(f"  🤖 처리: {results['processed']}건")
        print(f"  📤 업로드: {results['uploaded']}건")
        print(f"  📊 대시보드: {'생성 완료' if results['dashboard_created'] else '생성 실패'}")
        print("")
        
        print("📈 성공률:")
        print(f"  수집→처리: {success_rates['collection_to_processing']:.1f}%")
        print(f"  처리→업로드: {success_rates['processing_to_upload']:.1f}%")
        print(f"  전체 성공: {'✅' if success_rates['overall_success'] else '❌'}")
        print("")
        
        if results['dashboard_created']:
            print("🎉 입찰/낙찰 뉴스 자동화 파이프라인 성공 완료!")
            print("📊 조대표님께서 대시보드에서 최신 입찰/낙찰 정보를 확인하실 수 있습니다.")
        else:
            print("⚠️ 일부 단계에서 오류가 발생했습니다. 로그를 확인해주세요.")
        
        print("="*60)

def main():
    """메인 실행 함수"""
    print("🚀 입찰/낙찰 뉴스 통합 자동화 시스템")
    print("개발: 서대리 | 기획: 나실장 | 요청: 조대표님")
    print("="*60)
    
    try:
        # 통합 자동화 시스템 초기화 및 실행
        automation = BidIntegratedAutomation()
        final_report = automation.run_full_pipeline()
        
        # 성공 여부에 따른 종료 코드
        if final_report['results']['dashboard_created']:
            print("\n✅ 프로그램 정상 종료")
            exit(0)
        else:
            print("\n⚠️ 프로그램 부분 성공으로 종료")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다.")
        exit(2)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {str(e)}")
        exit(3)

if __name__ == "__main__":
    main() 