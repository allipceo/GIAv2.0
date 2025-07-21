import os
import requests
import json
import time
from dotenv import load_dotenv
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
COMPANY_MASTER_DB_ID = "235a613d-25ff-817b-a072-e801efbfc91e"  # 새로 생성된 회사 정보 DB

# 관계형 속성을 추가할 DB 목록
DB_LIST = [
    {
        'name': '📊 기업 위험 프로파일 DB',
        'db_id': '228a613d25ff8122a10bc35772c8a05c'
    },
    {
        'name': '💰 기업 재무 및 프로젝트 DB',
        'db_id': '228a613d25ff818d9bbac1b53e19dcbd'
    },
    {
        'name': '🔋 신재생에너지 프로젝트 DB',
        'db_id': '228a613d25ff814e9153fa459f1392ef'
    },
    {
        'name': '👥 기업 핵심 인물 DB',
        'db_id': '228a613d25ff813dbb4ef3d3d984d186'
    },
    {
        'name': '🏛️ 정부 정책 영향 분석 DB',
        'db_id': '228a613d25ff80f89903f8f92e549f44'
    },
    {
        'name': '🌍 글로벌 보험중개 시장 DB',
        'db_id': '22aa613d25ff80888257c652d865f85a'
    }
]

def add_relation_property(db_info):
    """DB에 관계형 속성 추가"""
    db_name = db_info['name']
    db_id = db_info['db_id']
    
    print(f"🔗 {db_name}에 관계형 속성 추가...")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    # 관계형 속성 추가 요청
    update_data = {
        'properties': {
            '회사명': {
                'relation': {
                    'single_property': {},
                    'database_id': COMPANY_MASTER_DB_ID
                }
            }
        }
    }
    
    try:
        url = f"https://api.notion.com/v1/databases/{db_id}"
        response = requests.patch(url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            print(f"✅ {db_name} 관계형 속성 추가 완료")
            return True
        else:
            print(f"❌ {db_name} 관계형 속성 추가 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {db_name} 관계형 속성 추가 오류: {e}")
        return False

def main():
    """메인 관계형 속성 추가 프로세스"""
    print("🔗 관계형 속성 추가 시작")
    print("=" * 50)
    
    success_count = 0
    total_count = len(DB_LIST)
    
    for db_info in DB_LIST:
        if add_relation_property(db_info):
            success_count += 1
        time.sleep(1)  # API 호출 간격 1초
    
    print("=" * 50)
    print(f"📊 관계형 속성 추가 완료: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("✅ 모든 DB에 관계형 속성 추가 성공")
        return True
    else:
        print("❌ 일부 DB 관계형 속성 추가 실패")
        return False

if __name__ == "__main__":
    main() 