#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아카이빙 결과 검증 스크립트
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: Notion DB에 업로드된 아카이빙 파일들의 정확성 검증
"""

import json
from notion_client import Client
from datetime import datetime

# Notion 설정
NOTION_TOKEN = ""
DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

def verify_notion_connection():
    """Notion 연결 상태 확인"""
    try:
        notion = Client(auth=NOTION_TOKEN)
        # 데이터베이스 정보 조회
        db_info = notion.databases.retrieve(database_id=DATABASE_ID)
        print("✅ Notion 연결 성공")
        print(f"📊 데이터베이스명: {db_info['title'][0]['plain_text']}")
        return notion
    except Exception as e:
        print(f"❌ Notion 연결 실패: {str(e)}")
        return None

def get_archived_files(notion):
    """아카이브된 파일 목록 조회"""
    try:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            sorts=[{"property": "검증일", "direction": "descending"}]
        )
        
        print(f"\n📋 아카이브된 파일 목록 (총 {len(response['results'])}개)")
        print("=" * 80)
        
        archived_files = []
        for i, page in enumerate(response['results'], 1):
            properties = page['properties']
            
            # 모듈명 추출
            module_name = properties.get('모듈명', {}).get('title', [])
            module_name = module_name[0]['plain_text'] if module_name else "N/A"
            
            # 버전 추출
            version = properties.get('버전', {}).get('rich_text', [])
            version = version[0]['plain_text'] if version else "N/A"
            
            # 검증일 추출
            verification_date = properties.get('검증일', {}).get('date', {})
            verification_date = verification_date.get('start', "N/A") if verification_date else "N/A"
            
            # 검증상태 추출
            verification_status = properties.get('검증상태', {}).get('select', {})
            verification_status = verification_status.get('name', "N/A") if verification_status else "N/A"
            
            # 작성자 추출
            author = properties.get('작성자', {}).get('rich_text', [])
            author = author[0]['plain_text'] if author else "N/A"
            
            # 코드전문 길이 추출
            code_length = properties.get('코드전문', {}).get('rich_text', [])
            code_length = code_length[0]['plain_text'] if code_length else "N/A"
            
            print(f"{i:2d}. {module_name}")
            print(f"    버전: {version}")
            print(f"    검증일: {verification_date}")
            print(f"    검증상태: {verification_status}")
            print(f"    작성자: {author}")
            print(f"    코드길이: {code_length}")
            print()
            
            archived_files.append({
                'page_id': page['id'],
                'module_name': module_name,
                'version': version,
                'verification_date': verification_date,
                'verification_status': verification_status,
                'author': author,
                'code_length': code_length
            })
        
        return archived_files
        
    except Exception as e:
        print(f"❌ 파일 목록 조회 실패: {str(e)}")
        return []

def verify_file_content(notion, page_id, module_name):
    """개별 파일 내용 검증"""
    try:
        # 페이지 블록 조회
        blocks = notion.blocks.children.list(block_id=page_id)
        
        code_blocks = []
        for block in blocks['results']:
            if block['type'] == 'code':
                code_content = block['code']['rich_text']
                if code_content:
                    code_blocks.append(code_content[0]['plain_text'])
        
        total_code_length = sum(len(block) for block in code_blocks)
        
        print(f"📁 {module_name} 내용 검증:")
        print(f"   - 코드 블록 수: {len(code_blocks)}")
        print(f"   - 총 코드 길이: {total_code_length:,}자")
        
        if total_code_length > 0:
            print(f"   ✅ 코드 내용 정상")
            return True
        else:
            print(f"   ❌ 코드 내용 없음")
            return False
            
    except Exception as e:
        print(f"   ❌ 내용 검증 실패: {str(e)}")
        return False

def verify_metadata_accuracy(archived_files):
    """메타데이터 정확성 검증"""
    print(f"\n🔍 메타데이터 정확성 검증")
    print("=" * 80)
    
    # 현재 브랜치에서 아카이빙된 파일들 필터링
    current_branch_files = [
        'process_grok_team_data.py',
        'notion_db_input_grok_team.py', 
        'process_chat_team_actual_data.py',
        'notion_db_input_chat_team.py',
        'enhanced_selective_extraction.py',
        'quality_monitoring_system.py'
    ]
    
    found_files = []
    missing_files = []
    
    for file_info in archived_files:
        if file_info['module_name'] in current_branch_files:
            found_files.append(file_info)
        else:
            # 기존 아카이브 파일들
            pass
    
    for expected_file in current_branch_files:
        if not any(f['module_name'] == expected_file for f in found_files):
            missing_files.append(expected_file)
    
    print(f"✅ 발견된 현재 브랜치 파일: {len(found_files)}개")
    for file_info in found_files:
        print(f"   - {file_info['module_name']} (검증상태: {file_info['verification_status']})")
    
    if missing_files:
        print(f"❌ 누락된 파일: {len(missing_files)}개")
        for missing_file in missing_files:
            print(f"   - {missing_file}")
    else:
        print(f"✅ 모든 예상 파일이 아카이브됨")
    
    return len(found_files), len(missing_files)

def main():
    """메인 검증 함수"""
    print("🔍 아카이빙 결과 검증 시작")
    print("=" * 80)
    
    # 1단계: Notion 연결 확인
    notion = verify_notion_connection()
    if not notion:
        print("🚫 검증 중단 - Notion 연결 실패")
        return
    
    # 2단계: 아카이브된 파일 목록 조회
    archived_files = get_archived_files(notion)
    if not archived_files:
        print("🚫 검증 중단 - 아카이브 파일 목록 조회 실패")
        return
    
    # 3단계: 메타데이터 정확성 검증
    found_count, missing_count = verify_metadata_accuracy(archived_files)
    
    # 4단계: 파일 내용 검증 (샘플)
    print(f"\n📄 파일 내용 검증 (샘플)")
    print("=" * 80)
    
    # 현재 브랜치 파일들 중 첫 번째 파일 내용 검증
    current_branch_files = [
        'process_grok_team_data.py',
        'notion_db_input_grok_team.py', 
        'process_chat_team_actual_data.py',
        'notion_db_input_chat_team.py',
        'enhanced_selective_extraction.py',
        'quality_monitoring_system.py'
    ]
    
    for file_info in archived_files:
        if file_info['module_name'] in current_branch_files:
            print(f"\n🔍 {file_info['module_name']} 상세 검증:")
            success = verify_file_content(notion, file_info['page_id'], file_info['module_name'])
            if success:
                print(f"   ✅ {file_info['module_name']} 검증 성공")
            else:
                print(f"   ❌ {file_info['module_name']} 검증 실패")
            break  # 첫 번째 파일만 검증
    
    # 5단계: 최종 결과 요약
    print(f"\n📊 검증 결과 요약")
    print("=" * 80)
    print(f"✅ Notion 연결: 성공")
    print(f"📋 총 아카이브 파일: {len(archived_files)}개")
    print(f"🎯 현재 브랜치 파일: {found_count}개")
    print(f"❌ 누락 파일: {missing_count}개")
    
    if missing_count == 0:
        print(f"🎉 모든 파일이 성공적으로 아카이브됨!")
    else:
        print(f"⚠️  일부 파일이 누락됨 - 재아카이빙 필요")

if __name__ == "__main__":
    main() 