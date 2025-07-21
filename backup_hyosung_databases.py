import os
import json
import requests
from datetime import datetime
import time

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')

# 백업할 DB ID들
HYOSUNG_DBS = {
    '기업 위험 프로파일': '228a613d25ff8122a10bc35772c8a05c',
    '글로벌 경쟁 분석': '228a613d25ff818d9bbac1b53e19dcbd', 
    '재무 및 프로젝트': '228a613d25ff814e9153fa459f1392ef',
    '태스크 관리': '228a613d25ff813dbb4ef3d3d984d186',
    '코드 관리': '228a613d25ff80f89903f8f92e549f44',
    '뉴스 정보': '22aa613d25ff80888257c652d865f85a'
}

def backup_database(db_name, db_id):
    """단순한 DB 백업 함수"""
    print(f"📦 {db_name} DB 백업 시작...")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    try:
        # DB 정보 조회
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # JSON 백업
            backup_file = f"backups/phase0_20250719_2310/{db_name}_backup.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {db_name} 백업 완료: {len(data.get('results', []))}개 레코드")
            return True
        else:
            print(f"❌ {db_name} 백업 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {db_name} 백업 오류: {e}")
        return False

def main():
    """메인 백업 프로세스"""
    print("🚀 효성중공업 DB 백업 시작")
    print("=" * 50)
    
    success_count = 0
    total_count = len(HYOSUNG_DBS)
    
    for db_name, db_id in HYOSUNG_DBS.items():
        if backup_database(db_name, db_id):
            success_count += 1
        time.sleep(1)  # API 호출 간격 1초
    
    print("=" * 50)
    print(f"📊 백업 완료: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("✅ 모든 DB 백업 성공")
        return True
    else:
        print("❌ 일부 DB 백업 실패")
        return False

if __name__ == "__main__":
    main() 