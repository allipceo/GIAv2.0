#!/usr/bin/env python3
import requests
import json

# Notion API 설정
TOKEN = ""
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_task_data():
    # 태스크 DB ID (스크린샷에서 확인된 URL 기반)
    task_db_id = "228a613d25ff814e9153fad59f1392af"
    
    # 새로운 태스크 생성
    task_data = {
        "parent": {"database_id": task_db_id},
        "properties": {
            "태스크명": {
                "title": [{"text": {"content": "GIA 1단계 - 뉴스 수집 시스템 초기 테스트"}}]
            },
            "우선순위": {"select": {"name": "높음"}},
            "상태": {"select": {"name": "진행중"}},
            "마감일": {"date": {"start": "2025-07-09"}}
        }
    }
    
    url = "https://api.notion.com/v1/pages"
    response = requests.post(url, headers=headers, json=task_data)
    
    if response.status_code == 200:
        task_id = response.json()["id"]
        print(f"✅ 태스크 생성 성공: {task_id}")
        return task_id
    else:
        print(f"❌ 태스크 생성 실패: {response.status_code}")
        print(response.text)
        return None

def create_todo_data(task_id):
    # TODO DB ID (스크린샷에서 확인된 URL 기반)  
    todo_db_id = "228a613d25ff813dbb4ef3ddd984d186"
    
    # 새로운 TODO 생성
    todo_data = {
        "parent": {"database_id": todo_db_id},
        "properties": {
            "할일명": {
                "title": [{"text": {"content": "뉴스 수집 테스트용 Notion 페이지 생성"}}]
            },
            "상태": {"select": {"name": "진행중"}},
            "우선순위": {"select": {"name": "높음"}},
            "시작일": {"date": {"start": "2025-07-08"}},
            "마감일": {"date": {"start": "2025-07-08"}}
        }
    }
    
    if task_id:
        todo_data["properties"]["상위태스크"] = {"relation": [{"id": task_id}]}
    
    url = "https://api.notion.com/v1/pages"
    response = requests.post(url, headers=headers, json=todo_data)
    
    if response.status_code == 200:
        todo_id = response.json()["id"]
        print(f"✅ TODO 생성 성공: {todo_id}")
        return todo_id
    else:
        print(f"❌ TODO 생성 실패: {response.status_code}")
        print(response.text)
        return None

# 실행
print("🚀 노션 DB 데이터 생성 시작")
task_id = create_task_data()
todo_id = create_todo_data(task_id)
print("🎉 완료!")