#!/usr/bin/env python3
"""
GIA Notion 템플릿 자동 생성 스크립트
- 태스크 DB, TODO DB에 템플릿 역할 페이지 자동 생성
- 생성 결과/에러 로그, 이력 Notion 페이지 기록, 안내문 출력 등 포함
"""
import requests
import json
import datetime

# --------------------
# 1. 템플릿 구성 요소 정의
# --------------------

# TASK 템플릿 구성 (실제 속성명/타입에 맞게 수정)
TASK_TEMPLATE_CONFIG = {
    "template_name": "[GIA] 새로운 TASK",
    "default_properties": {
        "태스크명": {"title": [{"text": {"content": "[GIA] 새로운 TASK"}}]},
        "목표": {"rich_text": [{"text": {"content": "구체적인 목표를 입력하세요."}}]},
        "우선순위": {"select": {"name": "중간"}},
        "상태": {"select": {"name": "대기"}},
        "개시일": {"date": {"start": "2025-07-08"}},
        "마감일": {"date": {"start": "2025-07-08"}},
        "기대효과": {"rich_text": [{"text": {"content": "예상되는 효과를 입력하세요."}}]}
        # 관계형 필드는 필요시 추가
    },
    "default_content": [
        # 안내문
        {"object": "block", "type": "callout", "callout": {"icon": {"emoji": "ℹ️"}, "rich_text": [{"type": "text", "text": {"content": "이 페이지를 복제하여 새 업무를 시작하세요."}}]}},
        # 섹션 헤딩
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📋 태스크 개요"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "여기에 태스크의 개요를 입력하세요."}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎯 상세 목표"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "목표 1"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "목표 2"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📈 기대 효과"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "여기에 기대 효과를 입력하세요."}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "세부 정보(클릭하여 펼치기)"}}], "children": [
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "여기에 추가 정보를 입력하세요."}}]}}
        ]}}
    ]
}

# TODO 템플릿 구성
TODO_TEMPLATE_CONFIG = {
    "template_name": "[GIA] 새로운 TODO",
    "default_properties": {
        "할일명": {"title": [{"text": {"content": "[GIA] 새로운 TODO"}}]},
        "상태": {"select": {"name": "대기"}},
        "우선순위": {"select": {"name": "중간"}},
        "시작일": {"date": {"start": "2025-07-08"}},
        "마감일": {"date": {"start": "2025-07-08"}}
    },
    "default_content": [
        {"object": "block", "type": "callout", "callout": {"icon": {"emoji": "ℹ️"}, "rich_text": [{"type": "text", "text": {"content": "이 템플릿을 사용하여 새로운 TODO를 생성하십시오."}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "✅ 작업 내용"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "여기에 할 일을 구체적으로 입력하세요."}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📝 참고사항"}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "세부 정보(클릭하여 펼치기)"}}], "children": [
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "여기에 참고사항을 입력하세요."}}]}}
        ]}}
    ]
}

# --------------------
# 2. NotionTemplateCreator 클래스 정의 (구현 예정)
# --------------------

class NotionTemplateCreator:
    def __init__(self, token):
        """
        Notion API 토큰 초기화
        """
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.log_file = "template_creation_log.txt"

    def log(self, message):
        """
        로그 파일에 메시지 기록
        """
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")

    def create_template(self, db_id, template_config):
        """
        템플릿 역할 페이지 생성 (Notion API pages.create)
        - db_id: 대상 DB ID
        - template_config: 템플릿 구성 요소(dict)
        반환: (성공 시) 페이지 ID, (실패 시) None
        """
        # DB ID 유효성 체크
        if not (isinstance(db_id, str) and len(db_id.replace('-', '')) == 32):
            msg = f"❌ DB ID 형식 오류: {db_id}"
            print(msg)
            self.log(msg)
            return None
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": db_id},
            "properties": template_config["default_properties"],
            "children": template_config["default_content"],
            "icon": {"emoji": "📝"}
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code in [200, 201]:
                page_id = response.json()["id"].replace("-", "")
                notion_url = f"https://www.notion.so/{page_id}"
                msg = f"✅ 템플릿 생성 성공: {template_config['template_name']} | {notion_url}"
                print(msg)
                self.log(msg)
                return notion_url
            else:
                msg = f"❌ 템플릿 생성 실패: {template_config['template_name']} | {response.status_code} | {response.text}"
                print(msg)
                self.log(msg)
                if response.status_code == 404:
                    print("[안내] 404 오류: Integration(토큰)이 해당 DB에 초대되어 있는지 확인하세요.")
                return None
        except Exception as e:
            msg = f"❌ 예외 발생: {e}"
            print(msg)
            self.log(msg)
            return None

    def _mark_as_template(self, page_id, template_name, title_prop):
        """
        (선택) 생성된 페이지의 제목을 template_name으로 업데이트
        - page_id: Notion 페이지 ID
        - template_name: 템플릿 이름
        - title_prop: DB의 title 속성명(예: '태스크명', '할일명')
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": {title_prop: {"title": [{"text": {"content": template_name}}]}}}
        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            if response.status_code in [200, 201]:
                msg = f"✅ 제목 업데이트 성공: {template_name}"
                print(msg)
                self.log(msg)
            else:
                msg = f"❌ 제목 업데이트 실패: {template_name} | {response.status_code} | {response.text}"
                print(msg)
                self.log(msg)
        except Exception as e:
            msg = f"❌ 예외 발생(제목 업데이트): {e}"
            print(msg)
            self.log(msg)

    def create_all_gia_templates(self, task_db_id, todo_db_id):
        """
        TASK/TO-DO 템플릿 역할 페이지를 각각 1개씩 생성
        생성된 Notion 링크를 반환
        """
        print("[실행] TASK 템플릿 생성...")
        task_url = self.create_template(task_db_id, TASK_TEMPLATE_CONFIG)
        print("[실행] TODO 템플릿 생성...")
        todo_url = self.create_template(todo_db_id, TODO_TEMPLATE_CONFIG)
        print("[안내] Notion API로는 DB 템플릿 직접 등록이 불가합니다. 생성된 페이지를 Notion UI에서 템플릿으로 등록하세요.")
        return task_url, todo_url

# --------------------
# 3. main 함수 (실행 예시)
# --------------------

def main():
    # 실제 실행 시 아래 값을 조대표님께 받은 값으로 교체
    token = "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"
    task_db_id = "228a613d25ff814e9153fa459f1392ef"
    todo_db_id = "228a613d25ff813dbb4ef3d3d984d186"

    creator = NotionTemplateCreator(token)
    creator.create_all_gia_templates(task_db_id, todo_db_id)

if __name__ == "__main__":
    main() 