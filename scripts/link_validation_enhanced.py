#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAGE 5-5 링크 검증 배치 (향상된 버전)
목적: 5분 간격 링크 검증 및 단계형 경보 시스템
"""

import json
import time
import os
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkValidationEnhanced:
    def __init__(self):
        """링크 검증 초기화"""
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.alert_suppression_window = 15 * 60  # 15분
        
    def run_link_validation(self) -> Dict[str, Any]:
        """링크 검증 실행"""
        logger.info("링크 검증 배치 시작")
        
        # 검증 대상 링크
        links = [
            {
                "name": "C2N2",
                "url": "https://www.notion.so/Z062_-62d899af747846aa91630239e9120a22",
                "type": "notion"
            },
            {
                "name": "C2N3", 
                "url": "https://www.notion.so/Z072_-e69469e716954b1ca7e3ded5736d1603",
                "type": "notion"
            },
            {
                "name": "TEST",
                "url": "https://example.com/test-link",
                "type": "external"
            }
        ]
        
        results = []
        total_success = 0
        total_failed = 0
        
        for link in links:
            result = self.validate_link(link)
            results.append(result)
            
            if result["status"] == "success":
                total_success += 1
            else:
                total_failed += 1
                
        # 전체 결과
        overall_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_links": len(links),
            "success_count": total_success,
            "failed_count": total_failed,
            "success_rate": (total_success / len(links)) * 100,
            "results": results,
            "consecutive_failures": self.consecutive_failures
        }
        
        # 결과 저장
        self.save_results(overall_result)
        
        # 경보 처리
        self.process_alerts(overall_result)
        
        return overall_result
        
    def validate_link(self, link: Dict[str, str]) -> Dict[str, Any]:
        """개별 링크 검증"""
        start_time = time.time()
        
        try:
            # HTTP 요청 (타임아웃 1.5초)
            response = requests.get(
                link["url"], 
                timeout=1.5,
                allow_redirects=True,
                max_redirects=1  # 3xx 최대 1회 허용
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # 검증 기준 확인
            is_https = link["url"].startswith("https://")
            is_notion = "notion.so" in link["url"] if link["type"] == "notion" else True
            is_200 = response.status_code == 200
            is_fast = latency_ms <= 1500
            
            # 종합 판정
            if is_200 and is_fast and is_https and is_notion:
                status = "success"
                verdict = "pass"
            else:
                status = "failed"
                verdict = "fail"
                
            result = {
                "name": link["name"],
                "url": link["url"],
                "status": status,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "is_https": is_https,
                "is_notion": is_notion,
                "verdict": verdict,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.Timeout:
            result = {
                "name": link["name"],
                "url": link["url"],
                "status": "failed",
                "status_code": 0,
                "latency_ms": 1500,
                "error": "timeout",
                "verdict": "timeout",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            result = {
                "name": link["name"],
                "url": link["url"],
                "status": "failed",
                "status_code": 0,
                "latency_ms": 0,
                "error": str(e),
                "verdict": "error",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        return result
        
    def save_results(self, result: Dict[str, Any]):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 파일 저장
        json_file = f"link_validation_results/link_validation_{timestamp}.json"
        os.makedirs("link_validation_results", exist_ok=True)
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        # MD 파일 저장
        md_file = f"link_validation_results/link_validation_{timestamp}.md"
        self.save_markdown_report(result, md_file)
        
        logger.info(f"결과 저장 완료: {json_file}, {md_file}")
        
    def save_markdown_report(self, result: Dict[str, Any], filename: str):
        """마크다운 보고서 저장"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# 링크 검증 배치 결과\n\n")
            f.write(f"**검증 시간**: {result['timestamp']}\n")
            f.write(f"**총 검증**: {result['total_links']}건\n")
            f.write(f"**성공**: {result['success_count']}건\n")
            f.write(f"**실패**: {result['failed_count']}건\n")
            f.write(f"**성공률**: {result['success_rate']:.1f}%\n\n")
            
            f.write("## 상세 결과\n\n")
            for link_result in result["results"]:
                status_icon = "✅" if link_result["status"] == "success" else "❌"
                f.write(f"### {link_result['name']}\n")
                f.write(f"- **URL**: {link_result['url']}\n")
                f.write(f"- **상태**: {status_icon} {link_result['status']}\n")
                f.write(f"- **응답 코드**: {link_result.get('status_code', 'N/A')}\n")
                f.write(f"- **응답시간**: {link_result.get('latency_ms', 0)}ms\n")
                f.write(f"- **판정**: {link_result['verdict']}\n\n")
                
    def process_alerts(self, result: Dict[str, Any]):
        """경보 처리"""
        if result["failed_count"] > 0:
            self.consecutive_failures += 1
            self.last_failure_time = datetime.utcnow()
        else:
            if self.consecutive_failures > 0:
                # 정상 복귀
                self.send_alert("L0", "해제", "링크 검증 정상 복귀")
            self.consecutive_failures = 0
            
        # 경보 발송
        if self.consecutive_failures >= 2:
            if self.should_send_alert():
                if self.consecutive_failures >= 5:
                    self.send_alert("L3", "위험", f"연속 {self.consecutive_failures}회 실패")
                elif self.consecutive_failures >= 3:
                    self.send_alert("L2", "주의", f"연속 {self.consecutive_failures}회 실패")
                else:
                    self.send_alert("L1", "경고", f"연속 {self.consecutive_failures}회 실패")
                    
    def should_send_alert(self) -> bool:
        """경보 발송 여부 판단 (15분 중복 억제)"""
        if self.last_failure_time is None:
            return True
            
        time_since_last_alert = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_last_alert > self.alert_suppression_window
        
    def send_alert(self, level: str, title: str, message: str):
        """경보 발송"""
        alert_data = {
            "level": level,
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "consecutive_failures": self.consecutive_failures
        }
        
        logger.info(f"경보 발송: {level} - {title} - {message}")
        
        # 실제 구현에서는 Slack, 이메일 등으로 발송
        if level in ["L2", "L3"]:
            logger.info(f"Slack 알림: {title} - {message}")
            
        if level == "L3":
            logger.info(f"이메일 알림: {title} - {message}")

def main():
    """메인 실행"""
    validator = LinkValidationEnhanced()
    result = validator.run_link_validation()
    
    print(f"링크 검증 완료: {result['success_count']}/{result['total_links']} 성공")
    print(f"성공률: {result['success_rate']:.1f}%")
    print(f"연속 실패: {result['consecutive_failures']}회")

if __name__ == "__main__":
    main()
