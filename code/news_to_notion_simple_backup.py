import json
import os
from notion_client import Client
from datetime import datetime
from email.utils import parsedate_to_datetime

# 환경변수에서 토큰 가져오기
NOTION_TOKEN = "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"
DATABASE_ID = "22aa613d25ff80888257c652d865f85a"

def upload_to_notion():
    # 노션 클라이언트 초기화
    notion = Client(auth=NOTION_TOKEN)
    
    # news_data.json 파일 읽기
    with open('news_data.json', 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    success_count = 0
    error_count = 0
    
    # 분야별로 5개씩만 처리
    categories = {}
    for news in news_data:
        keyword = news["keyword"]
        if keyword not in categories:
            categories[keyword] = []
        if len(categories[keyword]) < 5:
            categories[keyword].append(news)
    
    # 선별된 뉴스만 업로드
    selected_news = []
    for cat_news in categories.values():
        selected_news.extend(cat_news)
    
    print(f"📊 분야별 5개씩 총 {len(selected_news)}개 뉴스를 업로드합니다.")
    
    for news in selected_news:
        try:
            # 날짜 형식 변환 (RFC 2822 -> ISO 8601)
            if news.get("date"):
                date_obj = parsedate_to_datetime(news["date"])
                iso_date = date_obj.isoformat()
            else:
                iso_date = datetime.now().isoformat()
            
            # 노션 페이지 생성
            response = notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "제목": {
                        "title": [{"text": {"content": news["title"]}}]
                    },
                    "링크": {
                        "url": news["link"]
                    },
                    "날짜": {
                        "date": {"start": iso_date}
                    },
                    "분야": {
                        "multi_select": [{"name": news["keyword"]}]
                    },
                    "출처": {
                        "rich_text": [{"text": {"content": news.get("source", "Unknown")}}]
                    }
                }
            )
            success_count += 1
            print(f"✅ 성공: {news['title'][:50]}...")
            
        except Exception as e:
            error_count += 1
            print(f"❌ 실패: {news['title'][:50]}... - {str(e)}")
    
    print(f"\n📊 결과: 성공 {success_count}건, 실패 {error_count}건")

if __name__ == "__main__":
    upload_to_notion()