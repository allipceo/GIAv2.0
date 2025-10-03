#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 실행버튼 웹훅 서버
목적: Notion Automation에서 실행버튼 클릭 시 CASE1,2,3 자동 실행
"""

from flask import Flask, request, jsonify
import subprocess
import json
import os
import sys
import hmac
import hashlib
import time
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv("config.env")

app = Flask(__name__)

# 보안 설정
SECRET_KEY = os.environ.get("WEBHOOK_SECRET_KEY", "default_secret_key")
used_nonces = set()

def validate_security(data, signature):
    """보안 검증"""
    # 1. 타임스탬프 유효성 (5분)
    current_time = int(time.time())
    if abs(current_time - data.get('ts', 0)) > 300:
        return False, "Timestamp expired"
    
    # 2. nonce 재사용 차단
    nonce = data.get('nonce')
    if nonce in used_nonces:
        return False, "Nonce already used"
    
    # 3. 서명 검증
    expected_sig = hmac.new(
        SECRET_KEY.encode(),
        json.dumps(data, sort_keys=True).encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        try:
            # 진단용 3쌍 로그 포인트(body_raw/canonical/sig) + 파일 이중화
            body_raw = json.dumps(data, ensure_ascii=False)
            body_canonical = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            # 마스킹(길이 제한) 및 메타 포함
            from datetime import datetime as _dt
            log_rec = {
                "ts": int(time.time()),
                "level": "WARN",
                "route": getattr(request, 'path', '/unknown'),
                "client_ip": request.headers.get('X-Forwarded-For', request.remote_addr) if request else None,
                "request_id": request.headers.get('X-Request-Id') if request else None,
                "body_raw": (body_raw[:512] + "…") if len(body_raw) > 512 else body_raw,
                "canonical": (body_canonical[:512] + "…") if len(body_canonical) > 512 else body_canonical,
                "sig": (str(signature)[:128] + "…") if signature and len(str(signature)) > 128 else str(signature),
                "verdict": "invalid_signature"
            }
            print(json.dumps(log_rec, ensure_ascii=False))
            # 파일 이중화
            os.makedirs('logs', exist_ok=True)
            fname = f"logs/security_{_dt.utcnow().strftime('%Y%m%d')}.log"
            with open(fname, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_rec, ensure_ascii=False) + "\n")
        except Exception:
            pass
        return False, "Invalid signature"
    
    # 4. nonce 사용 표시
    used_nonces.add(nonce)
    
    return True, "Valid"

@app.route('/webhook/case1', methods=['POST'])
def handle_case1():
    """케이스1 실행버튼 처리"""
    try:
        data = request.json
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        nonce = request.headers.get('X-Nonce')
        
        # 보안 검증 강제 적용
        if not all([signature, timestamp, nonce]):
            return jsonify({"status": "error", "message": "Missing security headers"}), 400
        
        if not validate_security(data, signature):
            return jsonify({"status": "error", "message": "Security validation failed"}), 401
        
        target = data.get('target', 'Z062')
        notion_page_id = data.get('notion_page_id')
        
        print(f"🔧 케이스1 실행버튼 처리: {target}")
        
        # 케이스1 실행
        result = subprocess.run([
            'python', 'scripts/run_notion_workflow.py',
            '--case', '1',
            '--target', target,
            '--out', f'logs/webhook_case1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # 실행 결과 파싱
        success = result.returncode == 0
        status = "성공" if success else "실패"
        message = f"케이스1 실행 {status}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Notion 페이지 업데이트
        if notion_page_id:
            update_notion_page(notion_page_id, {
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'case': '케이스1'
            })
        
        return jsonify({
            'status': 'success',
            'case': '케이스1',
            'result': status,
            'message': message
        })
        
    except Exception as e:
        print(f"❌ 케이스1 실행 실패: {e}")
        return jsonify({
            'status': 'error',
            'case': '케이스1',
            'error': str(e)
        }), 500

@app.route('/webhook/case2', methods=['POST'])
def handle_case2():
    """케이스2 실행버튼 처리"""
    try:
        data = request.json
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        nonce = request.headers.get('X-Nonce')
        
        # 보안 검증 강제 적용
        if not all([signature, timestamp, nonce]):
            return jsonify({"status": "error", "message": "Missing security headers"}), 400
        
        if not validate_security(data, signature):
            return jsonify({"status": "error", "message": "Security validation failed"}), 401
        
        target = data.get('target', 'Z062')
        notion_page_id = data.get('notion_page_id')
        
        print(f"🔧 케이스2 실행버튼 처리: {target}")
        
        # 케이스2 실행
        result = subprocess.run([
            'python', 'scripts/run_notion_workflow.py',
            '--case', '2',
            '--target', target,
            '--out', f'logs/webhook_case2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # 실행 결과 파싱
        success = result.returncode == 0
        status = "성공" if success else "실패"
        message = f"케이스2 실행 {status}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Notion 페이지 업데이트
        if notion_page_id:
            update_notion_page(notion_page_id, {
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'case': '케이스2'
            })
        
        return jsonify({
            'status': 'success',
            'case': '케이스2',
            'result': status,
            'message': message
        })
        
    except Exception as e:
        print(f"❌ 케이스2 실행 실패: {e}")
        return jsonify({
            'status': 'error',
            'case': '케이스2',
            'error': str(e)
        }), 500

@app.route('/webhook/case3', methods=['POST'])
def handle_case3():
    """케이스3 실행버튼 처리"""
    try:
        data = request.json
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        nonce = request.headers.get('X-Nonce')
        
        # 보안 검증 강제 적용
        if not all([signature, timestamp, nonce]):
            return jsonify({"status": "error", "message": "Missing security headers"}), 400
        
        if not validate_security(data, signature):
            return jsonify({"status": "error", "message": "Security validation failed"}), 401
        
        target = data.get('target', 'Z062')
        notion_page_id = data.get('notion_page_id')
        
        print(f"🔧 케이스3 실행버튼 처리: {target}")
        
        # 케이스3 실행
        result = subprocess.run([
            'python', 'scripts/run_notion_workflow.py',
            '--case', '3',
            '--target', target,
            '--out', f'logs/webhook_case3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # 실행 결과 파싱
        success = result.returncode == 0
        status = "성공" if success else "실패"
        message = f"케이스3 실행 {status}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Notion 페이지 업데이트
        if notion_page_id:
            update_notion_page(notion_page_id, {
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'case': '케이스3'
            })
        
        return jsonify({
            'status': 'success',
            'case': '케이스3',
            'result': status,
            'message': message
        })
        
    except Exception as e:
        print(f"❌ 케이스3 실행 실패: {e}")
        return jsonify({
            'status': 'error',
            'case': '케이스3',
            'error': str(e)
        }), 500

@app.route('/webhook/all', methods=['POST'])
def handle_all():
    """전체 워크플로우 실행버튼 처리"""
    try:
        data = request.json
        target = data.get('target', 'Z062')
        notion_page_id = data.get('notion_page_id')
        
        print(f"🚀 전체 워크플로우 실행버튼 처리: {target}")
        
        # 전체 워크플로우 실행
        result = subprocess.run([
            'python', 'scripts/run_notion_workflow.py',
            '--case', 'all',
            '--target', target,
            '--out', f'logs/webhook_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        # 실행 결과 파싱
        success = result.returncode == 0
        status = "성공" if success else "실패"
        message = f"전체 워크플로우 실행 {status}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Notion 페이지 업데이트
        if notion_page_id:
            update_notion_page(notion_page_id, {
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'case': '전체 워크플로우'
            })
        
        return jsonify({
            'status': 'success',
            'case': '전체 워크플로우',
            'result': status,
            'message': message
        })
        
    except Exception as e:
        print(f"❌ 전체 워크플로우 실행 실패: {e}")
        return jsonify({
            'status': 'error',
            'case': '전체 워크플로우',
            'error': str(e)
        }), 500

def update_notion_page(page_id, result):
    """Notion 페이지에 실행 결과 업데이트"""
    try:
        # Notion API 클라이언트 사용
        sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
        from src.utils.notion_api import NotionClient
        
        client = NotionClient(os.environ.get("NOTION_TOKEN"))
        
        # 페이지 속성 업데이트
        properties = {
            "실행 상태": {
                "select": {"name": result['status']}
            },
            "실행 메시지": {
                "rich_text": [{"text": {"content": result['message']}}]
            },
            "실행 시간": {
                "date": {"start": result['timestamp']}
            }
        }
        
        client._req("PATCH", f"/pages/{page_id}", json={"properties": properties})
        print(f"✅ Notion 페이지 업데이트 완료: {page_id}")
        
    except Exception as e:
        print(f"❌ Notion 페이지 업데이트 실패: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """웹훅 서버 헬스체크(구)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'server': 'Notion 실행버튼 웹훅 서버'
    })

@app.route('/healthz', methods=['GET'])
def healthz():
    """프로브용 상세 헬스체크"""
    try:
        git_sha = os.environ.get("GIT_SHA", "dev")
        version = os.environ.get("APP_VERSION", "0.0.1")
        tz = "Asia/Seoul"
        # NTP 오프셋은 추정치(미계산) 0으로 표기. 5-2에서 개선 가능
        ntp_offset_ms = 0
        return jsonify({
            "status": "ok",
            "sha": git_sha,
            "version": version,
            "ts": int(time.time()),
            "tz": tz,
            "ntp_offset_ms": ntp_offset_ms
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sleep', methods=['GET'])
def sleep_handler():
    """요청 처리 중 종료 테스트용 핸들러"""
    try:
        ms = int(request.args.get('ms', '1000'))
        sleep(max(0, ms) / 1000.0)
        return jsonify({"status": "ok", "slept_ms": ms})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    print("🚀 Notion 실행버튼 웹훅 서버 시작...")
    print("📍 서버 주소: http://localhost:8000")
    print("🔧 사용 가능한 엔드포인트:")
    print("   - POST /webhook/case1")
    print("   - POST /webhook/case2") 
    print("   - POST /webhook/case3")
    print("   - POST /webhook/all")
    print("   - GET /health")
    print("   - GET /healthz")
    print()
    
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port, debug=True)
