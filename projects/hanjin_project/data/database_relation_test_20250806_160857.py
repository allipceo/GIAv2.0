
# 관계형 연결 테스트 스크립트 예시
def test_database_relations():
    # 1. 뉴스정보DB에서 프로젝트DB로의 관계 확인
    news_items = get_database_items("뉴스정보DB")
    for item in news_items:
        related_projects = item.get("관련_프로젝트", [])
        if related_projects:
            print(f"뉴스: {item['제목']} → 프로젝트: {len(related_projects)}개")
    
    # 2. 프로젝트DB에서 뉴스정보DB로의 롤업 확인
    projects = get_database_items("프로젝트DB")
    for project in projects:
        news_count = project.get("관련_뉴스_개수", 0)
        avg_importance = project.get("평균_중요도", 0)
        print(f"프로젝트: {project['이름']} → 뉴스: {news_count}개, 중요도: {avg_importance}")
    
    # 3. 효성중공업 재무데이터와 뉴스 연결 확인
    financial_data = get_database_items("효성중공업_재무_프로젝트_DB")
    for data in financial_data:
        related_news = data.get("관련_뉴스", [])
        if related_news:
            print(f"재무데이터: {data['항목명']} → 뉴스: {len(related_news)}개")
