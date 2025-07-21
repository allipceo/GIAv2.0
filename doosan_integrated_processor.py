#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 통합 데이터 처리 및 입력 스크립트
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 서술형 텍스트를 분석하여 구조화하고 노션 DB에 자동 입력
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
COMPANY_MASTER_DB_ID = os.getenv('COMPANY_MASTER_DB_ID')

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

class DoosanIntegratedProcessor:
    """두산중공업 통합 데이터 처리 및 입력 클래스"""
    
    def __init__(self):
        """초기화"""
        self.company_id = None
        self.processed_data = {}
        self.input_results = {}
        self.error_log = []
        
        # 텍스트 처리기 임포트
        from doosan_text_processor import DoosanTextProcessor
        self.text_processor = DoosanTextProcessor()
    
    def ensure_doosan_in_master(self) -> bool:
        """회사 정보 마스터 DB에 두산중공업이 있는지 확인하고 없으면 추가"""
        print("🏢 회사 정보 마스터 DB 확인...")
        
        try:
            # 기존 두산중공업 레코드 확인
            url = f"https://api.notion.com/v1/databases/{COMPANY_MASTER_DB_ID}/query"
            response = requests.post(url, headers=HEADERS, json={
                "filter": {
                    "property": "회사명",
                    "title": {
                        "equals": "두산중공업"
                    }
                }
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    self.company_id = data['results'][0]['id']
                    print(f"✅ 기존 두산중공업 레코드 확인: {self.company_id}")
                    return True
                else:
                    # 새로 추가
                    return self._add_doosan_to_master()
            else:
                print(f"❌ 회사 정보 DB 조회 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 회사 정보 확인 오류: {e}")
            return False
    
    def _add_doosan_to_master(self) -> bool:
        """회사 정보 마스터 DB에 두산중공업 추가"""
        print("➕ 회사 정보 마스터 DB에 두산중공업 추가...")
        
        doosan_data = {
            'parent': {'database_id': COMPANY_MASTER_DB_ID},
            'properties': {
                '회사명': {
                    'title': [{'type': 'text', 'text': {'content': '두산중공업'}}]
                },
                '업종': {
                    'select': {'name': '중공업'}
                },
                '설립년도': {
                    'number': 1962
                },
                '본사위치': {
                    'rich_text': [{'type': 'text', 'text': {'content': '서울특별시'}}]
                },
                '대표이사': {
                    'rich_text': [{'type': 'text', 'text': {'content': '정경훈'}}]
                },
                '매출규모': {
                    'select': {'name': '1조 이상'}
                },
                '상장여부': {
                    'checkbox': True
                },
                '프로젝트상태': {
                    'select': {'name': '조사중'}
                }
            }
        }
        
        try:
            url = "https://api.notion.com/v1/pages"
            response = requests.post(url, headers=HEADERS, json=doosan_data)
            
            if response.status_code == 200:
                result = response.json()
                self.company_id = result['id']
                print(f"✅ 두산중공업 정보 추가 완료: {self.company_id}")
                return True
            else:
                print(f"❌ 두산중공업 정보 추가 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 두산중공업 정보 추가 오류: {e}")
            return False
    
    def process_text_and_input(self, text_content: str) -> Dict:
        """텍스트 처리 및 노션 DB 입력"""
        print("🔄 텍스트 처리 및 DB 입력 시작...")
        
        # 1. 텍스트 처리
        print("📝 서술형 텍스트 분석 중...")
        self.processed_data = self.text_processor.process_markdown_text(text_content)
        
        # 2. 회사 정보 확인
        if not self.ensure_doosan_in_master():
            print("❌ 회사 정보 설정 실패 - 중단")
            return {"success": False, "error": "회사 정보 설정 실패"}
        
        # 3. 각 DB에 데이터 입력
        print("📝 노션 DB에 데이터 입력 중...")
        for db_name, data_list in self.processed_data.items():
            if data_list:
                result = self._input_data_to_db(db_name, data_list)
                self.input_results[db_name] = result
        
        return self.input_results
    
    def _input_data_to_db(self, db_name: str, data_list: List[Dict]) -> Dict:
        """DB에 데이터 입력"""
        print(f"📝 {db_name}에 {len(data_list)}개 레코드 입력...")
        
        db_id = DB_IDS.get(db_name)
        if not db_id:
            print(f"❌ {db_name}의 DB ID를 찾을 수 없습니다.")
            return {"success": False, "error": "DB ID 없음"}
        
        success_count = 0
        error_count = 0
        
        for i, data in enumerate(data_list, 1):
            try:
                # 노션 속성으로 변환
                properties = self._convert_to_notion_properties(db_name, data)
                
                # 페이지 생성
                page_id = self._create_notion_page(db_id, properties)
                
                if page_id:
                    success_count += 1
                    print(f"✅ 레코드 {i} 입력 성공")
                else:
                    error_count += 1
                    print(f"❌ 레코드 {i} 입력 실패")
                
                time.sleep(1)  # API 호출 간격
                
            except Exception as e:
                error_count += 1
                error_msg = f"레코드 {i} 처리 오류: {str(e)}"
                self.error_log.append(error_msg)
                print(f"❌ {error_msg}")
        
        result = {
            "success": True,
            "total": len(data_list),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": (success_count / len(data_list)) * 100 if data_list else 0
        }
        
        print(f"📊 {db_name} 입력 완료: {success_count}/{len(data_list)} 성공")
        return result
    
    def _convert_to_notion_properties(self, db_name: str, data: Dict) -> Dict:
        """데이터를 노션 속성으로 변환"""
        properties = {}
        
        # 회사명 관계형 속성 추가 (모든 DB에 공통)
        if self.company_id:
            properties['회사명'] = {
                'relation': [{'id': self.company_id}]
            }
        
        # DB별 속성 매핑
        if db_name == "📊 기업 위험 프로파일 DB":
            properties.update(self._convert_risk_profile_properties(data))
        elif db_name == "💰 기업 재무 및 프로젝트 DB":
            properties.update(self._convert_financial_properties(data))
        elif db_name == "🔋 신재생에너지 프로젝트 DB":
            properties.update(self._convert_renewable_energy_properties(data))
        elif db_name == "👥 기업 핵심 인물 DB":
            properties.update(self._convert_key_persons_properties(data))
        elif db_name == "🏛️ 정부 정책 영향 분석 DB":
            properties.update(self._convert_government_policy_properties(data))
        elif db_name == "🌍 글로벌 보험중개 시장 DB":
            properties.update(self._convert_insurance_market_properties(data))
        
        return properties
    
    def _convert_risk_profile_properties(self, data: Dict) -> Dict:
        """기업 위험 프로파일 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "리스크명" in data:
            properties["리스크명"] = {
                "title": [{"text": {"content": data["리스크명"]}}]
            }
        
        # Select 필드들
        select_fields = ["리스크 유형", "발생 확률", "영향도", "리스크 등급", "대응 현황"]
        for field in select_fields:
            if field in data and data[field]:
                properties[field] = {"select": {"name": data[field]}}
        
        # Number 필드들
        number_fields = ["발생 확률 점수", "영향도 점수"]
        for field in number_fields:
            if field in data and data[field]:
                try:
                    properties[field] = {"number": float(data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {data[field]}")
        
        # Rich Text 필드
        if "리스크 설명" in data:
            properties["리스크 설명"] = {
                "rich_text": [{"text": {"content": data["리스크 설명"]}}]
            }
        
        # Multi-select 필드
        if "관련 사업부" in data:
            departments = [dept.strip() for dept in data["관련 사업부"].split(',')]
            properties["관련 사업부"] = {
                "multi_select": [{"name": dept} for dept in departments if dept]
            }
        
        return properties
    
    def _convert_financial_properties(self, data: Dict) -> Dict:
        """기업 재무 및 프로젝트 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "항목명" in data:
            properties["항목명"] = {
                "title": [{"text": {"content": data["항목명"]}}]
            }
        
        # Select 필드들
        select_fields = ["데이터 유형", "단위", "지역", "중요도"]
        for field in select_fields:
            if field in data and data[field]:
                properties[field] = {"select": {"name": data[field]}}
        
        # Number 필드들
        number_fields = ["수치값", "전년 동기 대비"]
        for field in number_fields:
            if field in data and data[field]:
                try:
                    properties[field] = {"number": float(data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {data[field]}")
        
        # Rich Text 필드
        if "설명" in data:
            properties["설명"] = {
                "rich_text": [{"text": {"content": data["설명"]}}]
            }
        
        return properties
    
    def _convert_renewable_energy_properties(self, data: Dict) -> Dict:
        """신재생에너지 프로젝트 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "프로젝트명" in data:
            properties["프로젝트명"] = {
                "title": [{"text": {"content": data["프로젝트명"]}}]
            }
        
        # Select 필드들
        select_fields = ["프로젝트 유형", "단위", "지역", "진행 상태", "두산중공업 역할", "리스크 등급"]
        for field in select_fields:
            if field in data and data[field]:
                properties[field] = {"select": {"name": data[field]}}
        
        # Number 필드들
        number_fields = ["프로젝트 규모", "계약 금액"]
        for field in number_fields:
            if field in data and data[field]:
                try:
                    properties[field] = {"number": float(data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {data[field]}")
        
        # Rich Text 필드
        if "프로젝트 설명" in data:
            properties["프로젝트 설명"] = {
                "rich_text": [{"text": {"content": data["프로젝트 설명"]}}]
            }
        
        return properties
    
    def _convert_key_persons_properties(self, data: Dict) -> Dict:
        """핵심 인물 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "인물명" in data:
            properties["인물명"] = {
                "title": [{"text": {"content": data["인물명"]}}]
            }
        
        # Select 필드들
        select_fields = ["직책", "소속 부문", "담당 영역", "중요도"]
        for field in select_fields:
            if field in data and data[field]:
                properties[field] = {"select": {"name": data[field]}}
        
        # Rich Text 필드들
        text_fields = ["경력", "주요 성과", "연락처"]
        for field in text_fields:
            if field in data and data[field]:
                properties[field] = {
                    "rich_text": [{"text": {"content": data[field]}}]
                }
        
        return properties
    
    def _convert_government_policy_properties(self, data: Dict) -> Dict:
        """정부 정책 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "정책명" in data:
            properties["정책명"] = {
                "title": [{"text": {"content": data["정책명"]}}]
            }
        
        # Select 필드들
        select_fields = ["정책 분야", "발표 기관", "두산중공업 영향", "관련 사업부", "정책 우선순위"]
        for field in select_fields:
            if field in data and data[field]:
                properties[field] = {"select": {"name": data[field]}}
        
        # Rich Text 필드
        if "정책 내용" in data:
            properties["정책 내용"] = {
                "rich_text": [{"text": {"content": data["정책 내용"]}}]
            }
        
        # Number 필드
        if "예산 규모" in data and data["예산 규모"]:
            try:
                properties["예산 규모"] = {"number": float(data["예산 규모"])}
            except ValueError:
                self.error_log.append(f"숫자 변환 실패: 예산 규모 = {data['예산 규모']}")
        
        return properties
    
    def _convert_insurance_market_properties(self, data: Dict) -> Dict:
        """글로벌 보험중개 시장 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "회사명" in data:
            properties["회사명"] = {
                "title": [{"text": {"content": data["회사명"]}}]
            }
        
        # Select 필드들
        select_fields = ["회사 유형", "본사 위치", "주요 서비스", "두산중공업 경쟁력", "특화 영역", "록톤과의 관계"]
        for field in select_fields:
            if field in data and data[field]:
                properties[field] = {"select": {"name": data[field]}}
        
        # Number 필드들
        number_fields = ["연매출", "직원 수"]
        for field in number_fields:
            if field in data and data[field]:
                try:
                    properties[field] = {"number": float(data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {data[field]}")
        
        # Rich Text 필드
        if "회사 설명" in data:
            properties["회사 설명"] = {
                "rich_text": [{"text": {"content": data["회사 설명"]}}]
            }
        
        return properties
    
    def _create_notion_page(self, db_id: str, properties: Dict) -> str:
        """노션 페이지 생성"""
        url = "https://api.notion.com/v1/pages"
        
        payload = {
            "parent": {"database_id": db_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, headers=HEADERS, json=payload)
            response.raise_for_status()
            
            result = response.json()
            page_id = result["id"]
            
            return page_id
            
        except requests.exceptions.RequestException as e:
            error_msg = f"페이지 생성 실패: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - 응답: {e.response.text}"
            self.error_log.append(error_msg)
            return None
    
    def generate_integrated_report(self) -> str:
        """통합 처리 결과 보고서 생성"""
        report = f"""
# 두산중공업 통합 데이터 처리 및 입력 결과 보고서
생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

## 📊 텍스트 처리 결과
"""
        
        total_processed = 0
        for db_name, data_list in self.processed_data.items():
            report += f"- {db_name}: {len(data_list)}개 레코드 추출\n"
            total_processed += len(data_list)
        
        report += f"""
## 📝 노션 DB 입력 결과
"""
        
        total_success = 0
        total_error = 0
        
        for db_name, result in self.input_results.items():
            report += f"""
### {db_name}
- 총 레코드: {result['total']}
- 성공: {result['success_count']}
- 실패: {result['error_count']}
- 성공률: {result['success_rate']:.1f}%
"""
            total_success += result['success_count']
            total_error += result['error_count']
        
        if self.error_log:
            report += f"""
## ❌ 오류 로그
"""
            for error in self.error_log:
                report += f"- {error}\n"
        
        report += f"""
## 🎯 최종 결과
- 총 처리된 레코드: {total_processed}개
- 총 입력 성공: {total_success}개
- 총 입력 실패: {total_error}개
- 회사 ID: {self.company_id}
- 전체 성공률: {(total_success / (total_success + total_error)) * 100:.1f}%
"""
        
        return report

def main():
    """메인 실행 함수"""
    print("🔄 두산중공업 통합 데이터 처리 및 입력 시작")
    print("=" * 50)
    
    processor = DoosanIntegratedProcessor()
    
    # 예시 서술형 텍스트 (실제로는 팀원들이 제공한 텍스트 사용)
    sample_text = """
# 두산중공업 해외 프로젝트 현황

## 리스크 분석
두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다. 특히 미국 달러화 변동으로 인한 손실 위험이 높은 상황입니다.

## 재무 현황
2024년 매출 15,000억원을 달성했으며, 해외 프로젝트 비중이 60%를 차지합니다.

## 신재생에너지 프로젝트
태양광 발전소 200MW 프로젝트를 진행 중이며, ESS 사업도 확장하고 있습니다.

## 경영진
정경훈 대표이사가 경영을 총괄하고 있으며, 30년 경력의 전문가입니다.

## 정부 정책 영향
신재생에너지 지원 정책으로 인해 태양광 사업이 확대되고 있습니다.

## 보험 시장
글로벌 보험중개사들과 협력하여 해외 프로젝트 리스크를 관리하고 있습니다.
"""
    
    # 통합 처리 및 입력
    results = processor.process_text_and_input(sample_text)
    
    # 결과 보고서 생성
    report = processor.generate_integrated_report()
    print(report)
    
    # 보고서 저장
    with open('doosan_integrated_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 두산중공업 통합 데이터 처리 및 입력 완료")

if __name__ == "__main__":
    main() 