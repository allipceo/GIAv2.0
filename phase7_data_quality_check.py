#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 7 데이터 품질 검증 스크립트
Phase 8.0-A: 30분 내 기본 인프라 구축
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple

def load_env_from_file():
    """config.env 파일에서 환경 변수 로드"""
    env_vars = {}
    try:
        with open('config.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        return env_vars
    except FileNotFoundError:
        print("❌ config.env 파일을 찾을 수 없습니다.")
        return {}

class Phase7DataQualityChecker:
    def __init__(self):
        # 환경 변수 로드
        env_vars = load_env_from_file()
        
        self.notion_token = env_vars.get('NOTION_TOKEN')
        self.database_ids = {
            'key_personnel': env_vars.get('KEY_PERSONNEL_DB_ID'),
            'government_policy': env_vars.get('GOVERNMENT_POLICY_DB_ID'),
            'risk_profile': env_vars.get('RISK_PROFILE_DB_ID'),
            'renewable_energy': env_vars.get('RENEWABLE_ENERGY_DB_ID'),
            'financial_project': env_vars.get('FINANCIAL_PROJECT_DB_ID'),
            'global_insurance': env_vars.get('GLOBAL_INSURANCE_DB_ID')
        }
        
        # 각 DB별 필수 필드 정의
        self.required_fields = {
            'key_personnel': ['이름', '직책', '회사', '경력'],
            'government_policy': ['정책명', '발표일', '주요내용', '영향도'],
            'risk_profile': ['위험유형', '위험등급', '영향도', '대응방안'],
            'renewable_energy': ['프로젝트명', '위치', '용량', '상태'],
            'financial_project': ['프로젝트명', '투자금액', '수익률', '기간'],
            'global_insurance': ['회사명', '시장점유율', '주요서비스', '경쟁력']
        }
        
        # 분석 주제별 매핑
        self.analysis_topics = {
            '우태희_정책_시너지': ['key_personnel', 'government_policy'],
            '리스크_보험_니즈': ['risk_profile', 'renewable_energy'],
            '글로벌_경쟁_분석': ['global_insurance', 'financial_project']
        }
        
        self.quality_results = {}
    
    def get_database_schema(self, db_id: str) -> Dict:
        """데이터베이스 스키마 조회"""
        try:
            headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'https://api.notion.com/v1/databases/{db_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('properties', {})
            else:
                print(f"❌ 스키마 조회 실패: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ 스키마 조회 오류: {e}")
            return {}
    
    def get_database_content(self, db_id: str, max_pages: int = 10) -> List[Dict]:
        """데이터베이스 내용 조회"""
        try:
            headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'https://api.notion.com/v1/databases/{db_id}/query',
                headers=headers,
                json={'page_size': max_pages}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"❌ 데이터 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 데이터 조회 오류: {e}")
            return []
    
    def check_field_completeness(self, db_name: str, content: List[Dict]) -> Dict[str, Any]:
        """필드 완성도 검증"""
        try:
            schema = self.get_database_schema(self.database_ids[db_name])
            required_fields = self.required_fields.get(db_name, [])
            
            field_stats = {}
            total_pages = len(content)
            
            for field_name in required_fields:
                # 스키마에서 실제 필드명 찾기
                actual_field_name = None
                for schema_field, schema_info in schema.items():
                    if field_name.lower() in schema_field.lower() or field_name.lower() in schema_info.get('name', '').lower():
                        actual_field_name = schema_field
                        break
                
                if actual_field_name:
                    completed_pages = 0
                    for page in content:
                        properties = page.get('properties', {})
                        field_data = properties.get(actual_field_name, {})
                        
                        # 필드에 데이터가 있는지 확인
                        has_data = False
                        if field_data.get('type') == 'title' and field_data.get('title'):
                            has_data = True
                        elif field_data.get('type') == 'rich_text' and field_data.get('rich_text'):
                            has_data = True
                        elif field_data.get('type') == 'select' and field_data.get('select'):
                            has_data = True
                        elif field_data.get('type') == 'url' and field_data.get('url'):
                            has_data = True
                        elif field_data.get('type') == 'number' and field_data.get('number') is not None:
                            has_data = True
                        elif field_data.get('type') == 'date' and field_data.get('date'):
                            has_data = True
                        
                        if has_data:
                            completed_pages += 1
                    
                    completion_rate = (completed_pages / total_pages) * 100 if total_pages > 0 else 0
                    field_stats[field_name] = {
                        'completion_rate': completion_rate,
                        'completed_pages': completed_pages,
                        'total_pages': total_pages
                    }
                else:
                    field_stats[field_name] = {
                        'completion_rate': 0,
                        'completed_pages': 0,
                        'total_pages': total_pages,
                        'error': '필드명 매칭 실패'
                    }
            
            return field_stats
            
        except Exception as e:
            print(f"❌ 필드 완성도 검증 오류: {e}")
            return {}
    
    def check_data_quality(self, db_name: str, content: List[Dict]) -> Dict[str, Any]:
        """데이터 품질 검증"""
        try:
            quality_metrics = {
                'total_pages': len(content),
                'data_completeness': 0,
                'data_consistency': 0,
                'data_relevance': 0,
                'overall_quality_score': 0
            }
            
            if not content:
                return quality_metrics
            
            # 데이터 완성도 검증
            field_completeness = self.check_field_completeness(db_name, content)
            if field_completeness:
                total_completion = sum(field['completion_rate'] for field in field_completeness.values() if 'completion_rate' in field)
                avg_completion = total_completion / len(field_completeness)
                quality_metrics['data_completeness'] = avg_completion
            
            # 데이터 일관성 검증 (간단한 검증)
            consistency_score = 0
            if len(content) > 1:
                # 첫 번째 페이지와 나머지 페이지들의 구조 비교
                first_page_props = set(content[0].get('properties', {}).keys())
                consistent_pages = 0
                
                for page in content[1:]:
                    page_props = set(page.get('properties', {}).keys())
                    if first_page_props == page_props:
                        consistent_pages += 1
                
                consistency_score = (consistent_pages / (len(content) - 1)) * 100
                quality_metrics['data_consistency'] = consistency_score
            
            # 데이터 관련성 검증 (키워드 기반)
            relevance_keywords = {
                'key_personnel': ['효성', '우태희', '대표', 'CEO'],
                'government_policy': ['정책', '정부', '이재명', '신재생'],
                'risk_profile': ['위험', '리스크', '보험', '안전'],
                'renewable_energy': ['태양광', '풍력', '신재생', '에너지'],
                'financial_project': ['투자', '프로젝트', '수익', '금액'],
                'global_insurance': ['보험', '중개', '글로벌', 'Marsh']
            }
            
            keywords = relevance_keywords.get(db_name, [])
            relevant_pages = 0
            
            for page in content:
                page_text = json.dumps(page, ensure_ascii=False).lower()
                if any(keyword.lower() in page_text for keyword in keywords):
                    relevant_pages += 1
            
            relevance_score = (relevant_pages / len(content)) * 100 if content else 0
            quality_metrics['data_relevance'] = relevance_score
            
            # 전체 품질 점수 계산
            overall_score = (
                quality_metrics['data_completeness'] * 0.4 +
                quality_metrics['data_consistency'] * 0.3 +
                quality_metrics['data_relevance'] * 0.3
            )
            quality_metrics['overall_quality_score'] = overall_score
            
            return quality_metrics
            
        except Exception as e:
            print(f"❌ 데이터 품질 검증 오류: {e}")
            return {}
    
    def check_analysis_readiness(self, topic_name: str, db_names: List[str]) -> Dict[str, Any]:
        """분석 준비도 검증"""
        try:
            readiness_score = 0
            available_data = {}
            missing_data = []
            
            for db_name in db_names:
                db_id = self.database_ids.get(db_name)
                if db_id:
                    content = self.get_database_content(db_id)
                    quality = self.check_data_quality(db_name, content)
                    
                    if quality.get('overall_quality_score', 0) >= 70:  # 70% 이상이면 분석 가능
                        available_data[db_name] = quality
                        readiness_score += 50  # 각 DB당 50점
                    else:
                        missing_data.append({
                            'database': db_name,
                            'quality_score': quality.get('overall_quality_score', 0),
                            'issues': self.identify_quality_issues(quality)
                        })
            
            return {
                'topic_name': topic_name,
                'readiness_score': readiness_score,
                'available_databases': list(available_data.keys()),
                'missing_data': missing_data,
                'recommendation': self.get_analysis_recommendation(readiness_score, missing_data)
            }
            
        except Exception as e:
            print(f"❌ 분석 준비도 검증 오류: {e}")
            return {}
    
    def identify_quality_issues(self, quality_metrics: Dict) -> List[str]:
        """품질 이슈 식별"""
        issues = []
        
        if quality_metrics.get('data_completeness', 0) < 70:
            issues.append("데이터 완성도 부족")
        
        if quality_metrics.get('data_consistency', 0) < 70:
            issues.append("데이터 일관성 문제")
        
        if quality_metrics.get('data_relevance', 0) < 70:
            issues.append("데이터 관련성 부족")
        
        return issues
    
    def get_analysis_recommendation(self, readiness_score: float, missing_data: List) -> str:
        """분석 권장사항 생성"""
        if readiness_score >= 100:
            return "✅ 분석 준비 완료 - 즉시 분석 시작 가능"
        elif readiness_score >= 50:
            return "⚠️ 부분적 분석 가능 - 일부 데이터 보완 필요"
        else:
            return "❌ 분석 준비 부족 - 데이터 보완 후 재검토 필요"
    
    def run_comprehensive_quality_check(self) -> Dict[str, Any]:
        """종합 품질 검증 실행"""
        print("🔍 Phase 7 데이터 품질 종합 검증 시작")
        print("=" * 50)
        
        overall_results = {
            'timestamp': datetime.now().isoformat(),
            'database_quality': {},
            'analysis_readiness': {},
            'recommendations': []
        }
        
        # 1. 각 DB별 품질 검증
        print("\n1️⃣ 데이터베이스별 품질 검증")
        for db_name, db_id in self.database_ids.items():
            if db_id:
                print(f"\n📊 {db_name} DB 품질 검증 중...")
                
                content = self.get_database_content(db_id)
                quality = self.check_data_quality(db_name, content)
                
                overall_results['database_quality'][db_name] = quality
                
                print(f"   - 전체 품질 점수: {quality.get('overall_quality_score', 0):.1f}%")
                print(f"   - 데이터 완성도: {quality.get('data_completeness', 0):.1f}%")
                print(f"   - 데이터 일관성: {quality.get('data_consistency', 0):.1f}%")
                print(f"   - 데이터 관련성: {quality.get('data_relevance', 0):.1f}%")
        
        # 2. 분석 주제별 준비도 검증
        print("\n2️⃣ 분석 주제별 준비도 검증")
        for topic_name, db_names in self.analysis_topics.items():
            print(f"\n🎯 {topic_name} 분석 준비도 검증 중...")
            
            readiness = self.check_analysis_readiness(topic_name, db_names)
            overall_results['analysis_readiness'][topic_name] = readiness
            
            print(f"   - 준비도 점수: {readiness.get('readiness_score', 0)}/100")
            print(f"   - 사용 가능 DB: {', '.join(readiness.get('available_databases', []))}")
            print(f"   - 권장사항: {readiness.get('recommendation', 'N/A')}")
        
        # 3. 종합 권장사항 생성
        print("\n3️⃣ 종합 권장사항")
        print("=" * 50)
        
        total_quality_score = sum(
            quality.get('overall_quality_score', 0) 
            for quality in overall_results['database_quality'].values()
        ) / len(overall_results['database_quality']) if overall_results['database_quality'] else 0
        
        if total_quality_score >= 80:
            overall_results['recommendations'].append("✅ 전체적으로 우수한 데이터 품질 - Phase 8 분석 즉시 시작 가능")
        elif total_quality_score >= 60:
            overall_results['recommendations'].append("⚠️ 보통 수준의 데이터 품질 - 일부 보완 후 분석 시작 권장")
        else:
            overall_results['recommendations'].append("❌ 데이터 품질 개선 필요 - 보완 후 재검토 권장")
        
        for recommendation in overall_results['recommendations']:
            print(f"   {recommendation}")
        
        # 결과를 JSON 파일로 저장
        with open('phase7_data_quality_report.json', 'w', encoding='utf-8') as f:
            json.dump(overall_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 품질 검증 보고서 저장: phase7_data_quality_report.json")
        
        return overall_results

if __name__ == "__main__":
    # 환경 변수 확인
    env_vars = load_env_from_file()
    required_env_vars = ['NOTION_TOKEN']
    missing_vars = [var for var in required_env_vars if not env_vars.get(var)]
    
    if missing_vars:
        print(f"❌ 필수 환경 변수 누락: {missing_vars}")
        print("config.env 파일을 확인한 후 다시 실행해주세요.")
    else:
        checker = Phase7DataQualityChecker()
        result = checker.run_comprehensive_quality_check() 