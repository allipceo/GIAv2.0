#!/usr/bin/env python3
import requests
import json
import traceback

# Notion API 설정
TOKEN = ""
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def test_connection():
    """API 연결 테스트"""
    print("🔍 API 연결 테스트 중...")
    try:
        url = "https://api.notion.com/v1/search"
        data = {"filter": {"property": "object", "value": "database"}}
        
        response = requests.post(url, headers=headers, json=data)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            databases = response.json()["results"]
            print(f"✅ API 연결 성공! 발견된 DB 수: {len(databases)}")
            
            # DB 목록 출력
            for db in databases:
                if db.get("title") and len(db["title"]) > 0:
                    title = db["title"][0]["text"]["content"]
                    print(f"  - {title} (ID: {db['id']})")
            return True
        else:
            print(f"❌ API 연결 실패: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 연결 오류: {str(e)}")
        traceback.print_exc()
        return False

def find_databases():
    """정확한 DB ID 찾기"""
    print("\n📋 데이터베이스 ID 찾기...")
    try:
        url = "https://api.notion.com/v1/search"
        data = {"filter": {"property": "object", "value": "database"}}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            databases = response.json()["results"]
            task_db_id = None
            todo_db_id = None
            
            for db in databases:
                if db.get("title") and len(db["title"]) > 0:
                    title = db["title"][0]["text"]["content"]
                    if "태스크" in title:
                        task_db_id = db["id"]
                        print(f"✅ 태스크 DB 발견: {title} (ID: {task_db_id})")
                    elif "TO DO" in title:
                        todo_db_id = db["id"]
                        print(f"✅ TODO DB 발견: {title} (ID: {todo_db_id})")
            
            return task_db_id, todo_db_id
        else:
            print(f"❌ DB 검색 실패: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ DB 검색 오류: {str(e)}")
        traceback.print_exc()
        return None, None

def create_task_with_debug(task_db_id):
    """디버깅이 포함된 태스크 생성"""
    print(f"\n📝 태스크 생성 중... (DB ID: {task_db_id})")
    try:
        # 먼저 DB 스키마 확인
        db_url = f"https://api.notion.com/v1/databases/{task_db_id}"
        db_response = requests.get(db_url, headers=headers)
        
        if db_response.status_code == 200:
            db_info = db_response.json()
            print("✅ DB 스키마 확인 성공")
            print("사용 가능한 속성들:")
            for prop_name in db_info["properties"].keys():
                print(f"  - {prop_name}")
        else:
            print(f"❌ DB 스키마 확인 실패: {db_response.text}")
            return None
        
        # 태스크 데이터 생성
        task_data = {
            "parent": {"database_id": task_db_id},
            "properties": {
                "태스크명": {
                    "title": [{"text": {"content": "GIA 1단계 - 뉴스 수집 시스템 초기 테스트"}}]
                }
            }
        }
        
        # 선택적 속성 추가 (있는 경우에만)
        available_props = db_info["properties"].keys()
        
        if "우선순위" in available_props:
            task_data["properties"]["우선순위"] = {"select": {"name": "높음"}}
            
        if "상태" in available_props:
            task_data["properties"]["상태"] = {"select": {"name": "진행중"}}
            
        if "마감일" in available_props:
            task_data["properties"]["마감일"] = {"date": {"start": "2025-07-09"}}
            
        if "개시일" in available_props:
            task_data["properties"]["개시일"] = {"date": {"start": "2025-07-08"}}
        
        print("생성할 태스크 데이터:")
        print(json.dumps(task_data, indent=2, ensure_ascii=False))
        
        # 태스크 생성 요청
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=headers, json=task_data)
        
        print(f"태스크 생성 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            task_id = response.json()["id"]
            print(f"✅ 태스크 생성 성공! ID: {task_id}")
            return task_id
        else:
            print(f"❌ 태스크 생성 실패")
            print(f"응답 내용: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 태스크 생성 오류: {str(e)}")
        traceback.print_exc()
        return None

def create_todo_with_debug(todo_db_id, task_id=None):
    """디버깅이 포함된 TODO 생성"""
    print(f"\n✅ TODO 생성 중... (DB ID: {todo_db_id})")
    try:
        # DB 스키마 확인
        db_url = f"https://api.notion.com/v1/databases/{todo_db_id}"
        db_response = requests.get(db_url, headers=headers)
        
        if db_response.status_code == 200:
            db_info = db_response.json()
            print("✅ TODO DB 스키마 확인 성공")
            print("사용 가능한 속성들:")
            for prop_name in db_info["properties"].keys():
                print(f"  - {prop_name}")
        else:
            print(f"❌ TODO DB 스키마 확인 실패: {db_response.text}")
            return None
        
        # TODO 데이터 생성
        todo_data = {
            "parent": {"database_id": todo_db_id},
            "properties": {
                "할일명": {
                    "title": [{"text": {"content": "뉴스 수집 테스트용 Notion 페이지 생성"}}]
                }
            }
        }
        
        # 선택적 속성 추가
        available_props = db_info["properties"].keys()
        
        if "상태" in available_props:
            todo_data["properties"]["상태"] = {"select": {"name": "진행중"}}
            
        if "우선순위" in available_props:
            todo_data["properties"]["우선순위"] = {"select": {"name": "높음"}}
            
        if "시작일" in available_props:
            todo_data["properties"]["시작일"] = {"date": {"start": "2025-07-08"}}
            
        if "마감일" in available_props:
            todo_data["properties"]["마감일"] = {"date": {"start": "2025-07-08"}}
            
        if task_id and "상위태스크" in available_props:
            todo_data["properties"]["상위태스크"] = {"relation": [{"id": task_id}]}
        
        print("생성할 TODO 데이터:")
        print(json.dumps(todo_data, indent=2, ensure_ascii=False))
        
        # TODO 생성 요청
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=headers, json=todo_data)
        
        print(f"TODO 생성 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            todo_id = response.json()["id"]
            print(f"✅ TODO 생성 성공! ID: {todo_id}")
            return todo_id
        else:
            print(f"❌ TODO 생성 실패")
            print(f"응답 내용: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ TODO 생성 오류: {str(e)}")
        traceback.print_exc()
        return None

def main():
    print("🚀 GIA 프로젝트 - 노션 DB 데이터 생성 (디버그 모드)")
    print("=" * 60)
    
    # 1. API 연결 테스트
    if not test_connection():
        print("❌ API 연결 실패로 종료")
        return
    
    # 2. DB ID 찾기
    task_db_id, todo_db_id = find_databases()
    
    if not task_db_id:
        print("❌ 태스크 DB를 찾을 수 없음")
        return
        
    if not todo_db_id:
        print("❌ TODO DB를 찾을 수 없음")
        return
    
    # 3. 태스크 생성
    task_id = create_task_with_debug(task_db_id)
    
    # 4. TODO 생성
    todo_id = create_todo_with_debug(todo_db_id, task_id)
    
    # 5. 결과 요약
    print("\n" + "=" * 60)
    print("🎉 작업 완료!")
    if task_id:
        print(f"✅ 생성된 태스크 ID: {task_id}")
    if todo_id:
        print(f"✅ 생성된 TODO ID: {todo_id}")
    
    if task_id or todo_id:
        print("\n📋 노션 DB를 확인해보세요!")
    else:
        print("\n❌ 데이터 생성에 실패했습니다.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 전체 실행 오류: {str(e)}")
        traceback.print_exc()