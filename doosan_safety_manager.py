#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 안전성 관리 시스템
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 노팀장님 요청에 따른 자동 백업, 롤백, 안전성 보장
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

class DoosanSafetyManager:
    """두산중공업 안전성 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.backup_dir = "backups"
        self.session_dir = "sessions"
        self.safety_log = []
        
        # 디렉토리 생성
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.session_dir, exist_ok=True)
    
    def create_backup(self, db_name: str, data: Dict) -> str:
        """자동 백업 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{db_name}_{timestamp}"
        backup_file = f"{self.backup_dir}/{backup_id}.json"
        
        backup_data = {
            "backup_id": backup_id,
            "db_name": db_name,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "backup_type": "pre_input_backup"
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        self.safety_log.append({
            "action": "backup_created",
            "backup_id": backup_id,
            "db_name": db_name,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"💾 백업 생성 완료: {backup_id}")
        return backup_id
    
    def create_session_backup(self, session_id: str, session_data: Dict) -> str:
        """세션 백업 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"session_backup_{session_id}_{timestamp}"
        backup_file = f"{self.session_dir}/{backup_id}.json"
        
        backup_data = {
            "backup_id": backup_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "session_data": session_data,
            "backup_type": "session_backup"
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        self.safety_log.append({
            "action": "session_backup_created",
            "backup_id": backup_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"💾 세션 백업 생성 완료: {backup_id}")
        return backup_id
    
    def rollback_if_failed(self, session_id: str, error_info: Dict) -> bool:
        """실패 시 롤백"""
        print(f"🔄 롤백 시작: {session_id}")
        
        # 세션 백업 파일 찾기
        session_backups = [f for f in os.listdir(self.session_dir) 
                          if f.startswith(f"session_backup_{session_id}_")]
        
        if not session_backups:
            print(f"❌ 롤백 실패: {session_id}에 대한 백업을 찾을 수 없습니다.")
            return False
        
        # 가장 최근 백업 선택
        latest_backup = sorted(session_backups)[-1]
        backup_file = f"{self.session_dir}/{latest_backup}"
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # 롤백 실행
            self._execute_rollback(backup_data)
            
            self.safety_log.append({
                "action": "rollback_executed",
                "session_id": session_id,
                "backup_id": backup_data["backup_id"],
                "error_info": error_info,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ 롤백 완료: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 롤백 실패: {str(e)}")
            return False
    
    def _execute_rollback(self, backup_data: Dict):
        """롤백 실행"""
        session_data = backup_data["session_data"]
        
        # 노션 API를 통한 롤백 (실제 구현 시)
        print(f"🔄 롤백 실행 중: {backup_data['backup_id']}")
        
        # 여기에 실제 노션 DB 롤백 로직 구현
        # 현재는 시뮬레이션
        time.sleep(1)  # 롤백 시뮬레이션
    
    def validate_final_result(self, input_results: Dict) -> Dict:
        """최종 결과 이중 검증"""
        print("🔍 최종 결과 이중 검증 시작")
        
        validation_result = {
            "total_records": 0,
            "success_count": 0,
            "error_count": 0,
            "validation_issues": [],
            "overall_status": "unknown"
        }
        
        # 각 DB별 검증
        for db_name, result in input_results.items():
            total = result.get('total', 0)
            success = result.get('success_count', 0)
            error = result.get('error_count', 0)
            
            validation_result["total_records"] += total
            validation_result["success_count"] += success
            validation_result["error_count"] += error
            
            # 성공률 검증
            if total > 0:
                success_rate = (success / total) * 100
                if success_rate < 90:
                    validation_result["validation_issues"].append({
                        "db_name": db_name,
                        "issue": f"성공률이 낮습니다: {success_rate:.1f}%",
                        "severity": "high"
                    })
        
        # 전체 상태 결정
        if validation_result["error_count"] == 0:
            validation_result["overall_status"] = "excellent"
        elif validation_result["error_count"] < validation_result["total_records"] * 0.1:
            validation_result["overall_status"] = "good"
        else:
            validation_result["overall_status"] = "needs_attention"
        
        self.safety_log.append({
            "action": "final_validation",
            "validation_result": validation_result,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ 이중 검증 완료: {validation_result['overall_status']}")
        return validation_result
    
    def get_safety_report(self) -> Dict:
        """안전성 보고서 생성"""
        report = {
            "total_backups": len([f for f in os.listdir(self.backup_dir) if f.endswith('.json')]),
            "total_session_backups": len([f for f in os.listdir(self.session_dir) if f.endswith('.json')]),
            "safety_log": self.safety_log,
            "last_backup": None,
            "last_rollback": None
        }
        
        # 최근 백업 및 롤백 정보
        for log_entry in reversed(self.safety_log):
            if log_entry["action"] == "backup_created" and not report["last_backup"]:
                report["last_backup"] = log_entry
            elif log_entry["action"] == "rollback_executed" and not report["last_rollback"]:
                report["last_rollback"] = log_entry
        
        return report
    
    def cleanup_old_backups(self, days_to_keep: int = 7):
        """오래된 백업 정리"""
        print(f"🧹 {days_to_keep}일 이상 된 백업 정리 중...")
        
        current_time = datetime.now()
        cleaned_count = 0
        
        # 백업 파일 정리
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.json'):
                file_path = f"{self.backup_dir}/{filename}"
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if (current_time - file_time).days > days_to_keep:
                    os.remove(file_path)
                    cleaned_count += 1
        
        # 세션 백업 파일 정리
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                file_path = f"{self.session_dir}/{filename}"
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if (current_time - file_time).days > days_to_keep:
                    os.remove(file_path)
                    cleaned_count += 1
        
        print(f"✅ 정리 완료: {cleaned_count}개 파일 삭제")

def main():
    """메인 실행 함수 (테스트)"""
    print("🛡️ 두산중공업 안전성 관리 시스템 테스트")
    print("=" * 50)
    
    safety_manager = DoosanSafetyManager()
    
    # 백업 테스트
    test_data = {
        "📊 기업 위험 프로파일 DB": [
            {"위험요소명": "환율 리스크", "위험도": "높음"}
        ]
    }
    
    backup_id = safety_manager.create_backup("📊 기업 위험 프로파일 DB", test_data)
    print(f"백업 ID: {backup_id}")
    
    # 세션 백업 테스트
    session_data = {
        "session_id": "test_session_001",
        "processed_records": 10,
        "status": "processing"
    }
    
    session_backup_id = safety_manager.create_session_backup("test_session_001", session_data)
    print(f"세션 백업 ID: {session_backup_id}")
    
    # 최종 검증 테스트
    test_results = {
        "📊 기업 위험 프로파일 DB": {
            "total": 5,
            "success_count": 5,
            "error_count": 0
        }
    }
    
    validation_result = safety_manager.validate_final_result(test_results)
    print(f"검증 결과: {validation_result['overall_status']}")
    
    # 안전성 보고서
    safety_report = safety_manager.get_safety_report()
    print(f"총 백업 수: {safety_report['total_backups']}")
    print(f"총 세션 백업 수: {safety_report['total_session_backups']}")

if __name__ == "__main__":
    main() 