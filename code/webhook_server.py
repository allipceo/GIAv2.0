#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 프로젝트 웹훅 서버
작성일: 2025년 8월 18일
작성자: 서대리 (Lead Developer)
목적: 과업지시서 V1.2에 따른 4단계 - 실제 웹훅 연동
"""

import requests
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
import threading

# 노션 API 설정
NOTION_TOKEN = ""
COMPANY_DB_ID = "253a613d-25ff-819b-acfe-fa0547939de1"  # 조사 대상 기업 DB

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

app = Flask(__name__)

def process_phase3_analysis(page_id, company_name):
    """Phase 3 분석 실행 처리"""
    print(f"🔄 {company_name} Phase 3 분석 시작...")
    
    # 1. 실행 상태를 "실행중"으로 업데이트
    update_execution_status(page_id, "실행중", f"Phase 3 분석 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. 시뮬레이션: 분석 작업 수행 (실제로는 AI 분석 로직)
    print(f"⏳ {company_name} 분석 진행 중...")
    time.sleep(5)  # 5초 대기 (실제 분석 시간 시뮬레이션)
    
    # 3. 분석 결과 생성
    analysis_result = generate_analysis_result(company_name)
    
    # 4. 실행 상태를 "완료"로 업데이트
    update_execution_status(page_id, "완료", analysis_result)
    
    # 5. 체크박스 해제
    update_phase3_checkbox(page_id, False)
    
    print(f"✅ {company_name} Phase 3 분석 완료!")

def update_execution_status(page_id, status, result):
    """실행 상태 업데이트"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "실행 상태": {
                "select": {
                    "name": status
                }
            },
            "실행 일시": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "실행 결과": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": result
                        }
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print(f"✅ 실행 상태 업데이트: {status}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 실행 상태 업데이트 실패: {e}")
        return False

def update_phase3_checkbox(page_id, checked):
    """Phase 3 분석 실행 체크박스 업데이트"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "Phase 3 분석 실행": {
                "checkbox": checked
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print(f"✅ 체크박스 업데이트: {checked}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 체크박스 업데이트 실패: {e}")
        return False

def generate_analysis_result(company_name):
    """분석 결과 생성 (시뮬레이션)"""
    results = {
        "한진중공업": "해외 원전 사업 진출을 위한 맞춤형 보험 제안서 생성 완료. 주요 리스크: 정치적 불안정, 환율 변동, 기술 이전 제한. 추천 보험: 정치적 리스크 보험, 환율 헤지, 기술 보험.",
        "효성중공업": "신재생 에너지 기술 보험 분석 완료. 핵심 기술: ESS, 태양광 패널, 풍력 발전. 추천 보험: 기술 보험, 환경 책임 보험, 사업 중단 보험.",
        "두산에너빌리티": "해외 원전 특화 보험 제안서 완성. 핵심 제안: 원자력 책임 보험, 건설 All Risk, 운영 중단 보험, 정치적 리스크 보험."
    }
    
    return results.get(company_name, f"{company_name} 분석 완료 - 기본 결과")

def get_company_name(page_id):
    """페이지 ID로 기업명 조회"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        result = response.json()
        properties = result.get("properties", {})
        company_name = properties.get("기업명", {}).get("title", [{}])[0].get("text", {}).get("content", "Unknown")
        
        return company_name
    except requests.exceptions.RequestException as e:
        print(f"❌ 기업명 조회 실패: {e}")
        return "Unknown"

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """웹훅 핸들러"""
    try:
        data = request.get_json()
        print(f"📡 웹훅 수신: {json.dumps(data, indent=2)}")
        
        # 웹훅 데이터 파싱
        event_type = data.get("type", "")
        
        if event_type == "page.updated":
            page_id = data.get("page", {}).get("id", "")
            properties = data.get("page", {}).get("properties", {})
            
            # Phase 3 분석 실행 체크박스 변경 확인
            phase3_check = properties.get("Phase 3 분석 실행", {}).get("checkbox", False)
            
            if phase3_check:
                company_name = get_company_name(page_id)
                print(f"🎯 {company_name} Phase 3 분석 실행 감지!")
                
                # 별도 스레드에서 분석 실행 (비동기 처리)
                thread = threading.Thread(target=process_phase3_analysis, args=(page_id, company_name))
                thread.start()
                
                return jsonify({"status": "success", "message": f"{company_name} Phase 3 분석 시작"})
        
        return jsonify({"status": "success", "message": "웹훅 처리 완료"})
        
    except Exception as e:
        print(f"❌ 웹훅 처리 오류: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/test', methods=['GET'])
def test_webhook():
    """웹훅 테스트"""
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
    
    print("🧪 웹훅 테스트 실행...")
    response = requests.post("http://localhost:5000/webhook", json=test_data)
    
    return jsonify({
        "status": "test_completed",
        "response": response.json() if response.ok else response.text
    })

def main():
    """메인 실행 함수"""
    print("🚀 GIA 프로젝트 웹훅 서버 시작...")
    print("=" * 50)
    print("📡 웹훅 엔드포인트: http://localhost:5000/webhook")
    print("🏥 헬스 체크: http://localhost:5000/health")
    print("🧪 테스트: http://localhost:5000/test")
    print("=" * 50)
    print("💡 서버를 중지하려면 Ctrl+C를 누르세요.")
    
    # Flask 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()

