#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 증분 데이터 처리 스크립트
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 순차적으로 제공되는 데이터를 단계별로 처리하고 검증
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('config.env')

class DoosanIncrementalProcessor:
    """두산중공업 증분 데이터 처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.processing_history = []
        self.current_session = f"session_{datetime.now().strftime('%Y%m%d_%H%M')}"
        self.session_data = {
            "📊 기업 위험 프로파일 DB": [],
            "💰 기업 재무 및 프로젝트 DB": [],
            "🔋 신재생에너지 프로젝트 DB": [],
            "👥 기업 핵심 인물 DB": [],
            "🏛️ 정부 정책 영향 분석 DB": [],
            "🌍 글로벌 보험중개 시장 DB": []
        }
        
        # 세션 폴더 생성
        os.makedirs(f"sessions/{self.current_session}", exist_ok=True)
    
    def process_incremental_data(self, data_text: str, data_type: str = "기본정보") -> Dict:
        """증분 데이터 처리"""
        print(f"📝 증분 데이터 처리 시작: {data_type}")
        print("=" * 50)
        
        # 텍스트 처리기 임포트
        from doosan_text_processor import DoosanTextProcessor
        processor = DoosanTextProcessor()
        
        # 텍스트 처리
        processed_data = processor.process_markdown_text(data_text)
        
        # 세션 데이터에 추가
        for db_name, data_list in processed_data.items():
            self.session_data[db_name].extend(data_list)
        
        # 처리 기록 저장
        processing_record = {
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "processed_records": {db: len(data) for db, data in processed_data.items()},
            "total_records": sum(len(data) for data in processed_data.values())
        }
        self.processing_history.append(processing_record)
        
        # 세션 데이터 저장
        self._save_session_data()
        
        return {
            "success": True,
            "data_type": data_type,
            "processed_records": processing_record["processed_records"],
            "total_records": processing_record["total_records"],
            "session_id": self.current_session
        }
    
    def _save_session_data(self):
        """세션 데이터 저장"""
        session_file = f"sessions/{self.current_session}/session_data.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, ensure_ascii=False, indent=2)
        
        # 처리 기록 저장
        history_file = f"sessions/{self.current_session}/processing_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_history, f, ensure_ascii=False, indent=2)
    
    def get_session_summary(self) -> Dict:
        """세션 요약 정보"""
        total_records = sum(len(data) for data in self.session_data.values())
        total_processing_steps = len(self.processing_history)
        
        summary = {
            "session_id": self.current_session,
            "total_records": total_records,
            "processing_steps": total_processing_steps,
            "db_distribution": {db: len(data) for db, data in self.session_data.items()},
            "processing_timeline": self.processing_history
        }
        
        return summary
    
    def finalize_session(self) -> Dict:
        """세션 최종화 및 노션 DB 입력"""
        print("🎯 세션 최종화 및 노션 DB 입력 시작")
        print("=" * 50)
        
        # 통합 처리기 임포트
        from doosan_integrated_processor import DoosanIntegratedProcessor
        integrated_processor = DoosanIntegratedProcessor()
        
        # 모든 세션 데이터를 하나의 텍스트로 결합
        combined_text = self._combine_session_data()
        
        # 통합 처리 및 입력
        results = integrated_processor.process_text_and_input(combined_text)
        
        # 최종 보고서 생성
        final_report = self._generate_final_report(results)
        
        return {
            "success": True,
            "session_id": self.current_session,
            "total_records": sum(len(data) for data in self.session_data.values()),
            "input_results": results,
            "final_report": final_report
        }
    
    def _combine_session_data(self) -> str:
        """세션 데이터를 텍스트로 결합"""
        combined_text = f"# 두산중공업 통합 데이터 (세션: {self.current_session})\n\n"
        
        for db_name, data_list in self.session_data.items():
            if data_list:
                combined_text += f"## {db_name}\n\n"
                for data in data_list:
                    # 첫 번째 필드를 제목으로 사용
                    first_field = list(data.items())[0]
                    combined_text += f"### {first_field[1]}\n"
                    for key, value in data.items():
                        if key != list(data.keys())[0]:  # 첫 번째 필드 제외
                            combined_text += f"- {key}: {value}\n"
                    combined_text += "\n"
        
        return combined_text
    
    def _generate_final_report(self, input_results: Dict) -> str:
        """최종 보고서 생성"""
        report = f"""
# 두산중공업 증분 데이터 처리 최종 보고서
세션 ID: {self.current_session}
생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

## 📊 세션 요약
"""
        
        summary = self.get_session_summary()
        report += f"""
- 총 처리 단계: {summary['processing_steps']}단계
- 총 추출 레코드: {summary['total_records']}개
- 세션 ID: {summary['session_id']}

## 📝 DB별 데이터 분포
"""
        
        for db_name, count in summary['db_distribution'].items():
            if count > 0:
                report += f"- {db_name}: {count}개 레코드\n"
        
        report += f"""
## 📈 처리 타임라인
"""
        
        for i, record in enumerate(summary['processing_timeline'], 1):
            report += f"""
### 단계 {i}: {record['data_type']}
- 처리 시간: {record['timestamp']}
- 총 레코드: {record['total_records']}개
"""
            for db_name, count in record['processed_records'].items():
                if count > 0:
                    report += f"- {db_name}: {count}개\n"
        
        report += f"""
## 🎯 노션 DB 입력 결과
"""
        
        total_success = 0
        total_error = 0
        
        for db_name, result in input_results.items():
            report += f"""
### {db_name}
- 총 레코드: {result['total']}
- 성공: {result['success_count']}
- 실패: {result['error_count']}
- 성공률: {result['success_rate']:.1f}%
"""
            total_success += result['success_count']
            total_error += result['error_count']
        
        report += f"""
## 🎉 최종 결과
- 총 입력 성공: {total_success}개
- 총 입력 실패: {total_error}개
- 전체 성공률: {(total_success / (total_success + total_error)) * 100:.1f}%
"""
        
        return report

def main():
    """메인 실행 함수 (예시)"""
    print("🔄 두산중공업 증분 데이터 처리 시스템 시작")
    print("=" * 50)
    
    processor = DoosanIncrementalProcessor()
    
    # 예시: 단계별 데이터 처리
    sample_data_steps = [
        {
            "type": "기본정보",
            "content": """
# 두산중공업 기본 정보

## 경영진
정경훈 대표이사가 경영을 총괄하고 있으며, 30년 경력의 전문가입니다.

## 재무 현황
2024년 매출 15,000억원을 달성했으며, 해외 프로젝트 비중이 60%를 차지합니다.
"""
        },
        {
            "type": "리스크분석",
            "content": """
# 두산중공업 리스크 분석

## 해외 프로젝트 리스크
두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다. 특히 미국 달러화 변동으로 인한 손실 위험이 높은 상황입니다.
"""
        },
        {
            "type": "신재생에너지",
            "content": """
# 두산중공업 신재생에너지 프로젝트

## 태양광 프로젝트
태양광 발전소 200MW 프로젝트를 진행 중이며, ESS 사업도 확장하고 있습니다.
"""
        }
    ]
    
    # 단계별 처리
    for step_data in sample_data_steps:
        result = processor.process_incremental_data(
            step_data["content"], 
            step_data["type"]
        )
        print(f"✅ {step_data['type']} 처리 완료: {result['total_records']}개 레코드")
        time.sleep(1)  # 처리 간격
    
    # 세션 최종화
    final_result = processor.finalize_session()
    print("🎉 증분 데이터 처리 완료!")
    
    # 최종 보고서 저장
    with open(f'doosan_incremental_report_{processor.current_session}.md', 'w', encoding='utf-8') as f:
        f.write(final_result['final_report'])
    
    print(f"📊 최종 결과: {final_result['total_records']}개 레코드 처리 완료")

if __name__ == "__main__":
    main() 