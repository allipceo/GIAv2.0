import os
import requests
import json
import time
from dotenv import load_dotenv
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')

# 일반화할 DB 목록
DB_RENAME_LIST = [
    {
        'old_name': '효성중공업 기업 위험 프로파일',
        'new_name': '📊 기업 위험 프로파일 DB',
        'db_id': '228a613d25ff8122a10bc35772c8a05c'
    },
    {
        'old_name': '효성중공업 재무 및 프로젝트',
        'new_name': '💰 기업 재무 및 프로젝트 DB',
        'db_id': '228a613d25ff818d9bbac1b53e19dcbd'
    },
    {
        'old_name': '효성중공업 신재생에너지 프로젝트',
        'new_name': '🔋 신재생에너지 프로젝트 DB',
        'db_id': '228a613d25ff814e9153fa459f1392ef'
    },
    {
        'old_name': '효성중공업 핵심 인물',
        'new_name': '👥 기업 핵심 인물 DB',
        'db_id': '228a613d25ff813dbb4ef3d3d984d186'
    },
    {
        'old_name': '효성중공업 정부 정책 영향',
        'new_name': '🏛️ 정부 정책 영향 분석 DB',
        'db_id': '228a613d25ff80f89903f8f92e549f44'
    },
    {
        'old_name': '효성중공업 글로벌 보험중개 시장',
        'new_name': '🌍 글로벌 보험중개 시장 DB',
        'db_id': '22aa613d25ff80888257c652d865f85a'
    }
]

def rename_database(db_info):
    """DB 이름 변경"""
    old_name = db_info['old_name']
    new_name = db_info['new_name']
    db_id = db_info['db_id']
    
    print(f"🔄 {old_name} → {new_name}")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    # DB 이름 변경 요청
    update_data = {
        'title': [{'type': 'text', 'text': {'content': new_name}}]
    }
    
    try:
        url = f"https://api.notion.com/v1/databases/{db_id}"
        response = requests.patch(url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            print(f"✅ {new_name} 변경 완료")
            return True
        else:
            print(f"❌ {new_name} 변경 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {new_name} 변경 오류: {e}")
        return False

def main():
    """메인 DB 이름 변경 프로세스"""
    print("🔄 DB 이름 일반화 시작")
    print("=" * 50)
    
    success_count = 0
    total_count = len(DB_RENAME_LIST)
    
    for db_info in DB_RENAME_LIST:
        if rename_database(db_info):
            success_count += 1
        time.sleep(1)  # API 호출 간격 1초
    
    print("=" * 50)
    print(f"📊 DB 이름 변경 완료: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("✅ 모든 DB 이름 변경 성공")
        return True
    else:
        print("❌ 일부 DB 이름 변경 실패")
        return False

if __name__ == "__main__":
    main() 