import time
from notion_client import Client
import subprocess

NOTION_TOKEN = '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'
DATABASE_ID = '228a613d25ff80f89903f8f92e549f44'
CHECK_INTERVAL = 30  # 초 단위

notion = Client(auth=NOTION_TOKEN)

def get_triggered_rows():
    query = notion.databases.query(database_id=DATABASE_ID, filter={
        "property": "실행", "checkbox": {"equals": True}
    })
    return query.get('results', [])

def reset_trigger(row_id):
    notion.pages.update(page_id=row_id, properties={"실행": {"checkbox": False}})

def run_automation():
    subprocess.run(['python', 'run_code_management_automation.py'])

def main():
    print('[INFO] 노션 대시보드 트리거 감시 시작')
    while True:
        rows = get_triggered_rows()
        for row in rows:
            print(f"[INFO] 트리거 감지: {row['id']}")
            run_automation()
            reset_trigger(row['id'])
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main() 