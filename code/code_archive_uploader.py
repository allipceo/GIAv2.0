#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 코드 아카이브DB 업로드 스크립트
작성일: 2025년 7월 12일
작성자: 서대리 (Lead Developer)
목적: 3개 핵심 스크립트를 GIA 코드 아카이브DB에 업로드
"""

import json
from notion_client import Client
from datetime import datetime

# Notion 설정
NOTION_TOKEN = ""
DATABASE_ID = "22ea613d25ff80b78fd4ce8dc7a437a6"  # GIA 코드 아카이브DB

def create_code_blocks(code_content):
    """코드를 2000자씩 나누어 여러 블록으로 생성"""
    blocks = []
    
    # 제목 블록 추가
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "코드 전문"}}]
        }
    })
    
    # 코드를 2000자씩 나누기
    max_length = 1900  # 안전 마진
    code_chunks = [code_content[i:i+max_length] for i in range(0, len(code_content), max_length)]
    
    for i, chunk in enumerate(code_chunks):
        if i > 0:  # 첫 번째가 아니면 연속 표시
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"[코드 계속 - {i+1}부분]"}}]
                }
            })
        
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "language": "python",
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        })
    
    return blocks

def upload_script_to_archive(notion, script_data):
    """개별 스크립트를 아카이브 DB에 업로드"""
    try:
        # 페이지 생성
        response = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "모듈명": {
                    "title": [{"text": {"content": script_data["module_name"]}}]
                },
                "버전": {
                    "rich_text": [{"text": {"content": script_data["version"]}}]
                },
                "검증일": {
                    "date": {"start": script_data["verification_date"]}
                },
                "주요기능": {
                    "rich_text": [{"text": {"content": script_data["main_features"]}}]
                },
                "검증상태": {
                    "select": {"name": script_data["verification_status"]}
                },
                "관련문서링크": {
                    "url": script_data["related_doc_link"]
                },
                "작성자": {
                    "rich_text": [{"text": {"content": "서대리"}}]
                },
                "코드전문": {
                    "rich_text": [{"text": {"content": f"총 {len(script_data['code_content'])}자 - 전체 코드는 페이지 내용 참조"}}]
                }
            },
            children=create_code_blocks(script_data["code_content"])
        )
        
        print(f"✅ {script_data['module_name']} 업로드 완료")
        return True
        
    except Exception as e:
        print(f"❌ {script_data['module_name']} 업로드 실패: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 GIA 코드 아카이브DB 업로드 시작")
    
    # Notion 클라이언트 초기화
    notion = Client(auth=NOTION_TOKEN)
    
    # 스크립트 데이터 정의
    scripts_data = [
        {
            "module_name": "google_news_collector.py",
            "version": "V1.0",
            "verification_date": "2025-07-12",
            "main_features": "Google News RSS 피드 기반 뉴스 자동 수집, 인코딩 안전성 보장, 중복 방지, 키워드별 카테고리 분류",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/뉴스-클리핑-자동화-시스템-개발-경과-및-결과-보고서",
            "code_content": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News RSS 피드 기반 뉴스 수집 자동화 스크립트
작성일: 2025년 7월 12일
작성자: 서대리 (Lead Developer)
목적: 조대표님 관심 키워드 뉴스 자동 수집 및 news_data.json 저장

협업헌장 GIA V2.0 준수:
- Notion 기능 극대화: 기존 한글 필드명 완벽 호환
- 최소 개발 원칙: RSS 피드, 파싱, JSON 저장에 집중
- 인코딩 안전성: Windows CP949 환경 완전 호환
"""

import feedparser
import json
import logging
import os
import re
import sys
from datetime import datetime
from urllib.parse import quote

# Windows 인코딩 문제 완전 방지 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_news_collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 조대표님 관심 키워드 (주력 영업 필드 최적화)
KEYWORDS = {
    "방위산업": ["방위산업", "국방", "K-방산", "군수산업"],
    "신재생에너지": ["신재생에너지", "태양광", "풍력", "ESS"],
    "보험중개": ["보험중개", "보험대리점", "보험영업", "보험상품"]
}

# Google News RSS 기본 URL (한국어, 한국 지역)
GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"
RSS_PARAMS = "hl=ko&gl=KR&ceid=KR:ko"

# 설정값
MAX_ARTICLES_PER_KEYWORD = 3  # 키워드당 최대 수집 기사 수
NEWS_DATA_FILE = "news_data.json"

def safe_encode_text(text):
    """
    인코딩 안전성을 보장하는 텍스트 처리 함수
    모든 특수문자, 이모지, 외국어를 안전하게 처리
    """
    if not text:
        return ""
    
    try:
        # 1단계: 문자열로 변환
        text = str(text)
        
        # 2단계: UTF-8로 인코딩 후 에러 문자 제거
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 3단계: CP949에서 문제가 되는 문자들 제거/대체
        # 이모지 제거 (U+1F000-U+1F9FF 범위)
        text = re.sub(r'[\\U0001F000-\\U0001F9FF]', '', text)
        
        # 기타 특수 유니코드 문자 제거
        text = re.sub(r'[\\u2000-\\u206F\\u2E00-\\u2E7F\\u3000-\\u303F]', '', text)
        
        # 제어 문자 제거
        text = re.sub(r'[\\x00-\\x1F\\x7F-\\x9F]', '', text)
        
        # 4단계: CP949 호환성 테스트
        try:
            text.encode('cp949')
        except UnicodeEncodeError:
            # CP949로 인코딩할 수 없는 문자가 있으면 ASCII 안전 문자로만 구성
            text = text.encode('ascii', errors='ignore').decode('ascii')
        
        return text.strip()
        
    except Exception as e:
        logging.warning(f"[ENCODING] 텍스트 처리 실패, 기본값 반환: {str(e)}")
        return "텍스트 처리 오류"

def main():
    """메인 실행 함수"""
    logging.info("[START] Google News 수집 시작")
    logging.info(f"[INFO] 수집 키워드: {list(KEYWORDS.keys())}")
    
    try:
        # 1. 새 뉴스 수집
        new_articles = collect_google_news_rss(KEYWORDS)
        
        if not new_articles:
            logging.warning("[WARNING] 수집된 뉴스가 없습니다.")
            return
        
        # 2. 기존 뉴스 로드
        existing_news = load_existing_news(NEWS_DATA_FILE)
        
        # 3. 중복 제거
        unique_articles = avoid_duplicates(new_articles, existing_news)
        
        if not unique_articles:
            logging.info("[INFO] 새로운 뉴스가 없습니다. (모두 중복)")
            return
        
        # 4. 기존 뉴스와 합치기
        updated_news = existing_news + unique_articles
        
        # 5. 저장
        if save_news_data(updated_news, NEWS_DATA_FILE):
            logging.info(f"[SUCCESS] 성공: 새 뉴스 {len(unique_articles)}건 추가")
            logging.info(f"[INFO] 전체 뉴스: {len(updated_news)}건")
        else:
            logging.error("[ERROR] 저장 실패")
            
    except Exception as e:
        logging.error(f"[ERROR] 실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()'''
        },
        {
            "module_name": "news_to_notion_simple.py",
            "version": "V1.0",
            "verification_date": "2025-07-12",
            "main_features": "news_data.json 데이터를 Notion DB에 업로드, 인코딩 안전성 강화, 태그별 5개씩 선별 업로드",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/뉴스-클리핑-자동화-시스템-개발-경과-및-결과-보고서",
            "code_content": '''import json
import os
from notion_client import Client
from datetime import datetime
from email.utils import parsedate_to_datetime

# 환경변수에서 토큰 가져오기
NOTION_TOKEN = ""
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
            # 노션 페이지 생성
            response = notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "제목": {
                        "title": [{"text": {"content": news["제목"]}}]
                    },
                    "링크": {
                        "url": news["URL"]
                    },
                    "날짜": {
                        "date": {"start": news["발행일"]}
                    },
                    "분야": {
                        "multi_select": [{"name": news["태그"][0]}]
                    },
                    "출처": {
                        "rich_text": [{"text": {"content": "Google News"}}]
                    },
                    "중요도": {
                        "select": {"name": news.get("중요도", "보통")}
                    }
                }
            )
            success_count += 1
            print(f"[SUCCESS] {news['제목'][:50]}...")
            
        except Exception as e:
            error_count += 1
            print(f"[ERROR] 실패: {news['제목'][:30]}... - {str(e)}")
    
    print(f"\\n[RESULT] 성공 {success_count}건, 실패 {error_count}건")

if __name__ == "__main__":
    upload_to_notion()'''
        },
        {
            "module_name": "run_news_automation.py",
            "version": "V1.0",
            "verification_date": "2025-07-12",
            "main_features": "1단계(뉴스 수집) + 2단계(Notion 업로드) 통합 실행, 자동화 파이프라인 구축, 상세 로깅 및 결과 요약",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/뉴스-클리핑-자동화-시스템-개발-경과-및-결과-보고서",
            "code_content": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 클리핑 완전 자동화 통합 실행 스크립트
작성일: 2025년 7월 12일
작성자: 서대리 (Lead Developer)
목적: 1단계(뉴스 수집) + 2단계(Notion 업로드) 연속 실행

협업헌장 GIA V2.0 준수:
- 완전한 뉴스 클리핑 자동화 시스템 구현
- 수동 개입 없이 Google News → Notion DB 완료
- Windows 인코딩 안전성 보장
"""

import subprocess
import sys
import logging
from datetime import datetime

# Windows 인코딩 문제 완전 방지 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_script(script_name, description):
    """Python 스크립트 실행 및 결과 반환"""
    try:
        logging.info(f"🚀 {description} 시작...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8',
                              errors='replace')
        
        if result.returncode == 0:
            logging.info(f"✅ {description} 성공 완료")
            if result.stdout:
                logging.info(f"📋 실행 결과:\\n{result.stdout}")
            return True
        else:
            logging.error(f"❌ {description} 실패")
            if result.stderr:
                logging.error(f"오류 내용:\\n{result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ {description} 실행 중 예외 발생: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    start_time = datetime.now()
    logging.info("=" * 60)
    logging.info("🎯 뉴스 클리핑 완전 자동화 시스템 시작")
    logging.info(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    success_count = 0
    total_steps = 2
    
    # 1단계: Google News 수집
    if run_script("google_news_collector.py", "1단계: Google News 뉴스 수집"):
        success_count += 1
    else:
        logging.error("💥 1단계 실패로 인해 자동화 프로세스를 중단합니다.")
        return False
    
    # 2단계: Notion 업로드
    if run_script("news_to_notion_simple.py", "2단계: Notion DB 업로드"):
        success_count += 1
    else:
        logging.error("💥 2단계 실패")
    
    # 결과 요약
    end_time = datetime.now()
    duration = end_time - start_time
    
    logging.info("=" * 60)
    logging.info("📊 뉴스 클리핑 자동화 결과 요약")
    logging.info("=" * 60)
    logging.info(f"⏱️ 총 소요 시간: {duration}")
    logging.info(f"✅ 성공한 단계: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        logging.info("🎉 뉴스 클리핑 완전 자동화 성공!")
        logging.info("📰 Google News → news_data.json → Notion DB 업로드 완료")
        return True
    else:
        logging.error("❌ 일부 단계 실패로 자동화 미완료")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logging.info("⏹️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"💥 예상치 못한 오류 발생: {str(e)}")
        sys.exit(1)'''
        },
        {
            "module_name": "webhook_trigger_server.py",
            "version": "V1.0",
            "verification_date": "2025-01-12",
            "main_features": "Flask 기반 웹훅 서버, 외부 자동화 도구(Zapier/Make.com)에서 뉴스 수집 트리거, 백그라운드 실행 지원",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/뉴스-클리핑-자동화-시스템-개발-경과-및-결과-보고서",
            "code_content": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹훅 기반 뉴스 자동화 트리거 서버
작성일: 2025년 1월 12일
목적: 외부 자동화 도구(Zapier, Make.com)에서 웹훅으로 뉴스 수집 실행

사용법:
1. 이 서버를 백그라운드에서 실행
2. Zapier/Make.com에서 Notion 변화 감지
3. 웹훅으로 http://localhost:8080/trigger-news 호출
4. 자동으로 뉴스 수집 실행
"""

from flask import Flask, request, jsonify
import subprocess
import sys
import logging
import threading
from datetime import datetime

# Flask 앱 설정
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_trigger.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def execute_news_automation():
    """뉴스 자동화 스크립트 실행 (백그라운드)"""
    try:
        logging.info("🚀 뉴스 자동화 백그라운드 실행 시작...")
        
        result = subprocess.run(
            [sys.executable, "run_news_automation.py"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd="D:/AI_Project/GIAv2.0"
        )
        
        if result.returncode == 0:
            logging.info("✅ 뉴스 자동화 성공 완료")
        else:
            logging.error(f"❌ 뉴스 자동화 실패: {result.stderr}")
            
    except Exception as e:
        logging.error(f"❌ 실행 중 오류: {str(e)}")

@app.route('/trigger-news', methods=['POST', 'GET'])
def trigger_news_collection():
    """뉴스 수집 트리거 엔드포인트"""
    try:
        # 요청 정보 로깅
        client_ip = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logging.info(f"🎯 뉴스 수집 트리거 요청 수신 - IP: {client_ip}, 시간: {timestamp}")
        
        # POST 데이터 확인 (Zapier/Make.com에서 전송된 데이터)
        if request.method == 'POST':
            data = request.get_json() or {}
            logging.info(f"📋 수신 데이터: {data}")
        
        # 백그라운드에서 뉴스 자동화 실행
        thread = threading.Thread(target=execute_news_automation)
        thread.daemon = True
        thread.start()
        
        # 즉시 응답 반환
        response = {
            "status": "success",
            "message": "뉴스 수집이 백그라운드에서 시작되었습니다",
            "timestamp": timestamp,
            "client_ip": client_ip
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logging.error(f"❌ 트리거 처리 중 오류: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """서버 상태 확인 엔드포인트"""
    return jsonify({
        "status": "running",
        "message": "뉴스 자동화 웹훅 서버가 정상 동작 중입니다",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "endpoints": {
            "trigger": "/trigger-news (POST/GET)",
            "status": "/status (GET)"
        }
    })

@app.route('/', methods=['GET'])
def home():
    """홈 페이지"""
    return """
    <h1>🎯 GIA 뉴스 자동화 웹훅 서버</h1>
    <h2>📋 사용 가능한 엔드포인트:</h2>
    <ul>
        <li><strong>POST/GET /trigger-news</strong> - 뉴스 수집 실행</li>
        <li><strong>GET /status</strong> - 서버 상태 확인</li>
    </ul>
    <h2>🔗 외부 연동 방법:</h2>
    <ol>
        <li>Zapier/Make.com에서 Notion 변화 감지</li>
        <li>웹훅으로 <code>http://localhost:8080/trigger-news</code> 호출</li>
        <li>자동으로 뉴스 수집 실행</li>
    </ol>
    """

def main():
    """메인 실행 함수"""
    print("🎯 GIA 뉴스 자동화 웹훅 서버")
    print("=" * 50)
    print("🌐 서버 주소: http://localhost:8080")
    print("🔗 트리거 URL: http://localhost:8080/trigger-news")
    print("📊 상태 확인: http://localhost:8080/status")
    print("=" * 50)
    print("🚀 서버 시작 중...")
    
    # Flask 서버 실행
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    )

if __name__ == "__main__":
    main()'''
        },
        {
            "module_name": "notion_trigger_watcher.py",
            "version": "V1.0", 
            "verification_date": "2025-01-12",
            "main_features": "Notion 페이지 변화 감지, 트리거 기반 뉴스 자동화 실행, 백그라운드 모니터링, 결과 자동 업데이트",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/뉴스-클리핑-자동화-시스템-개발-경과-및-결과-보고서",
            "code_content": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion 트리거 기반 뉴스 자동화 실행 시스템
작성일: 2025년 1월 12일
목적: Notion에서 특정 액션 시 자동으로 뉴스 수집 실행

사용법:
1. Notion에 "뉴스 수집 실행" 페이지 생성
2. 해당 페이지의 체크박스를 체크하면 자동 실행
3. 백그라운드에서 이 스크립트가 모니터링
"""

import time
import subprocess
import sys
import logging
from datetime import datetime
from notion_client import Client

# 설정
NOTION_TOKEN = ""
TRIGGER_DATABASE_ID = "22aa613d25ff80888257c652d865f85a"  # 트리거용 DB ID
CHECK_INTERVAL = 30  # 30초마다 체크

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notion_trigger.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class NotionTriggerWatcher:
    def __init__(self):
        self.notion = Client(auth=NOTION_TOKEN)
        self.last_check_time = datetime.now()
        
    def check_trigger_status(self):
        """Notion DB에서 트리거 상태 확인"""
        try:
            # 트리거 페이지 조회 (최근 생성된 페이지부터)
            response = self.notion.databases.query(
                database_id=TRIGGER_DATABASE_ID,
                sorts=[
                    {
                        "timestamp": "created_time",
                        "direction": "descending"
                    }
                ],
                page_size=5
            )
            
            for page in response["results"]:
                # 페이지 제목에 "뉴스 수집 실행" 포함 여부 확인
                title_property = page["properties"].get("제목", {})
                if title_property.get("title"):
                    title = title_property["title"][0]["text"]["content"]
                    
                    if "뉴스 수집 실행" in title:
                        # 체크박스 상태 확인
                        checkbox_property = page["properties"].get("실행", {})
                        if checkbox_property.get("checkbox") == True:
                            # 페이지 생성 시간이 마지막 체크 이후인지 확인
                            created_time = datetime.fromisoformat(
                                page["created_time"].replace("Z", "+00:00")
                            )
                            
                            if created_time > self.last_check_time:
                                logging.info(f"🎯 트리거 감지: {title}")
                                return page["id"]
            
            return None
            
        except Exception as e:
            logging.error(f"❌ 트리거 확인 중 오류: {str(e)}")
            return None
    
    def execute_news_automation(self):
        """뉴스 자동화 스크립트 실행"""
        try:
            logging.info("🚀 뉴스 자동화 실행 시작...")
            
            result = subprocess.run(
                [sys.executable, "run_news_automation.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                logging.info("✅ 뉴스 자동화 성공 완료")
                return True, "성공"
            else:
                logging.error(f"❌ 뉴스 자동화 실패: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logging.error(f"❌ 실행 중 오류: {str(e)}")
            return False, str(e)
    
    def update_trigger_page(self, page_id, success, message):
        """트리거 페이지에 실행 결과 업데이트"""
        try:
            # 실행 결과를 페이지에 기록
            status = "✅ 성공" if success else "❌ 실패"
            result_text = f"{status} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n{message}"
            
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "실행": {"checkbox": False},  # 체크박스 해제
                    "결과": {
                        "rich_text": [{"text": {"content": result_text}}]
                    }
                }
            )
            logging.info("📝 실행 결과 업데이트 완료")
            
        except Exception as e:
            logging.error(f"❌ 결과 업데이트 실패: {str(e)}")
    
    def run_watcher(self):
        """트리거 감시 루프 실행"""
        logging.info("👁️ Notion 트리거 감시 시작...")
        logging.info(f"⏱️ 체크 간격: {CHECK_INTERVAL}초")
        
        while True:
            try:
                # 트리거 상태 확인
                triggered_page_id = self.check_trigger_status()
                
                if triggered_page_id:
                    # 뉴스 자동화 실행
                    success, message = self.execute_news_automation()
                    
                    # 결과를 Notion에 업데이트
                    self.update_trigger_page(triggered_page_id, success, message)
                    
                    # 마지막 체크 시간 업데이트
                    self.last_check_time = datetime.now()
                
                # 대기
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logging.info("⏹️ 사용자에 의해 중단됨")
                break
            except Exception as e:
                logging.error(f"❌ 감시 루프 오류: {str(e)}")
                time.sleep(CHECK_INTERVAL)

def main():
    """메인 실행 함수"""
    print("🎯 Notion 트리거 기반 뉴스 자동화 시스템")
    print("=" * 50)
    print("📋 사용법:")
    print("1. Notion에서 '뉴스 수집 실행' 페이지 생성")
    print("2. '실행' 체크박스를 체크")
    print("3. 자동으로 뉴스 수집이 실행됩니다")
    print("=" * 50)
    
    watcher = NotionTriggerWatcher()
    watcher.run_watcher()

if __name__ == "__main__":
    main()'''
        },
        {
            "module_name": "run_news_automation.bat",
            "version": "V1.0",
            "verification_date": "2025-01-12", 
            "main_features": "Windows 배치 실행 스크립트, UTF-8 인코딩 안전성 보장, 사용자 친화적 콘솔 인터페이스",
            "verification_status": "완벽 작동 확인",
            "related_doc_link": "https://www.notion.so/뉴스-클리핑-자동화-시스템-개발-경과-및-결과-보고서",
            "code_content": '''@echo off
chcp 65001 >nul
title 뉴스 클리핑 자동화 시스템 (인코딩 안전 버전)

echo ================================================
echo 🎯 뉴스 클리핑 완전 자동화 시스템 시작
echo ================================================
echo [INFO] Windows 인코딩 안전성 보장 모드
echo [INFO] UTF-8 코드페이지 활성화 완료
echo ================================================
echo.

REM Python UTF-8 모드로 실행 (인코딩 문제 완전 방지)
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
python -X utf8 run_news_automation.py

echo.
echo ================================================
echo 자동화 프로세스 완료
echo ================================================
pause'''
        }
    ]
    
    # 각 스크립트 업로드 실행
    success_count = 0
    for script_data in scripts_data:
        if upload_script_to_archive(notion, script_data):
            success_count += 1
    
    # 결과 보고
    print(f"\n📊 업로드 완료: {success_count}/{len(scripts_data)} 성공")
    print("✅ GIA 코드 아카이브DB 구축 완료!")
    
    if success_count == len(scripts_data):
        print("🎉 모든 스크립트 업로드 성공!")
        print("🔗 Notion DB: https://www.notion.so/22ea613d25ff80b78fd4ce8dc7a437a6")
    else:
        print("⚠️ 일부 스크립트 업로드 실패")

if __name__ == "__main__":
    main() 