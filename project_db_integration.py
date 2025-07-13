#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 프로젝트 DB와 GIA 시스템 연동 스크립트
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 조대표님의 기존 프로젝트 DB에 GIA 시스템의 정보 DB와 관계형 연결 및 롤업 기능 구현
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
        logging.FileHandler('logs/project_db_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ProjectDBIntegration:
    """프로젝트 DB와 GIA 시스템 연동 클래스"""
    
    def __init__(self):
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        
        # DB ID 설정
        self.project_db_id = APIConfig.NOTION_PROJECT_DATABASE_ID
        self.news_db_id = APIConfig.NOTION_NEWS_DATABASE_ID
        self.bid_db_id = APIConfig.NOTION_BID_DATABASE_ID
        
        # 기존 프로젝트 DB 구조 정보
        self.project_fields = {
            "분야": ["보험", "보험중개", "방산", "신재생", "연구", "정책"],
            "상태": ["검토중", "개시", "진행중", "완료", "폐기"],
            "우선순위": ["높음", "중간", "낮음"]
        }
        
        # 분야 매핑 (프로젝트 DB 분야 → GIA 시스템 분야)
        self.field_mapping = {
            "방산": "방위산업",
            "신재생": "신재생에너지",
            "보험": "보험중개",
            "보험중개": "보험중개"
        }
    
    def add_relation_properties(self) -> bool:
        """프로젝트 DB에 관계형 속성 추가"""
        try:
            logging.info("🔗 프로젝트 DB에 관계형 속성 추가 시작")
            
            # 관련 뉴스 관계형 속성 추가
            news_relation_property = {
                "관련 뉴스": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.news_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 프로젝트",
                            "synced_property_id": "project_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=news_relation_property
            )
            
            if response:
                logging.info("✅ '관련 뉴스' 관계형 속성 추가 성공")
            
            # 관련 입찰정보 관계형 속성 추가
            bid_relation_property = {
                "관련 입찰정보": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.bid_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 프로젝트",
                            "synced_property_id": "project_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=bid_relation_property
            )
            
            if response:
                logging.info("✅ '관련 입찰정보' 관계형 속성 추가 성공")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ 관계형 속성 추가 실패: {str(e)}")
            return False
    
    def add_rollup_properties(self) -> bool:
        """프로젝트 DB에 롤업 속성 추가"""
        try:
            logging.info("📊 프로젝트 DB에 롤업 속성 추가 시작")
            
            # 중요 뉴스 개수 롤업
            news_count_rollup = {
                "중요 뉴스 수": {
                    "type": "rollup",
                    "rollup": {
                        "relation_property_name": "관련 뉴스",
                        "rollup_property_name": "중요도",
                        "function": "count_values",
                        "filter": {
                            "property": "중요도",
                            "select": {
                                "equals": "중요"
                            }
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=news_count_rollup
            )
            
            if response:
                logging.info("✅ '중요 뉴스 수' 롤업 속성 추가 성공")
            
            # 최신 입찰정보 날짜 롤업
            bid_latest_rollup = {
                "최신 입찰정보": {
                    "type": "rollup",
                    "rollup": {
                        "relation_property_name": "관련 입찰정보",
                        "rollup_property_name": "날짜",
                        "function": "latest_date"
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=bid_latest_rollup
            )
            
            if response:
                logging.info("✅ '최신 입찰정보' 롤업 속성 추가 성공")
            
            # 입찰정보 총 개수 롤업
            bid_count_rollup = {
                "입찰정보 총 개수": {
                    "type": "rollup",
                    "rollup": {
                        "relation_property_name": "관련 입찰정보",
                        "rollup_property_name": "제목",
                        "function": "count_values"
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.project_db_id,
                properties=bid_count_rollup
            )
            
            if response:
                logging.info("✅ '입찰정보 총 개수' 롤업 속성 추가 성공")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ 롤업 속성 추가 실패: {str(e)}")
            return False
    
    def add_reverse_relation_to_gia_dbs(self) -> bool:
        """GIA 시스템 DB들에 역방향 관계형 속성 추가"""
        try:
            logging.info("🔄 GIA 시스템 DB들에 역방향 관계형 속성 추가 시작")
            
            # 뉴스 정보 DB에 '관련 프로젝트' 속성 추가
            news_relation_property = {
                "관련 프로젝트": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.project_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 뉴스",
                            "synced_property_id": "news_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.news_db_id,
                properties=news_relation_property
            )
            
            if response:
                logging.info("✅ 뉴스 정보 DB에 '관련 프로젝트' 속성 추가 성공")
            
            # 입찰낙찰 공고 DB에 '관련 프로젝트' 속성 추가
            bid_relation_property = {
                "관련 프로젝트": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.project_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 입찰정보",
                            "synced_property_id": "bid_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.bid_db_id,
                properties=bid_relation_property
            )
            
            if response:
                logging.info("✅ 입찰낙찰 공고 DB에 '관련 프로젝트' 속성 추가 성공")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ 역방향 관계형 속성 추가 실패: {str(e)}")
            return False
    
    def auto_link_relevant_items(self) -> Dict:
        """관련 항목들 자동 연결"""
        try:
            logging.info("🤖 관련 항목들 자동 연결 시작")
            
            # 프로젝트 목록 가져오기
            projects = self.get_projects()
            
            stats = {
                "total_projects": len(projects),
                "linked_news": 0,
                "linked_bids": 0,
                "processing_errors": 0
            }
            
            for project in projects:
                try:
                    project_id = project["id"]
                    project_name = project["name"]
                    project_field = project["field"]
                    
                    logging.info(f"🔍 프로젝트 '{project_name}' 관련 항목 검색 중...")
                    
                    # 분야 매핑
                    gia_field = self.field_mapping.get(project_field)
                    if not gia_field:
                        logging.warning(f"⚠️  프로젝트 '{project_name}' 분야 '{project_field}' 매핑되지 않음")
                        continue
                    
                    # 관련 뉴스 찾기 및 연결
                    related_news = self.find_related_news(gia_field, project_name)
                    if related_news:
                        self.link_news_to_project(project_id, related_news)
                        stats["linked_news"] += len(related_news)
                        logging.info(f"✅ 프로젝트 '{project_name}'에 {len(related_news)}개 뉴스 연결")
                    
                    # 관련 입찰정보 찾기 및 연결
                    related_bids = self.find_related_bids(gia_field, project_name)
                    if related_bids:
                        self.link_bids_to_project(project_id, related_bids)
                        stats["linked_bids"] += len(related_bids)
                        logging.info(f"✅ 프로젝트 '{project_name}'에 {len(related_bids)}개 입찰정보 연결")
                    
                except Exception as e:
                    logging.error(f"❌ 프로젝트 '{project_name}' 연결 중 오류: {str(e)}")
                    stats["processing_errors"] += 1
            
            logging.info(f"🎯 자동 연결 완료: 뉴스 {stats['linked_news']}건, 입찰정보 {stats['linked_bids']}건")
            return stats
            
        except Exception as e:
            logging.error(f"❌ 자동 연결 실패: {str(e)}")
            return {"error": str(e)}
    
    def get_projects(self) -> List[Dict]:
        """프로젝트 목록 가져오기"""
        try:
            response = self.notion.databases.query(
                database_id=self.project_db_id,
                filter={
                    "property": "상태",
                    "select": {
                        "does_not_equal": "폐기"
                    }
                }
            )
            
            projects = []
            for page in response.get("results", []):
                project = {
                    "id": page["id"],
                    "name": self.get_title_from_page(page),
                    "field": self.get_select_from_page(page, "분야"),
                    "status": self.get_select_from_page(page, "상태"),
                    "priority": self.get_select_from_page(page, "우선순위")
                }
                projects.append(project)
            
            return projects
            
        except Exception as e:
            logging.error(f"❌ 프로젝트 목록 가져오기 실패: {str(e)}")
            return []
    
    def find_related_news(self, field: str, project_name: str) -> List[str]:
        """관련 뉴스 찾기"""
        try:
            # 분야로 필터링
            response = self.notion.databases.query(
                database_id=self.news_db_id,
                filter={
                    "property": "분야",
                    "multi_select": {
                        "contains": field
                    }
                }
            )
            
            related_news = []
            for page in response.get("results", []):
                news_title = self.get_title_from_page(page)
                
                # 프로젝트명과 관련성 체크 (간단한 키워드 매칭)
                if self.is_relevant_to_project(news_title, project_name, field):
                    related_news.append(page["id"])
            
            return related_news[:5]  # 최대 5개까지
            
        except Exception as e:
            logging.error(f"❌ 관련 뉴스 찾기 실패: {str(e)}")
            return []
    
    def find_related_bids(self, field: str, project_name: str) -> List[str]:
        """관련 입찰정보 찾기"""
        try:
            # 분야로 필터링
            response = self.notion.databases.query(
                database_id=self.bid_db_id,
                filter={
                    "property": "분야",
                    "multi_select": {
                        "contains": field
                    }
                }
            )
            
            related_bids = []
            for page in response.get("results", []):
                bid_title = self.get_title_from_page(page)
                
                # 프로젝트명과 관련성 체크
                if self.is_relevant_to_project(bid_title, project_name, field):
                    related_bids.append(page["id"])
            
            return related_bids[:3]  # 최대 3개까지
            
        except Exception as e:
            logging.error(f"❌ 관련 입찰정보 찾기 실패: {str(e)}")
            return []
    
    def is_relevant_to_project(self, content: str, project_name: str, field: str) -> bool:
        """프로젝트와의 관련성 판단"""
        content_lower = content.lower()
        project_lower = project_name.lower()
        
        # 프로젝트명이 포함되어 있으면 관련 있음
        if project_lower in content_lower:
            return True
        
        # 분야별 키워드 매칭
        field_keywords = {
            "방위산업": ["방위", "국방", "군사", "방산", "무기"],
            "신재생에너지": ["태양광", "풍력", "에너지", "전력", "발전"],
            "보험중개": ["보험", "중개", "손해", "생명보험"]
        }
        
        keywords = field_keywords.get(field, [])
        for keyword in keywords:
            if keyword in content_lower:
                return True
        
        return False
    
    def link_news_to_project(self, project_id: str, news_ids: List[str]):
        """뉴스를 프로젝트에 연결"""
        try:
            # 프로젝트 페이지 업데이트
            self.notion.pages.update(
                page_id=project_id,
                properties={
                    "관련 뉴스": {
                        "relation": [{"id": news_id} for news_id in news_ids]
                    }
                }
            )
            
        except Exception as e:
            logging.error(f"❌ 뉴스 연결 실패: {str(e)}")
    
    def link_bids_to_project(self, project_id: str, bid_ids: List[str]):
        """입찰정보를 프로젝트에 연결"""
        try:
            # 프로젝트 페이지 업데이트
            self.notion.pages.update(
                page_id=project_id,
                properties={
                    "관련 입찰정보": {
                        "relation": [{"id": bid_id} for bid_id in bid_ids]
                    }
                }
            )
            
        except Exception as e:
            logging.error(f"❌ 입찰정보 연결 실패: {str(e)}")
    
    def get_title_from_page(self, page: Dict) -> str:
        """페이지에서 제목 추출"""
        try:
            title_property = page.get("properties", {}).get("제목") or page.get("properties", {}).get("프로젝트명")
            if title_property and title_property.get("title"):
                return title_property["title"][0].get("plain_text", "")
            return ""
        except:
            return ""
    
    def get_select_from_page(self, page: Dict, property_name: str) -> str:
        """페이지에서 선택 속성 값 추출"""
        try:
            select_property = page.get("properties", {}).get(property_name, {})
            if select_property.get("select"):
                return select_property["select"].get("name", "")
            return ""
        except:
            return ""
    
    def run_full_integration(self) -> Dict:
        """전체 연동 프로세스 실행"""
        logging.info("🚀 프로젝트 DB 연동 프로세스 시작")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "final_stats": {},
            "success": False
        }
        
        try:
            # 1단계: 관계형 속성 추가
            logging.info("1️⃣ 관계형 속성 추가")
            relation_success = self.add_relation_properties()
            results["steps"]["relations"] = relation_success
            
            # 2단계: 역방향 관계 추가
            logging.info("2️⃣ 역방향 관계 추가")
            reverse_success = self.add_reverse_relation_to_gia_dbs()
            results["steps"]["reverse_relations"] = reverse_success
            
            # 3단계: 롤업 속성 추가
            logging.info("3️⃣ 롤업 속성 추가")
            rollup_success = self.add_rollup_properties()
            results["steps"]["rollups"] = rollup_success
            
            # 4단계: 자동 연결
            logging.info("4️⃣ 자동 연결")
            auto_link_stats = self.auto_link_relevant_items()
            results["steps"]["auto_linking"] = auto_link_stats
            
            # 최종 결과
            results["final_stats"] = auto_link_stats
            results["success"] = True
            results["end_time"] = datetime.now().isoformat()
            
            logging.info("🎉 프로젝트 DB 연동 프로세스 완료!")
            
            return results
            
        except Exception as e:
            logging.error(f"❌ 연동 프로세스 실패: {str(e)}")
            results["error"] = str(e)
            results["success"] = False
            return results

def main():
    """메인 실행 함수"""
    integrator = ProjectDBIntegration()
    
    # 전체 연동 프로세스 실행
    results = integrator.run_full_integration()
    
    # 결과 저장
    with open('project_db_integration_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    if results["success"]:
        print("\n🎉 프로젝트 DB 연동 성공!")
        print(f"📊 연결된 뉴스: {results['final_stats'].get('linked_news', 0)}건")
        print(f"📋 연결된 입찰정보: {results['final_stats'].get('linked_bids', 0)}건")
        print("📄 결과 저장: project_db_integration_results.json")
    else:
        print("\n❌ 프로젝트 DB 연동 실패!")
        print(f"오류: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 