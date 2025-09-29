import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 로그 설정
logging.basicConfig(filename='news_to_notion.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def load_news_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_news():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    payload = {"page_size": 100}
    res = requests.post(url, headers=HEADERS, json=payload)
    if res.status_code != 200:
        logging.error(f"기존 뉴스 조회 실패: {res.status_code} {res.text}")
        return set()
    results = res.json().get('results', [])
    existing = set()
    for page in results:
        props = page['properties']
        title = props.get('제목', {}).get('title', [{}])[0].get('plain_text', '')
        date = props.get('발행일', {}).get('date', {}).get('start', '')
        if title and date:
            existing.add((title, date))
    return existing

def create_notion_page(news):
    url = "https://api.notion.com/v1/pages"
    properties = {
        "제목": {"title": [{"text": {"content": news["제목"]}}]},
        "URL": {"url": news["URL"]},
        "발행일": {"date": {"start": news["발행일"]}},
        "요약": {"rich_text": [{"text": {"content": news.get("요약", "")}}]},
        "태그": {"multi_select": [{"name": tag} for tag in news.get("태그", [])]},
        "중요도": {"select": {"name": news.get("중요도", "중간")}},
        "요약 품질 평가": {"select": {"name": news.get("요약 품질 평가", "")}}
    }
    payload = {"parent": {"database_id": NOTION_DATABASE_ID}, "properties": properties}
    res = requests.post(url, headers=HEADERS, json=payload)
    if res.status_code in [200, 201]:
        logging.info(f"입력 성공: {news['제목']} ({news['발행일']})")
        return True
    else:
        logging.error(f"입력 실패: {news['제목']} ({news['발행일']}) | {res.status_code} | {res.text}")
        return False

def main():
    news_list = load_news_data('news_data.json')
    existing = get_existing_news()
    count = 0
    for news in news_list:
        key = (news['제목'], news['발행일'])
        if key in existing:
            logging.info(f"중복 SKIP: {news['제목']} ({news['발행일']})")
            continue
        if create_notion_page(news):
            count += 1
    print(f"총 {count}건 입력 완료. (중복 제외)")

if __name__ == "__main__":
    main() 