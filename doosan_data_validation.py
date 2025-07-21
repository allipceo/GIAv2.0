#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 데이터 검증 스크립트
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 두산중공업 데이터의 형식 및 품질 검증
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple

class DoosanDataValidator:
    """두산중공업 데이터 검증 클래스"""
    
    def __init__(self):
        """검증 규칙 초기화"""
        self.validation_rules = self._load_validation_rules()
        self.validation_results = {}
    
    def _load_validation_rules(self) -> Dict:
        """검증 규칙 로드 (일반화된 DB 구조)"""
        return {
            "📊 기업 위험 프로파일 DB": {
                "required_fields": ["리스크명", "리스크 유형", "리스크 설명", "발생 확률", "발생 확률 점수", "영향도", "영향도 점수", "관련 사업부", "대응 현황"],
                "select_options": {
                    "리스크 유형": ["사이버 리스크", "운영 리스크", "재무 리스크", "전략 리스크", "규제 리스크"],
                    "발생 확률": ["매우 낮음", "낮음", "보통", "높음", "매우 높음"],
                    "영향도": ["매우 낮음", "낮음", "보통", "높음", "치명적"],
                    "리스크 등급": ["매우 높음", "높음", "보통", "낮음", "매우 낮음"],
                    "관련 사업부": ["중공업", "TNS", "첨단소재", "전체"],
                    "대응 현황": ["대응 계획", "대응 진행중", "완료"]
                },
                "number_fields": ["발생 확률 점수", "영향도 점수"],
                "number_ranges": {
                    "발생 확률 점수": (1, 5),
                    "영향도 점수": (1, 5)
                }
            },
            "💰 기업 재무 및 프로젝트 DB": {
                "required_fields": ["항목명", "데이터 유형", "수치값", "단위", "기준일", "사업 부문", "지역", "중요도"],
                "select_options": {
                    "데이터 유형": ["재무", "프로젝트"],
                    "단위": ["억원", "MW", "MWh", "%", "달러", "유로"],
                    "사업 부문": ["중공업", "첨단소재", "TNS"],
                    "지역": ["국내", "해외", "미주", "유럽", "아시아", "전체"],
                    "중요도": ["매우중요", "중요", "보통"]
                },
                "number_fields": ["수치값", "전년 동기 대비"],
                "date_fields": ["기준일"]
            },
            "🔋 신재생에너지 프로젝트 DB": {
                "required_fields": ["프로젝트명", "프로젝트 유형", "프로젝트 규모", "단위", "지역", "진행 상태", "시작일", "두산중공업 역할", "계약 금액", "리스크 등급"],
                "select_options": {
                    "프로젝트 유형": ["태양광", "풍력", "ESS", "수소", "바이오", "기타"],
                    "단위": ["MW", "MWh", "톤", "기타"],
                    "지역": ["국내", "미국", "유럽", "아시아", "중동", "기타"],
                    "진행 상태": ["계획", "진행중", "완료", "중단"],
                    "두산중공업 역할": ["변압기", "인버터", "ESS", "건설", "운영", "기타"],
                    "리스크 등급": ["매우 높음", "높음", "보통", "낮음", "매우 낮음"]
                },
                "number_fields": ["프로젝트 규모", "계약 금액"],
                "date_fields": ["시작일", "완료일"]
            },
            "👥 기업 핵심 인물 DB": {
                "required_fields": ["인물명", "직책", "소속 부문", "담당 영역", "경력", "중요도"],
                "select_options": {
                    "직책": ["대표이사", "사장", "부사장", "이사", "팀장", "기타"],
                    "소속 부문": ["지주회사", "중공업", "첨단소재", "TNS", "기타"],
                    "담당 영역": ["경영총괄", "기술개발", "해외사업", "재무", "인사", "마케팅", "기타"],
                    "중요도": ["매우중요", "중요", "보통"]
                }
            },
            "🏛️ 정부 정책 영향 분석 DB": {
                "required_fields": ["정책명", "정책 분야", "발표 기관", "발표일", "시행일", "정책 내용", "두산중공업 영향", "관련 사업부", "정책 우선순위"],
                "select_options": {
                    "정책 분야": ["신재생에너지", "탄소중립", "제조업", "무역", "금융", "기타"],
                    "발표 기관": ["산업통상자원부", "기획재정부", "환경부", "과학기술정보통신부", "기타"],
                    "두산중공업 영향": ["매우 긍정", "긍정", "중립", "부정", "매우 부정"],
                    "관련 사업부": ["중공업", "TNS", "첨단소재", "전체"],
                    "정책 우선순위": ["최우선", "우선", "보통", "낮음"]
                },
                "number_fields": ["예산 규모"],
                "date_fields": ["발표일", "시행일"]
            },
            "🌍 글로벌 보험중개 시장 DB": {
                "required_fields": ["회사명", "회사 유형", "본사 위치", "연매출", "직원 수", "주요 서비스", "두산중공업 경쟁력", "특화 영역", "록톤과의 관계"],
                "select_options": {
                    "회사 유형": ["글로벌 보험중개사", "국내 보험중개사", "기타"],
                    "본사 위치": ["미국", "영국", "독일", "일본", "한국", "기타"],
                    "주요 서비스": ["기업보험", "재보험", "컨설팅", "리스크관리", "기타"],
                    "두산중공업 경쟁력": ["우세", "동등", "열세"],
                    "특화 영역": ["전력", "건설", "제조", "IT", "금융", "기타"],
                    "록톤과의 관계": ["경쟁사", "협력사", "중립"]
                },
                "number_fields": ["연매출", "직원 수"]
            }
        }
    
    def validate_markdown_table(self, db_name: str, markdown_content: str) -> Dict:
        """마크다운 테이블 검증"""
        print(f"\n🔍 {db_name} 마크다운 테이블 검증 시작...")
        
        # 마크다운 테이블 파싱
        lines = markdown_content.strip().split('\n')
        table_data = []
        headers = []
        
        for line in lines:
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if not headers:
                    headers = cells
                elif not all(cell.startswith('-') for cell in cells):
                    table_data.append(dict(zip(headers, cells)))
        
        # 각 행 검증
        validation_results = {
            "total_rows": len(table_data),
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": [],
            "warnings": []
        }
        
        for i, row in enumerate(table_data, 1):
            row_validation = self._validate_row(db_name, row, i)
            if row_validation["is_valid"]:
                validation_results["valid_rows"] += 1
            else:
                validation_results["invalid_rows"] += 1
                validation_results["errors"].extend(row_validation["errors"])
            validation_results["warnings"].extend(row_validation["warnings"])
        
        return validation_results
    
    def _validate_row(self, db_name: str, row: Dict, row_num: int) -> Dict:
        """개별 행 검증"""
        rules = self.validation_rules[db_name]
        errors = []
        warnings = []
        
        # 필수 필드 검증
        for field in rules["required_fields"]:
            if field not in row or not row[field].strip():
                errors.append(f"행 {row_num}: 필수 필드 '{field}' 누락")
        
        # Select 옵션 검증
        for field, valid_options in rules.get("select_options", {}).items():
            if field in row and row[field].strip():
                value = row[field].strip()
                if value not in valid_options:
                    errors.append(f"행 {row_num}: '{field}' 필드 값 '{value}'가 유효하지 않음. 유효한 옵션: {', '.join(valid_options)}")
        
        # Number 필드 검증
        for field in rules.get("number_fields", []):
            if field in row and row[field].strip():
                try:
                    value = float(row[field])
                    # 범위 검증
                    if field in rules.get("number_ranges", {}):
                        min_val, max_val = rules["number_ranges"][field]
                        if not (min_val <= value <= max_val):
                            errors.append(f"행 {row_num}: '{field}' 값 {value}가 범위({min_val}-{max_val})를 벗어남")
                except ValueError:
                    errors.append(f"행 {row_num}: '{field}' 필드가 숫자가 아님: '{row[field]}'")
        
        # Date 필드 검증
        for field in rules.get("date_fields", []):
            if field in row and row[field].strip():
                date_str = row[field].strip()
                if not self._is_valid_date(date_str):
                    errors.append(f"행 {row_num}: '{field}' 날짜 형식 오류: '{date_str}'. YYYY-MM-DD 형식 사용")
        
        # URL 필드 검증
        url_fields = ["데이터 소스", "관련 링크"]
        for field in url_fields:
            if field in row and row[field].strip():
                url = row[field].strip()
                if not self._is_valid_url(url):
                    warnings.append(f"행 {row_num}: '{field}' URL 형식 의심: '{url}'")
        
        # Multi-select 필드 검증
        multi_select_fields = ["관련 사업부", "담당 영역", "주요 서비스", "특화 영역", "두산중공업 역할"]
        for field in multi_select_fields:
            if field in row and row[field].strip():
                values = [v.strip() for v in row[field].split(',')]
                valid_options = rules.get("select_options", {}).get(field, [])
                for value in values:
                    if value and value not in valid_options:
                        errors.append(f"행 {row_num}: '{field}' 값 '{value}'가 유효하지 않음")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _is_valid_date(self, date_str: str) -> bool:
        """날짜 형식 검증"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """URL 형식 검증"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    def validate_csv_data(self, db_name: str, csv_content: str) -> Dict:
        """CSV 데이터 검증"""
        print(f"\n🔍 {db_name} CSV 데이터 검증 시작...")
        
        lines = csv_content.strip().split('\n')
        if len(lines) < 2:
            return {"total_rows": 0, "valid_rows": 0, "invalid_rows": 0, "errors": ["CSV 데이터가 부족합니다."]}
        
        headers = [h.strip() for h in lines[0].split(',')]
        data = []
        
        for line in lines[1:]:
            cells = [cell.strip() for cell in line.split(',')]
            if len(cells) == len(headers):
                data.append(dict(zip(headers, cells)))
        
        # 각 행 검증
        validation_results = {
            "total_rows": len(data),
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": [],
            "warnings": []
        }
        
        for i, row in enumerate(data, 1):
            row_validation = self._validate_row(db_name, row, i)
            if row_validation["is_valid"]:
                validation_results["valid_rows"] += 1
            else:
                validation_results["invalid_rows"] += 1
                validation_results["errors"].extend(row_validation["errors"])
            validation_results["warnings"].extend(row_validation["warnings"])
        
        return validation_results
    
    def validate_json_data(self, db_name: str, json_content: str) -> Dict:
        """JSON 데이터 검증"""
        print(f"\n🔍 {db_name} JSON 데이터 검증 시작...")
        
        try:
            data = json.loads(json_content)
            if isinstance(data, list):
                table_data = data
            else:
                table_data = [data]
        except json.JSONDecodeError as e:
            return {
                "total_rows": 0,
                "valid_rows": 0,
                "invalid_rows": 0,
                "errors": [f"JSON 파싱 오류: {str(e)}"]
            }
        
        # 각 행 검증
        validation_results = {
            "total_rows": len(table_data),
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": [],
            "warnings": []
        }
        
        for i, row in enumerate(table_data, 1):
            row_validation = self._validate_row(db_name, row, i)
            if row_validation["is_valid"]:
                validation_results["valid_rows"] += 1
            else:
                validation_results["invalid_rows"] += 1
                validation_results["errors"].extend(row_validation["errors"])
            validation_results["warnings"].extend(row_validation["warnings"])
        
        return validation_results
    
    def generate_validation_report(self, results: Dict) -> str:
        """검증 결과 보고서 생성"""
        report = f"""
# 두산중공업 데이터 검증 결과 보고서
생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

## 📊 전체 검증 결과
"""
        
        total_valid = 0
        total_invalid = 0
        total_errors = 0
        total_warnings = 0
        
        for db_name, result in results.items():
            report += f"""
### {db_name}
- 총 레코드: {result['total_rows']}
- 유효 레코드: {result['valid_rows']}
- 무효 레코드: {result['invalid_rows']}
- 오류 수: {len(result['errors'])}
- 경고 수: {len(result['warnings'])}
"""
            total_valid += result['valid_rows']
            total_invalid += result['invalid_rows']
            total_errors += len(result['errors'])
            total_warnings += len(result['warnings'])
        
        # 오류 및 경고 상세
        if total_errors > 0:
            report += f"""
## ❌ 오류 상세
"""
            for db_name, result in results.items():
                if result['errors']:
                    report += f"\n### {db_name}\n"
                    for error in result['errors']:
                        report += f"- {error}\n"
        
        if total_warnings > 0:
            report += f"""
## ⚠️ 경고 상세
"""
            for db_name, result in results.items():
                if result['warnings']:
                    report += f"\n### {db_name}\n"
                    for warning in result['warnings']:
                        report += f"- {warning}\n"
        
        report += f"""
## 🎯 최종 결과
- 총 유효 레코드: {total_valid}개
- 총 무효 레코드: {total_invalid}개
- 총 오류: {total_errors}개
- 총 경고: {total_warnings}개
- 전체 유효성: {(total_valid / (total_valid + total_invalid)) * 100:.1f}% (총 {total_valid + total_invalid}개 중)
"""
        
        return report

def main():
    """메인 실행 함수"""
    print("🔍 두산중공업 데이터 검증 시작")
    print("=" * 50)
    
    validator = DoosanDataValidator()
    
    # 예시 데이터 검증 (실제로는 시대리, 채팀장, 고과장이 제공한 데이터 사용)
    sample_data = {
        "📊 기업 위험 프로파일 DB": """
| 리스크명 | 리스크 유형 | 발생 확률 | 영향도 | 리스크 등급 | 대응 현황 | 리스크 설명 | 관련 사업부 | 발생 확률 점수 | 영향도 점수 |
|---------|------------|----------|--------|------------|----------|------------|------------|--------------|------------|
| 해외 프로젝트 환율 리스크 | 재무 리스크 | 높음 | 높음 | 높음 | 대응 진행중 | 해외 프로젝트에서 환율 변동으로 인한 손실 위험 | 중공업,해외사업 | 4 | 4 |
"""
    }
    
    validation_results = {}
    
    for db_name, data in sample_data.items():
        result = validator.validate_markdown_table(db_name, data)
        validation_results[db_name] = result
    
    # 검증 결과 보고서 생성
    report = validator.generate_validation_report(validation_results)
    print(report)
    
    # 보고서 저장
    with open('doosan_data_validation_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 두산중공업 데이터 검증 완료")

if __name__ == "__main__":
    main() 