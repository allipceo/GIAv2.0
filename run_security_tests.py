#!/usr/bin/env python3
"""
STAGE 5-3 보안·가드 테스트 스크립트
5가지 케이스 테스트 및 로그 캡처
"""

import requests
import json
import hmac
import hashlib
import base64
import time
import os
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8080"
HMAC_SECRET = "default_secret_key"  # 서버와 동일한 시크릿

def generate_signature(payload, secret):
    """HMAC-SHA256 서명 생성"""
    # Canonical JSON 생성
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    
    # 현재 시간과 nonce (유효한 타임스탬프)
    ts = str(int(time.time()))
    nonce = f"test-nonce-{int(time.time() * 1000)}"
    
    # 서명 문자열 생성 (헤더의 timestamp 사용)
    input_string = f"{ts}.{nonce}.{canonical}"
    
    # HMAC-SHA256 서명
    signature = hmac.new(
        secret.encode('utf-8'),
        input_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Base64URL 인코딩
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return ts, nonce, signature_b64, canonical

def test_valid_signature():
    """케이스 1: 유효 서명 통과"""
    print("=== 케이스 1: 유효 서명 통과 ===")
    
    payload = {
        "case": "case1",
        "page_id": "test-page-123",
        "action": "test-action"
    }
    
    ts, nonce, sig, canonical = generate_signature(payload, HMAC_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": sig
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook/case1", 
                              json=payload, 
                              headers=headers,
                              timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Request Headers: {headers}")
        print(f"Canonical: {canonical}")
        print(f"Signature: {sig}")
        
        return {
            "case": "valid_signature",
            "status": response.status_code,
            "response": response.text,
            "headers": dict(response.headers),
            "request_headers": headers,
            "canonical": canonical,
            "signature": sig
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"case": "valid_signature", "error": str(e)}

def test_invalid_signature():
    """케이스 2: 서명 불일치 차단"""
    print("\n=== 케이스 2: 서명 불일치 차단 ===")
    
    payload = {
        "case": "case1",
        "page_id": "test-page-123",
        "action": "test-action"
    }
    
    ts, nonce, sig, canonical = generate_signature(payload, "wrong-secret-key")
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": sig
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook/case1", 
                              json=payload, 
                              headers=headers,
                              timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Request Headers: {headers}")
        print(f"Canonical: {canonical}")
        print(f"Signature: {sig}")
        
        return {
            "case": "invalid_signature",
            "status": response.status_code,
            "response": response.text,
            "headers": dict(response.headers),
            "request_headers": headers,
            "canonical": canonical,
            "signature": sig
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"case": "invalid_signature", "error": str(e)}

def test_timestamp_expired():
    """케이스 3: ts 윈도우 초과 차단"""
    print("\n=== 케이스 3: ts 윈도우 초과 차단 ===")
    
    payload = {
        "case": "case1",
        "page_id": "test-page-123",
        "action": "test-action"
    }
    
    # 11분 전 타임스탬프 (윈도우 초과)
    expired_ts = str(int(time.time()) - 660)  # 11분 = 660초
    nonce = f"test-nonce-{int(time.time() * 1000)}"
    
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    input_string = f"{expired_ts}.{nonce}.{canonical}"
    
    signature = hmac.new(
        HMAC_SECRET.encode('utf-8'),
        input_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    sig = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": expired_ts,
        "X-Nonce": nonce,
        "X-Signature": sig
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook/case1", 
                              json=payload, 
                              headers=headers,
                              timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Request Headers: {headers}")
        print(f"Canonical: {canonical}")
        print(f"Signature: {sig}")
        print(f"Expired Timestamp: {expired_ts}")
        
        return {
            "case": "timestamp_expired",
            "status": response.status_code,
            "response": response.text,
            "headers": dict(response.headers),
            "request_headers": headers,
            "canonical": canonical,
            "signature": sig,
            "expired_timestamp": expired_ts
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"case": "timestamp_expired", "error": str(e)}

def test_nonce_reuse():
    """케이스 4: nonce 재사용 차단"""
    print("\n=== 케이스 4: nonce 재사용 차단 ===")
    
    payload = {
        "case": "case1",
        "page_id": "test-page-123",
        "action": "test-action"
    }
    
    # 동일한 nonce 사용
    ts = str(int(time.time()))
    reused_nonce = "reused-nonce-12345"
    
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    input_string = f"{ts}.{reused_nonce}.{canonical}"
    
    signature = hmac.new(
        HMAC_SECRET.encode('utf-8'),
        input_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    sig = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Nonce": reused_nonce,
        "X-Signature": sig
    }
    
    try:
        # 첫 번째 요청
        response1 = requests.post(f"{BASE_URL}/webhook/case1", 
                                json=payload, 
                                headers=headers,
                                timeout=10)
        
        print(f"First Request - Status Code: {response1.status_code}")
        print(f"First Request - Response: {response1.text}")
        
        # 두 번째 요청 (동일한 nonce)
        response2 = requests.post(f"{BASE_URL}/webhook/case1", 
                                json=payload, 
                                headers=headers,
                                timeout=10)
        
        print(f"Second Request - Status Code: {response2.status_code}")
        print(f"Second Request - Response: {response2.text}")
        print(f"Headers: {dict(response2.headers)}")
        print(f"Request Headers: {headers}")
        print(f"Canonical: {canonical}")
        print(f"Signature: {sig}")
        print(f"Reused Nonce: {reused_nonce}")
        
        return {
            "case": "nonce_reuse",
            "first_status": response1.status_code,
            "first_response": response1.text,
            "second_status": response2.status_code,
            "second_response": response2.text,
            "headers": dict(response2.headers),
            "request_headers": headers,
            "canonical": canonical,
            "signature": sig,
            "reused_nonce": reused_nonce
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"case": "nonce_reuse", "error": str(e)}

def test_schema_mismatch():
    """케이스 5: JSON Schema 불일치 또는 옵션 미허용 차단"""
    print("\n=== 케이스 5: JSON Schema 불일치 또는 옵션 미허용 차단 ===")
    
    # 잘못된 스키마의 페이로드
    payload = {
        "case": "case2",  # case2는 다른 스키마 요구
        "page_id": "invalid-page-id",
        "action": "invalid-action",
        "invalid_field": "should_not_exist"
    }
    
    ts, nonce, sig, canonical = generate_signature(payload, HMAC_SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": sig
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook/case2", 
                              json=payload, 
                              headers=headers,
                              timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Request Headers: {headers}")
        print(f"Canonical: {canonical}")
        print(f"Signature: {sig}")
        print(f"Invalid Payload: {payload}")
        
        return {
            "case": "schema_mismatch",
            "status": response.status_code,
            "response": response.text,
            "headers": dict(response.headers),
            "request_headers": headers,
            "canonical": canonical,
            "signature": sig,
            "invalid_payload": payload
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"case": "schema_mismatch", "error": str(e)}

def capture_security_log():
    """보안 로그 캡처"""
    log_files = []
    today = datetime.now().strftime("%Y%m%d")
    
    # 보안 로그 파일 찾기
    for root, dirs, files in os.walk("."):
        for file in files:
            if f"security_{today}" in file and file.endswith(".log"):
                log_files.append(os.path.join(root, file))
    
    print(f"\n=== 보안 로그 파일 발견: {log_files} ===")
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n--- {log_file} (최근 5줄) ---")
                for line in lines[-5:]:
                    # 민감 정보 마스킹
                    masked_line = line.replace(HMAC_SECRET, "***MASKED***")
                    print(masked_line.strip())
        except Exception as e:
            print(f"로그 파일 읽기 오류: {e}")

def main():
    """메인 테스트 실행"""
    print("STAGE 5-3 보안·가드 테스트 시작")
    print("=" * 50)
    
    results = []
    
    # 각 케이스 테스트
    results.append(test_valid_signature())
    results.append(test_invalid_signature())
    results.append(test_timestamp_expired())
    results.append(test_nonce_reuse())
    results.append(test_schema_mismatch())
    
    # 보안 로그 캡처
    capture_security_log()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약:")
    for result in results:
        if "error" in result:
            print(f"❌ {result['case']}: {result['error']}")
        else:
            print(f"✅ {result['case']}: Status {result.get('status', 'N/A')}")
    
    return results

if __name__ == "__main__":
    main()
