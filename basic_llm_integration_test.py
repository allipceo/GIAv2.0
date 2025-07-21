#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기본 LLM 연동 테스트 스크립트
Phase 8.0-A: 30분 내 기본 인프라 구축
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

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

class BasicLLMIntegrationTest:
    def __init__(self):
        # 환경 변수 로드
        env_vars = load_env_from_file()
        
        self.notion_token = env_vars.get('NOTION_TOKEN')
        self.notion_database_ids = {
            'key_personnel': env_vars.get('KEY_PERSONNEL_DB_ID'),
            'government_policy': env_vars.get('GOVERNMENT_POLICY_DB_ID'),
            'risk_profile': env_vars.get('RISK_PROFILE_DB_ID'),
            'renewable_energy': env_vars.get('RENEWABLE_ENERGY_DB_ID'),
            'financial_project': env_vars.get('FINANCIAL_PROJECT_DB_ID'),
            'global_insurance': env_vars.get('GLOBAL_INSURANCE_DB_ID')
        }
        self.test_results = {}
        
    def test_notion_api_connection(self) -> bool:
        """노션 API 연결 테스트"""
        try:
            headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            # 간단한 데이터베이스 조회 테스트
            for db_name, db_id in self.notion_database_ids.items():
                if db_id:
                    response = requests.get(
                        f'https://api.notion.com/v1/databases/{db_id}',
                        headers=headers
                    )
                    if response.status_code == 200:
                        print(f"✅ {db_name} DB 연결 성공")
                        self.test_results[f'{db_name}_connection'] = True
                    else:
                        print(f"❌ {db_name} DB 연결 실패: {response.status_code}")
                        self.test_results[f'{db_name}_connection'] = False
                        
            return True
        except Exception as e:
            print(f"❌ 노션 API 연결 오류: {e}")
            return False
    
    def extract_sample_data(self, db_name: str, db_id: str) -> List[Dict]:
        """샘플 데이터 추출"""
        try:
            headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'https://api.notion.com/v1/databases/{db_id}/query',
                headers=headers,
                json={'page_size': 3}  # 샘플 3개만 추출
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"❌ {db_name} 데이터 추출 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ {db_name} 데이터 추출 오류: {e}")
            return []
    
    def convert_to_llm_input(self, notion_data: List[Dict], db_name: str) -> str:
        """노션 데이터를 LLM 입력 형식으로 변환"""
        try:
            llm_input = f"# {db_name} 데이터 분석\n\n"
            
            for i, page in enumerate(notion_data, 1):
                properties = page.get('properties', {})
                llm_input += f"## 항목 {i}\n"
                
                for prop_name, prop_data in properties.items():
                    if prop_data.get('type') == 'title' and prop_data.get('title'):
                        llm_input += f"- 제목: {prop_data['title'][0]['plain_text']}\n"
                    elif prop_data.get('type') == 'rich_text' and prop_data.get('rich_text'):
                        llm_input += f"- 내용: {prop_data['rich_text'][0]['plain_text']}\n"
                    elif prop_data.get('type') == 'select' and prop_data.get('select'):
                        llm_input += f"- 분류: {prop_data['select']['name']}\n"
                    elif prop_data.get('type') == 'url' and prop_data.get('url'):
                        llm_input += f"- 링크: {prop_data['url']}\n"
                
                llm_input += "\n"
            
            return llm_input
            
        except Exception as e:
            print(f"❌ LLM 입력 형식 변환 오류: {e}")
            return ""
    
    def test_llm_analysis(self, llm_input: str, analysis_type: str) -> str:
        """LLM 분석 테스트 (시뮬레이션)"""
        try:
            # 실제 LLM API 호출 대신 시뮬레이션
            analysis_prompt = f"""
다음 데이터를 바탕으로 {analysis_type} 분석을 수행해주세요:

{llm_input}

분석 결과를 다음 형식으로 제공해주세요:
1. 주요 발견사항
2. 핵심 인사이트
3. 전략적 제언
"""
            
            # 시뮬레이션된 분석 결과
            simulated_result = f"""
# {analysis_type} 분석 결과

## 주요 발견사항
- 데이터 품질: 양호
- 분석 가능 항목: {len(llm_input.split('##')) - 1}개
- 데이터 완성도: 85%

## 핵심 인사이트
- 효성중공업의 신재생에너지 진출 가속화
- 정부 정책과의 시너지 효과 확인
- 해외 시장 진출 확대 추세

## 전략적 제언
- 신재생에너지 포트폴리오 다각화
- 정부 정책 변화에 대한 선제적 대응
- 글로벌 파트너십 강화
"""
            
            return simulated_result
            
        except Exception as e:
            print(f"❌ LLM 분석 테스트 오류: {e}")
            return ""
    
    def test_result_storage(self, analysis_result: str, db_name: str) -> bool:
        """분석 결과 저장 테스트"""
        try:
            # 결과를 마크다운 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_result_{db_name}_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(analysis_result)
            
            print(f"✅ 분석 결과 저장 성공: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 분석 결과 저장 오류: {e}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        print("🚀 Phase 8.0-A: 기본 LLM 연동 테스트 시작")
        print("=" * 50)
        
        # 1. 노션 API 연결 테스트
        print("\n1️⃣ 노션 API 연결 테스트")
        connection_success = self.test_notion_api_connection()
        
        # 2. 샘플 데이터 추출 및 LLM 입력 변환 테스트
        print("\n2️⃣ 데이터 추출 및 변환 테스트")
        for db_name, db_id in self.notion_database_ids.items():
            if db_id and self.test_results.get(f'{db_name}_connection'):
                print(f"\n📊 {db_name} 데이터 처리 중...")
                
                # 데이터 추출
                sample_data = self.extract_sample_data(db_name, db_id)
                if sample_data:
                    # LLM 입력 형식 변환
                    llm_input = self.convert_to_llm_input(sample_data, db_name)
                    if llm_input:
                        # LLM 분석 테스트
                        analysis_result = self.test_llm_analysis(llm_input, f"{db_name} 분석")
                        if analysis_result:
                            # 결과 저장 테스트
                            storage_success = self.test_result_storage(analysis_result, db_name)
                            self.test_results[f'{db_name}_full_pipeline'] = storage_success
        
        # 3. 테스트 결과 요약
        print("\n3️⃣ 테스트 결과 요약")
        print("=" * 50)
        
        success_count = sum(1 for result in self.test_results.values() if result)
        total_count = len(self.test_results)
        
        print(f"✅ 성공: {success_count}/{total_count}")
        print(f"📊 성공률: {(success_count/total_count)*100:.1f}%")
        
        return {
            'success_rate': (success_count/total_count)*100,
            'test_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # 환경 변수 확인
    env_vars = load_env_from_file()
    required_env_vars = ['NOTION_TOKEN']
    missing_vars = [var for var in required_env_vars if not env_vars.get(var)]
    
    if missing_vars:
        print(f"❌ 필수 환경 변수 누락: {missing_vars}")
        print("config.env 파일을 확인한 후 다시 실행해주세요.")
    else:
        tester = BasicLLMIntegrationTest()
        result = tester.run_comprehensive_test()
        
        # 결과를 JSON 파일로 저장
        with open('llm_integration_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 테스트 결과 저장: llm_integration_test_result.json") 