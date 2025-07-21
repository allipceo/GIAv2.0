import os
import requests
import json
from dotenv import load_dotenv
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
PARENT_PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"  # GIA_작업장 1단계

def create_company_master_database():
    """중앙 회사 정보 마스터 DB 생성"""
    print("🏢 중앙 회사 정보 마스터 DB 생성 시작...")
    
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    # 회사 정보 마스터 DB 스키마
    db_data = {
        'parent': {'type': 'page_id', 'page_id': PARENT_PAGE_ID},
        'title': [{'type': 'text', 'text': {'content': '📊 회사 정보 마스터 DB'}}],
        'properties': {
            '회사명': {'title': {}},
            '업종': {
                'select': {
                    'options': [
                        {'name': '중공업', 'color': 'blue'},
                        {'name': '에너지', 'color': 'green'},
                        {'name': '건설', 'color': 'yellow'},
                        {'name': 'IT', 'color': 'purple'},
                        {'name': '금융', 'color': 'orange'}
                    ]
                }
            },
            '설립년도': {'number': {'format': 'number_with_commas'}},
            '본사위치': {'rich_text': {}},
            '대표이사': {'rich_text': {}},
            '매출규모': {
                'select': {
                    'options': [
                        {'name': '1조 이상', 'color': 'red'},
                        {'name': '5000억-1조', 'color': 'orange'},
                        {'name': '1000억-5000억', 'color': 'yellow'},
                        {'name': '1000억 미만', 'color': 'green'}
                    ]
                }
            },
            '상장여부': {'checkbox': {}},
            '프로젝트상태': {
                'select': {
                    'options': [
                        {'name': '조사중', 'color': 'yellow'},
                        {'name': '제안준비', 'color': 'blue'},
                        {'name': '협상중', 'color': 'orange'},
                        {'name': '계약완료', 'color': 'green'}
                    ]
                }
            },
            '담당자': {'people': {}},
            '생성일': {'created_time': {}},
            '수정일': {'last_edited_time': {}}
        }
    }
    
    try:
        url = "https://api.notion.com/v1/databases"
        response = requests.post(url, headers=headers, json=db_data)
        
        if response.status_code == 200:
            result = response.json()
            db_id = result['id']
            print(f"✅ 회사 정보 마스터 DB 생성 완료")
            print(f"📋 DB ID: {db_id}")
            
            # DB ID를 파일에 저장
            with open('company_master_db_id.txt', 'w') as f:
                f.write(db_id)
            
            return db_id
        else:
            print(f"❌ DB 생성 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ DB 생성 오류: {e}")
        return None

if __name__ == "__main__":
    db_id = create_company_master_database()
    if db_id:
        print(f"🎯 다음 단계: config.env에 COMPANY_MASTER_DB_ID={db_id} 추가")
    else:
        print("❌ DB 생성 실패 - 노팀장 보고 필요") 