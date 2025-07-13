#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA Phase 3 보고서 아카이브 업데이트 스크립트
작성일: 2025년 7월 13일
작성자: 서대리 (Lead Developer)
목적: 이번 세션에서 생성된 중요한 보고서들을 코드 아카이브 DB에 업로드
"""

import json
import os
from notion_client import Client
from datetime import datetime

# Notion 설정
NOTION_TOKEN = "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"
DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

def create_report_blocks(report_content):
    """보고서 내용을 블록으로 생성"""
    blocks = []
    
    # 제목 블록
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📋 Phase 3 보고서 내용"}}]
        }
    })
    
    # 내용을 1900자씩 나누기
    max_length = 1900
    content_chunks = [report_content[i:i+max_length] for i in range(0, len(report_content), max_length)]
    
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

def read_file_content(file_path):
    """파일 내용 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ 파일을 찾을 수 없습니다: {file_path}")
        return None
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {file_path} - {str(e)}")
        return None

def upload_report_to_archive(notion, report_data):
    """보고서를 아카이브 DB에 업로드"""
    try:
        # 보고서 내용 읽기
        report_content = read_file_content(report_data["file_path"])
        if not report_content:
            return False
        
        # 페이지 생성
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "모듈명": {
                    "title": [{"text": {"content": report_data["module_name"]}}]
                },
                "버전": {
                    "rich_text": [{"text": {"content": report_data["version"]}}]
                },
                "검증일": {
                    "date": {"start": report_data["verification_date"]}
                },
                "주요기능": {
                    "rich_text": [{"text": {"content": report_data["main_features"]}}]
                },
                "검증상태": {
                    "select": {"name": report_data["verification_status"]}
                },
                "관련문서링크": {
                    "url": report_data["related_doc_link"]
                },
                "작성자": {
                    "rich_text": [{"text": {"content": report_data["author"]}}]
                },
                "코드전문": {
                    "rich_text": [{"text": {"content": f"총 {len(report_content)}자 - Phase 3 최종 보고서"}}]
                }
            },
            children=create_report_blocks(report_content)
        )
        
        print(f"✅ {report_data['module_name']} 업로드 완료")
        return True
        
    except Exception as e:
        print(f"❌ {report_data['module_name']} 업로드 실패: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("📋 GIA Phase 3 보고서 아카이브 업데이트 시작")
    print("=" * 60)
    
    # Notion 클라이언트 초기화
    notion = Client(auth=NOTION_TOKEN)
    
    # Phase 3 보고서 데이터 정의
    phase3_reports = [
        {
            "module_name": "GIA_프로젝트_Phase3_최종개발경과보고서_20250713.md",
            "file_path": "GIA_프로젝트_Phase3_최종개발경과보고서_20250713.md",
            "version": "V3.0",
            "verification_date": "2025-07-13",
            "main_features": "Phase 3 전체 개발 경과, 핵심 성과 및 혁신, 205개 관계형 연결 성과, 향후 발전 방안",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA_프로젝트_통합_최종보고서_20250713",
            "author": "서대리 (Lead Developer)"
        },
        {
            "module_name": "GIA_프로젝트_통합_최종보고서_20250713.md",
            "file_path": "GIA_프로젝트_통합_최종보고서_20250713.md",
            "version": "V3.0",
            "verification_date": "2025-07-13",
            "main_features": "나실장&서대리 통합 보고서, 듀얼 관점 분석, 비즈니스 임팩트 및 기술적 혁신 종합",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA_프로젝트_통합_최종보고서_20250713",
            "author": "나실장 & 서대리"
        }
    ]
    
    print(f"📊 업로드 대상: {len(phase3_reports)}개 Phase 3 보고서")
    print("=" * 60)
    
    # 각 보고서 업로드 실행
    success_count = 0
    failed_reports = []
    
    for report_data in phase3_reports:
        print(f"\n🔄 처리 중: {report_data['module_name']}")
        if upload_report_to_archive(notion, report_data):
            success_count += 1
        else:
            failed_reports.append(report_data['module_name'])
    
    # 결과 보고
    print("\n" + "=" * 60)
    print("📊 Phase 3 보고서 아카이브 업데이트 결과")
    print("=" * 60)
    print(f"✅ 성공: {success_count}/{len(phase3_reports)} 보고서")
    print(f"📈 성공률: {success_count/len(phase3_reports)*100:.1f}%")
    
    if failed_reports:
        print(f"❌ 실패한 보고서: {', '.join(failed_reports)}")
    
    print("\n🎉 GIA Phase 3 보고서 아카이브 업데이트 완료!")
    print("🔗 코드 아카이브 DB: https://www.notion.so/22ea613d25ff80b78fd4ce8dc7a437a6")
    
    return success_count == len(phase3_reports)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🌟 모든 Phase 3 보고서가 성공적으로 아카이브되었습니다!")
        else:
            print("\n⚠️ 일부 보고서 아카이브 과정에서 문제가 발생했습니다.")
    except Exception as e:
        print(f"\n💥 실행 중 오류 발생: {str(e)}") 