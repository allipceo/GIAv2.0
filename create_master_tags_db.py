import requests

def create_master_tags_database():
    headers = {
        "Authorization": "Bearer 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",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    database_data = {
        "parent": {"page_id": "227a613d25ff800ca97de24f6eb521a8"},
        "title": [{"text": {"content": "마스터 태그"}}],
        "properties": {
            "태그명": {"title": {}},
            "분류": {"select": {
                "options": [
                    {"name": "분야별", "color": "yellow"},
                    {"name": "작업유형", "color": "blue"},
                    {"name": "기술분류", "color": "green"}
                ]
            }},
            "설명": {"rich_text": {}}
        }
    }
    
    response = requests.post(
        "https://api.notion.com/v1/databases",
        headers=headers,
        json=database_data
    )
    
    print(f"DB 생성 결과: {response.status_code}")
    return response.json()

# 실행
create_master_tags_database() 