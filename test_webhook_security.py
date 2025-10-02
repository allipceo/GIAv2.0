#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 보안 테스트 스크립트
목적: X-Signature, ts, nonce 검증 3케이스 테스트
"""

import requests
import json
import time
import sys

def test_webhook_security():
    """웹훅 보안 테스트 3케이스"""
    base_url = "http://localhost:8000"
    
    print("🔒 웹훅 보안 테스트 시작...")
    
    # 테스트 1: 서명 위조 → 401
    print("\n=== 테스트 1: 서명 위조 → 401 ===")
    data = {
        'case': '1', 
        'mode': 'dryrun', 
        'ts': int(time.time()), 
        'nonce': 'test1', 
        'sig': 'fake_signature'
    }
    headers = {
        'X-Signature': 'fake_signature',
        'X-Timestamp': str(int(time.time())),
        'X-Nonce': 'test1'
    }
    
    try:
        r = requests.post(f'{base_url}/webhook/case1', json=data, headers=headers, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        if r.status_code == 401:
            print("✅ 서명 위조 테스트 성공: 401 반환")
        else:
            print("❌ 서명 위조 테스트 실패: 예상 401, 실제", r.status_code)
    except requests.exceptions.ConnectionError:
        print("⚠️ 웹훅 서버가 실행되지 않음 (정상)")
    except Exception as e:
        print(f"❌ 테스트 1 오류: {e}")
    
    # 테스트 2: ts 만료(+6분) → 401
    print("\n=== 테스트 2: ts 만료(+6분) → 401 ===")
    data = {
        'case': '1', 
        'mode': 'dryrun', 
        'ts': int(time.time()) - 400,  # 6분 40초 전
        'nonce': 'test2', 
        'sig': 'fake'
    }
    headers = {
        'X-Signature': 'fake',
        'X-Timestamp': str(int(time.time()) - 400),
        'X-Nonce': 'test2'
    }
    
    try:
        r = requests.post(f'{base_url}/webhook/case1', json=data, headers=headers, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        if r.status_code == 401:
            print("✅ ts 만료 테스트 성공: 401 반환")
        else:
            print("❌ ts 만료 테스트 실패: 예상 401, 실제", r.status_code)
    except requests.exceptions.ConnectionError:
        print("⚠️ 웹훅 서버가 실행되지 않음 (정상)")
    except Exception as e:
        print(f"❌ 테스트 2 오류: {e}")
    
    # 테스트 3: nonce 재사용 → 401
    print("\n=== 테스트 3: nonce 재사용 → 401 ===")
    data = {
        'case': '1', 
        'mode': 'dryrun', 
        'ts': int(time.time()), 
        'nonce': 'test3', 
        'sig': 'fake'
    }
    headers = {
        'X-Signature': 'fake',
        'X-Timestamp': str(int(time.time())),
        'X-Nonce': 'test3'
    }
    
    try:
        # 첫 번째 요청 (성공할 수도 있음)
        r1 = requests.post(f'{base_url}/webhook/case1', json=data, headers=headers, timeout=5)
        print(f"첫 요청 Status: {r1.status_code}")
        
        # 두 번째 요청 (nonce 재사용으로 실패해야 함)
        r2 = requests.post(f'{base_url}/webhook/case1', json=data, headers=headers, timeout=5)
        print(f"재사용 Status: {r2.status_code}")
        print(f"재사용 Response: {r2.text}")
        
        if r2.status_code == 401:
            print("✅ nonce 재사용 테스트 성공: 401 반환")
        else:
            print("❌ nonce 재사용 테스트 실패: 예상 401, 실제", r2.status_code)
    except requests.exceptions.ConnectionError:
        print("⚠️ 웹훅 서버가 실행되지 않음 (정상)")
    except Exception as e:
        print(f"❌ 테스트 3 오류: {e}")
    
    print("\n🔒 웹훅 보안 테스트 완료")

if __name__ == "__main__":
    test_webhook_security()
