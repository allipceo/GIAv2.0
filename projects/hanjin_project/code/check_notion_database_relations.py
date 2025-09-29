#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
노션 데이터베이스 관계 및 롤업 점검 스크립트
작성일: 2025년 8월 5일
작성자: 서대리 (Lead Developer)
목적: 노션 DB 간 관계 및 롤업 기능 상태 점검
"""

import requests
import json
from datetime import datetime

# 노션 API 설정
NOTION_TOKEN = "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"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_database_info(database_id):
    """데이터베이스 정보 조회"""
    url = f"https://api.notion.com/v1/databases/{database_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 데이터베이스 정보 조회 실패: {e}")
        return None

def check_database_relations():
    """데이터베이스 관계 및 롤업 점검"""
    print("="*80)
    print("🔍 노션 데이터베이스 관계 및 롤업 점검")
    print("="*80)
    
    # 알려진 데이터베이스 ID들 (실제 ID로 교체 필요)
    databases = {
        "뉴스정보DB": "227a613d-25ff-800c-a97d-e24f6eb521a8",
        "프로젝트DB": "227a613d-25ff-800c-a97d-e24f6eb521a9", 
        "태스크DB": "227a613d-25ff-800c-a97d-e24f6eb521aa",
        "효성중공업_재무_프로젝트_DB": "227a613d-25ff-800c-a97d-e24f6eb521ab",
        "두산중공업_재무_프로젝트_DB": "227a613d-25ff-800c-a97d-e24f6eb521ac",
        "한진중공업_재무_프로젝트_DB": "227a613d-25ff-800c-a97d-e24f6eb521ad"
    }
    
    print("📊 데이터베이스 현황 점검")
    print("-" * 50)
    
    database_status = {}
    
    for db_name, db_id in databases.items():
        print(f"\n🔍 {db_name} 점검 중...")
        
        db_info = get_database_info(db_id)
        if db_info:
            properties = db_info.get("properties", {})
            
            # 관계형 속성 확인
            relation_properties = []
            rollup_properties = []
            
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "")
                
                if prop_type == "relation":
                    relation_properties.append({
                        "name": prop_name,
                        "database_id": prop_info.get("relation", {}).get("database_id", ""),
                        "type": prop_info.get("relation", {}).get("type", "")
                    })
                elif prop_type == "rollup":
                    rollup_properties.append({
                        "name": prop_name,
                        "relation_property": prop_info.get("rollup", {}).get("relation_property_name", ""),
                        "rollup_property": prop_info.get("rollup", {}).get("rollup_property_name", ""),
                        "function": prop_info.get("rollup", {}).get("function", "")
                    })
            
            database_status[db_name] = {
                "exists": True,
                "relation_count": len(relation_properties),
                "rollup_count": len(rollup_properties),
                "relation_properties": relation_properties,
                "rollup_properties": rollup_properties
            }
            
            print(f"   ✅ 데이터베이스 존재")
            print(f"   📊 관계형 속성: {len(relation_properties)}개")
            print(f"   📈 롤업 속성: {len(rollup_properties)}개")
            
            if relation_properties:
                print("   🔗 관계형 속성 목록:")
                for rel in relation_properties:
                    print(f"      - {rel['name']} → DB: {rel['database_id'][:8]}...")
            
            if rollup_properties:
                print("   📊 롤업 속성 목록:")
                for roll in rollup_properties:
                    print(f"      - {roll['name']} ({roll['function']})")
        else:
            database_status[db_name] = {
                "exists": False,
                "relation_count": 0,
                "rollup_count": 0
            }
            print(f"   ❌ 데이터베이스 없음")
    
    return database_status

def analyze_relationships(database_status):
    """관계형 연결 분석"""
    print("\n" + "="*80)
    print("🔗 관계형 연결 분석")
    print("="*80)
    
    total_relations = sum(db["relation_count"] for db in database_status.values())
    total_rollups = sum(db["rollup_count"] for db in database_status.values())
    
    print(f"📊 전체 관계형 속성: {total_relations}개")
    print(f"📈 전체 롤업 속성: {total_rollups}개")
    
    # 관계형 연결 맵 생성
    relation_map = {}
    for db_name, status in database_status.items():
        if status["exists"]:
            for rel in status["relation_properties"]:
                source_db = db_name
                target_db_id = rel["database_id"]
                
                # 대상 DB 이름 찾기
                target_db_name = "알 수 없는 DB"
                for name, info in database_status.items():
                    if info["exists"]:
                        # 실제로는 DB ID로 매칭해야 함
                        if name in target_db_id:
                            target_db_name = name
                            break
                
                relation_map[f"{source_db} → {target_db_name}"] = {
                    "relation_name": rel["name"],
                    "type": rel["type"]
                }
    
    print("\n🔗 관계형 연결 맵:")
    for connection, details in relation_map.items():
        print(f"   {connection}")
        print(f"      - 관계명: {details['relation_name']}")
        print(f"      - 유형: {details['type']}")

def check_rollup_functions(database_status):
    """롤업 기능 분석"""
    print("\n" + "="*80)
    print("📊 롤업 기능 분석")
    print("="*80)
    
    rollup_functions = {}
    for db_name, status in database_status.items():
        if status["exists"]:
            for roll in status["rollup_properties"]:
                func = roll["function"]
                if func not in rollup_functions:
                    rollup_functions[func] = []
                rollup_functions[func].append(f"{db_name}.{roll['name']}")
    
    print("📈 롤업 함수별 사용 현황:")
    for func, properties in rollup_functions.items():
        print(f"   {func}: {len(properties)}개")
        for prop in properties:
            print(f"      - {prop}")

def generate_recommendations(database_status):
    """개선 권장사항 생성"""
    print("\n" + "="*80)
    print("💡 개선 권장사항")
    print("="*80)
    
    recommendations = []
    
    # 1. 관계형 연결 부족한 DB 확인
    for db_name, status in database_status.items():
        if status["exists"] and status["relation_count"] == 0:
            recommendations.append(f"⚠️ {db_name}: 관계형 연결이 없습니다. 다른 DB와 연결을 고려하세요.")
    
    # 2. 롤업 기능 부족한 DB 확인
    for db_name, status in database_status.items():
        if status["exists"] and status["rollup_count"] == 0:
            recommendations.append(f"⚠️ {db_name}: 롤업 기능이 없습니다. 데이터 집계를 위한 롤업을 추가하세요.")
    
    # 3. 권장 관계형 연결
    if "뉴스정보DB" in database_status and "프로젝트DB" in database_status:
        recommendations.append("💡 뉴스정보DB ↔ 프로젝트DB: 뉴스와 프로젝트 간 연결로 관련성 파악")
    
    if "효성중공업_재무_프로젝트_DB" in database_status and "뉴스정보DB" in database_status:
        recommendations.append("💡 효성중공업_재무_프로젝트_DB ↔ 뉴스정보DB: 재무데이터와 뉴스 연결")
    
    # 4. 권장 롤업 기능
    recommendations.append("💡 프로젝트DB에 '관련 뉴스 개수' 롤업 추가")
    recommendations.append("💡 뉴스정보DB에 '평균 중요도' 롤업 추가")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("✅ 모든 데이터베이스가 적절한 관계형 연결과 롤업 기능을 갖추고 있습니다!")

def create_relationship_test():
    """관계형 연결 테스트 생성"""
    print("\n" + "="*80)
    print("🧪 관계형 연결 테스트")
    print("="*80)
    
    test_script = """
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
"""
    
    print("📝 테스트 스크립트 생성:")
    print(test_script)
    
    # 테스트 파일 저장
    test_file = f"../data/database_relation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"💾 테스트 파일 저장: {test_file}")

def main():
    """메인 실행 함수"""
    # 1. 데이터베이스 관계 점검
    database_status = check_database_relations()
    
    # 2. 관계형 연결 분석
    analyze_relationships(database_status)
    
    # 3. 롤업 기능 분석
    check_rollup_functions(database_status)
    
    # 4. 개선 권장사항
    generate_recommendations(database_status)
    
    # 5. 테스트 스크립트 생성
    create_relationship_test()
    
    print("\n" + "="*80)
    print("✅ 노션 데이터베이스 관계 및 롤업 점검 완료!")
    print("="*80)

if __name__ == "__main__":
    main() 