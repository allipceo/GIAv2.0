#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAGE 5-6 대시보드 시스템
목적: 실행 이력 모니터링 및 알림 시스템 구축
"""

import json
import time
import os
import redis
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask import Flask, render_template, jsonify
import threading

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardSystem:
    def __init__(self):
        """대시보드 시스템 초기화"""
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.app = Flask(__name__)
        self.setup_routes()
        self.alert_thresholds = {
            "L1": {"consecutive_failures": 2, "skip_count": 2},
            "L2": {"consecutive_failures": 3, "skip_count": 3},
            "L3": {"consecutive_failures": 5, "conflict_count": 3}
        }
        self.alert_suppression = {}  # 경보 억제 관리
        
    def setup_routes(self):
        """Flask 라우트 설정"""
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
            
        @self.app.route('/api/metrics')
        def get_metrics():
            return jsonify(self.get_dashboard_metrics())
            
        @self.app.route('/api/recent-executions')
        def get_recent_executions():
            return jsonify(self.get_recent_executions())
            
        @self.app.route('/api/alerts')
        def get_alerts():
            return jsonify(self.get_active_alerts())
            
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """대시보드 메트릭 수집"""
        # 최근 N건 실행 요약
        recent_count = int(os.getenv("RECENT_COUNT", "20"))
        
        # 실제 데이터 수집 (시뮬레이션)
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
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return metrics
        
    def get_recent_executions(self) -> List[Dict[str, Any]]:
        """최근 실행 이력 조회"""
        # 실제 구현에서는 Redis에서 최근 실행 이력 조회
        recent_executions = [
            {
                "task_id": "Z083_20251004230001",
                "target": "Z083",
                "status": "completed",
                "conflict_detected": False,
                "latency_ms": 1200,
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "task_id": "Z072_20251004230002",
                "target": "Z072",
                "status": "skipped",
                "conflict_detected": True,
                "latency_ms": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        return recent_executions
        
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """활성 경보 조회"""
        active_alerts = []
        
        # L1 경고: 연속 2회 실패 또는 스킵
        if self.check_l1_alert():
            active_alerts.append({
                "level": "L1",
                "type": "경고",
                "message": "연속 2회 실패 또는 스킵",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        # L2 주의: 연속 3회
        if self.check_l2_alert():
            active_alerts.append({
                "level": "L2",
                "type": "주의",
                "message": "연속 3회 실패",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        # L3 위험: 연속 5회 또는 10분 내 경합 3회 이상
        if self.check_l3_alert():
            active_alerts.append({
                "level": "L3",
                "type": "위험",
                "message": "연속 5회 실패 또는 경합 다발",
                "timestamp": datetime.utcnow().isoformat()
            })
            
        return active_alerts
        
    def check_l1_alert(self) -> bool:
        """L1 경고 확인"""
        # 연속 2회 실패 또는 스킵 확인
        return False  # 시뮬레이션
        
    def check_l2_alert(self) -> bool:
        """L2 주의 확인"""
        # 연속 3회 실패 확인
        return False  # 시뮬레이션
        
    def check_l3_alert(self) -> bool:
        """L3 위험 확인"""
        # 연속 5회 실패 또는 10분 내 경합 3회 이상 확인
        return False  # 시뮬레이션
        
    def send_alert(self, level: str, message: str):
        """경보 발송"""
        # 경보 억제 확인 (동일 원인 15분 중복 억제)
        alert_key = f"{level}:{message}"
        if alert_key in self.alert_suppression:
            last_sent = self.alert_suppression[alert_key]
            if (datetime.utcnow() - last_sent).total_seconds() < 900:  # 15분
                return False
                
        # 경보 발송
        logger.info(f"경보 발송: {level} - {message}")
        
        # Slack 알림 (기본)
        self.send_slack_alert(level, message)
        
        # L3는 이메일 병행
        if level == "L3":
            self.send_email_alert(level, message)
            
        # 억제 시간 기록
        self.alert_suppression[alert_key] = datetime.utcnow()
        
        return True
        
    def send_slack_alert(self, level: str, message: str):
        """Slack 알림 발송"""
        # 실제 구현에서는 Slack API 호출
        logger.info(f"Slack 알림: {level} - {message}")
        
    def send_email_alert(self, level: str, message: str):
        """이메일 알림 발송"""
        # 실제 구현에서는 SMTP 이메일 발송
        logger.info(f"이메일 알림: {level} - {message}")
        
    def send_recovery_alert(self, message: str):
        """복구 알림 발송"""
        # 정상 1회 성공 시 해제 메시지 발송
        logger.info(f"복구 알림: {message}")
        self.send_slack_alert("RECOVERY", message)
        
    def start_monitoring(self):
        """모니터링 시작"""
        def monitor_loop():
            while True:
                try:
                    # 대시보드 메트릭 업데이트 (5분 주기)
                    metrics = self.get_dashboard_metrics()
                    
                    # 경보 확인
                    self.check_alerts()
                    
                    time.sleep(300)  # 5분 간격
                    
                except Exception as e:
                    logger.error(f"모니터링 오류: {e}")
                    time.sleep(60)
                    
        # 백그라운드 모니터링 스레드 시작
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
    def check_alerts(self):
        """경보 확인 및 발송"""
        # L1 경고 확인
        if self.check_l1_alert():
            self.send_alert("L1", "연속 2회 실패 또는 스킵")
            
        # L2 주의 확인
        if self.check_l2_alert():
            self.send_alert("L2", "연속 3회 실패")
            
        # L3 위험 확인
        if self.check_l3_alert():
            self.send_alert("L3", "연속 5회 실패 또는 경합 다발")
            
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """대시보드 서버 실행"""
        self.start_monitoring()
        
        logger.info(f"대시보드 서버 시작: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """메인 실행"""
    dashboard = DashboardSystem()
    dashboard.run()

if __name__ == "__main__":
    main()

