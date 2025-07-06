import requests
import time

NOTION_TOKEN = "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"
NOTION_VERSION = "2022-06-28"
PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# 1. 마스터 태그 DB 생성 및 20개 태그 입력
MASTER_TAGS = [
    ("보험", "분야별"), ("보험중개", "분야별"), ("방산", "분야별"), ("신재생", "분야별"), ("연구", "분야별"), ("정책", "분야별"),
    ("기획", "작업유형"), ("계획", "작업유형"), ("분석", "작업유형"), ("연구", "작업유형"), ("제안", "작업유형"), ("보고", "작업유형"), ("수집", "작업유형"), ("현황", "작업유형"), ("영업", "작업유형"),
    ("OA", "기술분류"), ("DB", "기술분류"), ("보안", "기술분류"), ("앱개발", "기술분류"), ("앱활용", "기술분류")
]

# 2. 프로젝트/태스크/TO DO DB 속성 정의
PROJECT_DB_PROPS = {
    "프로젝트명": {"title": {}},
    "분야": {"select": {"options": [{"name": t[0], "color": "yellow"} for t in MASTER_TAGS if t[1] == "분야별"]}},
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
    "마감일": {"date": {}},
    "관련태스크": {"relation": {"database_id": ""}},
}

# 태스크/TO DO DB 속성은 실제 생성 후 관계형 연결 필요

# 3. DB 생성 함수
def create_database(title, properties):
    data = {
        "parent": {"page_id": PAGE_ID},
        "title": [{"text": {"content": title}}],
        "properties": properties
    }
    resp = requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json=data)
    print(f"{title} DB 생성 결과: {resp.status_code}")
    return resp.json()

# 4. 마스터 태그 DB 생성 및 태그 입력
def create_master_tags_db():
    props = {
        "태그명": {"title": {}},
        "분류": {"select": {"options": [
            {"name": "분야별", "color": "yellow"},
            {"name": "작업유형", "color": "blue"},
            {"name": "기술분류", "color": "green"}
        ]}},
        "설명": {"rich_text": {}}
    }
    db = create_database("마스터 태그", props)
    db_id = db.get("id")
    # 태그 20개 입력
    for tag, cat in MASTER_TAGS:
        page = {
            "parent": {"database_id": db_id},
            "properties": {
                "태그명": {"title": [{"text": {"content": tag}}]},
                "분류": {"select": {"name": cat}},
                "설명": {"rich_text": [{"text": {"content": f"{cat} 태그"}}]}
            }
        }
        requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=page)
    print("마스터 태그 20개 입력 완료")
    return db_id

# 5. 전체 시스템 구축
if __name__ == "__main__":
    # 1. 마스터 태그 DB 및 태그 입력
    master_tag_db_id = create_master_tags_db()
    # 2. 프로젝트 DB 생성 (관계형 연결은 후처리)
    project_db = create_database("프로젝트", PROJECT_DB_PROPS)
    # 3. 태스크 DB, TO DO DB 생성 (관계형 연결은 후처리)
    # ... (추가 구현 필요)
    print("전체 시스템 구축 1차 완료 (마스터 태그, 프로젝트 DB)") 