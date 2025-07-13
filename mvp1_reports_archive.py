#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA MVP 1차 구축 관련 보고서 아카이브 스크립트
작성일: 2025년 7월 13일
작성자: 서대리 (Lead Developer)
목적: MVP 1차 구축 관련 모든 보고서들을 코드 아카이브 DB에 업로드

MVP 1차 구축 보고서 핵심 내용:
- MVP 1.0 구축 완료 보고서
- 시스템 구축 결과 보고서
- 개발 경과 및 성과 분석
"""

import json
import os
from notion_client import Client
from datetime import datetime

# Notion 설정
NOTION_TOKEN = "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"
DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

def create_report_blocks(report_content):
    """보고서를 2000자씩 나누어 여러 블록으로 생성"""
    blocks = []
    
    # 제목 블록 추가
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📋 MVP 1차 구축 보고서 전문"}}]
        }
    })
    
    # 보고서를 1900자씩 나누기 (안전 마진)
    max_length = 1900
    report_chunks = [report_content[i:i+max_length] for i in range(0, len(report_content), max_length)]
    
    for i, chunk in enumerate(report_chunks):
        if i > 0:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"[보고서 계속 - {i+1}부분]"}}]
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "language": "markdown",
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        })
    
    return blocks

def read_file_content(file_path):
    """파일 내용 읽기 (인코딩 안전성 강화)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp949') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 파일 읽기 실패 ({file_path}): {str(e)}")
            return None

def upload_report_to_archive(notion, report_data):
    """보고서를 노션 코드 아카이브에 업로드"""
    try:
        # 파일 내용 읽기
        report_content = read_file_content(report_data["file_path"])
        if report_content is None:
            return False
        
        # 보고서 블록 생성
        children_blocks = create_report_blocks(report_content)
        
        # 페이지 속성 설정 (한국어 속성명 사용)
        properties = {
            "모듈명": {"title": [{"text": {"content": report_data["module_name"]}}]},
            "버전": {"rich_text": [{"text": {"content": report_data["version"]}}]},
            "검증일": {"date": {"start": report_data["verification_date"]}},
            "주요기능": {"rich_text": [{"text": {"content": report_data["main_features"]}}]},
            "검증상태": {"select": {"name": report_data["verification_status"]}},
            "관련문서링크": {"url": report_data["related_doc_link"]},
            "작성자": {"rich_text": [{"text": {"content": report_data["author"]}}]},
            "코드전문": {"rich_text": [{"text": {"content": f"총 {len(report_content)}자 - MVP 1차 구축 보고서"}}]}
        }
        
        # 노션 페이지 생성
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=properties,
            children=children_blocks
        )
        
        print(f"✅ {report_data['module_name']} 업로드 완료")
        return True
        
    except Exception as e:
        print(f"❌ {report_data['module_name']} 업로드 실패: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("📋 GIA MVP 1차 구축 보고서 아카이브 시작")
    print("=" * 60)
    
    # Notion 클라이언트 초기화
    notion = Client(auth=NOTION_TOKEN)
    
    # MVP 1차 구축 보고서 데이터 정의
    mvp1_reports = [
        {
            "module_name": "MVP1.0_구축완료_보고서.md",
            "file_path": "MVP1.0_구축완료_보고서.md",
            "version": "V1.0",
            "verification_date": "2025-07-13",
            "main_features": "MVP 1.0 구축 완료 보고서, 핵심 작업 완료 현황, 시스템 아키텍처, 실행 방법 및 예상 효과",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/MVP1.0_구축완료_보고서",
            "author": "서대리 (Lead Developer)"
        },
        {
            "module_name": "GIA MVP1.0시스템 구축결과보고_서대리_0713.md",
            "file_path": "GIA MVP1.0시스템 구축결과보고_서대리_0713.md",
            "version": "V1.0",
            "verification_date": "2025-07-13",
            "main_features": "MVP 1.0 시스템 구축 결과, 3주차 지시문 이행 현황, 신규 개발 성과, 최종 시스템 완성도",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/GIA_MVP1.0시스템_구축결과보고",
            "author": "서대리 (Lead Developer)"
        }
    ]
    
    print(f"📊 업로드 대상: {len(mvp1_reports)}개 MVP 1차 구축 보고서")
    print("=" * 60)
    
    # 각 보고서 업로드 실행
    success_count = 0
    failed_reports = []
    
    for report_data in mvp1_reports:
        print(f"\n🔄 처리 중: {report_data['module_name']}")
        if upload_report_to_archive(notion, report_data):
            success_count += 1
        else:
            failed_reports.append(report_data['module_name'])
    
    # 결과 보고
    print("\n" + "=" * 60)
    print("📊 MVP 1차 구축 보고서 아카이브 결과")
    print("=" * 60)
    print(f"✅ 성공: {success_count}/{len(mvp1_reports)} 보고서")
    print(f"📈 성공률: {success_count/len(mvp1_reports)*100:.1f}%")
    
    if failed_reports:
        print(f"❌ 실패한 보고서: {', '.join(failed_reports)}")
    
    print("\n🎉 GIA MVP 1차 구축 보고서 아카이브 완료!")
    print("🔗 코드 아카이브 DB: https://www.notion.so/22ea613d25ff80b78fd4ce8dc7a437a6")
    print("\n💡 MVP 1차 구축 보고서 주요 성과:")
    print("   - 완전 자동화 시스템 구축 완료")
    print("   - 91% 업무 효율성 향상 달성")
    print("   - 조대표님 맞춤 대시보드 완성")
    print("   - LLM 기반 지능형 정보 처리")
    
    return success_count == len(mvp1_reports)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🌟 모든 MVP 1차 구축 보고서가 성공적으로 아카이브되었습니다!")
        else:
            print("\n⚠️ 일부 보고서 아카이브 과정에서 문제가 발생했습니다.")
    except Exception as e:
        print(f"\n💥 실행 중 오류 발생: {str(e)}") 