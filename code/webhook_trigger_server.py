#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 기반 뉴스 자동화 트리거 서버
작성일: 2025년 1월 12일
목적: 외부 자동화 도구(Zapier, Make.com)에서 웹훅으로 뉴스 수집 실행

사용법:
1. 이 서버를 백그라운드에서 실행
2. Zapier/Make.com에서 Notion 변화 감지
3. 웹훅으로 http://localhost:8080/trigger-news 호출
4. 자동으로 뉴스 수집 실행
"""

from flask import Flask, request, jsonify
import subprocess
import sys
import logging
import threading
from datetime import datetime

# Flask 앱 설정
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_trigger.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def execute_news_automation():
    """뉴스 자동화 스크립트 실행 (백그라운드)"""
    try:
        logging.info("🚀 뉴스 자동화 백그라운드 실행 시작...")
        
        result = subprocess.run(
            [sys.executable, "run_news_automation.py"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd="D:/AI_Project/GIAv2.0"
        )
        
        if result.returncode == 0:
            logging.info("✅ 뉴스 자동화 성공 완료")
        else:
            logging.error(f"❌ 뉴스 자동화 실패: {result.stderr}")
            
    except Exception as e:
        logging.error(f"❌ 실행 중 오류: {str(e)}")

@app.route('/trigger-news', methods=['POST', 'GET'])
def trigger_news_collection():
    """뉴스 수집 트리거 엔드포인트"""
    try:
        # 요청 정보 로깅
        client_ip = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logging.info(f"🎯 뉴스 수집 트리거 요청 수신 - IP: {client_ip}, 시간: {timestamp}")
        
        # POST 데이터 확인 (Zapier/Make.com에서 전송된 데이터)
        if request.method == 'POST':
            data = request.get_json() or {}
            logging.info(f"📋 수신 데이터: {data}")
        
        # 백그라운드에서 뉴스 자동화 실행
        thread = threading.Thread(target=execute_news_automation)
        thread.daemon = True
        thread.start()
        
        # 즉시 응답 반환
        response = {
            "status": "success",
            "message": "뉴스 수집이 백그라운드에서 시작되었습니다",
            "timestamp": timestamp,
            "client_ip": client_ip
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logging.error(f"❌ 트리거 처리 중 오류: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """서버 상태 확인 엔드포인트"""
    return jsonify({
        "status": "running",
        "message": "뉴스 자동화 웹훅 서버가 정상 동작 중입니다",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "endpoints": {
            "trigger": "/trigger-news (POST/GET)",
            "status": "/status (GET)"
        }
    })

@app.route('/', methods=['GET'])
def home():
    """홈 페이지"""
    return """
    <h1>🎯 GIA 뉴스 자동화 웹훅 서버</h1>
    <h2>📋 사용 가능한 엔드포인트:</h2>
    <ul>
        <li><strong>POST/GET /trigger-news</strong> - 뉴스 수집 실행</li>
        <li><strong>GET /status</strong> - 서버 상태 확인</li>
    </ul>
    <h2>🔗 외부 연동 방법:</h2>
    <ol>
        <li>Zapier/Make.com에서 Notion 변화 감지</li>
        <li>웹훅으로 <code>http://localhost:8080/trigger-news</code> 호출</li>
        <li>자동으로 뉴스 수집 실행</li>
    </ol>
    """

def main():
    """메인 실행 함수"""
    print("🎯 GIA 뉴스 자동화 웹훅 서버")
    print("=" * 50)
    print("🌐 서버 주소: http://localhost:8080")
    print("🔗 트리거 URL: http://localhost:8080/trigger-news")
    print("📊 상태 확인: http://localhost:8080/status")
    print("=" * 50)
    print("🚀 서버 시작 중...")
    
    # Flask 서버 실행
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    )

if __name__ == "__main__":
    main() 