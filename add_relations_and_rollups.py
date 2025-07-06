import requests

NOTION_TOKEN = "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"
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# 실제 DB ID는 생성된 DB의 id를 사용해야 함
PROJECT_DB_ID = "228a613d-25ff-818d-9bba-c1b53e19dcbd"
TASK_DB_ID = "228a613d-25ff-814e-9153-fa459f1392ef"
TODO_DB_ID = "228a613d-25ff-813d-bb4e-f3d3d984d186"

# 1. 프로젝트 DB에 태스크 Relation 추가
def add_project_task_relation():
    patch = {
        "properties": {
            "관련태스크": {
                "relation": {
                    "database_id": TASK_DB_ID,
                    "type": "dual_property",
                    "dual_property": {}
                }
            }
        }
    }
    resp = requests.patch(f"https://api.notion.com/v1/databases/{PROJECT_DB_ID}", headers=HEADERS, json=patch)
    print(f"프로젝트-태스크 관계형 추가 결과: {resp.status_code}")
    print(resp.text)

# 2. 태스크 DB에 프로젝트/TO DO Relation 추가
def add_task_relations():
    patch = {
        "properties": {
            "상위프로젝트": {
                "relation": {
                    "database_id": PROJECT_DB_ID,
                    "type": "dual_property",
                    "dual_property": {}
                }
            },
            "관련할일": {
                "relation": {
                    "database_id": TODO_DB_ID,
                    "type": "dual_property",
                    "dual_property": {}
                }
            }
        }
    }
    resp = requests.patch(f"https://api.notion.com/v1/databases/{TASK_DB_ID}", headers=HEADERS, json=patch)
    print(f"태스크 관계형 추가 결과: {resp.status_code}")
    print(resp.text)

# 3. TO DO DB에 상위태스크 Relation 추가
def add_todo_relation():
    patch = {
        "properties": {
            "상위태스크": {
                "relation": {
                    "database_id": TASK_DB_ID,
                    "type": "dual_property",
                    "dual_property": {}
                }
            }
        }
    }
    resp = requests.patch(f"https://api.notion.com/v1/databases/{TODO_DB_ID}", headers=HEADERS, json=patch)
    print(f"TO DO-태스크 관계형 추가 결과: {resp.status_code}")
    print(resp.text)

if __name__ == "__main__":
    add_project_task_relation()
    add_task_relations()
    add_todo_relation() 