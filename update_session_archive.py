#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 세션 완료 아카이브 스크립트
작성일: 2025년 7월 13일
작성자: 서대리 (Lead Developer)
목적: 이번 세션에서 생성된 누락 파일들만 코드 아카이브 DB에 업로드
"""

import json
import os
from notion_client import Client
from datetime import datetime

# Notion 설정
NOTION_TOKEN = "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"
DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

def read_file_content(file_path):
    """파일 내용을 읽어오는 함수 (인코딩 오류 방지)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp949') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"⚠️ 파일 읽기 실패 ({file_path}): {str(e)}")
            return None
    except FileNotFoundError:
        print(f"⚠️ 파일을 찾을 수 없음: {file_path}")
        return None
    except Exception as e:
        print(f"⚠️ 파일 읽기 중 오류 ({file_path}): {str(e)}")
        return None

def create_content_blocks(content):
    """내용을 블록으로 생성 (2000자 제한 대응)"""
    blocks = []
    
    # 제목 블록
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📋 문서 내용 전문"}}]
        }
    })
    
    # 내용을 1900자씩 나누기 (안전 마진)
    max_length = 1900
    content_chunks = [content[i:i+max_length] for i in range(0, len(content), max_length)]
    
    for i, chunk in enumerate(content_chunks):
        if i > 0:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"[내용 계속 - {i+1}부분]"}}]
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        })
    
    return blocks

def upload_file_to_archive(notion, file_data):
    """파일을 아카이브 DB에 업로드"""
    try:
        # 파일 내용 읽기
        file_content = read_file_content(file_data["file_path"])
        if not file_content:
            return False
        
        # 페이지 생성
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "모듈명": {
                    "title": [{"text": {"content": file_data["module_name"]}}]
                },
                "버전": {
                    "rich_text": [{"text": {"content": file_data["version"]}}]
                },
                "검증일": {
                    "date": {"start": file_data["verification_date"]}
                },
                "주요기능": {
                    "rich_text": [{"text": {"content": file_data["main_features"]}}]
                },
                "검증상태": {
                    "select": {"name": file_data["verification_status"]}
                },
                "관련문서링크": {
                    "url": file_data["related_doc_link"] if file_data["related_doc_link"] else None
                },
                "작성자": {
                    "rich_text": [{"text": {"content": file_data["author"]}}]
                },
                "코드전문": {
                    "rich_text": [{"text": {"content": f"총 {len(file_content)}자 - {file_data['description']}"}}]
                }
            },
            children=create_content_blocks(file_content)
        )
        
        print(f"✅ {file_data['module_name']} 업로드 완료")
        return True
        
    except Exception as e:
        print(f"❌ {file_data['module_name']} 업로드 실패: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 GIA 세션 완료 파일 아카이브 시작")
    print("=" * 60)
    
    # Notion 클라이언트 초기화
    notion = Client(auth=NOTION_TOKEN)
    
    # 이번 세션에서 생성된 누락 파일들
    session_files = [
        {
            "module_name": "GIA_원클릭아카이브시스템_세션완료보고서_20250713.md",
            "file_path": "GIA_원클릭아카이브시스템_세션완료보고서_20250713.md",
            "version": "V1.0",
            "verification_date": "2025-07-13",
            "main_features": "원클릭 아카이브 시스템 구축 세션 완료 보고서, 100% 목표 달성, 85% 시간 단축 성과, 비즈니스 임팩트 분석",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA_원클릭아카이브시스템_구축경과_및_재활용가이드_20250713",
            "author": "서대리 (AI Assistant)",
            "description": "세션 완료 보고서"
        },
        {
            "module_name": "GIA_원클릭아카이브_신규브랜치_적용지시문_조대표용.md",
            "file_path": "GIA_원클릭아카이브_신규브랜치_적용지시문_조대표용.md",
            "version": "V1.0",
            "verification_date": "2025-07-13",
            "main_features": "조대표용 표준 지시문, 새로운 브랜치에서 원클릭 아카이브 시스템 적용, 10-15분 구축 가이드, 5단계 프로세스",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": None,
            "author": "서대리 (AI Assistant)",
            "description": "조대표용 표준 지시문"
        }
    ]
    
    print(f"📊 업로드 대상: {len(session_files)}개 세션 완료 파일")
    print("=" * 60)
    
    # 각 파일 업로드 실행
    success_count = 0
    failed_files = []
    
    for file_data in session_files:
        print(f"\n🔄 처리 중: {file_data['module_name']}")
        if upload_file_to_archive(notion, file_data):
            success_count += 1
        else:
            failed_files.append(file_data['module_name'])
    
    # 결과 보고
    print("\n" + "=" * 60)
    print("📊 세션 완료 파일 아카이브 결과")
    print("=" * 60)
    print(f"✅ 성공: {success_count}/{len(session_files)} 파일")
    print(f"📈 성공률: {success_count/len(session_files)*100:.1f}%")
    
    if failed_files:
        print(f"❌ 실패한 파일: {', '.join(failed_files)}")
    
    print("\n🎉 GIA 세션 완료 파일 아카이브 완료!")
    print("🔗 코드 아카이브 DB: https://www.notion.so/22ea613d25ff80b78fd4ce8dc7a437a6")
    
    print("\n💡 이번 세션 아카이브 내용:")
    print("   - 세션 완료 보고서 (100% 목표 달성)")
    print("   - 조대표용 표준 지시문 (재사용 가능)")
    print("   - 원클릭 아카이브 시스템 완성")
    
    return success_count == len(session_files)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🌟 모든 세션 완료 파일이 성공적으로 아카이브되었습니다!")
        else:
            print("\n⚠️ 일부 파일 아카이브 과정에서 문제가 발생했습니다.")
    except Exception as e:
        print(f"\n💥 실행 중 오류 발생: {str(e)}") 