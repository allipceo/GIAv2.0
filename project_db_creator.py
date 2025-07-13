#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIA 프로젝트 DB 생성 및 관계형 연결 시스템
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 조대표님 맞춤 프로젝트 DB 생성 및 뉴스/입찰/통계 정보와의 관계형 연결
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from mvp_config import APIConfig

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectDatabaseCreator:
    """프로젝트 DB 생성 및 관계형 연결 관리자"""
    
    def __init__(self):
        self.notion_api_key = APIConfig.NOTION_API_TOKEN
        self.workspace_id = APIConfig.NOTION_DASHBOARD_PAGE_ID
        self.base_url = "https://api.notion.com/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # 기존 정보 DB ID들
        self.news_db_id = APIConfig.NOTION_NEWS_DATABASE_ID
        self.bid_db_id = APIConfig.NOTION_BID_DATABASE_ID
        self.stats_policy_db_id = self.get_stats_policy_db_id()
        
        # 생성될 프로젝트 DB ID
        self.project_db_id = None
    
    def get_stats_policy_db_id(self) -> Optional[str]:
        """통계/정책 DB ID 가져오기"""
        try:
            with open('stats_policy_db_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('stats_policy_db_id')
        except FileNotFoundError:
            logger.warning("통계/정책 DB 설정 파일이 없음")
            return None
        except Exception as e:
            logger.error(f"통계/정책 DB ID 조회 실패: {str(e)}")
            return None
    
    def create_project_database(self) -> str:
        """조대표님 맞춤 프로젝트 DB 생성"""
        logger.info("프로젝트 DB 생성 시작")
        
        try:
            # 프로젝트 DB 스키마 정의
            database_schema = {
                "parent": {
                    "type": "page_id",
                    "page_id": self.workspace_id
                },
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "프로젝트 DB"
                        }
                    }
                ],
                "properties": {
                    "프로젝트명": {
                        "title": {}
                    },
                    "사업분야": {
                        "select": {
                            "options": [
                                {"name": "신재생에너지", "color": "green"},
                                {"name": "방위산업", "color": "blue"},
                                {"name": "보험중개", "color": "orange"},
                                {"name": "종합", "color": "purple"}
                            ]
                        }
                    },
                    "프로젝트 유형": {
                        "select": {
                            "options": [
                                {"name": "신규사업", "color": "green"},
                                {"name": "기존사업 확장", "color": "blue"},
                                {"name": "파트너십", "color": "purple"},
                                {"name": "투자", "color": "yellow"},
                                {"name": "연구개발", "color": "red"}
                            ]
                        }
                    },
                    "상태": {
                        "select": {
                            "options": [
                                {"name": "기획", "color": "gray"},
                                {"name": "진행중", "color": "blue"},
                                {"name": "검토중", "color": "yellow"},
                                {"name": "완료", "color": "green"},
                                {"name": "보류", "color": "red"}
                            ]
                        }
                    },
                    "우선순위": {
                        "select": {
                            "options": [
                                {"name": "최우선", "color": "red"},
                                {"name": "높음", "color": "orange"},
                                {"name": "보통", "color": "yellow"},
                                {"name": "낮음", "color": "gray"}
                            ]
                        }
                    },
                                         "예상 수익": {
                         "number": {
                             "format": "won"
                         }
                     },
                    "시작일": {
                        "date": {}
                    },
                    "목표 완료일": {
                        "date": {}
                    },
                    "담당자": {
                        "people": {}
                    },
                    "프로젝트 설명": {
                        "rich_text": {}
                    },
                    "핵심 KPI": {
                        "rich_text": {}
                    },
                    "위험요소": {
                        "rich_text": {}
                    },
                    "관련 뉴스": {
                        "relation": {
                            "database_id": self.news_db_id,
                            "type": "dual_property",
                            "dual_property": {
                                "synced_property_name": "관련 프로젝트"
                            }
                        }
                    },
                    "관련 입찰정보": {
                        "relation": {
                            "database_id": self.bid_db_id,
                            "type": "dual_property", 
                            "dual_property": {
                                "synced_property_name": "관련 프로젝트"
                            }
                        }
                    },
                    "관련 통계정책": {
                        "relation": {
                            "database_id": self.stats_policy_db_id,
                            "type": "dual_property",
                            "dual_property": {
                                "synced_property_name": "관련 프로젝트"
                            }
                        }
                    } if self.stats_policy_db_id else {
                        "rich_text": {}
                    },
                    # 롤업 속성들
                    "중요 뉴스 수": {
                        "rollup": {
                            "relation_property_name": "관련 뉴스",
                            "rollup_property_name": "중요도",
                            "function": "count_values"
                        }
                    },
                    "최신 뉴스 날짜": {
                        "rollup": {
                            "relation_property_name": "관련 뉴스", 
                            "rollup_property_name": "날짜",
                            "function": "latest_date"
                        }
                    },
                    "관련 입찰 건수": {
                        "rollup": {
                            "relation_property_name": "관련 입찰정보",
                            "rollup_property_name": "제목",
                            "function": "count"
                        }
                    },
                    "통계정보 건수": {
                        "rollup": {
                            "relation_property_name": "관련 통계정책",
                            "rollup_property_name": "제목", 
                            "function": "count"
                        }
                    } if self.stats_policy_db_id else {
                        "formula": {
                            "expression": "0"
                        }
                    }
                }
            }
            
            # 데이터베이스 생성 요청
            response = requests.post(
                f"{self.base_url}/databases",
                headers=self.headers,
                json=database_schema
            )
            
            if response.status_code == 200:
                db_data = response.json()
                self.project_db_id = db_data['id']
                logger.info(f"프로젝트 DB 생성 완료: {self.project_db_id}")
                
                # DB ID 저장
                self.save_project_db_config()
                
                return self.project_db_id
            else:
                logger.error(f"프로젝트 DB 생성 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"프로젝트 DB 생성 중 오류 발생: {str(e)}")
            return None
    
    def save_project_db_config(self):
        """프로젝트 DB 설정 저장"""
        try:
            config = {
                "project_db_id": self.project_db_id,
                "created_at": datetime.now().isoformat(),
                "news_db_id": self.news_db_id,
                "bid_db_id": self.bid_db_id,
                "stats_policy_db_id": self.stats_policy_db_id
            }
            
            with open('project_db_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info("프로젝트 DB 설정 저장 완료")
            
        except Exception as e:
            logger.error(f"프로젝트 DB 설정 저장 실패: {str(e)}")
    
    def create_sample_projects(self) -> bool:
        """샘플 프로젝트 데이터 생성"""
        if not self.project_db_id:
            logger.error("프로젝트 DB ID가 없음")
            return False
        
        logger.info("샘플 프로젝트 생성 시작")
        
        # 조대표님 비즈니스에 맞는 샘플 프로젝트들
        sample_projects = [
            {
                "프로젝트명": "신재생에너지 시장 진출 전략",
                "사업분야": "신재생에너지",
                "프로젝트 유형": "신규사업",
                "상태": "진행중",
                "우선순위": "최우선",
                "예상 수익": 5000000000,  # 50억원
                "시작일": "2025-01-01",
                "목표 완료일": "2025-12-31",
                "프로젝트 설명": "태양광, 풍력 등 신재생에너지 분야 진출을 위한 종합 전략 수립 및 실행",
                "핵심 KPI": "시장점유율 3% 달성, 매출 50억원",
                "위험요소": "정부정책 변화, 경쟁사 선점"
            },
            {
                "프로젝트명": "방위산업 파트너십 확대",
                "사업분야": "방위산업", 
                "프로젝트 유형": "파트너십",
                "상태": "검토중",
                "우선순위": "높음",
                "예상 수익": 3000000000,  # 30억원
                "시작일": "2025-03-01",
                "목표 완료일": "2025-10-31",
                "프로젝트 설명": "국내외 방위산업 업체와의 전략적 파트너십 구축",
                "핵심 KPI": "파트너십 3건 체결, 공동수주 10억원",
                "위험요소": "정치적 이슈, 기술보안 문제"
            },
            {
                "프로젝트명": "보험중개 디지털 전환",
                "사업분야": "보험중개",
                "프로젝트 유형": "기존사업 확장", 
                "상태": "기획",
                "우선순위": "보통",
                "예상 수익": 2000000000,  # 20억원
                "시작일": "2025-06-01",
                "목표 완료일": "2025-11-30",
                "프로젝트 설명": "기존 보험중개 사업의 디지털화 및 자동화 시스템 구축",
                "핵심 KPI": "업무효율 50% 향상, 고객만족도 90%",
                "위험요소": "기술적 복잡성, 직원 적응"
            }
        ]
        
        success_count = 0
        for project in sample_projects:
            try:
                page_data = self.create_project_page_data(project)
                
                response = requests.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"샘플 프로젝트 생성 성공: {project['프로젝트명']}")
                else:
                    logger.error(f"샘플 프로젝트 생성 실패: {project['프로젝트명']} - {response.status_code}")
                    
            except Exception as e:
                logger.error(f"샘플 프로젝트 생성 중 오류: {project['프로젝트명']} - {str(e)}")
        
        logger.info(f"샘플 프로젝트 생성 완료: {success_count}건 성공")
        return success_count > 0
    
    def create_project_page_data(self, project: Dict) -> Dict:
        """프로젝트 페이지 데이터 생성"""
        page_data = {
            "parent": {
                "database_id": self.project_db_id
            },
            "properties": {
                "프로젝트명": {
                    "title": [
                        {
                            "text": {
                                "content": project.get('프로젝트명', 'Unknown')
                            }
                        }
                    ]
                },
                "사업분야": {
                    "select": {
                        "name": project.get('사업분야', '종합')
                    }
                },
                "프로젝트 유형": {
                    "select": {
                        "name": project.get('프로젝트 유형', '신규사업')
                    }
                },
                "상태": {
                    "select": {
                        "name": project.get('상태', '기획')
                    }
                },
                "우선순위": {
                    "select": {
                        "name": project.get('우선순위', '보통')
                    }
                },
                "예상 수익": {
                    "number": project.get('예상 수익', 0)
                },
                "시작일": {
                    "date": {
                        "start": project.get('시작일', datetime.now().strftime('%Y-%m-%d'))
                    }
                },
                "목표 완료일": {
                    "date": {
                        "start": project.get('목표 완료일', datetime.now().strftime('%Y-%m-%d'))
                    }
                },
                "프로젝트 설명": {
                    "rich_text": [
                        {
                            "text": {
                                "content": project.get('프로젝트 설명', '')
                            }
                        }
                    ]
                },
                "핵심 KPI": {
                    "rich_text": [
                        {
                            "text": {
                                "content": project.get('핵심 KPI', '')
                            }
                        }
                    ]
                },
                "위험요소": {
                    "rich_text": [
                        {
                            "text": {
                                "content": project.get('위험요소', '')
                            }
                        }
                    ]
                }
            }
        }
        
        return page_data
    
    def update_existing_databases_with_relations(self) -> bool:
        """기존 DB들에 프로젝트 관계 속성 추가"""
        logger.info("기존 DB들에 관계형 속성 추가 시작")
        
        success = True
        
        # 뉴스 DB에 관련 프로젝트 속성 추가
        if not self.add_relation_property_to_db(self.news_db_id, "뉴스정보DB"):
            success = False
        
        # 입찰 DB에 관련 프로젝트 속성 추가  
        if not self.add_relation_property_to_db(self.bid_db_id, "입찰낙찰공고DB"):
            success = False
        
        # 통계/정책 DB에 관련 프로젝트 속성 추가
        if self.stats_policy_db_id:
            if not self.add_relation_property_to_db(self.stats_policy_db_id, "통계/정책정보DB"):
                success = False
        
        return success
    
    def add_relation_property_to_db(self, db_id: str, db_name: str) -> bool:
        """특정 DB에 프로젝트 관계 속성 추가"""
        try:
            # 기존 DB 정보 조회
            response = requests.get(
                f"{self.base_url}/databases/{db_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"{db_name} 조회 실패: {response.status_code}")
                return False
            
            # 관련 프로젝트 속성 추가
            new_property = {
                "관련프로젝트": {
                    "relation": {
                        "database_id": self.project_db_id,
                        "type": "dual_property",
                        "dual_property": {}
                    }
                }
            }
            
            update_response = requests.patch(
                f"{self.base_url}/databases/{db_id}",
                headers=self.headers,
                json={"properties": new_property}
            )
            
            if update_response.status_code == 200:
                logger.info(f"{db_name}에 관계형 속성 추가 성공")
                return True
            else:
                logger.error(f"{db_name} 관계형 속성 추가 실패: {update_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"{db_name} 관계형 속성 추가 중 오류: {str(e)}")
            return False


def main():
    """메인 실행 함수"""
    print("🚀 GIA 프로젝트 DB 생성 및 관계형 연결 시스템 시작")
    print("=" * 60)
    
    creator = ProjectDatabaseCreator()
    
    # 1. 프로젝트 DB 생성
    print("1️⃣ 프로젝트 DB 생성 중...")
    project_db_id = creator.create_project_database()
    
    if project_db_id:
        print(f"✅ 프로젝트 DB 생성 성공: {project_db_id}")
        
        # 2. 샘플 프로젝트 생성
        print("2️⃣ 샘플 프로젝트 생성 중...")
        sample_success = creator.create_sample_projects()
        
        if sample_success:
            print("✅ 샘플 프로젝트 생성 성공")
        else:
            print("⚠️ 샘플 프로젝트 생성 실패")
        
        # 3. 기존 DB들과 관계형 연결 (선택적)
        print("3️⃣ 기존 DB들과 관계형 연결 시도...")
        relation_success = creator.update_existing_databases_with_relations()
        
        if relation_success:
            print("✅ 관계형 연결 성공")
        else:
            print("⚠️ 관계형 연결 부분 실패 (DB 권한 문제일 수 있음)")
        
        print(f"\n🎉 프로젝트 DB 시스템 구축 완료!")
        print(f"📊 프로젝트 DB URL: https://www.notion.so/{project_db_id}")
        print(f"🔗 이제 뉴스, 입찰, 통계 정보를 프로젝트와 연결할 수 있습니다.")
        
    else:
        print("❌ 프로젝트 DB 생성 실패")


if __name__ == "__main__":
    main() 