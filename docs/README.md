# GIAv2.0
Goodfface Intelligent Agent Version 2.0
This is the begining

# GIAv2.0 신재생에너지 뉴스 자동 입력 기능

## 1. 개요
- 구글 뉴스 등에서 수집한 신재생에너지 뉴스 데이터를 Notion DB에 자동 입력하는 Python 스크립트
- 중복 체크, 에러/실행 로그, 환경변수(.env) 적용, DB 속성명/타입 100% 일치

## 2. 환경설정
1. `.env.example` 파일을 복사해 `.env` 파일 생성
2. Notion Integration Token, Database ID 입력

## 3. 실행법
```bash
pip install -r requirements.txt
python news_to_notion.py
```

## 4. DB 속성명/타입(100% 일치 필요)
- 제목 (title)
- URL (url)
- 발행일 (date)
- 요약 (rich_text)
- 태그 (multi_select)
- 중요도 (select)
- 요약 품질 평가 (select)

## 5. 주의사항
- Notion DB 속성명/타입이 실제 DB와 100% 일치해야 함(띄어쓰기, 대소문자, 한글/영문 등)
- .env 파일에 올바른 토큰/DB ID 입력
- Notion Integration이 DB에 읽기/쓰기 권한을 가져야 함
- 실행/에러 로그는 news_to_notion.log에 기록됨
