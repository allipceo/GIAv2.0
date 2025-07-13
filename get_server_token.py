#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실행 중인 웹훅 서버에서 실제 토큰을 가져오는 스크립트
"""
import requests
import json

def get_server_token():
    """웹훅 서버에서 실제 토큰을 가져옴"""
    try:
        response = requests.get("http://localhost:8000/status")
        if response.status_code == 200:
            data = response.json()
            token = data.get('webhook_token', '')
            print(f"🔑 실제 서버 토큰: {token}")
            return token
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return None

def test_with_real_token():
    """실제 토큰으로 테스트"""
    token = get_server_token()
    if not token:
        return False
    
    print(f"\n🧪 실제 토큰으로 테스트: {token[:30]}...")
    
    # 테스트 엔드포인트 호출
    try:
        response = requests.get("http://localhost:8000/test", params={"token": token})
        print(f"✅ 테스트 결과: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - 상태: {data.get('status', 'unknown')}")
            print(f"   - 메시지: {data.get('message', 'unknown')}")
            print(f"   - 브랜치: {data.get('branch', 'unknown')}")
            
            # 노션 버튼용 URL 생성
            print(f"\n🔗 노션 버튼용 URL:")
            print(f"   - 테스트: http://localhost:8000/test?token={token}")
            print(f"   - 전체 아카이브: http://localhost:8000/archive_trigger?token={token}&archive_type=both")
            
            return True
        else:
            print(f"❌ 테스트 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 요청 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_with_real_token()
    if success:
        print("\n🎉 웹훅 서버 테스트 성공! 노션 버튼 생성 준비 완료!")
    else:
        print("\n❌ 웹훅 서버 테스트 실패.") 