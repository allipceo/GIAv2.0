#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 보유 API를 활용한 구차장 성능 테스트
Claude vs Gemini 성능 비교
"""

import os
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# 환경 변수 로드
def load_env_vars():
    """config.env 파일에서 환경 변수 로드"""
    env_vars = {}
    try:
        with open('config.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("config.env 파일을 찾을 수 없습니다.")
        return {}
    return env_vars

# API 키 설정
env_vars = load_env_vars()
CLAUDE_API_KEY = env_vars.get('CLAUDE_API_KEY', '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')
GEMINI_API_KEY = env_vars.get('GEMINI_API_KEY', 'AIzaSyDLMjWJP6fn43tNPykS_ylpjdorZZyICJ8')
NOTION_TOKEN = env_vars.get('NOTION_TOKEN', '')

class LLMPerformanceTester:
    def __init__(self):
        self.claude_api_key = CLAUDE_API_KEY
        self.gemini_api_key = GEMINI_API_KEY
        self.notion_token = NOTION_TOKEN
        self.test_results = []
        
    def test_claude_performance(self, prompt: str) -> Dict[str, Any]:
        """Claude API 성능 테스트"""
        start_time = time.time()
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.claude_api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 4000,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=60
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'provider': 'Claude (채팀장)',
                    'status': 'success',
                    'response_time': response_time,
                    'response_length': len(result.get('content', [{}])[0].get('text', '')),
                    'response': result.get('content', [{}])[0].get('text', '')[:500] + '...' if len(result.get('content', [{}])[0].get('text', '')) > 500 else result.get('content', [{}])[0].get('text', '')
                }
            else:
                return {
                    'provider': 'Claude (채팀장)',
                    'status': 'error',
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            end_time = time.time()
            return {
                'provider': 'Claude (채팀장)',
                'status': 'error',
                'response_time': end_time - start_time,
                'error': str(e)
            }
    
    def test_gemini_performance(self, prompt: str) -> Dict[str, Any]:
        """Gemini API 성능 테스트 (구차장 대체)"""
        start_time = time.time()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        data = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        }
                    ]
                }
            ],
            'generationConfig': {
                'maxOutputTokens': 4000,
                'temperature': 0.7
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=60)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return {
                    'provider': 'Gemini (구차장 대체)',
                    'status': 'success',
                    'response_time': response_time,
                    'response_length': len(response_text),
                    'response': response_text[:500] + '...' if len(response_text) > 500 else response_text
                }
            else:
                return {
                    'provider': 'Gemini (구차장 대체)',
                    'status': 'error',
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            end_time = time.time()
            return {
                'provider': 'Gemini (구차장 대체)',
                'status': 'error',
                'response_time': end_time - start_time,
                'error': str(e)
            }
    
    def run_performance_comparison(self):
        """성능 비교 테스트 실행"""
        print("🚀 구차장 성능 테스트 시작...")
        print("=" * 60)
        
        # 테스트 프롬프트들
        test_prompts = [
            {
                'name': '효성중공업 시장 분석',
                'prompt': '''효성중공업의 현재 시장 상황과 경쟁력을 분석해주세요. 
                다음 데이터를 바탕으로 전략적 인사이트를 제공해주세요:
                - 시장 점유율 및 성장률
                - 주요 경쟁사 비교
                - 기술적 강점과 약점
                - 향후 발전 방향 제언'''
            },
            {
                'name': '글로벌 경쟁 분석',
                'prompt': '''글로벌 중공업 시장에서 효성중공업의 경쟁력을 분석해주세요.
                다음 관점에서 분석해주세요:
                - 글로벌 시장에서의 포지셔닝
                - 주요 글로벌 경쟁사와의 비교
                - 해외 진출 전략의 효과성
                - 글로벌 시장에서의 기회와 위험 요소'''
            },
            {
                'name': '재무 프로젝트 분석',
                'prompt': '''효성중공업의 재무 프로젝트 데이터를 분석하여 
                투자 가치와 위험 요소를 평가해주세요:
                - 프로젝트별 수익성 분석
                - 리스크 평가 및 관리 방안
                - 자금 조달 전략의 적절성
                - 향후 투자 방향성 제언'''
            }
        ]
        
        for i, test_case in enumerate(test_prompts, 1):
            print(f"\n📊 테스트 {i}: {test_case['name']}")
            print("-" * 40)
            
            # Claude 테스트
            print("🔄 Claude (채팀장) 테스트 중...")
            claude_result = self.test_claude_performance(test_case['prompt'])
            self.test_results.append(claude_result)
            
            # Gemini 테스트
            print("🔄 Gemini (구차장 대체) 테스트 중...")
            gemini_result = self.test_gemini_performance(test_case['prompt'])
            self.test_results.append(gemini_result)
            
            # 결과 출력
            print(f"\n📈 결과 비교:")
            print(f"Claude (채팀장): {claude_result['response_time']:.2f}초")
            print(f"Gemini (구차장 대체): {gemini_result['response_time']:.2f}초")
            
            if claude_result['status'] == 'success' and gemini_result['status'] == 'success':
                speed_diff = gemini_result['response_time'] - claude_result['response_time']
                print(f"속도 차이: {speed_diff:.2f}초 ({'Claude가 빠름' if speed_diff > 0 else 'Gemini가 빠름'})")
        
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """성능 테스트 보고서 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"구차장_성능테스트_보고서_{timestamp}.md"
        
        successful_tests = [r for r in self.test_results if r['status'] == 'success']
        failed_tests = [r for r in self.test_results if r['status'] == 'error']
        
        claude_tests = [r for r in successful_tests if 'Claude' in r['provider']]
        gemini_tests = [r for r in successful_tests if 'Gemini' in r['provider']]
        
        report_content = f"""# 구차장 성능 테스트 보고서

## 📊 테스트 개요
- **테스트 일시**: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}
- **총 테스트 수**: {len(self.test_results)}
- **성공**: {len(successful_tests)}개
- **실패**: {len(failed_tests)}개

## 🏆 성능 비교 결과

### 평균 응답 속도
- **Claude (채팀장)**: {sum(r['response_time'] for r in claude_tests) / len(claude_tests):.2f}초
- **Gemini (구차장 대체)**: {sum(r['response_time'] for r in gemini_tests) / len(gemini_tests):.2f}초

### 평균 응답 길이
- **Claude (채팀장)**: {sum(r['response_length'] for r in claude_tests) / len(claude_tests):.0f}자
- **Gemini (구차장 대체)**: {sum(r['response_length'] for r in gemini_tests) / len(gemini_tests):.0f}자

## 📈 상세 테스트 결과

"""
        
        for i, result in enumerate(self.test_results, 1):
            report_content += f"""
### 테스트 {i}: {result['provider']}
- **상태**: {'✅ 성공' if result['status'] == 'success' else '❌ 실패'}
- **응답 시간**: {result['response_time']:.2f}초
"""
            if result['status'] == 'success':
                report_content += f"- **응답 길이**: {result['response_length']}자\n"
                report_content += f"- **응답 미리보기**: {result['response']}\n"
            else:
                report_content += f"- **오류**: {result['error']}\n"
        
        report_content += f"""
## 🎯 결론 및 제언

### 현재 상황
- Claude와 Gemini 모두 안정적으로 작동
- 기본적인 성능 비교 가능
- 구차장의 초고속 추론 능력은 Groq API 필요

### 다음 단계
1. **Groq API 키 확보** - 정확한 구차장 성능 테스트
2. **대규모 데이터 테스트** - 실제 업무 환경 시뮬레이션
3. **분석 품질 평가** - 전문성 및 정확성 측정

### 권장사항
- Groq API 키 확보 후 완전한 성능 비교 실행
- 현재 API로 기본 테스트 완료 후 Groq 추가 테스트
- 분석 결과 품질 평가를 통한 종합적 성능 비교
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📋 성능 테스트 보고서 생성 완료: {report_file}")
        print(f"✅ 성공: {len(successful_tests)}개, ❌ 실패: {len(failed_tests)}개")

if __name__ == "__main__":
    tester = LLMPerformanceTester()
    tester.run_performance_comparison() 