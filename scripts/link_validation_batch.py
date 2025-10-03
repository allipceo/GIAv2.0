#!/usr/bin/env python3
"""
링크 검증 배치 스크립트
최근 24시간 대상 링크 수집 및 검증
"""

import time
import json
import os
import logging
import requests
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/link_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_recent_links_from_notion():
    """Notion API로 최근 24시간 링크 수집"""
    try:
        # 실제 환경에서는 Notion API 호출
        # 여기서는 시뮬레이션 데이터
        recent_links = [
            {
                'url': 'https://www.notion.so/Z062_-62d899af747846aa91630239e9120a22',
                'source': 'C2N2',
                'section': '개발결과',
                'created_time': datetime.now().isoformat(),
                'page_id': '62d899af747846aa91630239e9120a22'
            },
            {
                'url': 'https://www.notion.so/Z072_-e69469e716954b1ca7e3ded5736d1603',
                'source': 'C2N3',
                'section': '케이스 3 결과 링크',
                'created_time': datetime.now().isoformat(),
                'page_id': 'e69469e716954b1ca7e3ded5736d1603'
            },
            {
                'url': 'https://example.com/test-link',
                'source': 'TEST',
                'section': '테스트',
                'created_time': datetime.now().isoformat(),
                'page_id': 'test123'
            }
        ]
        
        logger.info(f"최근 24시간 링크 {len(recent_links)}건 수집")
        return recent_links
        
    except Exception as e:
        logger.error(f"링크 수집 실패: {e}")
        return []

def validate_ssl_certificate(url):
    """SSL 인증서 유효성 검증"""
    try:
        parsed = urlparse(url)
        if parsed.scheme != 'https':
            return True, "HTTP (SSL 검증 불필요)"
        
        # SSL 인증서 검증
        context = ssl.create_default_context()
        with requests.Session() as session:
            response = session.get(url, timeout=10, verify=True)
            return True, "SSL 유효"
    except ssl.SSLError as e:
        if "certificate verify failed" in str(e):
            return False, "ssl_invalid_self_signed"
        elif "certificate has expired" in str(e):
            return False, "ssl_expired"
        else:
            return False, f"ssl_error_{str(e)[:20]}"
    except Exception as e:
        return False, f"ssl_unknown_{str(e)[:20]}"

def validate_http_response(url):
    """HTTP 응답 검증 (리다이렉션 1회 허용)"""
    try:
        response = requests.get(
            url, 
            timeout=10, 
            allow_redirects=True, 
            max_redirects=1
        )
        
        if response.status_code == 200:
            return True, "HTTP_200", response.elapsed.total_seconds() * 1000
        else:
            return False, f"HTTP_{response.status_code}", response.elapsed.total_seconds() * 1000
            
    except requests.exceptions.Timeout:
        return False, "HTTP_TIMEOUT", 0
    except requests.exceptions.ConnectionError:
        return False, "HTTP_CONNECTION_ERROR", 0
    except Exception as e:
        return False, f"HTTP_ERROR_{str(e)[:20]}", 0

def validate_url_format(url):
    """URL 형식 검증"""
    try:
        parsed = urlparse(url)
        
        # Notion URL 검증
        if "notion.so" in parsed.netloc:
            if not re.match(r'^https://www\.notion\.so/', url):
                return False, "not_notion_url_format"
            return True, "notion_url_valid"
        
        # 외부 URL 검증 (절대경로)
        if parsed.scheme in ['http', 'https'] and parsed.netloc:
            return True, "external_url_valid"
        else:
            return False, "not_absolute_url"
            
    except Exception as e:
        return False, f"url_parse_error_{str(e)[:20]}"

def validate_single_link(link_info):
    """단일 링크 검증"""
    url = link_info['url']
    source = link_info['source']
    
    logger.info(f"링크 검증: {source} - {url}")
    
    result = {
        'url': url,
        'source': source,
        'section': link_info.get('section', ''),
        'page_id': link_info.get('page_id', ''),
        'created_time': link_info.get('created_time', ''),
        'validation_time': datetime.now().isoformat(),
        'validations': {}
    }
    
    # 1. URL 형식 검증
    format_valid, format_msg = validate_url_format(url)
    result['validations']['format'] = {
        'valid': format_valid,
        'message': format_msg
    }
    
    if not format_valid:
        result['overall_valid'] = False
        result['error_code'] = format_msg
        return result
    
    # 2. HTTP 응답 검증
    http_valid, http_msg, response_time = validate_http_response(url)
    result['validations']['http'] = {
        'valid': http_valid,
        'message': http_msg,
        'response_time_ms': response_time
    }
    
    if not http_valid:
        result['overall_valid'] = False
        result['error_code'] = http_msg
        return result
    
    # 3. SSL 인증서 검증 (HTTPS만)
    if url.startswith('https://'):
        ssl_valid, ssl_msg = validate_ssl_certificate(url)
        result['validations']['ssl'] = {
            'valid': ssl_valid,
            'message': ssl_msg
        }
        
        if not ssl_valid:
            result['overall_valid'] = False
            result['error_code'] = ssl_msg
            return result
    
    # 4. 응답 시간 검증
    if response_time > 3000:
        result['overall_valid'] = False
        result['error_code'] = f"response_time_critical_{response_time:.0f}ms"
        return result
    elif response_time > 1500:
        result['warnings'] = [f"response_time_warning_{response_time:.0f}ms"]
    
    result['overall_valid'] = True
    result['error_code'] = None
    
    logger.info(f"링크 검증 완료: {http_msg}, {response_time:.0f}ms")
    return result

def check_alert_conditions(validation_results):
    """알림 조건 체크"""
    try:
        # 실패 건수 체크
        failed_count = len([r for r in validation_results if not r['overall_valid']])
        
        # P95 위험 체크 (시뮬레이션)
        p95_critical = False  # 실제로는 KPI 데이터에서 가져와야 함
        
        alerts = {
            'link_failures_high': failed_count >= 3,
            'p95_critical': p95_critical,
            'total_failures': failed_count
        }
        
        if alerts['link_failures_high']:
            logger.warning(f"링크 실패 누적: {failed_count}건 >= 3건")
        
        if alerts['p95_critical']:
            logger.warning("P95 위험 상태 지속")
        
        return alerts
        
    except Exception as e:
        logger.error(f"알림 조건 체크 실패: {e}")
        return {}

def save_validation_results(validation_results, alerts):
    """검증 결과 저장"""
    try:
        timestamp = int(time.time())
        
        # JSON 결과 저장
        results_data = {
            'validation_info': {
                'timestamp': timestamp,
                'validation_time': datetime.now().isoformat(),
                'total_links': len(validation_results),
                'valid_links': len([r for r in validation_results if r['overall_valid']]),
                'failed_links': len([r for r in validation_results if not r['overall_valid']])
            },
            'alerts': alerts,
            'detailed_results': validation_results
        }
        
        # JSON 파일 저장
        results_dir = Path('link_validation_results')
        results_dir.mkdir(exist_ok=True)
        
        json_file = results_dir / f'link_validation_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        # 마크다운 보고서 생성
        md_file = results_dir / f'link_validation_{timestamp}.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"""# 링크 검증 배치 결과

**검증 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}
**검증 ID**: {timestamp}

## 검증 요약
- **총 검증**: {len(validation_results)}건
- **성공**: {len([r for r in validation_results if r['overall_valid']])}건
- **실패**: {len([r for r in validation_results if not r['overall_valid']])}건
- **성공률**: {len([r for r in validation_results if r['overall_valid']])/len(validation_results)*100:.1f}%

## 알림 상태
- **링크 실패 누적**: {'🚨 활성' if alerts.get('link_failures_high', False) else '✅ 정상'} ({alerts.get('total_failures', 0)}건)
- **P95 위험**: {'🚨 활성' if alerts.get('p95_critical', False) else '✅ 정상'}

## 상세 결과
""")
            
            for i, result in enumerate(validation_results, 1):
                status = "✅ 성공" if result['overall_valid'] else "❌ 실패"
                f.write(f"\n### {i}. {result['source']} - {result['section']}\n")
                f.write(f"- **URL**: {result['url']}\n")
                f.write(f"- **상태**: {status}\n")
                
                if not result['overall_valid']:
                    f.write(f"- **오류 코드**: {result.get('error_code', 'N/A')}\n")
                
                # 검증 세부사항
                for validation_type, validation_result in result['validations'].items():
                    valid_status = "✅" if validation_result['valid'] else "❌"
                    f.write(f"- **{validation_type}**: {valid_status} {validation_result['message']}\n")
                    
                    if 'response_time_ms' in validation_result:
                        f.write(f"  - 응답시간: {validation_result['response_time_ms']:.0f}ms\n")
                
                if 'warnings' in result:
                    for warning in result['warnings']:
                        f.write(f"- **경고**: {warning}\n")
        
        logger.info(f"검증 결과 저장: {json_file}, {md_file}")
        return json_file, md_file
        
    except Exception as e:
        logger.error(f"검증 결과 저장 실패: {e}")
        raise

def main():
    """메인 실행 함수"""
    try:
        logger.info("링크 검증 배치 시작")
        
        # 최근 24시간 링크 수집
        recent_links = get_recent_links_from_notion()
        
        if not recent_links:
            logger.warning("검증 대상 링크 없음")
            return True
        
        # 링크 검증 실행
        validation_results = []
        for link_info in recent_links:
            result = validate_single_link(link_info)
            validation_results.append(result)
        
        # 알림 조건 체크
        alerts = check_alert_conditions(validation_results)
        
        # 결과 저장
        json_file, md_file = save_validation_results(validation_results, alerts)
        
        logger.info(f"링크 검증 배치 완료: {json_file}, {md_file}")
        
        # 알림 조건 체크
        if any(alerts.values()):
            logger.warning("알림 조건 감지됨 - 알림 훅 실행 필요")
        
        return True
        
    except Exception as e:
        logger.error(f"링크 검증 배치 실패: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
