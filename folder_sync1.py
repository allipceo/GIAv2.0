import os
from notion_client import Client
from datetime import datetime

NOTION_TOKEN = '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'
DATABASE_ID = '228a613d25ff8122a10bc35772c8a05c'

# 3KB = 3072 bytes
MAX_SIZE = 3072
MAX_LINES = 30

FIELDS = {
    'title': '코드명',
    'select': '개선이력',
    'date': '작성일',
    'author': '작성자',
    'snippet': '주요내용',
}


def get_registered_files(notion):
    results = notion.databases.query(database_id=DATABASE_ID).get('results', [])
    file_map = {}
    for row in results:
        title_prop = row['properties'].get(FIELDS['title'], {})
        if title_prop.get('title') and len(title_prop['title']) > 0:
            file_name = title_prop['title'][0]['plain_text']
            file_map[file_name] = row['id']
    return file_map


def extract_snippet(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        size = os.path.getsize(file_path)
        if size <= MAX_SIZE:
            snippet = content[:2000]  # Notion rich_text 제한 고려
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= MAX_LINES:
                        break
                    lines.append(line)
            snippet = ''.join(lines)[:2000]
        return snippet
    except Exception as e:
        return f'[스니펫 추출 오류: {str(e)}]'


def upsert_file_to_notion(notion, file_name, file_map, snippet):
    properties = {
        FIELDS['title']: {"title": [{"text": {"content": file_name}}]},
        FIELDS['select']: {"select": {"name": "최초등록"}},
        FIELDS['date']: {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
        FIELDS['author']: {"rich_text": [{"text": {"content": "서대리"}}]},
        FIELDS['snippet']: {"rich_text": [{"text": {"content": snippet}}]},
    }
    try:
        if file_name in file_map:
            notion.pages.update(page_id=file_map[file_name], properties=properties)
            return '업데이트'
        else:
            notion.pages.create(parent={"database_id": DATABASE_ID}, properties=properties)
            return '신규등록'
    except Exception as e:
        return f'오류: {str(e)}'


def main():
    print("🚀 노션 코드 동기화 시작!")
    notion = Client(auth=NOTION_TOKEN)
    file_map = get_registered_files(notion)
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != os.path.basename(__file__)]
    total = len(py_files)
    new_count = 0
    update_count = 0
    error_count = 0
    errors = []
    for file_name in py_files:
        snippet = extract_snippet(file_name)
        result = upsert_file_to_notion(notion, file_name, file_map, snippet)
        if result == '신규등록':
            new_count += 1
            print(f"🆕 [신규등록] {file_name}")
        elif result == '업데이트':
            update_count += 1
            print(f"✅ [업데이트] {file_name}")
        else:
            error_count += 1
            errors.append((file_name, result))
            print(f"❌ [오류] {file_name}: {result}")
    print("\n📊 실행 결과 요약:")
    print(f"   총 파일: {total}")
    print(f"   신규 등록: {new_count}")
    print(f"   업데이트: {update_count}")
    print(f"   오류: {error_count}")
    if error_count > 0:
        for fname, msg in errors:
            print(f"   - {fname}: {msg}")
    print(f"   완료 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 코드 동기화 완료!")

if __name__ == '__main__':
    main() 