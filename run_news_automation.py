#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 클리핑 완전 자동화 통합 실행 스크립트
작성일: 2025년 7월 12일
작성자: 서대리 (Lead Developer)
목적: 1단계(뉴스 수집) + 2단계(Notion 업로드) 연속 실행

협업헌장 GIA V2.0 준수:
- 완전한 뉴스 클리핑 자동화 시스템 구현
- 수동 개입 없이 Google News → Notion DB 완료
- Windows 인코딩 안전성 보장
"""

import subprocess
import sys
import logging
from datetime import datetime

# Windows 인코딩 문제 완전 방지 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_script(script_name, description):
    """Python 스크립트 실행 및 결과 반환"""
    try:
        logging.info(f"🚀 {description} 시작...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8',
                              errors='replace')
        
        if result.returncode == 0:
            logging.info(f"✅ {description} 성공 완료")
            if result.stdout:
                logging.info(f"📋 실행 결과:\n{result.stdout}")
            return True
        else:
            logging.error(f"❌ {description} 실패")
            if result.stderr:
                logging.error(f"오류 내용:\n{result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ {description} 실행 중 예외 발생: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    start_time = datetime.now()
    logging.info("=" * 60)
    logging.info("🎯 뉴스 클리핑 완전 자동화 시스템 시작")
    logging.info(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    success_count = 0
    total_steps = 2
    
    # 1단계: Google News 수집
    if run_script("google_news_collector.py", "1단계: Google News 뉴스 수집"):
        success_count += 1
    else:
        logging.error("💥 1단계 실패로 인해 자동화 프로세스를 중단합니다.")
        return False
    
    # 2단계: Notion 업로드
    if run_script("news_to_notion_simple.py", "2단계: Notion DB 업로드"):
        success_count += 1
    else:
        logging.error("💥 2단계 실패")
    
    # 결과 요약
    end_time = datetime.now()
    duration = end_time - start_time
    
    logging.info("=" * 60)
    logging.info("📊 뉴스 클리핑 자동화 결과 요약")
    logging.info("=" * 60)
    logging.info(f"⏱️ 총 소요 시간: {duration}")
    logging.info(f"✅ 성공한 단계: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        logging.info("🎉 뉴스 클리핑 완전 자동화 성공!")
        logging.info("📰 Google News → news_data.json → Notion DB 업로드 완료")
        print("\n" + "="*50)
        print("🎯 뉴스 클리핑 자동화 완료!")
        print("="*50)
        print("✅ 1단계: Google News 뉴스 수집 완료")
        print("✅ 2단계: Notion DB 업로드 완료")
        print(f"⏱️ 총 소요 시간: {duration}")
        print("\n🔗 Notion 뉴스정보DB에서 결과를 확인하세요!")
        return True
    else:
        logging.error("❌ 일부 단계 실패로 자동화 미완료")
        print("\n" + "="*50)
        print("⚠️ 뉴스 클리핑 자동화 부분 실패")
        print("="*50)
        print(f"📊 성공: {success_count}/{total_steps} 단계")
        print("📋 자세한 내용은 news_automation.log를 확인하세요.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logging.info("⏹️ 사용자에 의해 중단되었습니다.")
        print("\n⏹️ 자동화 프로세스가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"💥 예상치 못한 오류 발생: {str(e)}")
        print(f"\n💥 오류 발생: {str(e)}")
        sys.exit(1) 