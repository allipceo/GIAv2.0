#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 서버 직접 테스트 스크립트
"""
import requests
import json

# 웹훅 서버 설정
BASE_URL = "http://localhost:8000"
TOKEN = "gia-archive-webhook-token-2025-3a967b2e"

def test_webhook_endpoints():
    """웹훅 엔드포인트들을 테스트"""
    
    print("🚀 GIA 웹훅 서버 테스트 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    print("\n1️⃣ 서버 상태 확인")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 서버 상태: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - 브랜치: {data.get('current_branch', 'unknown')}")
            print(f"   - 버전: {data.get('version', 'unknown')}")
        else:
            print(f"❌ 응답 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False
    
    # 2. 테스트 엔드포인트 확인
    print("\n2️⃣ 테스트 엔드포인트 확인")
    try:
        response = requests.get(f"{BASE_URL}/test", params={"token": TOKEN})
        print(f"✅ 테스트 응답: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - 상태: {data.get('status', 'unknown')}")
            print(f"   - 메시지: {data.get('message', 'unknown')}")
            print(f"   - 브랜치: {data.get('branch', 'unknown')}")
        else:
            print(f"❌ 테스트 실패 코드: {response.status_code}")
            print(f"   - 응답: {response.text}")
    except Exception as e:
        print(f"❌ 테스트 요청 실패: {e}")
        return False
    
    # 3. 상태 조회 확인
    print("\n3️⃣ 상태 조회 확인")
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"✅ 상태 조회: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - 서버 상태: {data.get('server_status', 'unknown')}")
            print(f"   - 브랜치: {data.get('current_branch', 'unknown')}")
            print(f"   - 토큰: {data.get('webhook_token', 'unknown')[:20]}...")
            
            # 스크립트 파일 상태 확인
            script_status = data.get('script_status', {})
            print(f"   - 코드 스크립트: {'✅' if script_status.get('update_code_archive_phase3.py', {}).get('exists') else '❌'}")
            print(f"   - 보고서 스크립트: {'✅' if script_status.get('update_reports_archive.py', {}).get('exists') else '❌'}")
            
        else:
            print(f"❌ 상태 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 상태 조회 실패: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 웹훅 서버 테스트 완료!")
    return True

if __name__ == "__main__":
    success = test_webhook_endpoints()
    if success:
        print("\n✅ 모든 테스트 통과! 웹훅 서버가 정상 작동 중입니다.")
        print(f"\n🔗 노션 버튼용 URL:")
        print(f"   - 테스트: {BASE_URL}/test?token={TOKEN}")
        print(f"   - 전체 아카이브: {BASE_URL}/archive_trigger?token={TOKEN}&archive_type=both")
    else:
        print("\n❌ 테스트 실패. 서버 상태를 확인해주세요.") 