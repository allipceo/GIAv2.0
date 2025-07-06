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

# 샘플 프로젝트/태스크/TO DO 데이터 정의
data = [
    {
        "project": {
            "name": "해상풍력 발전사업 리스크 보험",
            "field": "보험",
            "status": "진행중",
            "priority": "중간",
            "due": "2025-08-15"
        },
        "tasks": [
            {
                "name": "시장 동향 분석",
                "status": "진행중",
                "priority": "중간",
                "due": "2025-07-20",
                "todos": [
                    {"name": "국내외 해상풍력 시장 조사", "status": "진행중", "priority": "중간", "due": "2025-07-10"},
                    {"name": "주요 리스크 요인 정리", "status": "진행중", "priority": "중간", "due": "2025-07-12"},
                    {"name": "경쟁사 보험 상품 비교", "status": "진행중", "priority": "중간", "due": "2025-07-15"}
                ]
            },
            {
                "name": "보험사 제휴 협상",
                "status": "진행중",
                "priority": "중간",
                "due": "2025-08-01",
                "todos": [
                    {"name": "협상 대상 보험사 선정", "status": "진행중", "priority": "중간", "due": "2025-07-18"},
                    {"name": "제휴 조건 초안 작성", "status": "진행중", "priority": "중간", "due": "2025-07-22"}
                ]
            }
        ]
    },
    {
        "project": {
            "name": "방산 수출기업 대상 마케팅",
            "field": "방산",
            "status": "진행중",
            "priority": "낮음",
            "due": "2025-09-01"
        },
        "tasks": [
            {
                "name": "타겟 기업 리스트 작성",
                "status": "진행중",
                "priority": "낮음",
                "due": "2025-08-01",
                "todos": [
                    {"name": "국내 방산기업 DB 구축", "status": "진행중", "priority": "낮음", "due": "2025-07-20"},
                    {"name": "수출 실적 분석", "status": "진행중", "priority": "낮음", "due": "2025-07-25"}
                ]
            },
            {
                "name": "네트워킹 이벤트 기획",
                "status": "진행중",
                "priority": "낮음",
                "due": "2025-08-15",
                "todos": [
                    {"name": "참가 기업 섭외", "status": "진행중", "priority": "낮음", "due": "2025-07-30"},
                    {"name": "행사 일정 조율", "status": "진행중", "priority": "낮음", "due": "2025-08-05"}
                ]
            }
        ]
    }
]

def create_project(p):
    data = {
        "parent": {"database_id": PROJECT_DB_ID},
        "properties": {
            "프로젝트명": {"title": [{"text": {"content": p["name"]}}]},
            "분야": {"select": {"name": p["field"]}},
            "상태": {"select": {"name": p["status"]}},
            "우선순위": {"select": {"name": p["priority"]}},
            "마감일": {"date": {"start": p["due"]}}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"프로젝트 생성 결과: {resp.status_code}")
    return resp.json().get("id")

def create_task(t, project_id):
    data = {
        "parent": {"database_id": TASK_DB_ID},
        "properties": {
            "태스크명": {"title": [{"text": {"content": t["name"]}}]},
            "상태": {"select": {"name": t["status"]}},
            "우선순위": {"select": {"name": t["priority"]}},
            "마감일": {"date": {"start": t["due"]}},
            "상위프로젝트": {"relation": [{"id": project_id}]}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"태스크 생성 결과: {resp.status_code}")
    return resp.json().get("id")

def create_todo(todo, task_id):
    data = {
        "parent": {"database_id": TODO_DB_ID},
        "properties": {
            "할일명": {"title": [{"text": {"content": todo["name"]}}]},
            "상태": {"select": {"name": todo["status"]}},
            "우선순위": {"select": {"name": todo["priority"]}},
            "마감일": {"date": {"start": todo["due"]}},
            "상위태스크": {"relation": [{"id": task_id}]}
        }
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"TO DO 생성 결과: {resp.status_code}")
    return resp.json().get("id")

if __name__ == "__main__":
    for project in data:
        project_id = create_project(project["project"])
        for task in project["tasks"]:
            task_id = create_task(task, project_id)
            for todo in task["todos"]:
                create_todo(todo, task_id)
    print("모든 프로젝트/태스크/TO DO 샘플 데이터 생성 완료") 