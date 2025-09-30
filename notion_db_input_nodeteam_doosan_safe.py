#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
노반장 두산중공업 데이터 안전한 Notion DB 입력 스크립트
작성일: 2025년 7월 20일
작성자: 서대리 (Lead Developer)
목적: 기존 DB 속성을 정확히 준수하여 안전하게 데이터 입력
"""

import json
import time
from notion_client import Client
from datetime import datetime

# Notion 설정
NOTION_TOKEN = ""

# 데이터베이스 ID들 (기존 효성중공업 DB 활용)
BUSINESS_PROJECT_DB_ID = "228a613d25ff8122a10bc35772c8a05c"  # 기업 재무 및 프로젝트 DB
RISK_PROFILE_DB_ID = "228a613d25ff818d9bbac1b53e19dcbd"      # 기업 위험 프로파일 DB
GLOBAL_INSURANCE_DB_ID = "22aa613d25ff80888257c652d865f85a"   # 글로벌 보험중개 시장 DB
POLICY_ANALYSIS_DB_ID = "228a613d25ff80f89903f8f92e549f44"   # 정부 정책 영향 분석 DB
KEY_PERSONNEL_DB_ID = "228a613d25ff813dbb4ef3d3d984d186"     # 기업 핵심 인물 DB

def create_notion_client():
    """Notion 클라이언트 생성"""
    try:
        notion = Client(auth=NOTION_TOKEN)
        print("✅ Notion 클라이언트 생성 성공")
        return notion
    except Exception as e:
        print(f"❌ Notion 클라이언트 생성 실패: {str(e)}")
        return None

def input_business_opportunities_safe(notion, opportunities):
    """영업 기회 데이터를 기업 재무 및 프로젝트 DB에 안전하게 입력"""
    print(f"\n📊 영업 기회 데이터 안전 입력 시작 ({len(opportunities)}개)")
    
    success_count = 0
    for i, opportunity in enumerate(opportunities, 1):
        try:
            # 기존 DB 속성에 맞게 데이터 변환
            response = notion.pages.create(
                parent={"database_id": BUSINESS_PROJECT_DB_ID},
                properties={
                    "코드명": {
                        "title": [{"text": {"content": f"두산중공업_{opportunity['opportunity_name']}"}}]
                    },
                    "단계": {
                        "select": {"name": "1단계-연결테스트"}
                    },
                    "적용브랜치": {
                        "rich_text": [{"text": {"content": "GIA-FEATURE-두산중공업"}}]
                    },
                    "작성자": {
                        "rich_text": [{"text": {"content": "노반장"}}]
                    },
                    "작성일": {
                        "date": {"start": opportunity["extraction_date"]}
                    },
                    "개선이력": {
                        "rich_text": [{"text": {"content": f"영업 기회: {opportunity['potential_scale']}"}}]
                    },
                    "파일원본코드": {
                        "rich_text": [{"text": {"content": "nodeteam_doosan_data.txt"}}]
                    },
                    "매뉴얼갱신": {
                        "checkbox": False
                    }
                }
            )
            
            print(f"✅ [{i}/{len(opportunities)}] {opportunity['opportunity_name']} 입력 성공")
            success_count += 1
            
            # API 제한 방지를 위한 대기
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ [{i}/{len(opportunities)}] {opportunity['opportunity_name']} 입력 실패: {str(e)}")
    
    print(f"📊 영업 기회 입력 완료: {success_count}/{len(opportunities)} 성공")
    return success_count

def input_ma_jv_trends_safe(notion, ma_jv_data):
    """M&A/JV 동향 데이터를 기업 위험 프로파일 DB에 안전하게 입력"""
    print(f"\n📊 M&A/JV 동향 데이터 안전 입력 시작 ({len(ma_jv_data)}개)")
    
    success_count = 0
    for i, investment in enumerate(ma_jv_data, 1):
        try:
            # 기존 DB 속성에 맞게 데이터 변환
            response = notion.pages.create(
                parent={"database_id": RISK_PROFILE_DB_ID},
                properties={
                    "프로젝트명": {
                        "title": [{"text": {"content": f"두산중공업_{investment['investment_type']}_{investment['target_company']}"}}]
                    },
                    "분야": {
                        "select": {"name": "보험"}
                    },
                    "상태": {
                        "select": {"name": "진행중"}
                    },
                    "우선순위": {
                        "select": {"name": "중간"}
                    },
                    "마감일": {
                        "date": {"start": investment["extraction_date"]}
                    }
                }
            )
            
            print(f"✅ [{i}/{len(ma_jv_data)}] {investment['target_company']} 입력 성공")
            success_count += 1
            
            # API 제한 방지를 위한 대기
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ [{i}/{len(ma_jv_data)}] {investment['target_company']} 입력 실패: {str(e)}")
    
    print(f"📊 M&A/JV 동향 입력 완료: {success_count}/{len(ma_jv_data)} 성공")
    return success_count

def input_key_personnel_safe(notion, personnel_data):
    """핵심 인물 데이터를 기업 핵심 인물 DB에 안전하게 입력"""
    print(f"\n📊 핵심 인물 데이터 안전 입력 시작 ({len(personnel_data)}개)")
    
    success_count = 0
    for i, person in enumerate(personnel_data, 1):
        try:
            # 기존 DB 속성에 맞게 데이터 변환
            response = notion.pages.create(
                parent={"database_id": KEY_PERSONNEL_DB_ID},
                properties={
                    "할일명": {
                        "title": [{"text": {"content": f"두산중공업_{person['name']}_영업접근"}}]
                    },
                    "상태": {
                        "select": {"name": "진행중"}
                    },
                    "우선순위": {
                        "select": {"name": "높음"}
                    },
                    "시작일": {
                        "date": {"start": person["extraction_date"]}
                    },
                    "마감일": {
                        "date": {"start": person["extraction_date"]}
                    },
                    "상세내용": {
                        "rich_text": [{"text": {"content": f"직책: {person['position']}, 정부영향력: {person['government_influence']}, 해외네트워크: {person['overseas_network']}"}}]
                    },
                    "필요자원": {
                        "rich_text": [{"text": {"content": "록톤 글로벌 네트워크, 원전 전문성"}}]
                    },
                    "담당": {
                        "multi_select": [{"name": "노반장"}]
                    }
                }
            )
            
            print(f"✅ [{i}/{len(personnel_data)}] {person['name']} 입력 성공")
            success_count += 1
            
            # API 제한 방지를 위한 대기
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ [{i}/{len(personnel_data)}] {person['name']} 입력 실패: {str(e)}")
    
    print(f"📊 핵심 인물 입력 완료: {success_count}/{len(personnel_data)} 성공")
    return success_count

def input_policy_analysis_safe(notion, policy_data):
    """정책 분석 데이터를 정부 정책 영향 분석 DB에 안전하게 입력"""
    print(f"\n📊 정책 분석 데이터 안전 입력 시작 ({len(policy_data)}개)")
    
    success_count = 0
    for i, policy in enumerate(policy_data, 1):
        try:
            # 기존 DB 속성에 맞게 데이터 변환
            response = notion.pages.create(
                parent={"database_id": POLICY_ANALYSIS_DB_ID},
                properties={
                    "파일명": {
                        "title": [{"text": {"content": f"두산중공업_{policy['policy_area']}_분석"}}]
                    },
                    "프로젝트": {
                        "select": {"name": "GIA V2.0"}
                    },
                    "주요내용": {
                        "select": {"name": "마스터DB설계"}
                    },
                    "생성일": {
                        "date": {"start": policy["extraction_date"]}
                    },
                    "결과": {
                        "rich_text": [{"text": {"content": f"영향수준: {policy['impact_level']}, 비즈니스기회: {policy['business_opportunity']}"}}]
                    },
                    "품질지표": {
                        "rich_text": [{"text": {"content": f"정책동향: {policy['policy_trend']}"}}]
                    },
                    "태그": {
                        "multi_select": [{"name": "두산중공업"}, {"name": "정책분석"}]
                    },
                    "실행": {
                        "checkbox": False
                    }
                }
            )
            
            print(f"✅ [{i}/{len(policy_data)}] {policy['policy_area']} 입력 성공")
            success_count += 1
            
            # API 제한 방지를 위한 대기
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ [{i}/{len(policy_data)}] {policy['policy_area']} 입력 실패: {str(e)}")
    
    print(f"📊 정책 분석 입력 완료: {success_count}/{len(policy_data)} 성공")
    return success_count

def main():
    """메인 실행 함수"""
    print("🚀 노반장 두산중공업 데이터 안전한 Notion DB 입력 시작")
    
    # Notion 클라이언트 생성
    notion = create_notion_client()
    if not notion:
        print("🚫 입력 중단 - Notion 클라이언트 생성 실패")
        return
    
    # 처리된 데이터 파일 읽기
    try:
        # 가장 최근 처리 결과 파일 찾기
        import glob
        result_files = glob.glob("nodeteam_doosan_processing_results_*.json")
        if not result_files:
            print("❌ 처리된 데이터 파일을 찾을 수 없습니다.")
            print("📝 먼저 process_nodeteam_doosan_data.py를 실행해주세요.")
            return
        
        latest_file = max(result_files)
        print(f"📁 데이터 파일 로드: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
    except Exception as e:
        print(f"❌ 데이터 파일 읽기 실패: {str(e)}")
        return
    
    # 각 카테고리별 데이터 안전 입력
    total_success = 0
    total_count = 0
    
    # 1. 영업 기회 데이터 입력
    if "business_opportunities" in processed_data:
        success = input_business_opportunities_safe(notion, processed_data["business_opportunities"])
        total_success += success
        total_count += len(processed_data["business_opportunities"])
    
    # 2. M&A/JV 동향 데이터 입력
    if "ma_jv_trends" in processed_data:
        success = input_ma_jv_trends_safe(notion, processed_data["ma_jv_trends"])
        total_success += success
        total_count += len(processed_data["ma_jv_trends"])
    
    # 3. 핵심 인물 데이터 입력
    if "key_personnel" in processed_data:
        success = input_key_personnel_safe(notion, processed_data["key_personnel"])
        total_success += success
        total_count += len(processed_data["key_personnel"])
    
    # 4. 정책 분석 데이터 입력
    if "policy_analysis" in processed_data:
        success = input_policy_analysis_safe(notion, processed_data["policy_analysis"])
        total_success += success
        total_count += len(processed_data["policy_analysis"])
    
    # 최종 결과 출력
    print(f"\n🎉 노반장 두산중공업 데이터 안전한 Notion DB 입력 완료!")
    print(f"📊 최종 결과:")
    print(f"   - 총 입력 시도: {total_count}개")
    print(f"   - 성공: {total_success}개")
    print(f"   - 실패: {total_count - total_success}개")
    print(f"   - 성공률: {(total_success/total_count)*100:.1f}%")
    
    # 입력 결과 저장
    input_result = {
        "input_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source": "노반장 두산중공업 조사",
        "input_method": "안전한 기존 DB 활용",
        "total_attempted": total_count,
        "total_successful": total_success,
        "success_rate": f"{(total_success/total_count)*100:.1f}%",
        "input_status": "완료"
    }
    
    result_filename = f"nodeteam_doosan_safe_input_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(input_result, f, ensure_ascii=False, indent=2)
    
    print(f"📋 안전 입력 결과 저장: {result_filename}")

if __name__ == "__main__":
    main() 