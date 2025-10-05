#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAGE 5-6 실행 예약·충돌 방지·이력 기록 시스템
목적: Redis 기반 실행 예약 및 충돌 방지 시스템 구축
"""

import json
import time
import os
import redis
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
import gzip
from apscheduler.schedulers.background import BackgroundScheduler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExecutionScheduler:
    def __init__(self):
        """실행 스케줄러 초기화"""
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.scheduler = BackgroundScheduler()
        self.setup_redis_keyspaces()
        self.setup_scheduler()
        
    def setup_redis_keyspaces(self):
        """Redis 키공간 구성"""
        # 예약 키공간: reservations:{task_id}
        # 러닝 락 키공간: running:{target}:{time_bucket}
        logger.info("Redis 키공간 구성 완료")
        
    def setup_scheduler(self):
        """스케줄러 설정"""
        # JSONL 롤오버·압축 작업 배치 등록
        self.scheduler.add_job(
            self.rollover_logs,
            'cron',
            hour=0,  # 매일 자정
            id='log_rollover',
            replace_existing=True
        )
        
        # 압축 작업 (7일 후)
        self.scheduler.add_job(
            self.compress_old_logs,
            'cron',
            hour=1,  # 매일 새벽 1시
            id='log_compression',
            replace_existing=True
        )
        
    def create_reservation(self, task_id: str, target: str, scheduled_time: str) -> Dict[str, Any]:
        """실행 예약 생성"""
        reservation = {
            "task_id": task_id,
            "target": target,
            "scheduled_time": scheduled_time,
            "status": "pending",
            "conflict_detected": False,
            "created_ts": datetime.utcnow().isoformat()
        }
        
        # Redis Hash로 저장
        key = f"reservations:{task_id}"
        self.redis_client.hset(key, mapping=reservation)
        
        logger.info(f"예약 생성: {task_id} -> {target}")
        return reservation
        
    def detect_conflict(self, target: str, time_bucket: str) -> tuple[bool, str]:
        """충돌 감지"""
        # 러닝 락 키 생성
        lock_key = f"running:{target}:{time_bucket}"
        
        # 기존 실행 확인
        if self.redis_client.exists(lock_key):
            logger.warning(f"충돌 감지: {target} at {time_bucket}")
            return True, "conflict_detected"
            
        # 락 획득 시도
        if self.redis_client.setnx(lock_key, "locked"):
            # TTL 설정 (5분)
            self.redis_client.expire(lock_key, 300)
            logger.info(f"락 획득: {lock_key}")
            return False, "locked"
        else:
            logger.warning(f"락 획득 실패: {lock_key}")
            return True, "lock_failed"
            
    def execute_task(self, task_id: str, target: str) -> Dict[str, Any]:
        """작업 실행"""
        start_time = time.time()
        
        try:
            # 충돌 감지
            time_bucket = datetime.utcnow().strftime("%Y%m%d%H%M")
            conflict, reason = self.detect_conflict(target, time_bucket)
            
            if conflict:
                # 충돌 시 스킵 처리
                self.update_reservation_status(task_id, "skipped", conflict_detected=True)
                result = {
                    "task_id": task_id,
                    "target": target,
                    "status": "skipped",
                    "conflict_detected": True,
                    "reason": reason,
                    "latency_ms": 0
                }
            else:
                # 정상 실행
                # 실제 작업 수행 (예시)
                time.sleep(0.1)  # 시뮬레이션
                
                self.update_reservation_status(task_id, "completed")
                result = {
                    "task_id": task_id,
                    "target": target,
                    "status": "completed",
                    "conflict_detected": False,
                    "latency_ms": int((time.time() - start_time) * 1000)
                }
                
            # 이력 기록
            self.log_execution_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"작업 실행 실패: {task_id} - {e}")
            self.update_reservation_status(task_id, "failed")
            return {
                "task_id": task_id,
                "target": target,
                "status": "failed",
                "error": str(e),
                "latency_ms": int((time.time() - start_time) * 1000)
            }
            
    def update_reservation_status(self, task_id: str, status: str, conflict_detected: bool = False):
        """예약 상태 업데이트"""
        key = f"reservations:{task_id}"
        self.redis_client.hset(key, "status", status)
        if conflict_detected:
            self.redis_client.hset(key, "conflict_detected", "true")
            
    def generate_unique_id(self, target: str) -> str:
        """고유번호 생성"""
        # 패턴: ^Zd{3}_.+$
        pattern = r"^Zd{3}_.+$"
        
        # base_id 생성: Z{문서번호 세 자리}_{UTC-YYYYMMDDHHmmss}
        now = datetime.utcnow()
        base_id = f"Z{target[:3]}_{now.strftime('%Y%m%d%H%M%S')}"
        
        # 최근 N건 조회 (기본 20건)
        recent_count = int(os.getenv("RECENT_COUNT", "20"))
        recent_ids = self.get_recent_ids(recent_count)
        
        # 충돌 검사
        if base_id in recent_ids:
            # 증분 suffix 부여
            suffix = 1
            while f"{base_id}-{suffix:03d}" in recent_ids:
                suffix += 1
            base_id = f"{base_id}-{suffix:03d}"
            
        logger.info(f"고유번호 생성: {base_id}")
        return base_id
        
    def get_recent_ids(self, count: int) -> List[str]:
        """최근 N건 ID 조회"""
        # 실제 구현에서는 Redis에서 최근 실행 이력 조회
        # 여기서는 시뮬레이션
        return []
        
    def log_execution_history(self, result: Dict[str, Any]):
        """실행 이력 기록"""
        log_entry = {
            "ts": int(time.time()),
            "actor": "execution_scheduler",
            "task_id": result.get("task_id"),
            "target": result.get("target"),
            "reserved": True,
            "conflict": result.get("conflict_detected", False),
            "skipped": result.get("status") == "skipped",
            "unique_id": result.get("task_id"),
            "status": result.get("status"),
            "latency_ms": result.get("latency_ms", 0)
        }
        
        # JSONL 로그 파일에 기록
        log_file = f"logs/execution_history_{datetime.now().strftime('%Y%m%d')}.jsonl"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        logger.info(f"실행 이력 기록: {log_entry}")
        
    def rollover_logs(self):
        """로그 롤오버 (일 단위)"""
        logger.info("로그 롤오버 시작")
        
        # 오늘 로그 파일 압축
        today = datetime.now().strftime('%Y%m%d')
        log_file = f"logs/execution_history_{today}.jsonl"
        
        if os.path.exists(log_file):
            # gz 압축
            with open(log_file, 'rb') as f_in:
                with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # 원본 파일 삭제
            os.remove(log_file)
            logger.info(f"로그 압축 완료: {log_file}.gz")
            
    def compress_old_logs(self):
        """오래된 로그 압축 (7일 후 삭제)"""
        logger.info("오래된 로그 압축 시작")
        
        cutoff_date = datetime.now() - timedelta(days=7)
        log_dir = "logs"
        
        for filename in os.listdir(log_dir):
            if filename.startswith("execution_history_") and filename.endswith(".jsonl.gz"):
                filepath = os.path.join(log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    logger.info(f"오래된 로그 삭제: {filename}")
                    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """대시보드 메트릭 수집"""
        # 최근 N건 실행 요약
        recent_count = int(os.getenv("RECENT_COUNT", "20"))
        
        # 시뮬레이션 데이터
        metrics = {
            "recent_executions": {
                "total": recent_count,
                "success": 18,
                "skipped": 2,
                "pattern_match_rate": "100%"
            },
            "conflict_occurrences": {
                "total": 5,
                "resolved": 5,
                "unique_id_rate": "100%"
            },
            "skip_success_ratio": {
                "skip_rate": "10%",
                "success_rate": "90%"
            },
            "latency_metrics": {
                "avg_ms": 1200,
                "p95_ms": 1800
            }
        }
        
        return metrics
        
    def start(self):
        """스케줄러 시작"""
        self.scheduler.start()
        logger.info("실행 스케줄러 시작")
        
    def stop(self):
        """스케줄러 중지"""
        self.scheduler.shutdown()
        logger.info("실행 스케줄러 중지")

def main():
    """메인 실행"""
    scheduler = ExecutionScheduler()
    
    try:
        scheduler.start()
        
        # 테스트 실행
        task_id = scheduler.generate_unique_id("083")
        target = "Z083"
        scheduled_time = datetime.utcnow().isoformat()
        
        # 예약 생성
        reservation = scheduler.create_reservation(task_id, target, scheduled_time)
        print(f"예약 생성: {reservation}")
        
        # 작업 실행
        result = scheduler.execute_task(task_id, target)
        print(f"작업 실행 결과: {result}")
        
        # 대시보드 메트릭
        metrics = scheduler.get_dashboard_metrics()
        print(f"대시보드 메트릭: {metrics}")
        
        # 스케줄러가 계속 실행되도록 대기
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        scheduler.stop()

if __name__ == "__main__":
    main()

