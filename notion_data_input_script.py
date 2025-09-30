#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
노션 데이터 입력 스크립트
작성일: 2025년 1월 18일
작성자: 서대리 (Lead Developer)
목적: 팀원들이 작성한 데이터를 노션 DB에 자동 입력
"""

import requests
import json
import time
import csv
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# 노션 API 설정
NOTION_TOKEN = ""

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

class NotionDataInputter:
    """노션 데이터 입력 클래스"""
    
    def __init__(self):
        """초기화"""
        self.db_ids = self._load_db_ids()
        self.input_results = {}
        self.error_log = []
        
    def _load_db_ids(self) -> Dict:
        """DB ID 로드"""
        try:
            with open('hyosung_dbs_created_20250719_003144.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ DB ID 파일을 찾을 수 없습니다.")
            return {}
    
    def parse_markdown_table(self, markdown_content: str) -> List[Dict]:
        """마크다운 테이블 파싱"""
        lines = markdown_content.strip().split('\n')
        table_data = []
        headers = []
        
        for line in lines:
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if not headers:
                    headers = cells
                elif not all(cell.startswith('-') for cell in cells):
                    row_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            row_data[headers[i]] = cell
                    table_data.append(row_data)
        
        return table_data
    
    def parse_csv_data(self, csv_content: str) -> List[Dict]:
        """CSV 데이터 파싱"""
        lines = csv_content.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = [h.strip() for h in lines[0].split(',')]
        data = []
        
        for line in lines[1:]:
            cells = [cell.strip() for cell in line.split(',')]
            if len(cells) == len(headers):
                row_data = dict(zip(headers, cells))
                data.append(row_data)
        
        return data
    
    def parse_json_data(self, json_content: str) -> List[Dict]:
        """JSON 데이터 파싱"""
        try:
            data = json.loads(json_content)
            if isinstance(data, list):
                return data
            else:
                return [data]
        except json.JSONDecodeError as e:
            self.error_log.append(f"JSON 파싱 오류: {str(e)}")
            return []
    
    def create_notion_page(self, db_id: str, properties: Dict) -> Optional[str]:
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
    
    def convert_to_notion_properties(self, db_name: str, row_data: Dict) -> Dict:
        """데이터를 노션 속성으로 변환"""
        properties = {}
        
        # DB별 속성 매핑
        if db_name == "기업 위험 프로파일 DB":
            properties = self._convert_risk_profile_properties(row_data)
        elif db_name == "기업 재무 및 프로젝트 DB":
            properties = self._convert_financial_properties(row_data)
        elif db_name == "신재생에너지 프로젝트 DB":
            properties = self._convert_renewable_energy_properties(row_data)
        elif db_name == "핵심 인물 DB":
            properties = self._convert_key_persons_properties(row_data)
        elif db_name == "정부 정책 DB":
            properties = self._convert_government_policy_properties(row_data)
        elif db_name == "글로벌 보험중개 시장 DB":
            properties = self._convert_insurance_market_properties(row_data)
        
        return properties
    
    def _convert_risk_profile_properties(self, row_data: Dict) -> Dict:
        """기업 위험 프로파일 DB 속성 변환"""
        properties = {}
        
        # Title 필드 (필수)
        if "리스크명" in row_data:
            properties["리스크명"] = {
                "title": [{"text": {"content": row_data["리스크명"]}}]
            }
        
        # Select 필드들
        select_fields = ["리스크 유형", "발생 확률", "영향도", "리스크 등급", "대응 현황"]
        for field in select_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"select": {"name": row_data[field]}}
        
        # Number 필드들
        number_fields = ["발생 확률 점수", "영향도 점수"]
        for field in number_fields:
            if field in row_data and row_data[field]:
                try:
                    properties[field] = {"number": float(row_data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {row_data[field]}")
        
        # Rich Text 필드
        if "리스크 설명" in row_data:
            properties["리스크 설명"] = {
                "rich_text": [{"text": {"content": row_data["리스크 설명"]}}]
            }
        
        # Multi-select 필드
        if "관련 사업부" in row_data:
            departments = [dept.strip() for dept in row_data["관련 사업부"].split(',')]
            properties["관련 사업부"] = {
                "multi_select": [{"name": dept} for dept in departments if dept]
            }
        
        return properties
    
    def _convert_financial_properties(self, row_data: Dict) -> Dict:
        """기업 재무 및 프로젝트 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "항목명" in row_data:
            properties["항목명"] = {
                "title": [{"text": {"content": row_data["항목명"]}}]
            }
        
        # Select 필드들
        select_fields = ["데이터 유형", "단위", "지역", "중요도"]
        for field in select_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"select": {"name": row_data[field]}}
        
        # Number 필드들
        number_fields = ["수치값", "전년 동기 대비"]
        for field in number_fields:
            if field in row_data and row_data[field]:
                try:
                    properties[field] = {"number": float(row_data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {row_data[field]}")
        
        # Date 필드
        if "기준일" in row_data:
            properties["기준일"] = {"date": {"start": row_data["기준일"]}}
        
        # Multi-select 필드
        if "사업 부문" in row_data:
            departments = [dept.strip() for dept in row_data["사업 부문"].split(',')]
            properties["사업 부문"] = {
                "multi_select": [{"name": dept} for dept in departments if dept]
            }
        
        # URL 필드
        if "데이터 소스" in row_data:
            properties["데이터 소스"] = {"url": row_data["데이터 소스"]}
        
        return properties
    
    def _convert_renewable_energy_properties(self, row_data: Dict) -> Dict:
        """신재생에너지 프로젝트 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "프로젝트명" in row_data:
            properties["프로젝트명"] = {
                "title": [{"text": {"content": row_data["프로젝트명"]}}]
            }
        
        # Select 필드들
        select_fields = ["프로젝트 유형", "단위", "지역", "진행 상태", "리스크 등급"]
        for field in select_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"select": {"name": row_data[field]}}
        
        # Number 필드들
        number_fields = ["프로젝트 규모", "계약 금액"]
        for field in number_fields:
            if field in row_data and row_data[field]:
                try:
                    properties[field] = {"number": float(row_data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {row_data[field]}")
        
        # Date 필드들
        date_fields = ["시작일", "완료일"]
        for field in date_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"date": {"start": row_data[field]}}
        
        # Multi-select 필드
        if "효성중공업 역할" in row_data:
            roles = [role.strip() for role in row_data["효성중공업 역할"].split(',')]
            properties["효성중공업 역할"] = {
                "multi_select": [{"name": role} for role in roles if role]
            }
        
        # Rich Text 필드
        if "관련 정책" in row_data:
            properties["관련 정책"] = {
                "rich_text": [{"text": {"content": row_data["관련 정책"]}}]
            }
        
        # URL 필드
        if "데이터 소스" in row_data:
            properties["데이터 소스"] = {"url": row_data["데이터 소스"]}
        
        return properties
    
    def _convert_key_persons_properties(self, row_data: Dict) -> Dict:
        """핵심 인물 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "인물명" in row_data:
            properties["인물명"] = {
                "title": [{"text": {"content": row_data["인물명"]}}]
            }
        
        # Select 필드들
        select_fields = ["직책", "소속 부문", "중요도"]
        for field in select_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"select": {"name": row_data[field]}}
        
        # Multi-select 필드
        if "담당 영역" in row_data:
            areas = [area.strip() for area in row_data["담당 영역"].split(',')]
            properties["담당 영역"] = {
                "multi_select": [{"name": area} for area in areas if area]
            }
        
        # Rich Text 필드들
        rich_text_fields = ["경력", "학력", "주요 성과"]
        for field in rich_text_fields:
            if field in row_data and row_data[field]:
                properties[field] = {
                    "rich_text": [{"text": {"content": row_data[field]}}]
                }
        
        return properties
    
    def _convert_government_policy_properties(self, row_data: Dict) -> Dict:
        """정부 정책 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "정책명" in row_data:
            properties["정책명"] = {
                "title": [{"text": {"content": row_data["정책명"]}}]
            }
        
        # Select 필드들
        select_fields = ["정책 분야", "발표 기관", "효성중공업 영향", "정책 우선순위"]
        for field in select_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"select": {"name": row_data[field]}}
        
        # Number 필드
        if "예산 규모" in row_data:
            try:
                properties["예산 규모"] = {"number": float(row_data["예산 규모"])}
            except ValueError:
                self.error_log.append(f"숫자 변환 실패: 예산 규모 = {row_data['예산 규모']}")
        
        # Date 필드들
        date_fields = ["발표일", "시행일"]
        for field in date_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"date": {"start": row_data[field]}}
        
        # Rich Text 필드
        if "정책 내용" in row_data:
            properties["정책 내용"] = {
                "rich_text": [{"text": {"content": row_data["정책 내용"]}}]
            }
        
        # Multi-select 필드
        if "관련 사업부" in row_data:
            departments = [dept.strip() for dept in row_data["관련 사업부"].split(',')]
            properties["관련 사업부"] = {
                "multi_select": [{"name": dept} for dept in departments if dept]
            }
        
        # URL 필드
        if "관련 링크" in row_data:
            properties["관련 링크"] = {"url": row_data["관련 링크"]}
        
        return properties
    
    def _convert_insurance_market_properties(self, row_data: Dict) -> Dict:
        """글로벌 보험중개 시장 DB 속성 변환"""
        properties = {}
        
        # Title 필드
        if "회사명" in row_data:
            properties["회사명"] = {
                "title": [{"text": {"content": row_data["회사명"]}}]
            }
        
        # Select 필드들
        select_fields = ["회사 유형", "본사 위치", "효성중공업 경쟁력", "록톤과의 관계"]
        for field in select_fields:
            if field in row_data and row_data[field]:
                properties[field] = {"select": {"name": row_data[field]}}
        
        # Number 필드들
        number_fields = ["연매출", "직원 수"]
        for field in number_fields:
            if field in row_data and row_data[field]:
                try:
                    properties[field] = {"number": float(row_data[field])}
                except ValueError:
                    self.error_log.append(f"숫자 변환 실패: {field} = {row_data[field]}")
        
        # Multi-select 필드들
        multi_select_fields = ["주요 서비스", "특화 영역"]
        for field in multi_select_fields:
            if field in row_data and row_data[field]:
                items = [item.strip() for item in row_data[field].split(',')]
                properties[field] = {
                    "multi_select": [{"name": item} for item in items if item]
                }
        
        # Rich Text 필드들
        rich_text_fields = ["주요 고객", "분석 메모"]
        for field in rich_text_fields:
            if field in row_data and row_data[field]:
                properties[field] = {
                    "rich_text": [{"text": {"content": row_data[field]}}]
                }
        
        # URL 필드
        if "데이터 소스" in row_data:
            properties["데이터 소스"] = {"url": row_data["데이터 소스"]}
        
        return properties
    
    def input_data_to_notion(self, db_name: str, data: List[Dict], data_type: str = "markdown") -> Dict:
        """노션 DB에 데이터 입력"""
        print(f"\n🎯 {db_name}에 데이터 입력 시작...")
        
        if db_name not in self.db_ids:
            return {"error": f"DB '{db_name}'를 찾을 수 없습니다."}
        
        db_id = self.db_ids[db_name]["id"]
        success_count = 0
        error_count = 0
        
        for i, row_data in enumerate(data, 1):
            print(f"  📝 {i}/{len(data)}번째 항목 처리 중...")
            
            # 노션 속성으로 변환
            properties = self.convert_to_notion_properties(db_name, row_data)
            
            if not properties:
                error_count += 1
                self.error_log.append(f"행 {i}: 속성 변환 실패")
                continue
            
            # 노션 페이지 생성
            page_id = self.create_notion_page(db_id, properties)
            
            if page_id:
                success_count += 1
                print(f"    ✅ 성공: {list(row_data.values())[0] if row_data else 'Unknown'}")
            else:
                error_count += 1
                print(f"    ❌ 실패: {list(row_data.values())[0] if row_data else 'Unknown'}")
            
            # API 제한 방지
            time.sleep(1)
        
        result = {
            "db_name": db_name,
            "total_items": len(data),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": (success_count / len(data) * 100) if data else 0
        }
        
        self.input_results[db_name] = result
        return result
    
    def input_markdown_table(self, db_name: str, markdown_content: str) -> Dict:
        """마크다운 테이블 입력"""
        data = self.parse_markdown_table(markdown_content)
        return self.input_data_to_notion(db_name, data, "markdown")
    
    def input_csv_data(self, db_name: str, csv_content: str) -> Dict:
        """CSV 데이터 입력"""
        data = self.parse_csv_data(csv_content)
        return self.input_data_to_notion(db_name, data, "csv")
    
    def input_json_data(self, db_name: str, json_content: str) -> Dict:
        """JSON 데이터 입력"""
        data = self.parse_json_data(json_content)
        return self.input_data_to_notion(db_name, data, "json")
    
    def generate_input_report(self) -> str:
        """입력 결과 보고서 생성"""
        report = []
        report.append("=" * 80)
        report.append("📊 노션 데이터 입력 결과 보고서")
        report.append("=" * 80)
        
        total_success = 0
        total_error = 0
        
        for db_name, result in self.input_results.items():
            report.append(f"\n📁 {db_name}")
            report.append("-" * 40)
            
            if "error" in result:
                report.append(f"❌ 오류: {result['error']}")
                continue
            
            report.append(f"📊 총 항목: {result['total_items']}개")
            report.append(f"✅ 성공: {result['success_count']}개")
            report.append(f"❌ 실패: {result['error_count']}개")
            report.append(f"📈 성공률: {result['success_rate']:.1f}%")
            
            total_success += result['success_count']
            total_error += result['error_count']
        
        # 전체 요약
        total_items = sum(r['total_items'] for r in self.input_results.values() if 'total_items' in r)
        if total_items > 0:
            overall_success_rate = (total_success / total_items) * 100
            report.append(f"\n🎯 전체 요약")
            report.append("-" * 40)
            report.append(f"📊 총 입력 항목: {total_items}개")
            report.append(f"✅ 총 성공: {total_success}개")
            report.append(f"❌ 총 실패: {total_error}개")
            report.append(f"📈 전체 성공률: {overall_success_rate:.1f}%")
        
        # 오류 로그
        if self.error_log:
            report.append(f"\n🚨 오류 로그")
            report.append("-" * 40)
            for error in self.error_log:
                report.append(f"  - {error}")
        
        return "\n".join(report)

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚀 노션 데이터 입력 스크립트")
    print("=" * 80)
    
    inputter = NotionDataInputter()
    
    # 사용 예시
    print("\n📋 사용 방법:")
    print("1. 마크다운 테이블 입력: inputter.input_markdown_table(db_name, content)")
    print("2. CSV 데이터 입력: inputter.input_csv_data(db_name, content)")
    print("3. JSON 데이터 입력: inputter.input_json_data(db_name, content)")
    print("4. 결과 보고서: inputter.generate_input_report()")
    
    print("\n✅ 입력 스크립트 준비 완료!")
    print("팀원들이 데이터를 제출하면 즉시 노션에 입력 가능합니다.")
    
    return inputter

if __name__ == "__main__":
    inputter = main() 