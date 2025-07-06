import requests

NOTION_TOKEN = "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"
NOTION_VERSION = "2022-06-28"
PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

def create_database(title, properties):
    data = {
        "parent": {"page_id": PAGE_ID},
        "title": [{"text": {"content": title}}],
        "properties": properties
    }
    resp = requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json=data)
    print(f"{title} DB 생성 결과: {resp.status_code}")
    print(resp.text)
    return resp.json()

# 프로젝트 DB
project_props = {
    "프로젝트명": {"title": {}},
    "분야": {"select": {"options": [
        {"name": "보험", "color": "yellow"},
        {"name": "보험중개", "color": "yellow"},
        {"name": "방산", "color": "yellow"},
        {"name": "신재생", "color": "yellow"},
        {"name": "연구", "color": "yellow"},
        {"name": "정책", "color": "yellow"}
    ]}},
    "상태": {"select": {"options": [
        {"name": "검토중", "color": "gray"},
        {"name": "개시", "color": "blue"},
        {"name": "진행중", "color": "green"},
        {"name": "완료", "color": "purple"},
        {"name": "폐기", "color": "red"}
    ]}},
    "우선순위": {"select": {"options": [
        {"name": "높음", "color": "red"},
        {"name": "중간", "color": "yellow"},
        {"name": "낮음", "color": "blue"}
    ]}},
    "마감일": {"date": {}}
}

# 태스크 DB
Task_props = {
    "태스크명": {"title": {}},
    "상태": {"select": {"options": [
        {"name": "검토중", "color": "gray"},
        {"name": "개시", "color": "blue"},
        {"name": "진행중", "color": "green"},
        {"name": "완료", "color": "purple"},
        {"name": "폐기", "color": "red"}
    ]}},
    "우선순위": {"select": {"options": [
        {"name": "높음", "color": "red"},
        {"name": "중간", "color": "yellow"},
        {"name": "낮음", "color": "blue"}
    ]}},
    "마감일": {"date": {}}
}

# TO DO DB
Todo_props = {
    "할일명": {"title": {}},
    "상태": {"select": {"options": [
        {"name": "검토중", "color": "gray"},
        {"name": "개시", "color": "blue"},
        {"name": "진행중", "color": "green"},
        {"name": "완료", "color": "purple"},
        {"name": "폐기", "color": "red"}
    ]}},
    "우선순위": {"select": {"options": [
        {"name": "높음", "color": "red"},
        {"name": "중간", "color": "yellow"},
        {"name": "낮음", "color": "blue"}
    ]}},
    "마감일": {"date": {}}
}

if __name__ == "__main__":
    create_database("프로젝트", project_props)
    create_database("태스크", Task_props)
    create_database("TO DO", Todo_props) 