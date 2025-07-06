import requests

headers = {
    "Authorization": "Bearer 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",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# GIA_작업장01 페이지 정보 확인
page_id = "227a613d25ff800ca97de24f6eb521a8"
response = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)

print(f"연결 상태: {response.status_code}")
print(f"페이지 정보: {response.json()}") 