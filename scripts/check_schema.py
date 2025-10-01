#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 스키마 확인 스크립트
"""

import os
import sys
import json
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.notion_api import NotionClient

def main():
    load_dotenv("config.env")
    
    token = os.environ.get("NOTION_TOKEN")
    db_id = os.environ.get("DEV_DB_ID")
    
    if not token or not db_id:
        print("ERROR: 환경변수 설정 확인")
        return 1
    
    try:
        n = NotionClient(token)
        db_info = n.get_database(db_id)
        
        print("DB 스키마:")
        properties = db_info.get("properties", {})
        for prop_name, prop_info in properties.items():
            print(f"  {prop_name}: {prop_info.get('type', 'unknown')}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
