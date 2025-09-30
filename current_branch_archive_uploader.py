#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 브랜치 중요 파일 아카이빙 스크립트
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: 현재 브랜치에서 생성된 중요 파일들을 GIA 코드 아카이브DB에 업로드
주의: 기존 코드는 절대 수정하지 않음
"""

import json
import os
from notion_client import Client
from datetime import datetime

# Notion 설정 (기존 코드 그대로 사용)
NOTION_TOKEN = ""
DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

def create_code_blocks(code_content):
    """코드를 2000자씩 나누어 여러 블록으로 생성 (기존 함수 그대로 사용)"""
    blocks = []
    
    # 제목 블록 추가
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "코드 전문"}}]
        }
    })
    
    # 코드를 2000자씩 나누기
    max_length = 1900  # 안전 마진
    code_chunks = [code_content[i:i+max_length] for i in range(0, len(code_content), max_length)]
    
    for i, chunk in enumerate(code_chunks):
        if i > 0:  # 첫 번째가 아니면 연속 표시
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"[코드 계속 - {i+1}부분]"}}]
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "language": "python",
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        })
    
    return blocks

def upload_script_to_archive(notion, script_data):
    """개별 스크립트를 아카이브 DB에 업로드 (기존 함수 그대로 사용)"""
    try:
        # 페이지 생성
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "모듈명": {
                    "title": [{"text": {"content": script_data["module_name"]}}]
                },
                "버전": {
                    "rich_text": [{"text": {"content": script_data["version"]}}]
                },
                "검증일": {
                    "date": {"start": script_data["verification_date"]}
                },
                "주요기능": {
                    "rich_text": [{"text": {"content": script_data["main_features"]}}]
                },
                "검증상태": {
                    "select": {"name": script_data["verification_status"]}
                },
                "관련문서링크": {
                    "url": script_data["related_doc_link"]
                },
                "작성자": {
                    "rich_text": [{"text": {"content": "서대리"}}]
                },
                "코드전문": {
                    "rich_text": [{"text": {"content": f"총 {len(script_data['code_content'])}자 - 전체 코드는 페이지 내용 참조"}}]
                }
            },
            children=create_code_blocks(script_data["code_content"])
        )
        
        print(f"✅ {script_data['module_name']} 업로드 완료")
        return True
        
    except Exception as e:
        print(f"❌ {script_data['module_name']} 업로드 실패: {str(e)}")
        return False

def read_file_content(file_path):
    """파일 내용을 안전하게 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 실패 {file_path}: {str(e)}")
        return None

def main():
    """메인 실행 함수"""
    print("🚀 현재 브랜치 중요 파일 아카이빙 시작")
    print("⚠️  기존 코드는 절대 수정하지 않습니다!")
    
    # Notion 클라이언트 초기화
    try:
        notion = Client(auth=NOTION_TOKEN)
        print("✅ Notion 클라이언트 초기화 성공")
    except Exception as e:
        print(f"❌ Notion 클라이언트 초기화 실패: {str(e)}")
        print("🚫 아카이빙 중단 - 문제 발생")
        return
    
    # 아카이빙 대상 파일 목록 (현재 브랜치 중요 파일들)
    target_files = [
        {
            "file_path": "process_grok_team_data.py",
            "module_name": "process_grok_team_data.py",
            "version": "V1.0",
            "verification_date": "2025-07-20",
            "main_features": "구차장 두산에너빌리티 심층 조사 보고서 데이터 처리, 기술적 리스크, 규제 영향, 공급망 리스크 분석",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA-자료조사결과-데이터베이스-구조화-프로세스"
        },
        {
            "file_path": "notion_db_input_grok_team.py",
            "module_name": "notion_db_input_grok_team.py",
            "version": "V1.0",
            "verification_date": "2025-07-20",
            "main_features": "구차장 처리 데이터 Notion DB 자동 입력, 비즈니스/정책/보험시장 DB 연동, 에러 핸들링",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA-자료조사결과-데이터베이스-구조화-프로세스"
        },
        {
            "file_path": "process_chat_team_actual_data.py",
            "module_name": "process_chat_team_actual_data.py",
            "version": "V1.0",
            "verification_date": "2025-07-20",
            "main_features": "노팀장 효성중공업 심층 분석 데이터 처리, 기업 리스크 프로필, 보험 기회 분석",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA-자료조사결과-데이터베이스-구조화-프로세스"
        },
        {
            "file_path": "notion_db_input_chat_team.py",
            "module_name": "notion_db_input_chat_team.py",
            "version": "V1.0",
            "verification_date": "2025-07-20",
            "main_features": "노팀장 처리 데이터 Notion DB 자동 입력, 효성중공업 데이터 구조화, 보험 기회 매핑",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA-자료조사결과-데이터베이스-구조화-프로세스"
        },
        {
            "file_path": "enhanced_selective_extraction.py",
            "module_name": "enhanced_selective_extraction.py",
            "version": "V1.0",
            "verification_date": "2025-07-20",
            "main_features": "선택적 데이터베이스화 시스템, 핵심 정보 추출, 우선순위 기반 필터링",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA-자료조사결과-데이터베이스-구조화-프로세스"
        },
        {
            "file_path": "quality_monitoring_system.py",
            "module_name": "quality_monitoring_system.py",
            "version": "V1.0",
            "verification_date": "2025-07-20",
            "main_features": "데이터 품질 모니터링 시스템, 추출 정확도 측정, 분류 정확도 추적",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA-자료조사결과-데이터베이스-구조화-프로세스"
        }
    ]
    
    success_count = 0
    total_count = len(target_files)
    
    print(f"📋 총 {total_count}개 파일 아카이빙 시작")
    
    for i, file_info in enumerate(target_files, 1):
        print(f"\n📁 [{i}/{total_count}] {file_info['module_name']} 처리 중...")
        
        # 파일 존재 확인
        if not os.path.exists(file_info["file_path"]):
            print(f"❌ 파일이 존재하지 않음: {file_info['file_path']}")
            continue
        
        # 파일 내용 읽기
        code_content = read_file_content(file_info["file_path"])
        if code_content is None:
            print(f"❌ 파일 읽기 실패: {file_info['file_path']}")
            continue
        
        # 스크립트 데이터 준비
        script_data = {
            "module_name": file_info["module_name"],
            "version": file_info["version"],
            "verification_date": file_info["verification_date"],
            "main_features": file_info["main_features"],
            "verification_status": file_info["verification_status"],
            "related_doc_link": file_info["related_doc_link"],
            "code_content": code_content
        }
        
        # 업로드 실행
        try:
            if upload_script_to_archive(notion, script_data):
                success_count += 1
            else:
                print(f"❌ 업로드 실패: {file_info['module_name']}")
                print("🚫 아카이빙 중단 - 문제 발생")
                return
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
            print("🚫 아카이빙 중단 - 문제 발생")
            return
    
    print(f"\n🎉 아카이빙 완료!")
    print(f"✅ 성공: {success_count}/{total_count}")
    print(f"📊 성공률: {(success_count/total_count)*100:.1f}%")

if __name__ == "__main__":
    main() 