import os
from notion_client import Client
from datetime import datetime, date
import requests
import re

NOTION_TOKEN = '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'
DATABASE_ID = '228a613d25ff8122a10bc35772c8a05c'
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

def get_registered_files(notion, database_id):
    try:
        results = notion.databases.query(database_id=database_id).get('results', [])
        file_map = {}
        for row in results:
            title_prop = row['properties'].get('코드명', {})
            if title_prop.get('title') and len(title_prop['title']) > 0:
                file_name = title_prop['title'][0]['plain_text']
                file_map[file_name] = row['id']
        print("✅ 기존 파일 조회 성공")
        return file_map
    except Exception as e:
        print(f"❌ 기존 파일 조회 오류: {str(e)}")
        print(f"   오류 발생 Database ID: {database_id}")
        print("   Notion 통합에 해당 데이터베이스가 공유되었는지, ID가 정확한지 확인해주세요.")
        return None

def extract_snippet(file_content):
    snippet_match = re.search(r'# GI_SNIPPET\n(.*?)# /GI_SNIPPET', file_content, re.DOTALL)
    if snippet_match:
        return snippet_match.group(1).strip()
    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        if re.match(r'^\s*(def|class)\s+\w+:', line):
            snippet_lines = lines[i : i + 20]
            return "\n".join(snippet_lines).strip()
    snippet = file_content[:500].strip()
    if len(file_content) > 500:
        snippet += "..."
    return snippet

def upsert_file_to_notion(notion, file_name, file_map, database_id):
    try:
        file_path = os.path.join(os.getcwd(), file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        snippet_content = extract_snippet(file_content)
        formatted_code_content = f"```python\n{file_content}\n```"
        if os.path.getsize(file_path) > 3 * 1024:
            first_30_lines = "\n".join(file_content.splitlines()[:30])
            formatted_code_content = f"```python\n{first_30_lines}\n```\n\n(전체 코드는 3KB 초과로 인해 첫 30라인만 등록되었습니다. 로컬 저장소에서 확인해주세요.)"
        if len(formatted_code_content) > 2000:
            formatted_code_content = formatted_code_content[:1997] + "..."
        properties = {
            "코드명": {"title": [{"text": {"content": file_name}}]},
            "개선이력": {"rich_text": [{"text": {"content": "최초 등록"}}]},
            "작성일": {"date": {"start": date.today().isoformat()}},
            "작성자": {"rich_text": [{"text": {"content": "서대리"}}]},
            "주요내용": {"rich_text": [{"text": {"content": snippet_content}}]},
        }
        if file_name in file_map:
            notion.pages.update(page_id=file_map[file_name], properties=properties)
            print(f"✅ [업데이트] {file_name}")
            return True
        else:
            notion.pages.create(parent={"database_id": database_id}, properties=properties)
            print(f"🆕 [신규등록] {file_name}")
            return True
    except requests.exceptions.RequestException as req_e:
        print(f"❌ [등록 실패] {file_name}: Notion API 오류 발생 - {req_e}")
        if req_e.response is not None:
            print(f"   응답 상태 코드: {req_e.response.status_code}")
            print(f"   응답 내용: {req_e.response.json()}")
        print("   Notion 통합에 해당 데이터베이스가 공유되었는지, ID가 정확한지 확인해주세요.")
        return False
    except Exception as e:
        print(f"❌ [등록 실패] {file_name}: 기타 오류 발생 - {str(e)}")
        return False

def main():
    print("🚀 노션 코드 동기화 시작!")
    print("==================================================")
    notion = Client(auth=NOTION_TOKEN)
    try:
        notion.users.list()
        print("✅ 노션 연결 성공")
    except Exception as e:
        print(f"❌ 노션 연결 실패: {e}")
        print("   NOTION_TOKEN이 정확하고 유효한지 확인해주세요.")
        return
    file_map = get_registered_files(notion, DATABASE_ID)
    if file_map is None:
        print("==================================================")
        print("⚠️  DB 조회에 실패하여 파일 동기화를 중단합니다.")
        return
    python_files_found = [file_name for file_name in os.listdir('.') if file_name.endswith('.py') and file_name != os.path.basename(__file__)]
    print(f"📁 발견된 Python 파일: {len(python_files_found)}개")
    for fname in python_files_found:
        print(f"   📄 {fname}")
    print("==================================================")
    print("🔄 파일 동기화 처리 중...")
    new_registrations = 0
    updates = 0
    failures = 0
    for file_name in python_files_found:
        success = upsert_file_to_notion(notion, file_name, file_map, DATABASE_ID)
        if not success:
            failures += 1
        elif file_name in file_map:
            updates += 1
        else:
            new_registrations += 1
    print("==================================================")
    print("📊 최종 결과:")
    print(f"   🆕 신규 등록: {new_registrations}개")
    print(f"   ✅ 업데이트: {updates}개")
    print(f"   ❌ 실패: {failures}개")
    print(f"   📋 총 처리: {len(python_files_found)}개")
    if failures > 0:
        print("⚠️  파일 처리 실패. 오류 메시지를 확인해주세요.")
    else:
        print("🎉 모든 파일이 성공적으로 동기화되었습니다!")

if __name__ == '__main__':
    main() 