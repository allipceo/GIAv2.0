#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
분석 결과 저장 시스템
나반장과 노팀장의 분석 결과를 Notion DB에 체계적으로 저장
"""

import os
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
NOTION_TOKEN = env_vars.get('NOTION_TOKEN', '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')

class AnalysisResultStorageSystem:
    def __init__(self):
        self.notion_token = NOTION_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
    def create_analysis_results_db(self) -> str:
        """분석 결과 저장용 Notion DB 생성"""
        print("📊 분석 결과 저장용 Notion DB 생성 중...")
        
        db_data = {
            'parent': {
                'type': 'page_id',
                'page_id': '227a613d25ff800ca97de24f6eb521a8'  # GIA_작업장 1단계 페이지
            },
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': '분석 결과 저장소'
                    }
                }
            ],
            'properties': {
                '분석 제목': {
                    'title': {}
                },
                '분석자': {
                    'select': {
                        'options': [
                            {'name': '나반장', 'color': 'blue'},
                            {'name': '노팀장', 'color': 'green'},
                            {'name': '채팀장', 'color': 'yellow'},
                            {'name': '구차장', 'color': 'red'}
                        ]
                    }
                },
                '분석 유형': {
                    'select': {
                        'options': [
                            {'name': '시장 분석', 'color': 'blue'},
                            {'name': '경쟁 분석', 'color': 'green'},
                            {'name': '재무 분석', 'color': 'yellow'},
                            {'name': '전략 분석', 'color': 'red'},
                            {'name': '성능 테스트', 'color': 'purple'}
                        ]
                    }
                },
                '분석 일시': {
                    'date': {}
                },
                '응답 속도': {
                    'number': {
                        'format': 'number_with_commas'
                    }
                },
                '응답 길이': {
                    'number': {
                        'format': 'number_with_commas'
                    }
                },
                '분석 품질 점수': {
                    'number': {
                        'format': 'percent'
                    }
                },
                '상태': {
                    'select': {
                        'options': [
                            {'name': '진행 중', 'color': 'yellow'},
                            {'name': '완료', 'color': 'green'},
                            {'name': '오류', 'color': 'red'}
                        ]
                    }
                },
                '태그': {
                    'multi_select': {
                        'options': [
                            {'name': '효성중공업', 'color': 'blue'},
                            {'name': '글로벌', 'color': 'green'},
                            {'name': '재무', 'color': 'yellow'},
                            {'name': '성능', 'color': 'red'},
                            {'name': '전략', 'color': 'purple'}
                        ]
                    }
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
                print(f"✅ 분석 결과 저장용 DB 생성 완료: {db_id}")
                
                # DB ID를 config.env에 저장
                self.save_db_id_to_config(db_id)
                
                return db_id
            else:
                print(f"❌ DB 생성 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ DB 생성 중 오류: {str(e)}")
            return None
    
    def save_db_id_to_config(self, db_id: str):
        """DB ID를 config.env에 저장"""
        try:
            with open('config.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 기존 ANALYSIS_RESULTS_DB_ID 라인 찾기 및 업데이트
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ANALYSIS_RESULTS_DB_ID='):
                    lines[i] = f'ANALYSIS_RESULTS_DB_ID={db_id}\n'
                    updated = True
                    break
            
            # 없으면 새로 추가
            if not updated:
                lines.append(f'ANALYSIS_RESULTS_DB_ID={db_id}\n')
            
            with open('config.env', 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ DB ID가 config.env에 저장되었습니다: {db_id}")
            
        except Exception as e:
            print(f"❌ config.env 업데이트 실패: {str(e)}")
    
    def store_analysis_result(self, analysis_data: Dict[str, Any]) -> bool:
        """분석 결과를 Notion DB에 저장"""
        db_id = env_vars.get('ANALYSIS_RESULTS_DB_ID')
        if not db_id:
            print("❌ 분석 결과 DB ID가 설정되지 않았습니다.")
            return False
        
        print(f"📝 분석 결과 저장 중: {analysis_data.get('title', 'Unknown')}")
        
        # 날짜 형식 변환
        analysis_date = analysis_data.get('analysis_date', datetime.now().isoformat())
        if isinstance(analysis_date, str):
            analysis_date = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
        
        page_data = {
            'parent': {
                'database_id': db_id
            },
            'properties': {
                '분석 제목': {
                    'title': [
                        {
                            'text': {
                                'content': analysis_data.get('title', '분석 결과')
                            }
                        }
                    ]
                },
                '분석자': {
                    'select': {
                        'name': analysis_data.get('analyst', '나반장')
                    }
                },
                '분석 유형': {
                    'select': {
                        'name': analysis_data.get('analysis_type', '시장 분석')
                    }
                },
                '분석 일시': {
                    'date': {
                        'start': analysis_date.isoformat()
                    }
                },
                '응답 속도': {
                    'number': analysis_data.get('response_time', 0)
                },
                '응답 길이': {
                    'number': analysis_data.get('response_length', 0)
                },
                '분석 품질 점수': {
                    'number': analysis_data.get('quality_score', 0)
                },
                '상태': {
                    'select': {
                        'name': analysis_data.get('status', '완료')
                    }
                },
                '태그': {
                    'multi_select': [
                        {'name': tag} for tag in analysis_data.get('tags', [])
                    ]
                }
            },
            'children': [
                {
                    'object': 'block',
                    'type': 'heading_1',
                    'heading_1': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': '분석 요약'
                                }
                            }
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': analysis_data.get('summary', '분석 요약이 없습니다.')
                                }
                            }
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': '상세 분석'
                                }
                            }
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': analysis_data.get('detailed_analysis', '상세 분석 내용이 없습니다.')
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                'https://api.notion.com/v1/pages',
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                print(f"✅ 분석 결과 저장 완료: {analysis_data.get('title', 'Unknown')}")
                return True
            else:
                print(f"❌ 분석 결과 저장 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 분석 결과 저장 중 오류: {str(e)}")
            return False
    
    def get_analysis_results(self, filters: Dict = None) -> List[Dict]:
        """분석 결과 조회"""
        db_id = env_vars.get('ANALYSIS_RESULTS_DB_ID')
        if not db_id:
            print("❌ 분석 결과 DB ID가 설정되지 않았습니다.")
            return []
        
        query_data = {
            'database_id': db_id,
            'sorts': [
                {
                    'property': '분석 일시',
                    'direction': 'descending'
                }
            ]
        }
        
        if filters:
            query_data['filter'] = filters
        
        try:
            response = requests.post(
                'https://api.notion.com/v1/databases/' + db_id + '/query',
                headers=self.headers,
                json=query_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('results', [])
            else:
                print(f"❌ 분석 결과 조회 실패: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 분석 결과 조회 중 오류: {str(e)}")
            return []

def main():
    """메인 실행 함수"""
    print("🚀 분석 결과 저장 시스템 시작...")
    print("=" * 50)
    
    storage_system = AnalysisResultStorageSystem()
    
    # 1. 분석 결과 저장용 DB 생성
    db_id = storage_system.create_analysis_results_db()
    
    if db_id:
        # 2. 샘플 분석 결과 저장 테스트
        sample_analysis = {
            'title': '효성중공업 시장 분석 결과',
            'analyst': '나반장',
            'analysis_type': '시장 분석',
            'analysis_date': datetime.now().isoformat(),
            'response_time': 2.5,
            'response_length': 1500,
            'quality_score': 85,
            'status': '완료',
            'tags': ['효성중공업', '시장'],
            'summary': '효성중공업의 현재 시장 상황과 경쟁력을 종합적으로 분석한 결과입니다.',
            'detailed_analysis': '상세한 분석 내용이 여기에 포함됩니다...'
        }
        
        success = storage_system.store_analysis_result(sample_analysis)
        
        if success:
            print("✅ 샘플 분석 결과 저장 테스트 완료")
            
            # 3. 저장된 결과 조회 테스트
            results = storage_system.get_analysis_results()
            print(f"📊 저장된 분석 결과 수: {len(results)}개")
        else:
            print("❌ 샘플 분석 결과 저장 실패")
    
    print("\n📋 분석 결과 저장 시스템 구축 완료!")

if __name__ == "__main__":
    main() 