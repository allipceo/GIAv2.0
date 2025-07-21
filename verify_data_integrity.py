import os
import requests
import json
import time
from dotenv import load_dotenv
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
COMPANY_MASTER_DB_ID = "235a613d-25ff-817b-a072-e801efbfc91e"

def verify_company_master():
    """회사 정보 마스터 DB 검증"""
    print("🔍 회사 정보 마스터 DB 검증...")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"https://api.notion.com/v1/databases/{COMPANY_MASTER_DB_ID}/query"
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('results', [])
            
            # 효성중공업 레코드 확인
            hyosung_found = False
            for record in records:
                properties = record.get('properties', {})
                company_name = properties.get('회사명', {}).get('title', [])
                if company_name and company_name[0].get('text', {}).get('content') == '효성중공업':
                    hyosung_found = True
                    print(f"✅ 효성중공업 레코드 확인: {record['id']}")
                    break
            
            if hyosung_found:
                print(f"✅ 회사 정보 마스터 DB: {len(records)}개 레코드")
                return True
            else:
                print("❌ 효성중공업 레코드를 찾을 수 없음")
                return False
        else:
            print(f"❌ 회사 정보 마스터 DB 조회 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 회사 정보 마스터 DB 검증 오류: {e}")
        return False

def verify_relation_properties():
    """관계형 속성 검증"""
    print("🔍 관계형 속성 검증...")
    
    db_list = [
        {'name': '📊 기업 위험 프로파일 DB', 'id': '228a613d25ff8122a10bc35772c8a05c'},
        {'name': '💰 기업 재무 및 프로젝트 DB', 'id': '228a613d25ff818d9bbac1b53e19dcbd'},
        {'name': '🔋 신재생에너지 프로젝트 DB', 'id': '228a613d25ff814e9153fa459f1392ef'},
        {'name': '👥 기업 핵심 인물 DB', 'id': '228a613d25ff813dbb4ef3d3d984d186'},
        {'name': '🏛️ 정부 정책 영향 분석 DB', 'id': '228a613d25ff80f89903f8f92e549f44'},
        {'name': '🌍 글로벌 보험중개 시장 DB', 'id': '22aa613d25ff80888257c652d865f85a'}
    ]
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    success_count = 0
    total_count = len(db_list)
    
    for db_info in db_list:
        try:
            url = f"https://api.notion.com/v1/databases/{db_info['id']}/query"
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('results', [])
                
                # 관계형 속성 확인
                relation_found = False
                for record in records:
                    properties = record.get('properties', {})
                    if '회사명' in properties:
                        relation_found = True
                        break
                
                if relation_found:
                    print(f"✅ {db_info['name']}: {len(records)}개 레코드, 관계형 속성 확인")
                    success_count += 1
                else:
                    print(f"❌ {db_info['name']}: 관계형 속성 없음")
            else:
                print(f"❌ {db_info['name']}: 조회 실패")
                
        except Exception as e:
            print(f"❌ {db_info['name']} 검증 오류: {e}")
    
    print(f"📊 관계형 속성 검증: {success_count}/{total_count} 성공")
    return success_count == total_count

def verify_record_counts():
    """레코드 수 검증"""
    print("🔍 레코드 수 검증...")
    
    # 백업 파일에서 레코드 수 확인
    backup_dir = "backups/phase0_20250719_2310"
    expected_counts = {
        "기업 위험 프로파일_backup.json": 18,
        "글로벌 경쟁 분석_backup.json": 7,
        "재무 및 프로젝트_backup.json": 30,
        "태스크 관리_backup.json": 49,
        "코드 관리_backup.json": 17,
        "뉴스 정보_backup.json": 100
    }
    
    success_count = 0
    total_count = len(expected_counts)
    
    for filename, expected_count in expected_counts.items():
        filepath = os.path.join(backup_dir, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    actual_count = len(data.get('results', []))
                    
                    if actual_count == expected_count:
                        print(f"✅ {filename}: {actual_count}개 레코드 (예상: {expected_count})")
                        success_count += 1
                    else:
                        print(f"❌ {filename}: {actual_count}개 레코드 (예상: {expected_count})")
            except Exception as e:
                print(f"❌ {filename}: 파일 읽기 오류 - {e}")
        else:
            print(f"❌ {filename}: 파일 없음")
    
    print(f"📊 레코드 수 검증: {success_count}/{total_count} 성공")
    return success_count == total_count

def main():
    """메인 검증 프로세스"""
    print("🔍 데이터 무결성 검증 시작")
    print("=" * 50)
    
    # 1. 회사 정보 마스터 DB 검증
    master_ok = verify_company_master()
    time.sleep(1)
    
    # 2. 관계형 속성 검증
    relation_ok = verify_relation_properties()
    time.sleep(1)
    
    # 3. 레코드 수 검증
    count_ok = verify_record_counts()
    
    print("=" * 50)
    print("📊 검증 결과:")
    print(f"✅ 회사 정보 마스터 DB: {'성공' if master_ok else '실패'}")
    print(f"✅ 관계형 속성: {'성공' if relation_ok else '실패'}")
    print(f"✅ 레코드 수: {'성공' if count_ok else '실패'}")
    
    if master_ok and relation_ok and count_ok:
        print("🎉 모든 검증 성공!")
        return True
    else:
        print("❌ 일부 검증 실패")
        return False

if __name__ == "__main__":
    main() 