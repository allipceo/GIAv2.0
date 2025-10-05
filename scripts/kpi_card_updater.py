#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAGE 5-5 KPI 카드 업데이트
목적: 48h·7d KPI 자동 갱신 및 Notion 카드 업데이트
"""

import json
import time
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import requests

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KPICardUpdater:
    def __init__(self):
        """KPI 카드 업데이트 초기화"""
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.kpi_database_id = os.getenv("KPI_DATABASE_ID")
        
    def update_kpi_cards(self):
        """KPI 카드 업데이트"""
        logger.info("KPI 카드 업데이트 시작")
        
        try:
            # 48h KPI 계산
            kpi_48h = self.calculate_48h_kpi()
            
            # 7d KPI 계산
            kpi_7d = self.calculate_7d_kpi()
            
            # KPI 데이터 구성
            kpi_data = {
                "48h_kpi": kpi_48h,
                "7d_kpi": kpi_7d,
                "last_updated": datetime.utcnow().isoformat(),
                "trend": self.calculate_trend(kpi_48h, kpi_7d)
            }
            
            # Notion 카드 업데이트
            self.update_notion_cards(kpi_data)
            
            # 결과 저장
            self.save_kpi_snapshot(kpi_data)
            
            logger.info("KPI 카드 업데이트 완료")
            return kpi_data
            
        except Exception as e:
            logger.error(f"KPI 카드 업데이트 실패: {e}")
            raise
            
    def calculate_48h_kpi(self) -> Dict[str, Any]:
        """48시간 KPI 계산"""
        # 실제 KPI 계산 로직 (예시)
        return {
            "success_rate": 95.2,
            "p95_latency_ms": 1200,
            "total_requests": 1500,
            "failed_requests": 72,
            "avg_latency_ms": 850,
            "error_rate": 4.8
        }
        
    def calculate_7d_kpi(self) -> Dict[str, Any]:
        """7일 KPI 계산"""
        # 실제 KPI 계산 로직 (예시)
        return {
            "success_rate": 94.8,
            "p95_latency_ms": 1350,
            "total_requests": 10500,
            "failed_requests": 546,
            "avg_latency_ms": 920,
            "error_rate": 5.2
        }
        
    def calculate_trend(self, kpi_48h: Dict[str, Any], kpi_7d: Dict[str, Any]) -> Dict[str, str]:
        """트렌드 계산"""
        trend = {}
        
        # 성공률 트렌드
        if kpi_48h["success_rate"] > kpi_7d["success_rate"]:
            trend["success_rate"] = "↗️ 상승"
        elif kpi_48h["success_rate"] < kpi_7d["success_rate"]:
            trend["success_rate"] = "↘️ 하락"
        else:
            trend["success_rate"] = "➡️ 동일"
            
        # P95 지연시간 트렌드
        if kpi_48h["p95_latency_ms"] < kpi_7d["p95_latency_ms"]:
            trend["p95_latency"] = "↗️ 개선"
        elif kpi_48h["p95_latency_ms"] > kpi_7d["p95_latency_ms"]:
            trend["p95_latency"] = "↘️ 악화"
        else:
            trend["p95_latency"] = "➡️ 동일"
            
        return trend
        
    def update_notion_cards(self, kpi_data: Dict[str, Any]):
        """Notion 카드 업데이트"""
        if not self.notion_token or not self.kpi_database_id:
            logger.warning("Notion 토큰 또는 데이터베이스 ID가 설정되지 않음")
            return
            
        # 48h KPI 카드 업데이트
        self.update_48h_card(kpi_data["48h_kpi"], kpi_data["trend"])
        
        # 7d KPI 카드 업데이트
        self.update_7d_card(kpi_data["7d_kpi"], kpi_data["trend"])
        
    def update_48h_card(self, kpi_48h: Dict[str, Any], trend: Dict[str, str]):
        """48h KPI 카드 업데이트"""
        # Notion API를 통한 카드 업데이트
        logger.info("48h KPI 카드 업데이트")
        
        # 실제 구현에서는 Notion API 호출
        card_data = {
            "title": "48시간 KPI",
            "success_rate": f"{kpi_48h['success_rate']:.1f}%",
            "p95_latency": f"{kpi_48h['p95_latency_ms']}ms",
            "trend": trend["success_rate"],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        logger.info(f"48h KPI 카드 데이터: {card_data}")
        
    def update_7d_card(self, kpi_7d: Dict[str, Any], trend: Dict[str, str]):
        """7d KPI 카드 업데이트"""
        # Notion API를 통한 카드 업데이트
        logger.info("7d KPI 카드 업데이트")
        
        # 실제 구현에서는 Notion API 호출
        card_data = {
            "title": "7일 KPI",
            "success_rate": f"{kpi_7d['success_rate']:.1f}%",
            "p95_latency": f"{kpi_7d['p95_latency_ms']}ms",
            "trend": trend["success_rate"],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        logger.info(f"7d KPI 카드 데이터: {card_data}")
        
    def save_kpi_snapshot(self, kpi_data: Dict[str, Any]):
        """KPI 스냅샷 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 파일 저장
        json_file = f"kpi_snapshots/kpi_snapshot_{timestamp}.json"
        os.makedirs("kpi_snapshots", exist_ok=True)
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(kpi_data, f, ensure_ascii=False, indent=2)
            
        # MD 파일 저장
        md_file = f"kpi_snapshots/kpi_snapshot_{timestamp}.md"
        self.save_markdown_report(kpi_data, md_file)
        
        logger.info(f"KPI 스냅샷 저장 완료: {json_file}, {md_file}")
        
    def save_markdown_report(self, kpi_data: Dict[str, Any], filename: str):
        """마크다운 보고서 저장"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# KPI 카드 업데이트 결과\n\n")
            f.write(f"**업데이트 시간**: {kpi_data['last_updated']}\n\n")
            
            # 48h KPI
            f.write("## 48시간 KPI\n\n")
            f.write(f"- **성공률**: {kpi_data['48h_kpi']['success_rate']:.1f}%\n")
            f.write(f"- **P95 지연시간**: {kpi_data['48h_kpi']['p95_latency_ms']}ms\n")
            f.write(f"- **총 요청수**: {kpi_data['48h_kpi']['total_requests']:,}건\n")
            f.write(f"- **실패 요청수**: {kpi_data['48h_kpi']['failed_requests']:,}건\n")
            f.write(f"- **평균 지연시간**: {kpi_data['48h_kpi']['avg_latency_ms']}ms\n")
            f.write(f"- **에러율**: {kpi_data['48h_kpi']['error_rate']:.1f}%\n\n")
            
            # 7d KPI
            f.write("## 7일 KPI\n\n")
            f.write(f"- **성공률**: {kpi_data['7d_kpi']['success_rate']:.1f}%\n")
            f.write(f"- **P95 지연시간**: {kpi_data['7d_kpi']['p95_latency_ms']}ms\n")
            f.write(f"- **총 요청수**: {kpi_data['7d_kpi']['total_requests']:,}건\n")
            f.write(f"- **실패 요청수**: {kpi_data['7d_kpi']['failed_requests']:,}건\n")
            f.write(f"- **평균 지연시간**: {kpi_data['7d_kpi']['avg_latency_ms']}ms\n")
            f.write(f"- **에러율**: {kpi_data['7d_kpi']['error_rate']:.1f}%\n\n")
            
            # 트렌드
            f.write("## 트렌드 분석\n\n")
            f.write(f"- **성공률 트렌드**: {kpi_data['trend']['success_rate']}\n")
            f.write(f"- **P95 지연시간 트렌드**: {kpi_data['trend']['p95_latency']}\n\n")

def main():
    """메인 실행"""
    updater = KPICardUpdater()
    result = updater.update_kpi_cards()
    
    print("KPI 카드 업데이트 완료")
    print(f"48h 성공률: {result['48h_kpi']['success_rate']:.1f}%")
    print(f"7d 성공률: {result['7d_kpi']['success_rate']:.1f}%")
    print(f"트렌드: {result['trend']['success_rate']}")

if __name__ == "__main__":
    main()
