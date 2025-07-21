import os
import requests
import json
import time
from dotenv import load_dotenv
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
COMPANY_MASTER_DB_ID = "235a613d-25ff-817b-a072-e801efbfc91e"

def add_hyosung_to_master():
    """회사 정보 마스터 DB에 효성중공업 정보 추가"""
    print("🏢 회사 정보 마스터 DB에 효성중공업 정보 추가...")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    # 효성중공업 정보
    hyosung_data = {
        'parent': {'database_id': COMPANY_MASTER_DB_ID},
        'properties': {
            '회사명': {
                'title': [{'type': 'text', 'text': {'content': '효성중공업'}}]
            },
            '업종': {
                'select': {'name': '중공업'}
            },
            '설립년도': {
                'number': 1977
            },
            '본사위치': {
                'rich_text': [{'type': 'text', 'text': {'content': '울산광역시'}}]
            },
            '대표이사': {
                'rich_text': [{'type': 'text', 'text': {'content': '우태희'}}]
            },
            '매출규모': {
                'select': {'name': '1조 이상'}
            },
            '상장여부': {
                'checkbox': True
            },
            '프로젝트상태': {
                'select': {'name': '계약완료'}
            }
        }
    }
    
    try:
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=headers, json=hyosung_data)
        
        if response.status_code == 200:
            result = response.json()
            company_id = result['id']
            print(f"✅ 효성중공업 정보 추가 완료")
            print(f"📋 회사 ID: {company_id}")
            return company_id
        else:
            print(f"❌ 효성중공업 정보 추가 실패: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 효성중공업 정보 추가 오류: {e}")
        return None

def update_existing_records(company_id):
    """기존 레코드에 효성중공업 관계 설정"""
    print("🔗 기존 레코드에 효성중공업 관계 설정...")
    
    # 각 DB에서 레코드 조회 및 업데이트
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
    
    total_updated = 0
    
    for db_info in db_list:
        print(f"📝 {db_info['name']} 레코드 업데이트...")
        
        try:
            # DB에서 레코드 조회
            url = f"https://api.notion.com/v1/databases/{db_info['id']}/query"
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('results', [])
                
                # 배치 처리 (5개씩)
                batch_size = 5
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    
                    for record in batch:
                        page_id = record['id']
                        
                        # 회사명 관계 설정
                        update_data = {
                            'properties': {
                                '회사명': {
                                    'relation': [{'id': company_id}]
                                }
                            }
                        }
                        
                        update_url = f"https://api.notion.com/v1/pages/{page_id}"
                        update_response = requests.patch(update_url, headers=headers, json=update_data)
                        
                        if update_response.status_code == 200:
                            total_updated += 1
                        else:
                            print(f"❌ 레코드 업데이트 실패: {page_id}")
                    
                    time.sleep(1)  # API 호출 간격 1초
                
                print(f"✅ {db_info['name']}: {len(records)}개 레코드 처리 완료")
            else:
                print(f"❌ {db_info['name']} 레코드 조회 실패")
                
        except Exception as e:
            print(f"❌ {db_info['name']} 처리 오류: {e}")
    
    print(f"📊 총 {total_updated}개 레코드 업데이트 완료")
    return total_updated

def main():
    """메인 마이그레이션 프로세스"""
    print("🔄 효성중공업 데이터 마이그레이션 시작")
    print("=" * 50)
    
    # 1. 회사 정보 마스터 DB에 효성중공업 추가
    company_id = add_hyosung_to_master()
    if not company_id:
        print("❌ 효성중공업 정보 추가 실패 - 중단")
        return False
    
    time.sleep(1)  # API 호출 간격 1초
    
    # 2. 기존 레코드에 관계 설정
    total_updated = update_existing_records(company_id)
    
    print("=" * 50)
    print(f"✅ 마이그레이션 완료: {total_updated}개 레코드 업데이트")
    return True

if __name__ == "__main__":
    main() 