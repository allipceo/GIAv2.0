import requests

NOTION_TOKEN = "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"
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

PROJECT_DB_ID = "228a613d-25ff-818d-9bba-c1b53e19dcbd"
TASK_DB_ID = "228a613d-25ff-814e-9153-fa459f1392ef"
TODO_DB_ID = "228a613d-25ff-813d-bb4e-f3d3d984d186"

# 1. 샘플 프로젝트 생성
def create_project():
    data = {
        "parent": {"database_id": PROJECT_DB_ID},
        "properties": {
            "프로젝트명": {"title": [{"text": {"content": "한화시스템 사이버보안 보험 제안"}}]},
            "분야": {"select": {"name": "보험"}},
            "상태": {"select": {"name": "진행중"}},
            "우선순위": {"select": {"name": "높음"}},
            "마감일": {"date": {"start": "2025-07-31"}}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"프로젝트 샘플 생성 결과: {resp.status_code}")
    project_id = resp.json().get("id")
    return project_id

# 2. 샘플 태스크 생성 (프로젝트와 연결)
def create_task(project_id):
    data = {
        "parent": {"database_id": TASK_DB_ID},
        "properties": {
            "태스크명": {"title": [{"text": {"content": "고객사 현황 분석"}}]},
            "상태": {"select": {"name": "진행중"}},
            "우선순위": {"select": {"name": "높음"}},
            "마감일": {"date": {"start": "2025-07-15"}},
            "상위프로젝트": {"relation": [{"id": project_id}]}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"태스크 샘플 생성 결과: {resp.status_code}")
    task_id = resp.json().get("id")
    return task_id

# 3. 샘플 TO DO 생성 (태스크와 연결)
def create_todo(task_id):
    data = {
        "parent": {"database_id": TODO_DB_ID},
        "properties": {
            "할일명": {"title": [{"text": {"content": "한화시스템 조직도 파악"}}]},
            "상태": {"select": {"name": "진행중"}},
            "우선순위": {"select": {"name": "높음"}},
            "마감일": {"date": {"start": "2025-07-10"}},
            "상위태스크": {"relation": [{"id": task_id}]}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"TO DO 샘플 생성 결과: {resp.status_code}")
    todo_id = resp.json().get("id")
    return todo_id

if __name__ == "__main__":
    project_id = create_project()
    task_id = create_task(project_id)
    todo_id = create_todo(task_id)
    print(f"샘플 데이터 생성 완료: 프로젝트 {project_id}, 태스크 {task_id}, TO DO {todo_id}") 