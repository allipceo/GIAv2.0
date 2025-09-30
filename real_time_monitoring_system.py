#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 모니터링 시스템
분석 진행 상황과 성능 지표를 실시간으로 모니터링
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading

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
NOTION_TOKEN = env_vars.get('NOTION_TOKEN', '')

class RealTimeMonitoringSystem:
    def __init__(self):
        self.notion_token = NOTION_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        self.monitoring_data = {
            'total_analyses': 0,
            'completed_analyses': 0,
            'failed_analyses': 0,
            'average_response_time': 0,
            'average_quality_score': 0,
            'last_update': datetime.now().isoformat()
        }
        self.is_monitoring = False
        self.monitoring_thread = None
        
    def create_monitoring_dashboard_db(self) -> str:
        """모니터링 대시보드용 Notion DB 생성"""
        print("📊 모니터링 대시보드용 Notion DB 생성 중...")
        
        db_data = {
            'parent': {
                'type': 'page_id',
                'page_id': '227a613d25ff800ca97de24f6eb521a8'  # GIA_작업장 1단계 페이지
            },
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': '실시간 모니터링 대시보드'
                    }
                }
            ],
            'properties': {
                '지표명': {
                    'title': {}
                },
                '현재 값': {
                    'number': {
                        'format': 'number_with_commas'
                    }
                },
                '이전 값': {
                    'number': {
                        'format': 'number_with_commas'
                    }
                },
                '변화율': {
                    'number': {
                        'format': 'percent'
                    }
                },
                '상태': {
                    'select': {
                        'options': [
                            {'name': '정상', 'color': 'green'},
                            {'name': '주의', 'color': 'yellow'},
                            {'name': '위험', 'color': 'red'}
                        ]
                    }
                },
                '업데이트 시간': {
                    'date': {}
                },
                '설명': {
                    'rich_text': {}
                }
            }
        }
        
        try:
            response = requests.post(
                'https://api.notion.com/v1/databases',
                headers=self.headers,
                json=db_data
            )
            
            if response.status_code == 200:
                result = response.json()
                db_id = result['id']
                print(f"✅ 모니터링 대시보드 DB 생성 완료: {db_id}")
                
                # DB ID를 config.env에 저장
                self.save_monitoring_db_id_to_config(db_id)
                
                return db_id
            else:
                print(f"❌ 모니터링 DB 생성 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 모니터링 DB 생성 중 오류: {str(e)}")
            return None
    
    def save_monitoring_db_id_to_config(self, db_id: str):
        """모니터링 DB ID를 config.env에 저장"""
        try:
            with open('config.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 기존 MONITORING_DASHBOARD_DB_ID 라인 찾기 및 업데이트
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('MONITORING_DASHBOARD_DB_ID='):
                    lines[i] = f'MONITORING_DASHBOARD_DB_ID={db_id}\n'
                    updated = True
                    break
            
            # 없으면 새로 추가
            if not updated:
                lines.append(f'MONITORING_DASHBOARD_DB_ID={db_id}\n')
            
            with open('config.env', 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ 모니터링 DB ID가 config.env에 저장되었습니다: {db_id}")
            
        except Exception as e:
            print(f"❌ config.env 업데이트 실패: {str(e)}")
    
    def update_monitoring_metrics(self):
        """모니터링 지표 업데이트"""
        try:
            # 분석 결과 DB에서 데이터 수집
            analysis_db_id = env_vars.get('ANALYSIS_RESULTS_DB_ID')
            if analysis_db_id:
                response = requests.post(
                    f'https://api.notion.com/v1/databases/{analysis_db_id}/query',
                    headers=self.headers,
                    json={}
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    
                    # 지표 계산
                    total_analyses = len(results)
                    completed_analyses = len([r for r in results if r.get('properties', {}).get('상태', {}).get('select', {}).get('name') == '완료'])
                    failed_analyses = len([r for r in results if r.get('properties', {}).get('상태', {}).get('select', {}).get('name') == '오류'])
                    
                    # 평균 응답 시간 계산
                    response_times = []
                    for result in results:
                        response_time = result.get('properties', {}).get('응답 속도', {}).get('number', 0)
                        if response_time > 0:
                            response_times.append(response_time)
                    
                    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                    
                    # 평균 품질 점수 계산
                    quality_scores = []
                    for result in results:
                        quality_score = result.get('properties', {}).get('분석 품질 점수', {}).get('number', 0)
                        if quality_score > 0:
                            quality_scores.append(quality_score)
                    
                    avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                    
                    # 모니터링 데이터 업데이트
                    self.monitoring_data = {
                        'total_analyses': total_analyses,
                        'completed_analyses': completed_analyses,
                        'failed_analyses': failed_analyses,
                        'average_response_time': avg_response_time,
                        'average_quality_score': avg_quality_score,
                        'last_update': datetime.now().isoformat()
                    }
                    
                    # Notion 대시보드 업데이트
                    self.update_monitoring_dashboard()
                    
        except Exception as e:
            print(f"❌ 모니터링 지표 업데이트 중 오류: {str(e)}")
    
    def update_monitoring_dashboard(self):
        """Notion 모니터링 대시보드 업데이트"""
        db_id = env_vars.get('MONITORING_DASHBOARD_DB_ID')
        if not db_id:
            return
        
        # 기존 지표 페이지들 삭제 후 새로 생성
        try:
            # 기존 페이지들 조회
            response = requests.post(
                f'https://api.notion.com/v1/databases/{db_id}/query',
                headers=self.headers,
                json={}
            )
            
            if response.status_code == 200:
                existing_pages = response.json().get('results', [])
                
                # 기존 페이지들 삭제
                for page in existing_pages:
                    page_id = page['id']
                    requests.delete(
                        f'https://api.notion.com/v1/pages/{page_id}',
                        headers=self.headers
                    )
                
                # 새로운 지표들 생성
                metrics = [
                    {
                        'name': '총 분석 수',
                        'value': self.monitoring_data['total_analyses'],
                        'status': '정상'
                    },
                    {
                        'name': '완료된 분석',
                        'value': self.monitoring_data['completed_analyses'],
                        'status': '정상'
                    },
                    {
                        'name': '실패한 분석',
                        'value': self.monitoring_data['failed_analyses'],
                        'status': '주의' if self.monitoring_data['failed_analyses'] > 0 else '정상'
                    },
                    {
                        'name': '평균 응답 시간 (초)',
                        'value': round(self.monitoring_data['average_response_time'], 2),
                        'status': '정상'
                    },
                    {
                        'name': '평균 품질 점수 (%)',
                        'value': round(self.monitoring_data['average_quality_score'], 1),
                        'status': '정상'
                    }
                ]
                
                for metric in metrics:
                    self.create_metric_page(db_id, metric)
                    
        except Exception as e:
            print(f"❌ 모니터링 대시보드 업데이트 중 오류: {str(e)}")
    
    def create_metric_page(self, db_id: str, metric: Dict):
        """지표 페이지 생성"""
        page_data = {
            'parent': {
                'database_id': db_id
            },
            'properties': {
                '지표명': {
                    'title': [
                        {
                            'text': {
                                'content': metric['name']
                            }
                        }
                    ]
                },
                '현재 값': {
                    'number': metric['value']
                },
                '상태': {
                    'select': {
                        'name': metric['status']
                    }
                },
                '업데이트 시간': {
                    'date': {
                        'start': datetime.now().isoformat()
                    }
                },
                '설명': {
                    'rich_text': [
                        {
                            'text': {
                                'content': f'마지막 업데이트: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                            }
                        }
                    ]
                }
            }
        }
        
        try:
            response = requests.post(
                'https://api.notion.com/v1/pages',
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                print(f"✅ 지표 페이지 생성 완료: {metric['name']}")
            else:
                print(f"❌ 지표 페이지 생성 실패: {metric['name']}")
                
        except Exception as e:
            print(f"❌ 지표 페이지 생성 중 오류: {str(e)}")
    
    def start_monitoring(self, interval_seconds: int = 60):
        """실시간 모니터링 시작"""
        if self.is_monitoring:
            print("⚠️ 모니터링이 이미 실행 중입니다.")
            return
        
        self.is_monitoring = True
        print(f"🚀 실시간 모니터링 시작 (업데이트 간격: {interval_seconds}초)")
        
        def monitoring_loop():
            while self.is_monitoring:
                try:
                    self.update_monitoring_metrics()
                    time.sleep(interval_seconds)
                except Exception as e:
                    print(f"❌ 모니터링 루프 오류: {str(e)}")
                    time.sleep(interval_seconds)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """실시간 모니터링 중지"""
        self.is_monitoring = False
        print("🛑 실시간 모니터링 중지")
    
    def get_monitoring_summary(self) -> Dict:
        """모니터링 요약 정보 반환"""
        return {
            'monitoring_status': '실행 중' if self.is_monitoring else '중지됨',
            'last_update': self.monitoring_data['last_update'],
            'metrics': self.monitoring_data
        }

def main():
    """메인 실행 함수"""
    print("🚀 실시간 모니터링 시스템 시작...")
    print("=" * 50)
    
    monitoring_system = RealTimeMonitoringSystem()
    
    # 1. 모니터링 대시보드 DB 생성
    db_id = monitoring_system.create_monitoring_dashboard_db()
    
    if db_id:
        # 2. 초기 모니터링 지표 업데이트
        monitoring_system.update_monitoring_metrics()
        
        # 3. 실시간 모니터링 시작 (30초 간격)
        monitoring_system.start_monitoring(30)
        
        print("✅ 실시간 모니터링 시스템 구축 완료!")
        print("📊 모니터링이 30초 간격으로 실행됩니다.")
        print("🛑 중지하려면 Ctrl+C를 누르세요.")
        
        try:
            while True:
                time.sleep(10)
                summary = monitoring_system.get_monitoring_summary()
                print(f"📈 현재 상태: {summary['monitoring_status']} | 마지막 업데이트: {summary['last_update']}")
        except KeyboardInterrupt:
            monitoring_system.stop_monitoring()
            print("\n🛑 모니터링이 중지되었습니다.")

if __name__ == "__main__":
    main() 