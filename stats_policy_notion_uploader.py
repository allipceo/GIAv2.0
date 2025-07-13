"""
통계/정책 정보 노션 업로더
- 수집된 통계/정책 정보를 노션 데이터베이스에 업로드
- 통계/정책 DB 생성 및 관리
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging
from mvp_config import APIConfig
from stats_policy_db_schema import StatsPolicyDatabaseFields, get_field_mapping

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatsPolicyNotionUploader:
    def __init__(self):
        self.notion_api_key = APIConfig.NOTION_API_TOKEN
        self.workspace_id = APIConfig.NOTION_DASHBOARD_PAGE_ID
        self.base_url = "https://api.notion.com/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # 통계/정책 DB ID (생성될 예정)
        self.stats_policy_db_id = None
        
    def create_stats_policy_database(self) -> str:
        """통계/정책 정보 데이터베이스 생성"""
        logger.info("통계/정책 정보 데이터베이스 생성 시작")
        
        try:
            # 데이터베이스 스키마 정의
            database_schema = {
                "parent": {
                    "type": "page_id",
                    "page_id": self.workspace_id
                },
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "통계/정책 정보 DB"
                        }
                    }
                ],
                "properties": {
                    "제목": {
                        "title": {}
                    },
                    "분야": {
                        "select": {
                            "options": [
                                {"name": "신재생에너지", "color": "green"},
                                {"name": "방위산업", "color": "blue"},
                                {"name": "보험업계", "color": "orange"},
                                {"name": "경제일반", "color": "gray"}
                            ]
                        }
                    },
                    "유형": {
                        "select": {
                            "options": [
                                {"name": "통계", "color": "purple"},
                                {"name": "정책", "color": "red"},
                                {"name": "지표", "color": "yellow"},
                                {"name": "보고서", "color": "pink"}
                            ]
                        }
                    },
                    "출처": {
                        "select": {
                            "options": [
                                {"name": "전력거래소", "color": "green"},
                                {"name": "금융감독원", "color": "blue"},
                                {"name": "한국에너지공단", "color": "orange"},
                                {"name": "e-나라지표", "color": "yellow"},
                                {"name": "방위사업청", "color": "red"},
                                {"name": "공공데이터포털", "color": "gray"}
                            ]
                        }
                    },
                    "지표명": {
                        "rich_text": {}
                    },
                    "수치": {
                        "rich_text": {}
                    },
                    "단위": {
                        "rich_text": {}
                    },
                    "기준기간": {
                        "rich_text": {}
                    },
                    "중요도": {
                        "select": {
                            "options": [
                                {"name": "매우중요", "color": "red"},
                                {"name": "중요", "color": "orange"},
                                {"name": "보통", "color": "gray"}
                            ]
                        }
                    },
                    "사업연관성": {
                        "select": {
                            "options": [
                                {"name": "직접연관", "color": "red"},
                                {"name": "간접연관", "color": "orange"},
                                {"name": "참고용", "color": "gray"}
                            ]
                        }
                    },
                    "트렌드": {
                        "select": {
                            "options": [
                                {"name": "상승", "color": "green"},
                                {"name": "하락", "color": "red"},
                                {"name": "보합", "color": "gray"},
                                {"name": "변동", "color": "yellow"},
                                {"name": "정상", "color": "blue"}
                            ]
                        }
                    },
                    "원본링크": {
                        "url": {}
                    },
                    "상세정보": {
                        "rich_text": {}
                    },
                    "첨부파일": {
                        "files": {}
                    },
                    "수집일시": {
                        "date": {}
                    },
                    "발표일자": {
                        "rich_text": {}
                    },
                    "다음업데이트": {
                        "rich_text": {}
                    },
                    "관련프로젝트": {
                        "rich_text": {}
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
                self.stats_policy_db_id = db_data['id']
                logger.info(f"통계/정책 정보 데이터베이스 생성 완료: {self.stats_policy_db_id}")
                return self.stats_policy_db_id
            else:
                logger.error(f"데이터베이스 생성 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"데이터베이스 생성 중 오류 발생: {str(e)}")
            return None
    
    def upload_stats_policy_data(self, data_list: List[Dict]) -> Dict:
        """통계/정책 정보 데이터 업로드"""
        logger.info(f"통계/정책 정보 데이터 업로드 시작: {len(data_list)}건")
        
        if not self.stats_policy_db_id:
            logger.error("통계/정책 데이터베이스 ID가 없습니다. 먼저 create_stats_policy_database()를 호출하세요.")
            return {"success": 0, "failed": 0, "errors": []}
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for i, item in enumerate(data_list, 1):
            try:
                logger.info(f"업로드 중: {i}/{len(data_list)} - {item.get('title', 'Unknown')}")
                
                # 중복 체크
                if self._is_duplicate(item):
                    logger.info(f"중복 데이터 스킵: {item.get('title', 'Unknown')}")
                    continue
                
                # 노션 페이지 생성
                page_data = self._create_page_data(item)
                
                response = requests.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"업로드 성공: {item.get('title', 'Unknown')}")
                else:
                    failed_count += 1
                    error_msg = f"업로드 실패: {item.get('title', 'Unknown')} - {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                
                # API 제한 대응
                time.sleep(0.3)
                
            except Exception as e:
                failed_count += 1
                error_msg = f"업로드 중 오류: {item.get('title', 'Unknown')} - {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            "success": success_count,
            "failed": failed_count,
            "errors": errors
        }
        
        logger.info(f"통계/정책 정보 업로드 완료: 성공 {success_count}건, 실패 {failed_count}건")
        return result
    
    def _create_page_data(self, item: Dict) -> Dict:
        """노션 페이지 데이터 생성"""
        
        # 수집일시 처리
        collection_date = item.get('collection_date')
        if isinstance(collection_date, datetime):
            collection_date_str = collection_date.isoformat()
        else:
            collection_date_str = datetime.now().isoformat()
        
        page_data = {
            "parent": {
                "database_id": self.stats_policy_db_id
            },
            "properties": {
                "제목": {
                    "title": [
                        {
                            "text": {
                                "content": item.get('title', 'Unknown')
                            }
                        }
                    ]
                },
                "분야": {
                    "select": {
                        "name": item.get('category', '경제일반')
                    }
                },
                "유형": {
                    "select": {
                        "name": item.get('data_type', '통계')
                    }
                },
                "출처": {
                    "select": {
                        "name": item.get('source', '기타')
                    }
                },
                "지표명": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('indicator_name', '')
                            }
                        }
                    ]
                },
                "수치": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('value', '')
                            }
                        }
                    ]
                },
                "단위": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('unit', '')
                            }
                        }
                    ]
                },
                "기준기간": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('reference_period', '')
                            }
                        }
                    ]
                },
                "중요도": {
                    "select": {
                        "name": item.get('importance_level', '보통')
                    }
                },
                "사업연관성": {
                    "select": {
                        "name": item.get('business_relevance', '참고용')
                    }
                },
                "트렌드": {
                    "select": {
                        "name": item.get('trend_analysis', '보합')
                    }
                },
                "원본링크": {
                    "url": item.get('source_url', '')
                },
                "상세정보": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('detail_info', '')
                            }
                        }
                    ]
                },
                "수집일시": {
                    "date": {
                        "start": collection_date_str
                    }
                },
                "발표일자": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('publish_date', '')
                            }
                        }
                    ]
                },
                "다음업데이트": {
                    "rich_text": [
                        {
                            "text": {
                                "content": item.get('next_update', '')
                            }
                        }
                    ]
                }
            }
        }
        
        return page_data
    
    def _is_duplicate(self, item: Dict) -> bool:
        """중복 데이터 체크"""
        try:
            # 제목과 출처로 중복 체크
            query = {
                "filter": {
                    "and": [
                        {
                            "property": "제목",
                            "title": {
                                "equals": item.get('title', '')
                            }
                        },
                        {
                            "property": "출처",
                            "select": {
                                "equals": item.get('source', '')
                            }
                        }
                    ]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/databases/{self.stats_policy_db_id}/query",
                headers=self.headers,
                json=query
            )
            
            if response.status_code == 200:
                results = response.json()
                return len(results.get('results', [])) > 0
            else:
                logger.warning(f"중복 체크 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"중복 체크 중 오류: {str(e)}")
            return False
    
    def get_stats_policy_db_id(self) -> Optional[str]:
        """통계/정책 DB ID 조회"""
        return self.stats_policy_db_id
    
    def set_stats_policy_db_id(self, db_id: str):
        """통계/정책 DB ID 설정"""
        self.stats_policy_db_id = db_id
        logger.info(f"통계/정책 DB ID 설정 완료: {db_id}")

def main():
    """메인 실행 함수"""
    print("=== 통계/정책 정보 노션 업로더 ===")
    
    uploader = StatsPolicyNotionUploader()
    
    # 테스트 데이터 생성
    test_data = [
        {
            "title": "계통한계가격(SMP) - 2025-01-13",
            "category": "신재생에너지",
            "data_type": "통계",
            "source": "전력거래소",
            "indicator_name": "계통한계가격",
            "value": "116.82",
            "unit": "원/kWh",
            "reference_period": "2025-01-13",
            "importance_level": "중요",
            "business_relevance": "직접연관",
            "trend_analysis": "상승",
            "source_url": "https://new.kpx.or.kr",
            "detail_info": "전력 도매시장에서 형성되는 시간대별 전력가격으로, 신재생에너지 사업의 수익성에 직접적 영향",
            "attached_files": None,
            "collection_date": datetime.now(),
            "publish_date": "2025-01-13",
            "next_update": "2025-01-14",
            "related_projects": None
        }
    ]
    
    # 데이터베이스 생성
    db_id = uploader.create_stats_policy_database()
    if db_id:
        print(f"데이터베이스 생성 완료: {db_id}")
        
        # 테스트 데이터 업로드
        result = uploader.upload_stats_policy_data(test_data)
        print(f"업로드 결과: {result}")
    else:
        print("데이터베이스 생성 실패")

if __name__ == "__main__":
    main() 