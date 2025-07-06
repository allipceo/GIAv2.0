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

# 예시: 각 DB의 모든 페이지에 태그 속성(분야별, 작업유형, 기술분류) 업데이트
# 실제 태그 속성명/구조에 맞게 수정 필요

def get_all_pages(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    resp = requests.post(url, headers=HEADERS)
    results = resp.json().get("results", [])
    return results

def update_page_tags(page_id, tags):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {"properties": tags}
    resp = requests.patch(url, headers=HEADERS, json=data)
    print(f"페이지 {page_id} 태그 업데이트 결과: {resp.status_code}")

if __name__ == "__main__":
    # 프로젝트 DB: 분야별, 기술분류 태그 예시 적용
    for page in get_all_pages(PROJECT_DB_ID):
        tags = {
            # 예시: 실제 태그 속성명에 맞게 수정
            # "분야별": {"multi_select": [{"name": "보험"}]},
            # "기술분류": {"multi_select": [{"name": "DB"}]}
        }
        update_page_tags(page["id"], tags)
    # 태스크/TO DO DB도 유사하게 반복
    print("모든 샘플 데이터 태그 적용 완료 (예시)") 