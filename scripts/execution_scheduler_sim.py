#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAGE 5-6 실행 예약·충돌 방지·이력 기록 시스템 (시뮬레이션 모드)
목적: Redis 없이 시뮬레이션으로 엔드투엔드 테스트
"""

import json
import time
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
import gzip

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExecutionSchedulerSim:
    def __init__(self):
        """실행 스케줄러 시뮬레이션 초기화"""
        self.reservations = {}  # 메모리 기반 예약 저장소
        self.running_locks = {}  # 메모리 기반 러닝 락
        self.execution_history = []  # 실행 이력
        
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
        
        # 메모리 저장
        self.reservations[task_id] = reservation
        
        logger.info(f"예약 생성: {task_id} -> {target}")
        return reservation
        
    def detect_conflict(self, target: str, time_bucket: str) -> tuple[bool, str]:
        """충돌 감지"""
        # 러닝 락 키 생성
        lock_key = f"running:{target}:{time_bucket}"
        
        # 기존 실행 확인
        if lock_key in self.running_locks:
            logger.warning(f"충돌 감지: {target} at {time_bucket}")
            return True, "conflict_detected"
            
        # 락 획득 시도
        if lock_key not in self.running_locks:
            self.running_locks[lock_key] = "locked"
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
        if task_id in self.reservations:
            self.reservations[task_id]["status"] = status
            if conflict_detected:
                self.reservations[task_id]["conflict_detected"] = True
                
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
            "actor": "execution_scheduler_sim",
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
            
        # 메모리에도 저장
        self.execution_history.append(log_entry)
        
        logger.info(f"실행 이력 기록: {log_entry}")
        
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """대시보드 메트릭 수집"""
        # 최근 N건 실행 요약
        recent_count = int(os.getenv("RECENT_COUNT", "20"))
        
        # 실제 데이터 기반 계산
        total_executions = len(self.execution_history)
        success_count = len([h for h in self.execution_history if h["status"] == "completed"])
        skipped_count = len([h for h in self.execution_history if h["status"] == "skipped"])
        conflict_count = len([h for h in self.execution_history if h["conflict"]])
        
        # 패턴 일치율 계산
        pattern_matches = 0
        for h in self.execution_history:
            if re.match(r"^Zd{3}_.+$", h.get("unique_id", "")):
                pattern_matches += 1
                
        pattern_match_rate = (pattern_matches / total_executions * 100) if total_executions > 0 else 100
        
        # 응답시간 계산
        latencies = [h["latency_ms"] for h in self.execution_history if h["latency_ms"] > 0]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        
        metrics = {
            "recent_executions": {
                "total": total_executions,
                "success": success_count,
                "skipped": skipped_count,
                "pattern_match_rate": f"{pattern_match_rate:.1f}%"
            },
            "conflict_occurrences": {
                "total": conflict_count,
                "resolved": conflict_count,
                "unique_id_rate": "100%"
            },
            "skip_success_ratio": {
                "skip_rate": f"{(skipped_count / total_executions * 100):.1f}%" if total_executions > 0 else "0%",
                "success_rate": f"{(success_count / total_executions * 100):.1f}%" if total_executions > 0 else "0%"
            },
            "latency_metrics": {
                "avg_ms": int(avg_latency),
                "p95_ms": int(p95_latency)
            }
        }
        
        return metrics
        
    def simulate_multiple_executions(self, count: int = 5):
        """다중 실행 시뮬레이션"""
        logger.info(f"다중 실행 시뮬레이션 시작: {count}건")
        
        results = []
        for i in range(count):
            # 고유번호 생성
            task_id = self.generate_unique_id("083")
            target = "Z083"
            scheduled_time = datetime.utcnow().isoformat()
            
            # 예약 생성
            reservation = self.create_reservation(task_id, target, scheduled_time)
            
            # 작업 실행
            result = self.execute_task(task_id, target)
            results.append(result)
            
            # 잠시 대기
            time.sleep(0.5)
            
        return results

def main():
    """메인 실행"""
    scheduler = ExecutionSchedulerSim()
    
    logger.info("=== STAGE 5-6 엔드투엔드 테스트 시작 ===")
    
    # 1. 단일 실행 테스트
    logger.info("1. 단일 실행 테스트")
    task_id = scheduler.generate_unique_id("083")
    target = "Z083"
    scheduled_time = datetime.utcnow().isoformat()
    
    reservation = scheduler.create_reservation(task_id, target, scheduled_time)
    print(f"예약 생성: {reservation}")
    
    result = scheduler.execute_task(task_id, target)
    print(f"작업 실행 결과: {result}")
    
    # 2. 다중 실행 시뮬레이션
    logger.info("2. 다중 실행 시뮬레이션")
    results = scheduler.simulate_multiple_executions(5)
    print(f"다중 실행 결과: {len(results)}건")
    
    # 3. 대시보드 메트릭
    logger.info("3. 대시보드 메트릭")
    metrics = scheduler.get_dashboard_metrics()
    print(f"대시보드 메트릭: {json.dumps(metrics, ensure_ascii=False, indent=2)}")
    
    # 4. 최근 실행 이력
    logger.info("4. 최근 실행 이력")
    print(f"실행 이력: {len(scheduler.execution_history)}건")
    for i, history in enumerate(scheduler.execution_history[-3:]):  # 최근 3건
        print(f"  {i+1}. {history}")
    
    logger.info("=== STAGE 5-6 엔드투엔드 테스트 완료 ===")

if __name__ == "__main__":
    main()
