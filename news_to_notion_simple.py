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
    
    # news_data.json 파일 읽기 (강화된 인코딩 처리)
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        print(f"[INFO] news_data.json 파일 로드 완료: {len(news_data)}건")
    except FileNotFoundError:
        print("[ERROR] news_data.json 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"[ERROR] news_data.json 파일 형식 오류: {e}")
        return
    except UnicodeDecodeError as e:
        print(f"[ERROR] news_data.json 파일 인코딩 오류: {e}")
        print("UTF-8로 저장되었는지 확인하십시오.")
        return
    except Exception as e:
        print(f"[ERROR] 파일 읽기 중 예상치 못한 오류: {e}")
        return
    
    success_count = 0
    error_count = 0
    
    # 태그별로 5개씩만 처리
    categories = {}
    for news in news_data:
        tag = news["태그"][0] if news.get("태그") and len(news["태그"]) > 0 else "기타"
        if tag not in categories:
            categories[tag] = []
        if len(categories[tag]) < 5:
            categories[tag].append(news)
    
    # 선별된 뉴스만 업로드
    selected_news = []
    for cat_news in categories.values():
        selected_news.extend(cat_news)
    
    print(f"[INFO] 태그별 5개씩 총 {len(selected_news)}개 뉴스를 업로드합니다.")
    
    for news in selected_news:
        try:
            # 날짜 형식 변환 (YYYY-MM-DD -> ISO 8601)
            if news.get("발행일"):
                iso_date = datetime.strptime(news["발행일"], "%Y-%m-%d").isoformat()
            else:
                iso_date = datetime.now().isoformat()
            
            # 문자열 데이터 UTF-8 안전성 확보
            safe_title = str(news["제목"]).encode('utf-8').decode('utf-8')
            safe_url = str(news["URL"]).encode('utf-8').decode('utf-8')
            safe_tag = str(news["태그"][0]).encode('utf-8').decode('utf-8') if news.get("태그") and len(news["태그"]) > 0 else "기타"
            safe_importance = str(news.get("중요도", "보통")).encode('utf-8').decode('utf-8')
            
            # 노션 페이지 생성 (강화된 인코딩 처리)
            response = notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "제목": {
                        "title": [{"text": {"content": safe_title}}]
                    },
                    "링크": {
                        "url": safe_url
                    },
                    "날짜": {
                        "date": {"start": iso_date}
                    },
                    "분야": {
                        "multi_select": [{"name": safe_tag}]
                    },
                    "출처": {
                        "rich_text": [{"text": {"content": "Google News"}}]
                    },
                    "중요도": {
                        "select": {"name": safe_importance}
                    }
                }
            )
            success_count += 1
            print(f"[SUCCESS] {safe_title[:50]}...")
            
        except UnicodeEncodeError as e:
            error_count += 1
            print(f"[ERROR] 인코딩 실패: {news['제목'][:30]}... - {str(e)}")
        except UnicodeDecodeError as e:
            error_count += 1
            print(f"[ERROR] 디코딩 실패: {news['제목'][:30]}... - {str(e)}")
        except Exception as e:
            error_count += 1
            print(f"[ERROR] 실패: {news['제목'][:30]}... - {str(e)}")
    
    print(f"\n[RESULT] 성공 {success_count}건, 실패 {error_count}건")

if __name__ == "__main__":
    upload_to_notion()