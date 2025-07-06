import requests
import os
from datetime import datetime

NOTION_TOKEN = "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"
NOTION_VERSION = "2022-06-28"
PAGE_ID = "227a613d25ff800ca97de24f6eb521a8"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

CODES = [
    "test_notion_connection.py",
    "create_master_tags_db.py",
    "create_basic_dbs.py",
    "add_relations_and_rollups.py",
    "add_rollups.py",
    "add_sample_data_and_views.py",
    "create_remaining_projects.py",
    "create_dashboard_views.py",
    "apply_final_tags.py"
]

STAGE_MAP = {
    "test_notion_connection.py": "1단계-연결테스트",
    "create_master_tags_db.py": "2단계-DB생성",
    "create_basic_dbs.py": "2단계-DB생성",
    "add_relations_and_rollups.py": "3단계-관계형연결",
    "add_rollups.py": "3단계-관계형연결",
    "add_sample_data_and_views.py": "4단계-데이터입력",
    "create_remaining_projects.py": "4단계-데이터입력",
    "create_dashboard_views.py": "5단계-자동화",
    "apply_final_tags.py": "5단계-자동화"
}

# 1. 코드 관리용 DB 생성
def create_code_db():
    props = {
        "코드명": {"title": {}},
        "단계": {"select": {"options": [
            {"name": "1단계-연결테스트", "color": "gray"},
            {"name": "2단계-DB생성", "color": "blue"},
            {"name": "3단계-관계형연결", "color": "green"},
            {"name": "4단계-데이터입력", "color": "yellow"},
            {"name": "5단계-자동화", "color": "red"}
        ]}},
        "주요내용": {"rich_text": {}},
        "파일원본코드": {"rich_text": {}},
        "태그": {"multi_select": {"options": [
            {"name": "API연결", "color": "blue"},
            {"name": "DB생성", "color": "green"},
            {"name": "관계형", "color": "yellow"},
            {"name": "롤업", "color": "red"},
            {"name": "자동화", "color": "purple"}
        ]}},
        "작성일": {"date": {}},
        "적용브랜치": {"rich_text": {}},
        "개선이력": {"rich_text": {}},
        "실행결과": {"rich_text": {}},
        "재사용성": {"select": {"options": [
            {"name": "높음", "color": "green"},
            {"name": "중간", "color": "yellow"},
            {"name": "낮음", "color": "red"}
        ]}},
        "작성자": {"rich_text": {}}
    }
    data = {
        "parent": {"page_id": PAGE_ID},
        "title": [{"text": {"content": "개발코드 모음"}}],
        "properties": props
    }
    resp = requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json=data)
    print(f"코드 DB 생성 결과: {resp.status_code}")
    return resp.json().get("id")

# 2. 코드 파일 등록
def register_code(db_id, filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    code_md = f"```python\n{code}\n```"
    stage = STAGE_MAP.get(filename, "기타")
    today = datetime.now().strftime("%Y-%m-%d")
    props = {
        "코드명": {"title": [{"text": {"content": filename}}]},
        "단계": {"select": {"name": stage}},
        "주요내용": {"rich_text": [{"text": {"content": f"{filename} 자동화 코드"}}]},
        "파일원본코드": {"rich_text": [{"text": {"content": code_md}}]},
        "태그": {"multi_select": [{"name": "자동화"}]},
        "작성일": {"date": {"start": today}},
        "적용브랜치": {"rich_text": [{"text": {"content": "GI-AGENT-v1.0"}}]},
        "개선이력": {"rich_text": [{"text": {"content": "최초 등록"}}]},
        "실행결과": {"rich_text": [{"text": {"content": "성공"}}]},
        "재사용성": {"select": {"name": "높음"}},
        "작성자": {"rich_text": [{"text": {"content": "서대리"}}]}
    }
    data = {
        "parent": {"database_id": db_id},
        "properties": props
    }
    resp = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    print(f"코드 {filename} 등록 결과: {resp.status_code}")

if __name__ == "__main__":
    db_id = create_code_db()
    for codefile in CODES:
        if os.path.exists(codefile):
            register_code(db_id, codefile)
    print("모든 코드 자동 등록 완료") 