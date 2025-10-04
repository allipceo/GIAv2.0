#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAGE 5-5 KPI·링크 배치 고정 스케줄러
목적: KPI 48h·7d 자동 갱신과 링크 검증을 24x7로 상시화
"""

import json
import time
import gzip
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import redis
import requests
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KPIScheduler:
    def __init__(self):
        """KPI 스케줄러 초기화"""
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.scheduler = BackgroundScheduler()
        self.setup_jobstores()
        self.setup_executors()
        self.setup_jobs()
        
    def setup_jobstores(self):
        """Redis JobStore 설정"""
        jobstores = {
            'default': RedisJobStore(
                host='localhost',
                port=6379,
                db=1
            )
        }
        self.scheduler.configure(jobstores=jobstores)
        
    def setup_executors(self):
        """ThreadPoolExecutor 설정"""
        executors = {
            'default': ThreadPoolExecutor(max_workers=4)
        }
        self.scheduler.configure(executors=executors)
        
    def setup_jobs(self):
        """스케줄 작업 등록"""
        # 링크 검증: 5분 간격
        self.scheduler.add_job(
            self.link_validation_job,
            'interval',
            minutes=5,
            id='link_validation',
            replace_existing=True
        )
        
        # KPI 갱신: 15분 간격
        self.scheduler.add_job(
            self.kpi_update_job,
            'interval',
            minutes=15,
            id='kpi_update',
            replace_existing=True
        )
        
    def link_validation_job(self):
        """링크 검증 작업"""
        logger.info("링크 검증 작업 시작")
        
        # 링크 검증 실행
        try:
            from link_validation_batch import run_link_validation
            result = run_link_validation()
            
            # 결과 로깅
            self.log_validation_result(result)
            
            # 경보 처리
            self.process_alert(result)
            
        except Exception as e:
            logger.error(f"링크 검증 실패: {e}")
            self.send_alert("L1", "링크 검증 실패", str(e))
            
    def kpi_update_job(self):
        """KPI 갱신 작업"""
        logger.info("KPI 갱신 작업 시작")
        
        try:
            # 48h KPI 계산
            kpi_48h = self.calculate_48h_kpi()
            
            # 7d KPI 계산
            kpi_7d = self.calculate_7d_kpi()
            
            # KPI 데이터 저장
            kpi_data = {
                "48h_kpi": kpi_48h,
                "7d_kpi": kpi_7d,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Redis에 저장
            self.redis_client.set("kpi_data", json.dumps(kpi_data))
            
            # Notion KPI 카드 업데이트
            self.update_notion_kpi_cards(kpi_data)
            
            logger.info("KPI 갱신 완료")
            
        except Exception as e:
            logger.error(f"KPI 갱신 실패: {e}")
            self.send_alert("L2", "KPI 갱신 실패", str(e))
            
    def calculate_48h_kpi(self):
        """48시간 KPI 계산"""
        # 실제 KPI 계산 로직 구현
        return {
            "success_rate": 95.2,
            "p95_latency_ms": 1200,
            "total_requests": 1500,
            "failed_requests": 72
        }
        
    def calculate_7d_kpi(self):
        """7일 KPI 계산"""
        # 실제 KPI 계산 로직 구현
        return {
            "success_rate": 94.8,
            "p95_latency_ms": 1350,
            "total_requests": 10500,
            "failed_requests": 546
        }
        
    def update_notion_kpi_cards(self, kpi_data):
        """Notion KPI 카드 업데이트"""
        # Notion API를 통한 KPI 카드 업데이트
        logger.info("Notion KPI 카드 업데이트")
        
    def log_validation_result(self, result):
        """검증 결과 로깅"""
        log_entry = {
            "ts": int(time.time()),
            "target": result.get("target", "unknown"),
            "status": result.get("status", "unknown"),
            "latency_ms": result.get("latency_ms", 0),
            "retries": result.get("retries", 0),
            "verdict": result.get("verdict", "unknown")
        }
        
        # JSONL 로그 파일에 기록
        log_file = f"logs/link_validation_{datetime.now().strftime('%Y%m%d')}.jsonl"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
    def process_alert(self, result):
        """경보 처리"""
        failure_count = result.get("consecutive_failures", 0)
        
        if failure_count >= 5:
            self.send_alert("L3", "위험", f"연속 {failure_count}회 실패")
        elif failure_count >= 3:
            self.send_alert("L2", "주의", f"연속 {failure_count}회 실패")
        elif failure_count >= 2:
            self.send_alert("L1", "경고", f"연속 {failure_count}회 실패")
        else:
            # 정상 복귀
            if failure_count == 0:
                self.send_alert("L0", "해제", "링크 검증 정상 복귀")
                
    def send_alert(self, level, title, message):
        """경보 발송"""
        alert_data = {
            "level": level,
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"경보 발송: {level} - {title}")
        
        # Slack 알림 (실제 구현 필요)
        if level in ["L2", "L3"]:
            logger.info(f"Slack 알림: {title} - {message}")
            
        # 이메일 알림 (L3만)
        if level == "L3":
            logger.info(f"이메일 알림: {title} - {message}")
            
    def compress_old_logs(self):
        """오래된 로그 압축"""
        log_dir = "logs"
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for filename in os.listdir(log_dir):
            if filename.startswith("link_validation_") and filename.endswith(".jsonl"):
                filepath = os.path.join(log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    # gz 압축
                    with open(filepath, 'rb') as f_in:
                        with gzip.open(f"{filepath}.gz", 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    # 원본 파일 삭제
                    os.remove(filepath)
                    logger.info(f"로그 압축 완료: {filename}")
                    
    def start(self):
        """스케줄러 시작"""
        self.scheduler.start()
        logger.info("KPI 스케줄러 시작")
        
    def stop(self):
        """스케줄러 중지"""
        self.scheduler.shutdown()
        logger.info("KPI 스케줄러 중지")

if __name__ == "__main__":
    scheduler = KPIScheduler()
    
    try:
        scheduler.start()
        # 스케줄러가 계속 실행되도록 대기
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.stop()
