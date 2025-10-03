#!/usr/bin/env python3
"""
링크 유효성 검증 스크립트
C2N2: Z062 "개발결과" 섹션 링크
C2N3: Z072 "케이스 3 결과 링크" 섹션 링크
"""

import requests
import ssl
import time
import json
from datetime import datetime
from urllib.parse import urlparse
import re

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

def validate_single_link(url, link_name):
    """단일 링크 검증"""
    print(f"🔍 검증 중: {link_name}")
    print(f"   URL: {url}")
    
    result = {
        'url': url,
        'link_name': link_name,
        'timestamp': datetime.now().isoformat(),
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
    
    print(f"   ✅ 검증 완료: {http_msg}, {response_time:.0f}ms")
    return result

def run_link_validation():
    """링크 유효성 검증 실행"""
    print("🔗 링크 유효성 검증 시작")
    print("=" * 60)
    
    # 검증 대상 링크 (실제로는 Notion API에서 가져와야 함)
    test_links = [
        {
            'url': 'https://www.notion.so/Z062_-62d899af747846aa91630239e9120a22',
            'name': 'Z062 개발결과 섹션',
            'source': 'C2N2'
        },
        {
            'url': 'https://www.notion.so/Z072_-e69469e716954b1ca7e3ded5736d1603',
            'name': 'Z072 케이스 3 결과 링크',
            'source': 'C2N3'
        },
        {
            'url': 'https://example.com/test-link',
            'name': '외부 테스트 링크',
            'source': 'TEST'
        }
    ]
    
    results = []
    valid_count = 0
    total_count = len(test_links)
    
    for link in test_links:
        result = validate_single_link(link['url'], link['name'])
        result['source'] = link['source']
        results.append(result)
        
        if result['overall_valid']:
            valid_count += 1
        
        print()  # 빈 줄 추가
    
    # 결과 요약
    success_rate = (valid_count / total_count) * 100 if total_count > 0 else 0
    
    print("=" * 60)
    print("📊 검증 결과 요약")
    print(f"총 검증: {total_count}건")
    print(f"성공: {valid_count}건")
    print(f"실패: {total_count - valid_count}건")
    print(f"성공률: {success_rate:.1f}%")
    
    # 실패 원인 분석
    error_codes = {}
    for result in results:
        if not result['overall_valid']:
            error_code = result.get('error_code', 'unknown')
            error_codes[error_code] = error_codes.get(error_code, 0) + 1
    
    if error_codes:
        print("\n❌ 실패 원인 분포:")
        for error_code, count in error_codes.items():
            print(f"  {error_code}: {count}건")
    
    # 결과를 파일로 저장
    timestamp = int(time.time())
    report = {
        'validation_info': {
            'timestamp': timestamp,
            'validation_time': datetime.now().isoformat(),
            'total_links': total_count,
            'valid_links': valid_count,
            'success_rate': success_rate
        },
        'error_analysis': error_codes,
        'detailed_results': results
    }
    
    # JSON 리포트 저장
    with open(f'link_validation_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 마크다운 리포트 생성
    with open(f'link_validation_{timestamp}.md', 'w', encoding='utf-8') as f:
        f.write(f"""# 링크 유효성 검증 결과

**검증 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}
**검증 ID**: {timestamp}

## 검증 요약
- **총 검증**: {total_count}건
- **성공**: {valid_count}건
- **실패**: {total_count - valid_count}건
- **성공률**: {success_rate:.1f}%

## 실패 원인 분석
""")
        
        if error_codes:
            for error_code, count in error_codes.items():
                f.write(f"- **{error_code}**: {count}건\n")
        else:
            f.write("- 실패 없음\n")
        
        f.write("\n## 상세 결과\n")
        
        for i, result in enumerate(results, 1):
            status = "✅ 성공" if result['overall_valid'] else "❌ 실패"
            f.write(f"\n### {i}. {result['link_name']} ({result['source']})\n")
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
    
    print(f"📁 리포트 저장: link_validation_{timestamp}.md")
    return success_rate >= 100.0  # 100% 성공 시 통과

if __name__ == "__main__":
    success = run_link_validation()
    print(f"🎯 검증 결과: {'통과' if success else '실패'}")
