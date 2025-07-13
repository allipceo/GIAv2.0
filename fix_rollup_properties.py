#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
롤업 속성 추가 문제 해결 스크립트
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 노션 API 스키마 문제를 해결하여 롤업 기능 완성
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from notion_client import Client
from mvp_config import APIConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rollup_fix.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class RollupPropertiesFixer:
    """롤업 속성 추가 문제 해결 클래스"""
    
    def __init__(self):
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        self.project_db_id = APIConfig.NOTION_PROJECT_DATABASE_ID
        self.news_db_id = APIConfig.NOTION_NEWS_DATABASE_ID
        self.bid_db_id = APIConfig.NOTION_BID_DATABASE_ID
    
    def get_database_properties(self, db_id: str) -> Dict:
        """데이터베이스 속성 정보 가져오기"""
        try:
            db_info = self.notion.databases.retrieve(database_id=db_id)
            return db_info.get('properties', {})
        except Exception as e:
            logging.error(f"❌ DB 속성 정보 가져오기 실패: {str(e)}")
            return {}
    
    def find_relation_property_id(self, properties: Dict, relation_name: str) -> Optional[str]:
        """관계형 속성 ID 찾기"""
        for prop_name, prop_info in properties.items():
            if prop_name == relation_name and prop_info.get('type') == 'relation':
                return prop_info.get('id')
        return None
    
    def find_target_property_id(self, db_id: str, property_name: str) -> Optional[str]:
        """타겟 DB의 속성 ID 찾기"""
        try:
            properties = self.get_database_properties(db_id)
            for prop_name, prop_info in properties.items():
                if prop_name == property_name:
                    return prop_info.get('id')
            return None
        except Exception as e:
            logging.error(f"❌ 타겟 속성 ID 찾기 실패: {str(e)}")
            return None
    
    def add_news_count_rollup(self) -> bool:
        """뉴스 개수 롤업 속성 추가"""
        try:
            logging.info("📊 뉴스 개수 롤업 속성 추가 시작")
            
            # 프로젝트 DB 속성 정보 가져오기
            project_properties = self.get_database_properties(self.project_db_id)
            
            # 관련 뉴스 관계형 속성 ID 찾기
            news_relation_id = self.find_relation_property_id(project_properties, "관련 뉴스")
            if not news_relation_id:
                logging.error("❌ '관련 뉴스' 관계형 속성을 찾을 수 없습니다")
                return False
            
            # 뉴스 DB의 중요도 속성 ID 찾기
            importance_property_id = self.find_target_property_id(self.news_db_id, "중요도")
            if not importance_property_id:
                logging.error("❌ 뉴스 DB의 '중요도' 속성을 찾을 수 없습니다")
                return False
            
            # 롤업 속성 추가 (필터 없이 전체 개수)
            rollup_property = {
                "뉴스 총 개수": {
                    "type": "rollup",
                    "rollup": {
                        "relation_property_id": news_relation_id,
                        "rollup_property_id": importance_property_id,
                        "function": "count_values"
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=rollup_property
            )
            
            if response:
                logging.info("✅ '뉴스 총 개수' 롤업 속성 추가 성공")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"❌ 뉴스 개수 롤업 속성 추가 실패: {str(e)}")
            return False
    
    def add_bid_count_rollup(self) -> bool:
        """입찰정보 개수 롤업 속성 추가"""
        try:
            logging.info("📊 입찰정보 개수 롤업 속성 추가 시작")
            
            # 프로젝트 DB 속성 정보 가져오기
            project_properties = self.get_database_properties(self.project_db_id)
            
            # 관련 입찰정보 관계형 속성 ID 찾기
            bid_relation_id = self.find_relation_property_id(project_properties, "관련 입찰정보")
            if not bid_relation_id:
                logging.error("❌ '관련 입찰정보' 관계형 속성을 찾을 수 없습니다")
                return False
            
            # 입찰 DB의 제목 속성 ID 찾기
            title_property_id = self.find_target_property_id(self.bid_db_id, "제목")
            if not title_property_id:
                logging.error("❌ 입찰 DB의 '제목' 속성을 찾을 수 없습니다")
                return False
            
            # 롤업 속성 추가
            rollup_property = {
                "입찰정보 총 개수": {
                    "type": "rollup",
                    "rollup": {
                        "relation_property_id": bid_relation_id,
                        "rollup_property_id": title_property_id,
                        "function": "count_values"
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=rollup_property
            )
            
            if response:
                logging.info("✅ '입찰정보 총 개수' 롤업 속성 추가 성공")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"❌ 입찰정보 개수 롤업 속성 추가 실패: {str(e)}")
            return False
    
    def add_latest_news_date_rollup(self) -> bool:
        """최신 뉴스 날짜 롤업 속성 추가"""
        try:
            logging.info("📊 최신 뉴스 날짜 롤업 속성 추가 시작")
            
            # 프로젝트 DB 속성 정보 가져오기
            project_properties = self.get_database_properties(self.project_db_id)
            
            # 관련 뉴스 관계형 속성 ID 찾기
            news_relation_id = self.find_relation_property_id(project_properties, "관련 뉴스")
            if not news_relation_id:
                logging.error("❌ '관련 뉴스' 관계형 속성을 찾을 수 없습니다")
                return False
            
            # 뉴스 DB의 날짜 속성 ID 찾기
            date_property_id = self.find_target_property_id(self.news_db_id, "날짜")
            if not date_property_id:
                logging.error("❌ 뉴스 DB의 '날짜' 속성을 찾을 수 없습니다")
                return False
            
            # 롤업 속성 추가
            rollup_property = {
                "최신 뉴스 날짜": {
                    "type": "rollup",
                    "rollup": {
                        "relation_property_id": news_relation_id,
                        "rollup_property_id": date_property_id,
                        "function": "latest_date"
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=rollup_property
            )
            
            if response:
                logging.info("✅ '최신 뉴스 날짜' 롤업 속성 추가 성공")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"❌ 최신 뉴스 날짜 롤업 속성 추가 실패: {str(e)}")
            return False
    
    def run_rollup_fix(self) -> Dict:
        """롤업 속성 추가 전체 실행"""
        logging.info("🔧 롤업 속성 추가 수정 작업 시작")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "rollup_results": {},
            "success_count": 0,
            "total_count": 0
        }
        
        # 1. 뉴스 개수 롤업
        results["total_count"] += 1
        news_count_success = self.add_news_count_rollup()
        results["rollup_results"]["뉴스 총 개수"] = news_count_success
        if news_count_success:
            results["success_count"] += 1
        
        # 2. 입찰정보 개수 롤업
        results["total_count"] += 1
        bid_count_success = self.add_bid_count_rollup()
        results["rollup_results"]["입찰정보 총 개수"] = bid_count_success
        if bid_count_success:
            results["success_count"] += 1
        
        # 3. 최신 뉴스 날짜 롤업
        results["total_count"] += 1
        latest_news_success = self.add_latest_news_date_rollup()
        results["rollup_results"]["최신 뉴스 날짜"] = latest_news_success
        if latest_news_success:
            results["success_count"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        results["success_rate"] = f"{results['success_count']}/{results['total_count']}"
        
        logging.info(f"🎯 롤업 속성 추가 완료: {results['success_rate']} 성공")
        
        return results

def main():
    """메인 실행 함수"""
    fixer = RollupPropertiesFixer()
    
    # 롤업 속성 추가 실행
    results = fixer.run_rollup_fix()
    
    # 결과 저장
    with open('rollup_fix_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    if results["success_count"] == results["total_count"]:
        print(f"\n🎉 모든 롤업 속성 추가 성공! ({results['success_rate']})")
    else:
        print(f"\n⚠️  일부 롤업 속성 추가 실패 ({results['success_rate']})")
    
    print("📄 결과 저장: rollup_fix_results.json")

if __name__ == "__main__":
    main() 