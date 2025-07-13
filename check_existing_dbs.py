#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 DB 구조 확인 스크립트
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: 조대표님의 기존 프로젝트, 태스크, TODO DB 구조 파악
"""

import json
import logging
from typing import Dict, List
from notion_client import Client
from mvp_config import APIConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/existing_db_check.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ExistingDBChecker:
    """기존 DB 구조 확인 클래스"""
    
    def __init__(self):
        self.notion = Client(auth=APIConfig.NOTION_API_TOKEN)
        self.dbs = {
            "프로젝트": APIConfig.NOTION_PROJECT_DATABASE_ID,
            "태스크": APIConfig.NOTION_TASK_DATABASE_ID,
            "TODO": APIConfig.NOTION_TODO_DATABASE_ID
        }
    
    def check_database_structure(self, db_name: str, db_id: str) -> Dict:
        """DB 구조 확인"""
        try:
            logging.info(f"📊 {db_name} DB 구조 확인 중... ({db_id})")
            
            # DB 정보 가져오기
            db_info = self.notion.databases.retrieve(database_id=db_id)
            
            # 속성 정보 추출
            properties = db_info.get('properties', {})
            
            structure = {
                "db_name": db_name,
                "db_id": db_id,
                "title": db_info.get('title', [{}])[0].get('plain_text', ''),
                "properties": {},
                "property_count": len(properties)
            }
            
            # 각 속성의 세부 정보 추출
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get('type', 'unknown')
                
                structure["properties"][prop_name] = {
                    "type": prop_type,
                    "id": prop_info.get('id', '')
                }
                
                # 선택 타입의 경우 옵션 정보 추가
                if prop_type == 'select':
                    options = prop_info.get('select', {}).get('options', [])
                    structure["properties"][prop_name]["options"] = [
                        option.get('name', '') for option in options
                    ]
                elif prop_type == 'multi_select':
                    options = prop_info.get('multi_select', {}).get('options', [])
                    structure["properties"][prop_name]["options"] = [
                        option.get('name', '') for option in options
                    ]
                elif prop_type == 'relation':
                    relation_id = prop_info.get('relation', {}).get('database_id', '')
                    structure["properties"][prop_name]["relation_db_id"] = relation_id
            
            logging.info(f"✅ {db_name} DB 구조 확인 완료 ({len(properties)}개 속성)")
            return structure
            
        except Exception as e:
            logging.error(f"❌ {db_name} DB 구조 확인 실패: {str(e)}")
            return {
                "db_name": db_name,
                "db_id": db_id,
                "error": str(e)
            }
    
    def get_sample_data(self, db_name: str, db_id: str, limit: int = 3) -> List[Dict]:
        """샘플 데이터 가져오기"""
        try:
            logging.info(f"📋 {db_name} DB 샘플 데이터 가져오기 중...")
            
            # 페이지 목록 가져오기
            response = self.notion.databases.query(
                database_id=db_id,
                page_size=limit
            )
            
            sample_data = []
            for page in response.get('results', []):
                page_data = {
                    "page_id": page.get('id', ''),
                    "properties": {}
                }
                
                # 각 속성의 값 추출
                for prop_name, prop_data in page.get('properties', {}).items():
                    prop_type = prop_data.get('type', 'unknown')
                    
                    if prop_type == 'title':
                        title_list = prop_data.get('title', [])
                        page_data["properties"][prop_name] = title_list[0].get('plain_text', '') if title_list else ''
                    elif prop_type == 'rich_text':
                        text_list = prop_data.get('rich_text', [])
                        page_data["properties"][prop_name] = text_list[0].get('plain_text', '') if text_list else ''
                    elif prop_type == 'select':
                        select_data = prop_data.get('select', {})
                        page_data["properties"][prop_name] = select_data.get('name', '') if select_data else ''
                    elif prop_type == 'multi_select':
                        multi_select_data = prop_data.get('multi_select', [])
                        page_data["properties"][prop_name] = [item.get('name', '') for item in multi_select_data]
                    elif prop_type == 'date':
                        date_data = prop_data.get('date', {})
                        page_data["properties"][prop_name] = date_data.get('start', '') if date_data else ''
                    elif prop_type == 'checkbox':
                        page_data["properties"][prop_name] = prop_data.get('checkbox', False)
                    elif prop_type == 'relation':
                        relation_data = prop_data.get('relation', [])
                        page_data["properties"][prop_name] = [item.get('id', '') for item in relation_data]
                    elif prop_type == 'rollup':
                        rollup_data = prop_data.get('rollup', {})
                        page_data["properties"][prop_name] = rollup_data.get('type', 'unknown')
                    else:
                        page_data["properties"][prop_name] = f"[{prop_type}]"
                
                sample_data.append(page_data)
            
            logging.info(f"✅ {db_name} DB 샘플 데이터 {len(sample_data)}건 확인 완료")
            return sample_data
            
        except Exception as e:
            logging.error(f"❌ {db_name} DB 샘플 데이터 가져오기 실패: {str(e)}")
            return []
    
    def run_comprehensive_check(self) -> Dict:
        """모든 DB 종합 검사"""
        logging.info("🔍 조대표님 기존 DB 종합 검사 시작")
        
        results = {
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                name='', level=0, pathname='', lineno=0, msg='', args=(), exc_info=None
            )),
            "databases": {},
            "summary": {
                "total_databases": len(self.dbs),
                "successful_checks": 0,
                "failed_checks": 0
            }
        }
        
        for db_name, db_id in self.dbs.items():
            logging.info(f"\n--- {db_name} DB 검사 ---")
            
            # 구조 확인
            structure = self.check_database_structure(db_name, db_id)
            
            # 샘플 데이터 확인
            sample_data = self.get_sample_data(db_name, db_id)
            
            results["databases"][db_name] = {
                "structure": structure,
                "sample_data": sample_data
            }
            
            if "error" in structure:
                results["summary"]["failed_checks"] += 1
            else:
                results["summary"]["successful_checks"] += 1
        
        # 결과 저장
        with open('existing_db_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logging.info(f"\n🎯 기존 DB 검사 완료:")
        logging.info(f"   - 성공: {results['summary']['successful_checks']}개")
        logging.info(f"   - 실패: {results['summary']['failed_checks']}개")
        logging.info(f"   - 결과 저장: existing_db_analysis.json")
        
        return results
    
    def analyze_relationship_opportunities(self, results: Dict) -> Dict:
        """관계형 연결 가능성 분석"""
        logging.info("🔗 관계형 연결 가능성 분석 중...")
        
        # GIA 시스템 DB 정보
        gia_dbs = {
            "뉴스정보": APIConfig.NOTION_NEWS_DATABASE_ID,
            "입찰낙찰공고": APIConfig.NOTION_BID_DATABASE_ID
        }
        
        analysis = {
            "relationship_opportunities": [],
            "rollup_opportunities": [],
            "field_mapping_suggestions": {}
        }
        
        # 각 기존 DB별로 GIA 시스템과의 연결 가능성 분석
        for db_name, db_data in results["databases"].items():
            if "error" in db_data["structure"]:
                continue
                
            properties = db_data["structure"]["properties"]
            
            # 관계형 속성 추가 가능성
            analysis["relationship_opportunities"].append({
                "target_db": db_name,
                "suggested_relations": [
                    {
                        "name": "관련 뉴스",
                        "target_db": "뉴스정보DB",
                        "purpose": "프로젝트/태스크와 관련된 뉴스 정보 연결"
                    },
                    {
                        "name": "관련 입찰정보",
                        "target_db": "입찰낙찰공고DB",
                        "purpose": "프로젝트/태스크와 관련된 입찰/낙찰 정보 연결"
                    }
                ]
            })
            
            # 롤업 기회 분석
            analysis["rollup_opportunities"].append({
                "target_db": db_name,
                "suggested_rollups": [
                    {
                        "name": "중요 뉴스 수",
                        "source": "관련 뉴스",
                        "rollup_type": "count",
                        "filter": "중요도가 '중요' 또는 '매우중요'"
                    },
                    {
                        "name": "최근 입찰공고 수",
                        "source": "관련 입찰정보",
                        "rollup_type": "count", 
                        "filter": "날짜가 최근 30일 이내"
                    }
                ]
            })
        
        logging.info("✅ 관계형 연결 가능성 분석 완료")
        return analysis

def main():
    """메인 실행 함수"""
    checker = ExistingDBChecker()
    
    # 종합 검사 실행
    results = checker.run_comprehensive_check()
    
    # 관계형 연결 분석
    analysis = checker.analyze_relationship_opportunities(results)
    
    # 최종 보고서 생성
    final_report = {
        "db_analysis": results,
        "relationship_analysis": analysis,
        "recommendations": [
            "기존 프로젝트 DB에 '관련 뉴스' 관계형 속성 추가",
            "기존 태스크 DB에 '관련 입찰정보' 관계형 속성 추가", 
            "롤업 기능을 활용한 중요 정보 집계 표시",
            "조대표님 워크플로우에 최소한의 변화로 최대 효과 달성"
        ]
    }
    
    with open('existing_db_final_report.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    print("\n🎉 기존 DB 분석 완료!")
    print("📄 결과 파일:")
    print("   - existing_db_analysis.json")
    print("   - existing_db_final_report.json")

if __name__ == "__main__":
    main() 