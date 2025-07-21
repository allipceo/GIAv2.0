#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion DB 속성명 확인 스크립트
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: Notion DB의 실제 속성명을 확인하여 정확한 매핑 정보 제공
"""

import json
from notion_client import Client

# Notion 설정
NOTION_TOKEN = "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"

# 데이터베이스 ID들
BUSINESS_PROJECT_DB_ID = "228a613d25ff8122a10bc35772c8a05c"  # 기업 재무 및 프로젝트 DB
RISK_PROFILE_DB_ID = "228a613d25ff818d9bbac1b53e19dcbd"      # 기업 위험 프로파일 DB
GLOBAL_INSURANCE_DB_ID = "22aa613d25ff80888257c652d865f85a"   # 글로벌 보험중개 시장 DB
POLICY_ANALYSIS_DB_ID = "228a613d25ff80f89903f8f92e549f44"   # 정부 정책 영향 분석 DB
KEY_PERSONNEL_DB_ID = "228a613d25ff813dbb4ef3d3d984d186"     # 기업 핵심 인물 DB

def check_database_properties(notion, db_id, db_name):
    """데이터베이스 속성 확인"""
    try:
        db_info = notion.databases.retrieve(database_id=db_id)
        properties = db_info['properties']
        
        print(f"\n📋 {db_name} 속성 목록:")
        print("=" * 50)
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info['type']
            print(f"   - {prop_name} ({prop_type})")
            
            # Select 타입인 경우 옵션도 표시
            if prop_type == 'select' and 'select' in prop_info:
                options = prop_info['select']['options']
                if options:
                    print(f"     옵션: {[opt['name'] for opt in options]}")
        
        return properties
        
    except Exception as e:
        print(f"❌ {db_name} 속성 확인 실패: {str(e)}")
        return None

def main():
    """메인 실행 함수"""
    print("🔍 Notion DB 속성명 확인 시작")
    
    # Notion 클라이언트 생성
    try:
        notion = Client(auth=NOTION_TOKEN)
        print("✅ Notion 클라이언트 생성 성공")
    except Exception as e:
        print(f"❌ Notion 클라이언트 생성 실패: {str(e)}")
        return
    
    # 각 데이터베이스의 속성 확인
    databases = [
        (BUSINESS_PROJECT_DB_ID, "기업 재무 및 프로젝트 DB"),
        (RISK_PROFILE_DB_ID, "기업 위험 프로파일 DB"),
        (GLOBAL_INSURANCE_DB_ID, "글로벌 보험중개 시장 DB"),
        (POLICY_ANALYSIS_DB_ID, "정부 정책 영향 분석 DB"),
        (KEY_PERSONNEL_DB_ID, "기업 핵심 인물 DB")
    ]
    
    all_properties = {}
    
    for db_id, db_name in databases:
        properties = check_database_properties(notion, db_id, db_name)
        if properties:
            all_properties[db_name] = properties
    
    # 결과 저장
    result_filename = f"notion_db_properties_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(all_properties, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 속성 정보 저장: {result_filename}")
    print("✅ DB 속성명 확인 완료")

if __name__ == "__main__":
    from datetime import datetime
    main() 