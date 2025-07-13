#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 원클릭 아카이브 웹훅 리스너 서버
작성일: 2025년 7월 13일
작성자: 서대리 (Lead Developer)
목적: 노션 버튼 클릭으로 Phase 3 아카이브 스크립트를 자동 실행하는 웹훅 서버

나실장님 지시사항:
- FastAPI 사용으로 경량화 및 고성능 구현
- UUID 토큰 기반 보안 (URL 파라미터 방식)
- Git 브랜치 인식 및 아카이브 기록에 포함
- 노션 API를 통한 실시간 상태 업데이트
- Phase 3 아카이브 스크립트 자동 실행
"""

import os
import sys
import uuid
import subprocess
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from notion_client import Client
import asyncio

# 설정
WEBHOOK_TOKEN = "gia-archive-webhook-token-2025-" + str(uuid.uuid4())[:8]
NOTION_TOKEN = "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"
ARCHIVE_DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

# FastAPI 앱 초기화
app = FastAPI(
    title="GIA 원클릭 아카이브 서버",
    description="노션 버튼 클릭으로 Phase 3 아카이브 시스템을 자동 실행하는 웹훅 서버",
    version="1.0.0"
)

# CORS 설정 (노션에서 호출 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 노션에서의 호출을 위해 모든 origin 허용
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Notion 클라이언트 초기화
notion = Client(auth=NOTION_TOKEN)

def get_current_git_branch():
    """현재 Git 브랜치 이름을 가져옴"""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "unknown-branch"
    except Exception as e:
        print(f"브랜치 정보 가져오기 실패: {e}")
        return "unknown-branch"

def update_notion_status(status: str, message: str, branch: str = None):
    """노션 DB에 아카이브 상태 업데이트"""
    try:
        # 상태 업데이트용 페이지 생성 또는 업데이트
        status_data = {
            "모듈명": {
                "title": [{"text": {"content": f"아카이브 실행 상태 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}}]
            },
            "버전": {
                "rich_text": [{"text": {"content": "웹훅-V1.0"}}]
            },
            "검증일": {
                "date": {"start": datetime.now().strftime('%Y-%m-%d')}
            },
            "주요기능": {
                "rich_text": [{"text": {"content": f"원클릭 아카이브 실행: {message}"}}]
            },
            "검증상태": {
                "select": {"name": status}
            },
            "관련문서링크": {
                "url": "https://www.notion.so/22ea613d25ff80b78fd4ce8dc7a437a6"
            },
            "작성자": {
                "rich_text": [{"text": {"content": "웹훅 시스템"}}]
            },
            "코드전문": {
                "rich_text": [{"text": {"content": f"브랜치: {branch or 'unknown'} | 상태: {status} | {message}"}}]
            }
        }
        
        notion.pages.create(
            parent={"database_id": ARCHIVE_DATABASE_ID},
            properties=status_data
        )
        print(f"✅ 노션 상태 업데이트 완료: {status}")
        
    except Exception as e:
        print(f"❌ 노션 상태 업데이트 실패: {e}")

async def run_archive_script(script_name: str, branch: str):
    """아카이브 스크립트를 비동기로 실행"""
    try:
        print(f"🔄 {script_name} 실행 시작...")
        
        # 스크립트 실행
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✅ {script_name} 실행 성공")
            return True, stdout.decode('utf-8', errors='ignore')
        else:
            print(f"❌ {script_name} 실행 실패")
            print(f"에러: {stderr.decode('utf-8', errors='ignore')}")
            return False, stderr.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"❌ {script_name} 실행 중 예외 발생: {e}")
        return False, str(e)

@app.get("/")
async def root():
    """서버 상태 확인 엔드포인트"""
    current_branch = get_current_git_branch()
    return {
        "message": "GIA 원클릭 아카이브 서버가 정상 작동 중입니다",
        "version": "1.0.0",
        "current_branch": current_branch,
        "webhook_endpoint": "/archive_trigger",
        "server_time": datetime.now().isoformat(),
        "instructions": f"웹훅 호출: POST /archive_trigger?token={WEBHOOK_TOKEN}"
    }

@app.get("/test")
async def test_webhook(token: str = Query(..., description="인증 토큰")):
    """웹훅 테스트용 GET 엔드포인트 (노션 버튼 테스트용)"""
    if token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    
    current_branch = get_current_git_branch()
    
    return JSONResponse(content={
        "status": "success",
        "message": "웹훅 테스트 성공! 서버가 정상 작동 중입니다.",
        "branch": current_branch,
        "timestamp": datetime.now().isoformat(),
        "next_step": "이제 /archive_trigger 엔드포인트로 실제 아카이브를 실행할 수 있습니다."
    })

@app.post("/archive_trigger")
@app.get("/archive_trigger")  # 노션 버튼에서 GET 요청도 지원
async def trigger_archive(
    request: Request,
    token: str = Query(..., description="인증 토큰"),
    archive_type: str = Query("both", description="아카이브 타입: code, reports, both")
):
    """
    메인 아카이브 트리거 엔드포인트
    
    Args:
        token: 보안을 위한 UUID 기반 토큰
        archive_type: 실행할 아카이브 타입
            - "code": 코드 파일만 아카이브
            - "reports": 보고서만 아카이브  
            - "both": 코드와 보고서 모두 아카이브 (기본값)
    """
    
    # 토큰 검증
    if token != WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    
    # 현재 브랜치 정보 가져오기
    current_branch = get_current_git_branch()
    start_time = datetime.now()
    
    print(f"\n🚀 GIA 원클릭 아카이브 시작")
    print(f"📊 실행 정보:")
    print(f"   - 브랜치: {current_branch}")
    print(f"   - 타입: {archive_type}")
    print(f"   - 시작시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - 클라이언트 IP: {request.client.host}")
    
    # 노션에 시작 상태 업데이트
    update_notion_status("진행 중", f"{archive_type} 아카이브 시작", current_branch)
    
    results = []
    
    try:
        # 코드 아카이브 실행
        if archive_type in ["code", "both"]:
            if os.path.exists("update_code_archive_phase3.py"):
                success, output = await run_archive_script("update_code_archive_phase3.py", current_branch)
                results.append({
                    "script": "update_code_archive_phase3.py",
                    "success": success,
                    "output": output[:500] + "..." if len(output) > 500 else output
                })
            else:
                results.append({
                    "script": "update_code_archive_phase3.py",
                    "success": False,
                    "output": "스크립트 파일을 찾을 수 없습니다"
                })
        
        # 보고서 아카이브 실행
        if archive_type in ["reports", "both"]:
            if os.path.exists("update_reports_archive.py"):
                success, output = await run_archive_script("update_reports_archive.py", current_branch)
                results.append({
                    "script": "update_reports_archive.py",
                    "success": success,
                    "output": output[:500] + "..." if len(output) > 500 else output
                })
            else:
                results.append({
                    "script": "update_reports_archive.py",
                    "success": False,
                    "output": "스크립트 파일을 찾을 수 없습니다"
                })
        
        # 결과 분석
        total_scripts = len(results)
        successful_scripts = sum(1 for r in results if r["success"])
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 최종 상태 결정
        if successful_scripts == total_scripts:
            final_status = "완료"
            status_message = f"모든 스크립트 성공 ({successful_scripts}/{total_scripts})"
        elif successful_scripts > 0:
            final_status = "부분 완료"
            status_message = f"일부 스크립트 성공 ({successful_scripts}/{total_scripts})"
        else:
            final_status = "실패"
            status_message = f"모든 스크립트 실패 (0/{total_scripts})"
        
        # 노션에 최종 상태 업데이트
        update_notion_status(final_status, status_message, current_branch)
        
        print(f"\n📊 아카이브 완료:")
        print(f"   - 성공률: {successful_scripts}/{total_scripts}")
        print(f"   - 소요시간: {duration:.1f}초")
        print(f"   - 최종상태: {final_status}")
        
        return JSONResponse(content={
            "status": "completed",
            "final_status": final_status,
            "branch": current_branch,
            "archive_type": archive_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_scripts": total_scripts,
            "successful_scripts": successful_scripts,
            "success_rate": f"{successful_scripts/total_scripts*100:.1f}%",
            "results": results,
            "archive_db_url": f"https://www.notion.so/{ARCHIVE_DATABASE_ID}",
            "message": "✅ GIA 원클릭 아카이브가 완료되었습니다!"
        })
        
    except Exception as e:
        # 노션에 오류 상태 업데이트
        update_notion_status("실패", f"시스템 오류: {str(e)}", current_branch)
        
        print(f"❌ 아카이브 실행 중 오류 발생: {e}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"아카이브 실행 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/status")
async def get_server_status():
    """서버 및 시스템 상태 조회"""
    current_branch = get_current_git_branch()
    
    # 필요한 스크립트 파일 존재 여부 확인
    required_scripts = [
        "update_code_archive_phase3.py",
        "update_reports_archive.py"
    ]
    
    script_status = {}
    for script in required_scripts:
        script_status[script] = {
            "exists": os.path.exists(script),
            "size_kb": round(os.path.getsize(script) / 1024, 1) if os.path.exists(script) else 0
        }
    
    return {
        "server_status": "running",
        "current_branch": current_branch,
        "webhook_token": WEBHOOK_TOKEN,
        "archive_database_id": ARCHIVE_DATABASE_ID,
        "script_status": script_status,
        "system_info": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "server_time": datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 GIA 원클릭 아카이브 웹훅 서버 시작")
    print("=" * 60)
    print(f"🔗 웹훅 토큰: {WEBHOOK_TOKEN}")
    print(f"📊 아카이브 DB: {ARCHIVE_DATABASE_ID}")
    print(f"🌿 현재 브랜치: {get_current_git_branch()}")
    print(f"📅 서버 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("🔗 접속 URL:")
    print("   - 서버 상태: http://localhost:8000/")
    print("   - 상태 조회: http://localhost:8000/status")
    print(f"   - 테스트: http://localhost:8000/test?token={WEBHOOK_TOKEN}")
    print(f"   - 아카이브: http://localhost:8000/archive_trigger?token={WEBHOOK_TOKEN}")
    print("=" * 60)
    
    # 서버 실행
    uvicorn.run(
        "webhook_archive_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 