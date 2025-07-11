import requests

NOTION_TOKEN = "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"
DATABASE_ID = "22aa613d25ff80888257c652d865f85a"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

response = requests.get(
    f"https://api.notion.com/v1/databases/{DATABASE_ID}",
    headers=headers
)
print("DB 속성:", response.json().get("properties", {}).keys()) 