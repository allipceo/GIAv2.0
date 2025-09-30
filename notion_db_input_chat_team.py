"""
채팀장님 자료 노션 DB 입력 스크립트
- 처리된 데이터를 노션 DB에 자동 입력
- 품질 검증 후 안전한 입력 보장
"""

import json
import requests
from datetime import datetime
from typing import Dict, List

class NotionDBInputProcessor:
    def __init__(self):
        self.  # 실제 토큰으로 교체 필요
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # 노션 DB ID들 (실제 ID로 교체 필요)
        self.database_ids = {
            '핵심_사업부문_DB': 'your_business_db_id',
            '신재생_프로젝트_DB': 'your_project_db_id', 
            'SPC_사례_DB': 'your_spc_db_id'
        }
    
    def input_business_data(self, business_data: List[Dict]) -> Dict:
        """핵심 사업부문 DB 입력"""
        results = []
        
        for item in business_data:
            page_data = {
                "parent": {"database_id": self.database_ids['핵심_사업부문_DB']},
                "properties": {
                    "사업부문": {
                        "title": [{"text": {"content": item.get('사업부문', '')}}]
                    },
                    "지역": {
                        "rich_text": [{"text": {"content": item.get('지역', '')}}]
                    },
                    "조사기간": {
                        "rich_text": [{"text": {"content": item.get('조사기간', '')}}]
                    },
                    "시장규모": {
                        "rich_text": [{"text": {"content": item.get('시장규모', '')}}]
                    },
                    "연평균성장률": {
                        "rich_text": [{"text": {"content": item.get('연평균성장률', '')}}]
                    },
                    "주요경쟁사": {
                        "rich_text": [{"text": {"content": item.get('주요_경쟁사', '')}}]
                    },
                    "데이터확인일": {
                        "date": {"start": item.get('데이터_확인일', '')}
                    },
                    "팀원": {
                        "rich_text": [{"text": {"content": item.get('팀원', '')}}]
                    },
                    "처리일시": {
                        "rich_text": [{"text": {"content": item.get('처리_일시', '')}}]
                    }
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                if response.status_code == 200:
                    results.append({"status": "success", "id": response.json()["id"]})
                else:
                    results.append({"status": "error", "error": response.text})
                    
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
        
        return {
            "db_name": "핵심_사업부문_DB",
            "total_items": len(business_data),
            "success_count": len([r for r in results if r["status"] == "success"]),
            "error_count": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
    
    def input_project_data(self, project_data: List[Dict]) -> Dict:
        """신재생 프로젝트 DB 입력"""
        results = []
        
        for item in project_data:
            page_data = {
                "parent": {"database_id": self.database_ids['신재생_프로젝트_DB']},
                "properties": {
                    "프로젝트명": {
                        "title": [{"text": {"content": item.get('프로젝트명', '')}}]
                    },
                    "기술유형": {
                        "rich_text": [{"text": {"content": item.get('기술유형', '')}}]
                    },
                    "용량": {
                        "number": float(item.get('용량', 0)) if item.get('용량', '').isdigit() else 0
                    },
                    "참여형태": {
                        "rich_text": [{"text": {"content": item.get('참여형태', '')}}]
                    },
                    "참여지분율": {
                        "number": float(item.get('참여지분율', 0)) if item.get('참여지분율', '').isdigit() else 0
                    },
                    "착공연도": {
                        "number": int(item.get('착공연도', 0)) if item.get('착공연도', '').isdigit() else 0
                    },
                    "준공연도": {
                        "number": int(item.get('준공연도', 0)) if item.get('준공연도', '').isdigit() else 0
                    },
                    "PF대출기관": {
                        "rich_text": [{"text": {"content": item.get('PF_대출기관', '')}}]
                    },
                    "데이터확인일": {
                        "date": {"start": item.get('데이터_확인일', '')}
                    },
                    "팀원": {
                        "rich_text": [{"text": {"content": item.get('팀원', '')}}]
                    },
                    "처리일시": {
                        "rich_text": [{"text": {"content": item.get('처리_일시', '')}}]
                    }
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                if response.status_code == 200:
                    results.append({"status": "success", "id": response.json()["id"]})
                else:
                    results.append({"status": "error", "error": response.text})
                    
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
        
        return {
            "db_name": "신재생_프로젝트_DB",
            "total_items": len(project_data),
            "success_count": len([r for r in results if r["status"] == "success"]),
            "error_count": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
    
    def input_spc_data(self, spc_data: List[Dict]) -> Dict:
        """SPC 사례 DB 입력"""
        results = []
        
        for item in spc_data:
            page_data = {
                "parent": {"database_id": self.database_ids['SPC_사례_DB']},
                "properties": {
                    "SPC명": {
                        "title": [{"text": {"content": item.get('SPC명', '')}}]
                    },
                    "PF총액": {
                        "rich_text": [{"text": {"content": item.get('PF_총액', '')}}]
                    },
                    "참여지분율": {
                        "number": float(item.get('참여_지분율', 0)) if item.get('참여_지분율', '').isdigit() else 0
                    },
                    "대주단": {
                        "rich_text": [{"text": {"content": item.get('대주단', '')}}]
                    },
                    "보험가입현황": {
                        "rich_text": [{"text": {"content": item.get('보험_가입_현황', '')}}]
                    },
                    "공사개시일": {
                        "date": {"start": item.get('공사_개시일', '')}
                    },
                    "준공운영개시일": {
                        "date": {"start": item.get('준공_운영_개시일', '')}
                    },
                    "데이터확인일": {
                        "date": {"start": item.get('데이터_확인일', '')}
                    },
                    "팀원": {
                        "rich_text": [{"text": {"content": item.get('팀원', '')}}]
                    },
                    "처리일시": {
                        "rich_text": [{"text": {"content": item.get('처리_일시', '')}}]
                    }
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                if response.status_code == 200:
                    results.append({"status": "success", "id": response.json()["id"]})
                else:
                    results.append({"status": "error", "error": response.text})
                    
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
        
        return {
            "db_name": "SPC_사례_DB",
            "total_items": len(spc_data),
            "success_count": len([r for r in results if r["status"] == "success"]),
            "error_count": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
    
    def input_all_data(self, processed_data: Dict) -> Dict:
        """전체 데이터 노션 DB 입력"""
        print("🚀 채팀장님 자료 노션 DB 입력 시작...")
        
        input_results = {}
        
        # 핵심 사업부문 DB 입력
        if '핵심_사업부문_DB' in processed_data['results']:
            business_result = self.input_business_data(
                processed_data['results']['핵심_사업부문_DB']['데이터']
            )
            input_results['핵심_사업부문_DB'] = business_result
            print(f"✅ 핵심 사업부문 DB: {business_result['success_count']}/{business_result['total_items']} 입력 완료")
        
        # 신재생 프로젝트 DB 입력
        if '신재생_프로젝트_DB' in processed_data['results']:
            project_result = self.input_project_data(
                processed_data['results']['신재생_프로젝트_DB']['데이터']
            )
            input_results['신재생_프로젝트_DB'] = project_result
            print(f"✅ 신재생 프로젝트 DB: {project_result['success_count']}/{project_result['total_items']} 입력 완료")
        
        # SPC 사례 DB 입력
        if 'SPC_사례_DB' in processed_data['results']:
            spc_result = self.input_spc_data(
                processed_data['results']['SPC_사례_DB']['데이터']
            )
            input_results['SPC_사례_DB'] = spc_result
            print(f"✅ SPC 사례 DB: {spc_result['success_count']}/{spc_result['total_items']} 입력 완료")
        
        # 입력 결과 요약
        total_success = sum(result['success_count'] for result in input_results.values())
        total_items = sum(result['total_items'] for result in input_results.values())
        
        summary = {
            '입력_완료_일시': datetime.now().isoformat(),
            '총_입력_건수': total_items,
            '성공_건수': total_success,
            '실패_건수': total_items - total_success,
            '성공률': f"{total_success/total_items*100:.1f}%" if total_items > 0 else "0%",
            'DB별_결과': input_results
        }
        
        return summary

# 사용 예시
if __name__ == "__main__":
    processor = NotionDBInputProcessor()
    
    # 가상의 처리된 데이터
    processed_data = {
        'results': {
            '핵심_사업부문_DB': {
                '데이터': [
                    {
                        '사업부문': '원자력',
                        '지역': '한국',
                        '시장규모': '12조원',
                        '팀원': '채팀장',
                        '처리_일시': '2025-07-20T16:04:58'
                    }
                ]
            }
        }
    }
    
    result = processor.input_all_data(processed_data)
    print("📊 노션 DB 입력 완료:")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 