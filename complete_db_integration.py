#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완전한 DB 연동 시스템 - 프로젝트 DB + TODO DB + GIA 시스템
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 조대표님의 모든 기존 DB와 GIA 시스템의 완전한 연동
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
        logging.FileHandler('logs/complete_db_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class CompleteDBIntegration:
    """완전한 DB 연동 시스템"""
    
    def __init__(self):
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        
        # DB ID 설정
        self.project_db_id = APIConfig.NOTION_PROJECT_DATABASE_ID
        self.todo_db_id = APIConfig.NOTION_TODO_DATABASE_ID
        self.news_db_id = APIConfig.NOTION_NEWS_DATABASE_ID
        self.bid_db_id = APIConfig.NOTION_BID_DATABASE_ID
        
        # 분야 매핑
        self.field_mapping = {
            "방산": "방위산업",
            "신재생": "신재생에너지",
            "보험": "보험중개",
            "보험중개": "보험중개",
            "연구": "연구개발",
            "정책": "정책동향"
        }
        
        # 담당자 매핑 (TODO DB → GIA 시스템)
        self.assignee_mapping = {
            "서대리(커서)": "서대리",
            "나실장(제미나이)": "나실장",
            "조대표(오너)": "조대표",
            "노팀장(클로드)": "노팀장"
        }
    
    def add_todo_db_relations(self) -> bool:
        """TODO DB에 GIA 시스템 관계형 속성 추가"""
        try:
            logging.info("🔗 TODO DB에 GIA 시스템 관계형 속성 추가 시작")
            
            # 관련 뉴스 관계형 속성 추가
            news_relation_property = {
                "관련 뉴스": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.news_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 TODO",
                            "synced_property_id": "todo_news_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.todo_db_id,
                properties=news_relation_property
            )
            
            if response:
                logging.info("✅ TODO DB에 '관련 뉴스' 관계형 속성 추가 성공")
            
            # 관련 입찰정보 관계형 속성 추가
            bid_relation_property = {
                "관련 입찰정보": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.bid_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 TODO",
                            "synced_property_id": "todo_bid_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.todo_db_id,
                properties=bid_relation_property
            )
            
            if response:
                logging.info("✅ TODO DB에 '관련 입찰정보' 관계형 속성 추가 성공")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ TODO DB 관계형 속성 추가 실패: {str(e)}")
            return False
    
    def add_reverse_relations_to_gia(self) -> bool:
        """GIA 시스템 DB들에 TODO 관련 역방향 관계 추가"""
        try:
            logging.info("🔄 GIA 시스템 DB들에 TODO 관련 역방향 관계 추가 시작")
            
            # 뉴스 정보 DB에 '관련 TODO' 속성 추가
            news_todo_relation = {
                "관련 TODO": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.todo_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 뉴스",
                            "synced_property_id": "news_todo_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.news_db_id,
                properties=news_todo_relation
            )
            
            if response:
                logging.info("✅ 뉴스 정보 DB에 '관련 TODO' 속성 추가 성공")
            
            # 입찰낙찰 공고 DB에 '관련 TODO' 속성 추가
            bid_todo_relation = {
                "관련 TODO": {
                    "type": "relation",
                    "relation": {
                        "database_id": self.todo_db_id,
                        "type": "dual_property",
                        "dual_property": {
                            "synced_property_name": "관련 입찰정보",
                            "synced_property_id": "bid_todo_relation"
                        }
                    }
                }
            }
            
            response = self.notion.databases.update(
                database_id=self.bid_db_id,
                properties=bid_todo_relation
            )
            
            if response:
                logging.info("✅ 입찰낙찰 공고 DB에 '관련 TODO' 속성 추가 성공")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ GIA 시스템 역방향 관계 추가 실패: {str(e)}")
            return False
    
    def auto_link_todos_to_gia(self) -> Dict:
        """TODO와 GIA 시스템 정보 자동 연결"""
        try:
            logging.info("🤖 TODO와 GIA 시스템 정보 자동 연결 시작")
            
            # TODO 목록 가져오기
            todos = self.get_active_todos()
            
            stats = {
                "total_todos": len(todos),
                "linked_news": 0,
                "linked_bids": 0,
                "processing_errors": 0
            }
            
            for todo in todos:
                try:
                    todo_id = todo["id"]
                    todo_name = todo["name"]
                    todo_assignees = todo["assignees"]
                    todo_tags = todo["tags"]
                    
                    logging.info(f"🔍 TODO '{todo_name}' 관련 정보 검색 중...")
                    
                    # 관련 뉴스 찾기 및 연결
                    related_news = self.find_related_news_for_todo(todo_name, todo_tags, todo_assignees)
                    if related_news:
                        self.link_news_to_todo(todo_id, related_news)
                        stats["linked_news"] += len(related_news)
                        logging.info(f"✅ TODO '{todo_name}'에 {len(related_news)}개 뉴스 연결")
                    
                    # 관련 입찰정보 찾기 및 연결
                    related_bids = self.find_related_bids_for_todo(todo_name, todo_tags, todo_assignees)
                    if related_bids:
                        self.link_bids_to_todo(todo_id, related_bids)
                        stats["linked_bids"] += len(related_bids)
                        logging.info(f"✅ TODO '{todo_name}'에 {len(related_bids)}개 입찰정보 연결")
                    
                except Exception as e:
                    logging.error(f"❌ TODO '{todo_name}' 연결 중 오류: {str(e)}")
                    stats["processing_errors"] += 1
            
            logging.info(f"🎯 TODO 자동 연결 완료: 뉴스 {stats['linked_news']}건, 입찰정보 {stats['linked_bids']}건")
            return stats
            
        except Exception as e:
            logging.error(f"❌ TODO 자동 연결 실패: {str(e)}")
            return {"error": str(e)}
    
    def get_active_todos(self) -> List[Dict]:
        """활성 TODO 목록 가져오기"""
        try:
            response = self.notion.databases.query(
                database_id=self.todo_db_id,
                filter={
                    "and": [
                        {
                            "property": "상태",
                            "select": {
                                "does_not_equal": "완료"
                            }
                        },
                        {
                            "property": "상태",
                            "select": {
                                "does_not_equal": "폐기"
                            }
                        }
                    ]
                }
            )
            
            todos = []
            for page in response.get("results", []):
                todo = {
                    "id": page["id"],
                    "name": self.get_title_from_page(page, "할일명"),
                    "status": self.get_select_from_page(page, "상태"),
                    "priority": self.get_select_from_page(page, "우선순위"),
                    "assignees": self.get_multi_select_from_page(page, "담당"),
                    "tags": self.get_relation_names_from_page(page, "마스터태그"),
                    "content": self.get_rich_text_from_page(page, "상세내용")
                }
                todos.append(todo)
            
            return todos
            
        except Exception as e:
            logging.error(f"❌ TODO 목록 가져오기 실패: {str(e)}")
            return []
    
    def find_related_news_for_todo(self, todo_name: str, tags: List[str], assignees: List[str]) -> List[str]:
        """TODO와 관련된 뉴스 찾기"""
        try:
            # 키워드 조합 생성
            search_keywords = [todo_name] + tags + assignees
            
            # 모든 뉴스 검색
            response = self.notion.databases.query(
                database_id=self.news_db_id,
                page_size=20
            )
            
            related_news = []
            for page in response.get("results", []):
                news_title = self.get_title_from_page(page, "제목")
                news_content = self.get_rich_text_from_page(page, "주요내용")
                
                # 키워드 매칭
                if self.is_content_relevant(news_title + " " + news_content, search_keywords):
                    related_news.append(page["id"])
            
            return related_news[:3]  # 최대 3개
            
        except Exception as e:
            logging.error(f"❌ TODO 관련 뉴스 찾기 실패: {str(e)}")
            return []
    
    def find_related_bids_for_todo(self, todo_name: str, tags: List[str], assignees: List[str]) -> List[str]:
        """TODO와 관련된 입찰정보 찾기"""
        try:
            # 키워드 조합 생성
            search_keywords = [todo_name] + tags + assignees
            
            # 모든 입찰정보 검색
            response = self.notion.databases.query(
                database_id=self.bid_db_id,
                page_size=20
            )
            
            related_bids = []
            for page in response.get("results", []):
                bid_title = self.get_title_from_page(page, "제목")
                bid_content = self.get_rich_text_from_page(page, "주요내용")
                
                # 키워드 매칭
                if self.is_content_relevant(bid_title + " " + bid_content, search_keywords):
                    related_bids.append(page["id"])
            
            return related_bids[:2]  # 최대 2개
            
        except Exception as e:
            logging.error(f"❌ TODO 관련 입찰정보 찾기 실패: {str(e)}")
            return []
    
    def is_content_relevant(self, content: str, keywords: List[str]) -> bool:
        """콘텐츠와 키워드 관련성 판단"""
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword and keyword.lower() in content_lower:
                return True
        
        # 특정 키워드들은 더 가중치를 줌
        important_keywords = ["gia", "프로젝트", "시스템", "구축", "개발", "방산", "신재생", "보험"]
        for keyword in important_keywords:
            if keyword in content_lower:
                return True
        
        return False
    
    def link_news_to_todo(self, todo_id: str, news_ids: List[str]):
        """뉴스를 TODO에 연결"""
        try:
            self.notion.pages.update(
                page_id=todo_id,
                properties={
                    "관련 뉴스": {
                        "relation": [{"id": news_id} for news_id in news_ids]
                    }
                }
            )
        except Exception as e:
            logging.error(f"❌ 뉴스 연결 실패: {str(e)}")
    
    def link_bids_to_todo(self, todo_id: str, bid_ids: List[str]):
        """입찰정보를 TODO에 연결"""
        try:
            self.notion.pages.update(
                page_id=todo_id,
                properties={
                    "관련 입찰정보": {
                        "relation": [{"id": bid_id} for bid_id in bid_ids]
                    }
                }
            )
        except Exception as e:
            logging.error(f"❌ 입찰정보 연결 실패: {str(e)}")
    
    def get_title_from_page(self, page: Dict, property_name: str) -> str:
        """페이지에서 제목 추출"""
        try:
            title_property = page.get("properties", {}).get(property_name, {})
            if title_property.get("title"):
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
    
    def get_multi_select_from_page(self, page: Dict, property_name: str) -> List[str]:
        """페이지에서 다중 선택 속성 값 추출"""
        try:
            multi_select_property = page.get("properties", {}).get(property_name, {})
            if multi_select_property.get("multi_select"):
                return [item.get("name", "") for item in multi_select_property["multi_select"]]
            return []
        except:
            return []
    
    def get_rich_text_from_page(self, page: Dict, property_name: str) -> str:
        """페이지에서 텍스트 속성 값 추출"""
        try:
            rich_text_property = page.get("properties", {}).get(property_name, {})
            if rich_text_property.get("rich_text"):
                return rich_text_property["rich_text"][0].get("plain_text", "")
            return ""
        except:
            return ""
    
    def get_relation_names_from_page(self, page: Dict, property_name: str) -> List[str]:
        """페이지에서 관계형 속성의 이름들 추출 (간단히 ID만 반환)"""
        try:
            relation_property = page.get("properties", {}).get(property_name, {})
            if relation_property.get("relation"):
                return [item.get("id", "") for item in relation_property["relation"]]
            return []
        except:
            return []
    
    def run_complete_integration(self) -> Dict:
        """완전한 DB 연동 실행"""
        logging.info("🚀 완전한 DB 연동 프로세스 시작")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "final_stats": {},
            "success": False
        }
        
        try:
            # 1단계: TODO DB 관계형 속성 추가
            logging.info("1️⃣ TODO DB 관계형 속성 추가")
            todo_relation_success = self.add_todo_db_relations()
            results["steps"]["todo_relations"] = todo_relation_success
            
            # 2단계: GIA 시스템 역방향 관계 추가
            logging.info("2️⃣ GIA 시스템 역방향 관계 추가")
            reverse_relation_success = self.add_reverse_relations_to_gia()
            results["steps"]["reverse_relations"] = reverse_relation_success
            
            # 3단계: TODO 자동 연결
            logging.info("3️⃣ TODO 자동 연결")
            auto_link_stats = self.auto_link_todos_to_gia()
            results["steps"]["auto_linking"] = auto_link_stats
            
            # 최종 결과
            results["final_stats"] = auto_link_stats
            results["success"] = True
            results["end_time"] = datetime.now().isoformat()
            
            logging.info("🎉 완전한 DB 연동 프로세스 완료!")
            
            return results
            
        except Exception as e:
            logging.error(f"❌ 완전한 DB 연동 프로세스 실패: {str(e)}")
            results["error"] = str(e)
            results["success"] = False
            return results

def main():
    """메인 실행 함수"""
    integrator = CompleteDBIntegration()
    
    # 완전한 연동 프로세스 실행
    results = integrator.run_complete_integration()
    
    # 결과 저장
    with open('complete_db_integration_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    if results["success"]:
        print("\n🎉 완전한 DB 연동 성공!")
        print(f"📊 연결된 TODO-뉴스: {results['final_stats'].get('linked_news', 0)}건")
        print(f"📋 연결된 TODO-입찰정보: {results['final_stats'].get('linked_bids', 0)}건")
        print(f"📝 처리된 총 TODO: {results['final_stats'].get('total_todos', 0)}개")
        print("📄 결과 저장: complete_db_integration_results.json")
    else:
        print("\n❌ 완전한 DB 연동 실패!")
        print(f"오류: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 