#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
입찰낙찰 공고 DB 스키마 확인 스크립트
"""

import json
from notion_client import Client
from mvp_config import APIConfig

def check_bid_database_schema():
    """입찰낙찰 공고 DB의 실제 스키마 확인"""
    try:
        notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        
        # 데이터베이스 정보 조회
        database_info = notion.databases.retrieve(database_id=APIConfig.NOTION_BID_DATABASE_ID)
        
        print("📊 입찰낙찰 공고 DB 스키마 정보")
        print("=" * 60)
        print(f"DB ID: {APIConfig.NOTION_BID_DATABASE_ID}")
        print(f"DB 제목: {database_info.get('title', [{}])[0].get('text', {}).get('content', 'Unknown')}")
        print("\n🏷️ 필드 목록:")
        
        properties = database_info.get('properties', {})
        for field_name, field_info in properties.items():
            field_type = field_info.get('type', 'unknown')
            print(f"  - {field_name}: {field_type}")
            
            # 선택/다중선택 필드의 옵션 정보 출력
            if field_type == 'select' and 'select' in field_info:
                options = field_info['select'].get('options', [])
                if options:
                    print(f"    옵션: {[opt['name'] for opt in options]}")
            elif field_type == 'multi_select' and 'multi_select' in field_info:
                options = field_info['multi_select'].get('options', [])
                if options:
                    print(f"    옵션: {[opt['name'] for opt in options]}")
        
        print("\n" + "=" * 60)
        
        # 전체 스키마 JSON 저장
        with open('bid_db_schema.json', 'w', encoding='utf-8') as f:
            json.dump(database_info, f, ensure_ascii=False, indent=2)
        
        print("📄 전체 스키마 정보가 bid_db_schema.json에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    check_bid_database_schema() 