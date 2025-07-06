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

# 노션 공식 API는 DB 뷰(View) 생성/수정 기능을 직접 제공하지 않음
# 대신, 뷰 생성은 노션 UI에서 수동으로 하거나, DB 구조/필터/정렬 정보를 안내하는 방식으로 대체

def print_view_guides():
    print("[뷰 생성 가이드]")
    print("1. TO DO DB - '오늘 할 일' 뷰: 마감일이 오늘인 항목만 필터")
    print("2. 프로젝트 DB - '진행 중 프로젝트' 뷰: 상태=진행중 필터")
    print("3. 태스크 DB - '이번 주 마감' 뷰: 마감일이 이번 주 내인 항목 필터")
    print("각 DB에서 필터/정렬을 적용해 뷰를 추가하면 됩니다.")

if __name__ == "__main__":
    print_view_guides() 