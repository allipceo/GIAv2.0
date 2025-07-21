#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 대시보드 뷰 생성 스크립트
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 일반화된 DB에 두산중공업 데이터를 효과적으로 시각화할 수 있는 대시보드 뷰 생성
"""

import os
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('config.env')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')

# 일반화된 DB ID들
DB_IDS = {
    '📊 기업 위험 프로파일 DB': os.getenv('RISK_PROFILE_DB_ID'),
    '💰 기업 재무 및 프로젝트 DB': os.getenv('FINANCE_PROJECT_DB_ID'),
    '🔋 신재생에너지 프로젝트 DB': os.getenv('RENEWABLE_ENERGY_DB_ID'),
    '👥 기업 핵심 인물 DB': os.getenv('KEY_PERSONNEL_DB_ID'),
    '🏛️ 정부 정책 영향 분석 DB': os.getenv('POLICY_ANALYSIS_DB_ID'),
    '🌍 글로벌 보험중개 시장 DB': os.getenv('INSURANCE_MARKET_DB_ID')
}

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

class DoosanDashboardViewsCreator:
    """두산중공업 대시보드 뷰 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.created_views = {}
        self.error_log = []
    
    def create_risk_profile_views(self, db_id: str) -> Dict:
        """기업 위험 프로파일 DB 뷰 생성"""
        print("📊 기업 위험 프로파일 DB 뷰 생성...")
        
        views = {
            "전체 리스크": {
                "name": "전체 리스크",
                "type": "table",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                }
            },
            "높은 리스크": {
                "name": "높은 리스크",
                "type": "table",
                "query": {
                    "filter": {
                        "and": [
                            {
                                "property": "회사명",
                                "relation": {
                                    "contains": "두산중공업"
                                }
                            },
                            {
                                "property": "리스크 등급",
                                "select": {
                                    "equals": "높음"
                                }
                            }
                        ]
                    }
                }
            },
            "리스크 유형별": {
                "name": "리스크 유형별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "리스크 유형"
                }
            },
            "대응 현황별": {
                "name": "대응 현황별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "대응 현황"
                }
            }
        }
        
        return self._create_views_for_db(db_id, views, "기업 위험 프로파일")
    
    def create_financial_project_views(self, db_id: str) -> Dict:
        """기업 재무 및 프로젝트 DB 뷰 생성"""
        print("💰 기업 재무 및 프로젝트 DB 뷰 생성...")
        
        views = {
            "전체 재무 데이터": {
                "name": "전체 재무 데이터",
                "type": "table",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                }
            },
            "재무 데이터": {
                "name": "재무 데이터",
                "type": "table",
                "query": {
                    "filter": {
                        "and": [
                            {
                                "property": "회사명",
                                "relation": {
                                    "contains": "두산중공업"
                                }
                            },
                            {
                                "property": "데이터 유형",
                                "select": {
                                    "equals": "재무"
                                }
                            }
                        ]
                    }
                }
            },
            "프로젝트 데이터": {
                "name": "프로젝트 데이터",
                "type": "table",
                "query": {
                    "filter": {
                        "and": [
                            {
                                "property": "회사명",
                                "relation": {
                                    "contains": "두산중공업"
                                }
                            },
                            {
                                "property": "데이터 유형",
                                "select": {
                                    "equals": "프로젝트"
                                }
                            }
                        ]
                    }
                }
            },
            "중요도별": {
                "name": "중요도별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "중요도"
                }
            }
        }
        
        return self._create_views_for_db(db_id, views, "기업 재무 및 프로젝트")
    
    def create_renewable_energy_views(self, db_id: str) -> Dict:
        """신재생에너지 프로젝트 DB 뷰 생성"""
        print("🔋 신재생에너지 프로젝트 DB 뷰 생성...")
        
        views = {
            "전체 프로젝트": {
                "name": "전체 프로젝트",
                "type": "table",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                }
            },
            "진행 상태별": {
                "name": "진행 상태별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "진행 상태"
                }
            },
            "프로젝트 유형별": {
                "name": "프로젝트 유형별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "프로젝트 유형"
                }
            },
            "지역별": {
                "name": "지역별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "지역"
                }
            }
        }
        
        return self._create_views_for_db(db_id, views, "신재생에너지 프로젝트")
    
    def create_key_personnel_views(self, db_id: str) -> Dict:
        """기업 핵심 인물 DB 뷰 생성"""
        print("👥 기업 핵심 인물 DB 뷰 생성...")
        
        views = {
            "전체 인물": {
                "name": "전체 인물",
                "type": "table",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                }
            },
            "직책별": {
                "name": "직책별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "직책"
                }
            },
            "소속 부문별": {
                "name": "소속 부문별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "소속 부문"
                }
            },
            "중요도별": {
                "name": "중요도별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "중요도"
                }
            }
        }
        
        return self._create_views_for_db(db_id, views, "기업 핵심 인물")
    
    def create_government_policy_views(self, db_id: str) -> Dict:
        """정부 정책 영향 분석 DB 뷰 생성"""
        print("🏛️ 정부 정책 영향 분석 DB 뷰 생성...")
        
        views = {
            "전체 정책": {
                "name": "전체 정책",
                "type": "table",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                }
            },
            "정책 분야별": {
                "name": "정책 분야별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "정책 분야"
                }
            },
            "영향도별": {
                "name": "영향도별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "두산중공업 영향"
                }
            },
            "우선순위별": {
                "name": "우선순위별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "정책 우선순위"
                }
            }
        }
        
        return self._create_views_for_db(db_id, views, "정부 정책 영향 분석")
    
    def create_insurance_market_views(self, db_id: str) -> Dict:
        """글로벌 보험중개 시장 DB 뷰 생성"""
        print("🌍 글로벌 보험중개 시장 DB 뷰 생성...")
        
        views = {
            "전체 회사": {
                "name": "전체 회사",
                "type": "table",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                }
            },
            "회사 유형별": {
                "name": "회사 유형별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "회사 유형"
                }
            },
            "본사 위치별": {
                "name": "본사 위치별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "본사 위치"
                }
            },
            "경쟁력별": {
                "name": "경쟁력별",
                "type": "board",
                "query": {
                    "filter": {
                        "property": "회사명",
                        "relation": {
                            "contains": "두산중공업"
                        }
                    }
                },
                "board": {
                    "property": "두산중공업 경쟁력"
                }
            }
        }
        
        return self._create_views_for_db(db_id, views, "글로벌 보험중개 시장")
    
    def _create_views_for_db(self, db_id: str, views: Dict, db_name: str) -> Dict:
        """DB별 뷰 생성"""
        results = {
            "db_name": db_name,
            "total_views": len(views),
            "success_count": 0,
            "error_count": 0,
            "created_views": [],
            "errors": []
        }
        
        for view_name, view_config in views.items():
            try:
                # 뷰 생성 요청
                url = f"https://api.notion.com/v1/databases/{db_id}/views"
                
                payload = {
                    "name": view_config["name"],
                    "type": view_config["type"]
                }
                
                # 쿼리 설정
                if "query" in view_config:
                    payload["query"] = view_config["query"]
                
                # 보드 설정
                if "board" in view_config:
                    payload["board"] = view_config["board"]
                
                response = requests.post(url, headers=HEADERS, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    view_id = result["id"]
                    results["success_count"] += 1
                    results["created_views"].append({
                        "name": view_name,
                        "id": view_id
                    })
                    print(f"✅ {view_name} 뷰 생성 완료")
                else:
                    results["error_count"] += 1
                    error_msg = f"{view_name} 뷰 생성 실패: {response.status_code}"
                    results["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
                
                time.sleep(1)  # API 호출 간격
                
            except Exception as e:
                results["error_count"] += 1
                error_msg = f"{view_name} 뷰 생성 오류: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        
        return results
    
    def create_all_dashboard_views(self) -> Dict:
        """모든 DB의 대시보드 뷰 생성"""
        print("🎯 두산중공업 대시보드 뷰 생성 시작")
        print("=" * 50)
        
        all_results = {}
        
        # 각 DB별 뷰 생성
        view_creators = [
            (DB_IDS['📊 기업 위험 프로파일 DB'], self.create_risk_profile_views, "기업 위험 프로파일"),
            (DB_IDS['💰 기업 재무 및 프로젝트 DB'], self.create_financial_project_views, "기업 재무 및 프로젝트"),
            (DB_IDS['🔋 신재생에너지 프로젝트 DB'], self.create_renewable_energy_views, "신재생에너지 프로젝트"),
            (DB_IDS['👥 기업 핵심 인물 DB'], self.create_key_personnel_views, "기업 핵심 인물"),
            (DB_IDS['🏛️ 정부 정책 영향 분석 DB'], self.create_government_policy_views, "정부 정책 영향 분석"),
            (DB_IDS['🌍 글로벌 보험중개 시장 DB'], self.create_insurance_market_views, "글로벌 보험중개 시장")
        ]
        
        for db_id, creator_func, db_name in view_creators:
            if db_id:
                result = creator_func(db_id)
                all_results[db_name] = result
            else:
                print(f"❌ {db_name} DB ID를 찾을 수 없습니다.")
        
        return all_results
    
    def generate_views_report(self, results: Dict) -> str:
        """뷰 생성 결과 보고서 생성"""
        report = f"""
# 두산중공업 대시보드 뷰 생성 결과 보고서
생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

## 📊 전체 생성 결과
"""
        
        total_views = 0
        total_success = 0
        total_errors = 0
        
        for db_name, result in results.items():
            report += f"""
### {db_name}
- 총 뷰: {result['total_views']}
- 성공: {result['success_count']}
- 실패: {result['error_count']}
- 성공률: {(result['success_count'] / result['total_views']) * 100:.1f}%
"""
            
            if result['created_views']:
                report += "\n생성된 뷰:\n"
                for view in result['created_views']:
                    report += f"- {view['name']} (ID: {view['id']})\n"
            
            if result['errors']:
                report += "\n오류:\n"
                for error in result['errors']:
                    report += f"- {error}\n"
            
            total_views += result['total_views']
            total_success += result['success_count']
            total_errors += result['error_count']
        
        report += f"""
## 🎯 최종 결과
- 총 뷰: {total_views}개
- 성공: {total_success}개
- 실패: {total_errors}개
- 전체 성공률: {(total_success / total_views) * 100:.1f}%
"""
        
        return report

def main():
    """메인 실행 함수"""
    print("🎯 두산중공업 대시보드 뷰 생성 시작")
    print("=" * 50)
    
    creator = DoosanDashboardViewsCreator()
    
    # 모든 DB의 대시보드 뷰 생성
    results = creator.create_all_dashboard_views()
    
    # 결과 보고서 생성
    report = creator.generate_views_report(results)
    print(report)
    
    # 보고서 저장
    with open('doosan_dashboard_views_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # JSON 형태로도 저장
    with open('doosan_dashboard_views_20250719.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("✅ 두산중공업 대시보드 뷰 생성 완료")

if __name__ == "__main__":
    main() 