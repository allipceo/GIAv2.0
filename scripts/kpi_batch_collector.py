#!/usr/bin/env python3
"""
KPI 자동 수집 배치 스크립트
Linux cron 기반 일 1회 실행
"""

import time
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/kpi_batch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_kpi_metrics():
    """KPI 메트릭 수집"""
    try:
        current_time = int(time.time())
        
        # 7일 rolling 윈도우 계산
        start_ts = current_time - (7 * 24 * 60 * 60)  # 7일 전
        end_ts = current_time
        
        # 실제 환경에서는 Notion API, 데이터베이스 등에서 수집
        # 여기서는 시뮬레이션 데이터 생성
        kpi_data = {
            'collection_info': {
                'timestamp': current_time,
                'collection_time': datetime.now().isoformat(),
                'window_start': start_ts,
                'window_end': end_ts,
                'window_days': 7
            },
            'current_session': {
                'total_executions': 10,
                'success_count': 10,
                'success_rate': 1.0,
                'p95_latency_ms': 4200,
                'avg_latency_ms': 3100,
                'max_latency_ms': 4800,
                'dedup_skip_rate': 0.0
            },
            'rolling_7d': {
                'total_executions': 100,
                'success_count': 95,
                'success_rate': 0.95,
                'p95_latency_ms': 5800,
                'avg_latency_ms': 4500,
                'failures_by_cause': {
                    'network': 2,
                    'options': 2,
                    'schema': 1,
                    'permission': 0,
                    'other': 0
                }
            },
            'thresholds': {
                'p95_warning_ms': 6000,
                'p95_critical_ms': 8000,
                'success_rate_min': 0.90,
                'link_failure_max': 3
            },
            'alerts': {
                'p95_critical': False,
                'success_rate_low': False,
                'link_failures_high': False
            }
        }
        
        # 임계값 체크
        if kpi_data['current_session']['p95_latency_ms'] > kpi_data['thresholds']['p95_critical_ms']:
            kpi_data['alerts']['p95_critical'] = True
            logger.warning(f"P95 위험 초과: {kpi_data['current_session']['p95_latency_ms']}ms > {kpi_data['thresholds']['p95_critical_ms']}ms")
        
        if kpi_data['rolling_7d']['success_rate'] < kpi_data['thresholds']['success_rate_min']:
            kpi_data['alerts']['success_rate_low'] = True
            logger.warning(f"7일 성공률 저하: {kpi_data['rolling_7d']['success_rate']:.2%} < {kpi_data['thresholds']['success_rate_min']:.2%}")
        
        return kpi_data
        
    except Exception as e:
        logger.error(f"KPI 수집 실패: {e}")
        raise

def save_kpi_snapshot(kpi_data):
    """KPI 스냅샷 저장"""
    try:
        timestamp = kpi_data['collection_info']['timestamp']
        
        # metrics 디렉토리 생성
        metrics_dir = Path('metrics')
        metrics_dir.mkdir(exist_ok=True)
        
        # JSON 파일 저장
        json_file = metrics_dir / f'kpi_snapshot_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(kpi_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"KPI 스냅샷 저장: {json_file}")
        return json_file
        
    except Exception as e:
        logger.error(f"KPI 스냅샷 저장 실패: {e}")
        raise

def generate_kpi_summary(kpi_data):
    """KPI 요약 보고서 생성"""
    try:
        timestamp = kpi_data['collection_info']['timestamp']
        
        # 마크다운 요약 생성
        summary_content = f"""# KPI 배치 수집 보고서

**수집 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}
**수집 ID**: {timestamp}
**윈도우**: 7일 rolling

## 현재 세션 지표
- **총 실행**: {kpi_data['current_session']['total_executions']}건
- **성공**: {kpi_data['current_session']['success_count']}건
- **성공률**: {kpi_data['current_session']['success_rate']:.1%}
- **P95 지연시간**: {kpi_data['current_session']['p95_latency_ms']}ms
- **평균 지연시간**: {kpi_data['current_session']['avg_latency_ms']}ms
- **중복 스킵률**: {kpi_data['current_session']['dedup_skip_rate']:.1%}

## 7일 Rolling 지표
- **총 실행**: {kpi_data['rolling_7d']['total_executions']}건
- **성공**: {kpi_data['rolling_7d']['success_count']}건
- **성공률**: {kpi_data['rolling_7d']['success_rate']:.1%}
- **P95 지연시간**: {kpi_data['rolling_7d']['p95_latency_ms']}ms
- **평균 지연시간**: {kpi_data['rolling_7d']['avg_latency_ms']}ms

## 실패 원인 분포 (7일)
"""
        
        for cause, count in kpi_data['rolling_7d']['failures_by_cause'].items():
            summary_content += f"- **{cause}**: {count}건\n"
        
        summary_content += f"""
## 임계값 상태
- **P95 경고**: >{kpi_data['thresholds']['p95_warning_ms']}ms (현재: {kpi_data['current_session']['p95_latency_ms']}ms) {'✅' if kpi_data['current_session']['p95_latency_ms'] <= kpi_data['thresholds']['p95_warning_ms'] else '⚠️'}
- **P95 위험**: >{kpi_data['thresholds']['p95_critical_ms']}ms (현재: {kpi_data['current_session']['p95_latency_ms']}ms) {'✅' if kpi_data['current_session']['p95_latency_ms'] <= kpi_data['thresholds']['p95_critical_ms'] else '🚨'}
- **성공률 최소**: >{kpi_data['thresholds']['success_rate_min']:.1%} (현재: {kpi_data['rolling_7d']['success_rate']:.1%}) {'✅' if kpi_data['rolling_7d']['success_rate'] >= kpi_data['thresholds']['success_rate_min'] else '⚠️'}

## 알림 상태
- **P95 위험**: {'🚨 활성' if kpi_data['alerts']['p95_critical'] else '✅ 정상'}
- **성공률 저하**: {'⚠️ 활성' if kpi_data['alerts']['success_rate_low'] else '✅ 정상'}
- **링크 실패 누적**: {'🚨 활성' if kpi_data['alerts']['link_failures_high'] else '✅ 정상'}
"""
        
        # 마크다운 파일 저장
        metrics_dir = Path('metrics')
        md_file = metrics_dir / f'kpi_summary_{timestamp}.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        logger.info(f"KPI 요약 저장: {md_file}")
        return md_file
        
    except Exception as e:
        logger.error(f"KPI 요약 생성 실패: {e}")
        raise

def main():
    """메인 실행 함수"""
    try:
        logger.info("KPI 배치 수집 시작")
        
        # KPI 메트릭 수집
        kpi_data = collect_kpi_metrics()
        
        # 스냅샷 저장
        json_file = save_kpi_snapshot(kpi_data)
        
        # 요약 생성
        md_file = generate_kpi_summary(kpi_data)
        
        logger.info(f"KPI 배치 수집 완료: {json_file}, {md_file}")
        
        # 알림 체크
        if any(kpi_data['alerts'].values()):
            logger.warning("알림 조건 감지됨 - 알림 훅 실행 필요")
        
        return True
        
    except Exception as e:
        logger.error(f"KPI 배치 수집 실패: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
