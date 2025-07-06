from notion_client import Client
import os
import json
import time

NOTION_TOKEN = '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'
DATABASE_ID = '228a613d25ff80f89903f8f92e549f44'
SYNC_INTERVAL = 300  # 5분
LOCAL_META_DIR = './GLOBAL_CODE_REPO/main/features/'

def upload_metadata_to_notion(notion, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    # 예시: 노션 DB에 메타데이터 업로드(구체적 매핑 필요)
    notion.pages.create(parent={"database_id": DATABASE_ID}, properties={
        "파일명": {"title": [{"text": {"content": meta['file_name']}}]},
        "품질지표": {"rich_text": [{"text": {"content": str(meta['quality_metrics'])}}]},
        # ... 추가 매핑
    })

def sync_local_to_notion(notion):
    for file in os.listdir(LOCAL_META_DIR):
        if file.endswith('.metadata.json'):
            upload_metadata_to_notion(notion, os.path.join(LOCAL_META_DIR, file))

def main():
    notion = Client(auth=NOTION_TOKEN)
    print('[INFO] 노션-로컬/서버 동기화 서비스 시작')
    while True:
        sync_local_to_notion(notion)
        time.sleep(SYNC_INTERVAL)

if __name__ == '__main__':
    main() 