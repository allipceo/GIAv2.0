#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 프로젝트 웹훅 서버 테스트 스크립트
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 웹훅 서버 기능 테스트
"""

import requests
import json
import time

def test_webhook_server():
    """웹훅 서버 테스트"""
    base_url = "http://localhost:5000"
    
    print("🧪 웹훅 서버 테스트 시작...")
    print("=" * 50)
    
    # 1. 헬스 체크
    print("1️⃣ 헬스 체크 테스트...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.ok:
            print("✅ 웹훅 서버가 정상적으로 실행 중입니다.")
            print(f"   응답: {response.json()}")
        else:
            print("❌ 웹훅 서버 연결 실패")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 웹훅 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return False
    
    # 2. 웹훅 테스트
    print("\n2️⃣ 웹훅 기능 테스트...")
    test_data = {
        "type": "page.updated",
        "page": {
            "id": "test_page_id",
            "properties": {
                "Phase 3 분석 실행": {
                    "checkbox": True
                }
            }
        }
    }
    
    try:
        response = requests.post(f"{base_url}/webhook", json=test_data)
        if response.ok:
            result = response.json()
            print("✅ 웹훅 처리 성공!")
            print(f"   응답: {result}")
        else:
            print(f"❌ 웹훅 처리 실패: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 웹훅 테스트 실패: {e}")
    
    # 3. 테스트 엔드포인트 호출
    print("\n3️⃣ 테스트 엔드포인트 호출...")
    try:
        response = requests.get(f"{base_url}/test")
        if response.ok:
            result = response.json()
            print("✅ 테스트 엔드포인트 호출 성공!")
            print(f"   응답: {result}")
        else:
            print(f"❌ 테스트 엔드포인트 호출 실패: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 테스트 엔드포인트 호출 실패: {e}")
    
    print("\n🎉 웹훅 서버 테스트 완료!")
    print("=" * 50)
    print("📝 다음 단계:")
    print("   1. Notion에서 Phase 3 분석 실행 체크박스를 클릭")
    print("   2. 웹훅 서버 로그에서 자동화 워크플로우 실행 확인")
    print("   3. Notion DB에서 실행 상태 및 결과 업데이트 확인")
    
    return True

def main():
    """메인 실행 함수"""
    print("🚀 GIA 프로젝트 웹훅 서버 테스트 시작...")
    
    # 웹훅 서버가 시작될 때까지 잠시 대기
    print("⏳ 웹훅 서버 시작 대기 중... (5초)")
    time.sleep(5)
    
    # 테스트 실행
    success = test_webhook_server()
    
    if success:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    main()
