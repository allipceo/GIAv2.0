from notion_client import Client
import subprocess
import time

NOTION_TOKEN = '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'
DATABASE_ID = '228a613d25ff80f89903f8f92e549f44'
CHECK_INTERVAL = 60

actions = {
    '코드 스캐너 실행': lambda: subprocess.run(['python', 'create_intelligent_code_scanner.py']),
    '매뉴얼 갱신': lambda: subprocess.run(['python', 'setup_advanced_code_repository.py']),
}

def get_action_rows(notion):
    query = notion.databases.query(database_id=DATABASE_ID)
    return query.get('results', [])

def main():
    notion = Client(auth=NOTION_TOKEN)
    print('[INFO] 노션 코드 자동화 에이전트 시작')
    while True:
        rows = get_action_rows(notion)
        for row in rows:
            for action_name, action_func in actions.items():
                if row['properties'].get(action_name, {}).get('checkbox', False):
                    print(f'[INFO] {action_name} 트리거 감지')
                    action_func()
                    notion.pages.update(page_id=row['id'], properties={action_name: {"checkbox": False}})
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main() 