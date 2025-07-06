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

# 1. 프로젝트 DB에 태스크 완료율 롤업 추가
def add_project_rollup():
    patch = {
        "properties": {
            "태스크 완료율": {
                "rollup": {
                    "relation_property_name": "관련태스크",
                    "rollup_property_name": "상태",
                    "function": "percent_per_group",
                }
            }
        }
    }
    resp = requests.patch(f"https://api.notion.com/v1/databases/{PROJECT_DB_ID}", headers=HEADERS, json=patch)
    print(f"프로젝트 DB 롤업 추가 결과: {resp.status_code}")
    print(resp.text)

# 2. 태스크 DB에 TO DO 완료율 롤업 추가
def add_task_rollup():
    patch = {
        "properties": {
            "TO DO 완료율": {
                "rollup": {
                    "relation_property_name": "관련할일",
                    "rollup_property_name": "상태",
                    "function": "percent_per_group",
                }
            }
        }
    }
    resp = requests.patch(f"https://api.notion.com/v1/databases/{TASK_DB_ID}", headers=HEADERS, json=patch)
    print(f"태스크 DB 롤업 추가 결과: {resp.status_code}")
    print(resp.text)

if __name__ == "__main__":
    add_project_rollup()
    add_task_rollup() 