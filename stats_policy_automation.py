"""
통계/정책 정보 통합 자동화 시스템
- 데이터 수집 → 노션 업로드 → 대시보드 연동 전체 파이프라인
- 조대표님의 비즈니스 의사결정 지원을 위한 통계/정책 정보 자동화
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
from stats_policy_collector import StatsPolicyCollector
from stats_policy_notion_uploader import StatsPolicyNotionUploader
from mvp_config import APIConfig

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatsPolicyAutomation:
    def __init__(self):
        self.collector = StatsPolicyCollector()
        self.uploader = StatsPolicyNotionUploader()
        self.stats_policy_db_id = None
        
    def run_full_pipeline(self) -> Dict:
        """전체 파이프라인 실행"""
        logger.info("=== 통계/정책 정보 자동화 파이프라인 시작 ===")
        start_time = time.time()
        
        pipeline_result = {
            "start_time": datetime.now().isoformat(),
            "collection_phase": {},
            "upload_phase": {},
            "dashboard_phase": {},
            "total_time": 0,
            "success": False,
            "error_message": None
        }
        
        try:
            # 1단계: 통계/정책 DB 생성 또는 연결
            logger.info("1단계: 통계/정책 DB 준비")
            if not self._setup_database():
                pipeline_result["error_message"] = "데이터베이스 설정 실패"
                return pipeline_result
            
            # 2단계: 데이터 수집
            logger.info("2단계: 통계/정책 데이터 수집")
            collection_result = self._collect_data()
            pipeline_result["collection_phase"] = collection_result
            
            if collection_result["success_count"] == 0:
                pipeline_result["error_message"] = "데이터 수집 실패"
                return pipeline_result
            
            # 3단계: 노션 업로드
            logger.info("3단계: 노션 데이터베이스 업로드")
            upload_result = self._upload_data(collection_result["collected_data"])
            pipeline_result["upload_phase"] = upload_result
            
            # 4단계: 대시보드 연동 (간단한 확인)
            logger.info("4단계: 대시보드 연동 준비")
            dashboard_result = self._prepare_dashboard_integration()
            pipeline_result["dashboard_phase"] = dashboard_result
            
            # 파이프라인 완료
            end_time = time.time()
            pipeline_result["total_time"] = round(end_time - start_time, 2)
            pipeline_result["success"] = True
            
            logger.info("=== 통계/정책 정보 자동화 파이프라인 완료 ===")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"파이프라인 실행 중 오류 발생: {str(e)}")
            pipeline_result["error_message"] = str(e)
            pipeline_result["total_time"] = round(time.time() - start_time, 2)
            return pipeline_result
    
    def _setup_database(self) -> bool:
        """데이터베이스 설정"""
        try:
            # 기존 DB ID가 있는지 확인
            existing_db_id = self._get_existing_stats_db_id()
            
            if existing_db_id:
                logger.info(f"기존 통계/정책 DB 사용: {existing_db_id}")
                self.uploader.set_stats_policy_db_id(existing_db_id)
                self.stats_policy_db_id = existing_db_id
                return True
            else:
                # 새로 생성
                logger.info("새로운 통계/정책 DB 생성")
                db_id = self.uploader.create_stats_policy_database()
                if db_id:
                    self.stats_policy_db_id = db_id
                    self._save_stats_db_id(db_id)
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"데이터베이스 설정 중 오류: {str(e)}")
            return False
    
    def _collect_data(self) -> Dict:
        """데이터 수집 단계"""
        try:
            start_time = time.time()
            
            # 모든 소스에서 데이터 수집
            collected_data = self.collector.collect_all_data()
            
            collection_time = round(time.time() - start_time, 2)
            
            result = {
                "success_count": len(collected_data),
                "collection_time": collection_time,
                "collected_data": collected_data,
                "data_sources": self._get_data_source_summary(collected_data)
            }
            
            logger.info(f"데이터 수집 완료: {len(collected_data)}건, 소요시간: {collection_time}초")
            return result
            
        except Exception as e:
            logger.error(f"데이터 수집 중 오류: {str(e)}")
            return {
                "success_count": 0,
                "collection_time": 0,
                "collected_data": [],
                "error": str(e)
            }
    
    def _upload_data(self, collected_data: List[Dict]) -> Dict:
        """데이터 업로드 단계"""
        try:
            start_time = time.time()
            
            # 노션 업로드
            upload_result = self.uploader.upload_stats_policy_data(collected_data)
            
            upload_time = round(time.time() - start_time, 2)
            
            result = {
                "success_count": upload_result["success"],
                "failed_count": upload_result["failed"],
                "upload_time": upload_time,
                "errors": upload_result["errors"]
            }
            
            logger.info(f"데이터 업로드 완료: 성공 {upload_result['success']}건, 실패 {upload_result['failed']}건")
            return result
            
        except Exception as e:
            logger.error(f"데이터 업로드 중 오류: {str(e)}")
            return {
                "success_count": 0,
                "failed_count": 0,
                "upload_time": 0,
                "error": str(e)
            }
    
    def _prepare_dashboard_integration(self) -> Dict:
        """대시보드 연동 준비"""
        try:
            # 대시보드 연동을 위한 메타데이터 생성
            dashboard_info = {
                "stats_policy_db_id": self.stats_policy_db_id,
                "integration_ready": True,
                "last_update": datetime.now().isoformat(),
                "dashboard_sections": [
                    "신재생에너지 동향",
                    "방위산업 통계",
                    "보험업계 현황",
                    "경제지표 요약"
                ]
            }
            
            # 대시보드 연동 정보 저장
            self._save_dashboard_info(dashboard_info)
            
            logger.info("대시보드 연동 준비 완료")
            return dashboard_info
            
        except Exception as e:
            logger.error(f"대시보드 연동 준비 중 오류: {str(e)}")
            return {
                "integration_ready": False,
                "error": str(e)
            }
    
    def _get_data_source_summary(self, data_list: List[Dict]) -> Dict:
        """데이터 소스별 요약 정보 생성"""
        summary = {}
        
        for item in data_list:
            source = item.get('source', 'Unknown')
            if source not in summary:
                summary[source] = {
                    "count": 0,
                    "categories": set()
                }
            
            summary[source]["count"] += 1
            summary[source]["categories"].add(item.get('category', 'Unknown'))
        
        # set을 list로 변환
        for source in summary:
            summary[source]["categories"] = list(summary[source]["categories"])
        
        return summary
    
    def _get_existing_stats_db_id(self) -> Optional[str]:
        """기존 통계/정책 DB ID 조회"""
        try:
            with open('stats_policy_db_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('stats_policy_db_id')
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.warning(f"기존 DB ID 조회 중 오류: {str(e)}")
            return None
    
    def _save_stats_db_id(self, db_id: str):
        """통계/정책 DB ID 저장"""
        try:
            config = {
                'stats_policy_db_id': db_id,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open('stats_policy_db_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info(f"통계/정책 DB ID 저장 완료: {db_id}")
            
        except Exception as e:
            logger.error(f"DB ID 저장 중 오류: {str(e)}")
    
    def _save_dashboard_info(self, dashboard_info: Dict):
        """대시보드 연동 정보 저장"""
        try:
            with open('stats_policy_dashboard_info.json', 'w', encoding='utf-8') as f:
                json.dump(dashboard_info, f, ensure_ascii=False, indent=2)
                
            logger.info("대시보드 연동 정보 저장 완료")
            
        except Exception as e:
            logger.error(f"대시보드 정보 저장 중 오류: {str(e)}")
    
    def get_execution_summary(self, pipeline_result: Dict) -> str:
        """실행 결과 요약 생성"""
        summary = []
        summary.append("=== 통계/정책 정보 자동화 실행 결과 ===")
        summary.append(f"실행 시간: {pipeline_result.get('start_time', 'Unknown')}")
        summary.append(f"총 소요 시간: {pipeline_result.get('total_time', 0)}초")
        summary.append(f"실행 성공: {'예' if pipeline_result.get('success') else '아니오'}")
        
        if pipeline_result.get('error_message'):
            summary.append(f"오류: {pipeline_result['error_message']}")
        
        # 수집 단계 결과
        collection = pipeline_result.get('collection_phase', {})
        if collection:
            summary.append(f"\n[데이터 수집 단계]")
            summary.append(f"- 수집 건수: {collection.get('success_count', 0)}건")
            summary.append(f"- 수집 시간: {collection.get('collection_time', 0)}초")
            
            data_sources = collection.get('data_sources', {})
            if data_sources:
                summary.append(f"- 데이터 소스별 현황:")
                for source, info in data_sources.items():
                    summary.append(f"  * {source}: {info['count']}건")
        
        # 업로드 단계 결과
        upload = pipeline_result.get('upload_phase', {})
        if upload:
            summary.append(f"\n[데이터 업로드 단계]")
            summary.append(f"- 업로드 성공: {upload.get('success_count', 0)}건")
            summary.append(f"- 업로드 실패: {upload.get('failed_count', 0)}건")
            summary.append(f"- 업로드 시간: {upload.get('upload_time', 0)}초")
        
        # 대시보드 단계 결과
        dashboard = pipeline_result.get('dashboard_phase', {})
        if dashboard:
            summary.append(f"\n[대시보드 연동 단계]")
            summary.append(f"- 연동 준비: {'완료' if dashboard.get('integration_ready') else '실패'}")
            summary.append(f"- 통계/정책 DB ID: {dashboard.get('stats_policy_db_id', 'None')}")
        
        return "\n".join(summary)

def main():
    """메인 실행 함수"""
    print("=== 통계/정책 정보 통합 자동화 시스템 ===")
    print("조대표님의 비즈니스 의사결정 지원을 위한 통계/정책 정보 자동화 시작")
    
    # 자동화 실행
    automation = StatsPolicyAutomation()
    pipeline_result = automation.run_full_pipeline()
    
    # 결과 출력
    summary = automation.get_execution_summary(pipeline_result)
    print("\n" + summary)
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"stats_policy_execution_result_{timestamp}.json"
    
    try:
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(pipeline_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n실행 결과 저장: {result_filename}")
    except Exception as e:
        print(f"결과 저장 중 오류: {str(e)}")
    
    return pipeline_result

if __name__ == "__main__":
    main() 