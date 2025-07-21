#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 중복 데이터 처리 스크립트
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 순차적 데이터 제공 시 중복 감지 및 처리
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher
import re

class DoosanDuplicateHandler:
    """두산중공업 중복 데이터 처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.processed_records = {
            "📊 기업 위험 프로파일 DB": {},
            "💰 기업 재무 및 프로젝트 DB": {},
            "🔋 신재생에너지 프로젝트 DB": {},
            "👥 기업 핵심 인물 DB": {},
            "🏛️ 정부 정책 영향 분석 DB": {},
            "🌍 글로벌 보험중개 시장 DB": {}
        }
        
        # 중복 처리 정책
        self.duplicate_policies = {
            "📊 기업 위험 프로파일 DB": {
                "key_fields": ["위험요소명", "위험유형"],
                "merge_strategy": "latest_wins",  # 최신 정보 우선
                "similarity_threshold": 0.85
            },
            "💰 기업 재무 및 프로젝트 DB": {
                "key_fields": ["프로젝트명", "시작일"],
                "merge_strategy": "merge_fields",  # 필드 병합
                "similarity_threshold": 0.90
            },
            "🔋 신재생에너지 프로젝트 DB": {
                "key_fields": ["프로젝트명", "위치"],
                "merge_strategy": "latest_wins",
                "similarity_threshold": 0.85
            },
            "👥 기업 핵심 인물 DB": {
                "key_fields": ["이름", "직책"],
                "merge_strategy": "merge_fields",
                "similarity_threshold": 0.95
            },
            "🏛️ 정부 정책 영향 분석 DB": {
                "key_fields": ["정책명", "발표일"],
                "merge_strategy": "latest_wins",
                "similarity_threshold": 0.90
            },
            "🌍 글로벌 보험중개 시장 DB": {
                "key_fields": ["시장명", "지역"],
                "merge_strategy": "merge_fields",
                "similarity_threshold": 0.85
            }
        }
    
    def generate_record_key(self, record: Dict, db_name: str) -> str:
        """레코드 고유 키 생성"""
        policy = self.duplicate_policies[db_name]
        key_fields = policy["key_fields"]
        
        # 키 필드 값들을 조합하여 고유 키 생성
        key_values = []
        for field in key_fields:
            value = record.get(field, "")
            if isinstance(value, str):
                # 특수문자 제거 및 정규화
                normalized_value = re.sub(r'[^\w\s가-힣]', '', value).strip().lower()
                key_values.append(normalized_value)
            else:
                key_values.append(str(value))
        
        # 해시 생성
        key_string = "|".join(key_values)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
        
        # 정규화
        text1 = re.sub(r'[^\w\s가-힣]', '', text1).strip().lower()
        text2 = re.sub(r'[^\w\s가-힣]', '', text2).strip().lower()
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    def detect_duplicates(self, new_records: List[Dict], db_name: str) -> Dict:
        """중복 감지"""
        policy = self.duplicate_policies[db_name]
        existing_records = self.processed_records[db_name]
        
        duplicates = []
        unique_records = []
        merged_records = []
        
        for new_record in new_records:
            record_key = self.generate_record_key(new_record, db_name)
            
            # 정확한 키 매칭 확인
            if record_key in existing_records:
                existing_record = existing_records[record_key]
                duplicates.append({
                    "new_record": new_record,
                    "existing_record": existing_record,
                    "key": record_key,
                    "type": "exact_match"
                })
                continue
            
            # 유사도 기반 중복 확인
            is_similar = False
            for existing_key, existing_record in existing_records.items():
                similarity = self._calculate_record_similarity(new_record, existing_record)
                if similarity >= policy["similarity_threshold"]:
                    duplicates.append({
                        "new_record": new_record,
                        "existing_record": existing_record,
                        "key": existing_key,
                        "similarity": similarity,
                        "type": "similarity_match"
                    })
                    is_similar = True
                    break
            
            if not is_similar:
                unique_records.append(new_record)
        
        return {
            "duplicates": duplicates,
            "unique_records": unique_records,
            "total_new": len(new_records),
            "duplicate_count": len(duplicates),
            "unique_count": len(unique_records)
        }
    
    def _calculate_record_similarity(self, record1: Dict, record2: Dict) -> float:
        """레코드 간 유사도 계산"""
        similarities = []
        
        # 모든 필드에 대해 유사도 계산
        all_fields = set(record1.keys()) | set(record2.keys())
        
        for field in all_fields:
            value1 = str(record1.get(field, ""))
            value2 = str(record2.get(field, ""))
            
            if value1 and value2:
                similarity = self.calculate_similarity(value1, value2)
                similarities.append(similarity)
        
        # 평균 유사도 반환
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def merge_records(self, duplicate_info: Dict, db_name: str) -> Dict:
        """중복 레코드 병합"""
        policy = self.duplicate_policies[db_name]
        strategy = policy["merge_strategy"]
        
        new_record = duplicate_info["new_record"]
        existing_record = duplicate_info["existing_record"]
        
        if strategy == "latest_wins":
            # 최신 정보 우선 (새로운 레코드로 교체)
            return new_record
        
        elif strategy == "merge_fields":
            # 필드 병합 (빈 필드만 채우기)
            merged_record = existing_record.copy()
            
            for field, new_value in new_record.items():
                existing_value = merged_record.get(field, "")
                
                # 기존 값이 비어있거나 새 값이 더 상세한 경우 업데이트
                if not existing_value or (new_value and len(str(new_value)) > len(str(existing_value))):
                    merged_record[field] = new_value
            
            return merged_record
        
        else:
            # 기본적으로 최신 정보 우선
            return new_record
    
    def process_new_records(self, new_records: List[Dict], db_name: str) -> Dict:
        """새 레코드 처리 (중복 감지 및 처리 포함)"""
        print(f"🔍 {db_name} 중복 감지 중...")
        
        # 중복 감지
        detection_result = self.detect_duplicates(new_records, db_name)
        
        # 중복 처리
        merged_records = []
        for duplicate in detection_result["duplicates"]:
            merged_record = self.merge_records(duplicate, db_name)
            merged_records.append(merged_record)
            
            # 기존 레코드 업데이트
            record_key = self.generate_record_key(merged_record, db_name)
            self.processed_records[db_name][record_key] = merged_record
        
        # 고유 레코드 추가
        for unique_record in detection_result["unique_records"]:
            record_key = self.generate_record_key(unique_record, db_name)
            self.processed_records[db_name][record_key] = unique_record
        
        # 결과 요약
        result = {
            "db_name": db_name,
            "total_new_records": detection_result["total_new"],
            "duplicate_count": detection_result["duplicate_count"],
            "unique_count": detection_result["unique_count"],
            "merged_count": len(merged_records),
            "total_after_processing": len(self.processed_records[db_name]),
            "duplicates": detection_result["duplicates"]
        }
        
        return result
    
    def get_processing_summary(self) -> Dict:
        """처리 요약 정보"""
        summary = {
            "total_records": sum(len(records) for records in self.processed_records.values()),
            "db_distribution": {db: len(records) for db, records in self.processed_records.items()},
            "duplicate_policies": self.duplicate_policies
        }
        
        return summary
    
    def save_processing_state(self, filename: str = None):
        """처리 상태 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"doosan_duplicate_processing_{timestamp}.json"
        
        state = {
            "processed_records": self.processed_records,
            "duplicate_policies": self.duplicate_policies,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 처리 상태 저장 완료: {filename}")
    
    def load_processing_state(self, filename: str):
        """처리 상태 로드"""
        with open(filename, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.processed_records = state["processed_records"]
        self.duplicate_policies = state["duplicate_policies"]
        
        print(f"📂 처리 상태 로드 완료: {filename}")

def main():
    """메인 실행 함수 (테스트)"""
    print("🔄 두산중공업 중복 처리 시스템 테스트")
    print("=" * 50)
    
    handler = DoosanDuplicateHandler()
    
    # 테스트 데이터
    test_records = [
        {
            "위험요소명": "환율 리스크",
            "위험유형": "재무위험",
            "위험도": "높음",
            "설명": "해외 프로젝트로 인한 환율 변동 리스크"
        },
        {
            "위험요소명": "환율 리스크",
            "위험유형": "재무위험", 
            "위험도": "매우 높음",
            "설명": "미국 달러화 변동으로 인한 환율 리스크"
        },
        {
            "위험요소명": "원자재 가격 변동",
            "위험유형": "시장위험",
            "위험도": "중간",
            "설명": "철강 등 원자재 가격 변동 위험"
        }
    ]
    
    # 중복 처리 테스트
    result = handler.process_new_records(test_records, "📊 기업 위험 프로파일 DB")
    
    print(f"📊 처리 결과:")
    print(f"- 총 입력 레코드: {result['total_new_records']}")
    print(f"- 중복 감지: {result['duplicate_count']}")
    print(f"- 고유 레코드: {result['unique_count']}")
    print(f"- 병합된 레코드: {result['merged_count']}")
    print(f"- 최종 총 레코드: {result['total_after_processing']}")
    
    # 요약 정보
    summary = handler.get_processing_summary()
    print(f"\n📈 전체 요약:")
    print(f"- 총 레코드: {summary['total_records']}")
    for db, count in summary['db_distribution'].items():
        if count > 0:
            print(f"- {db}: {count}개")

if __name__ == "__main__":
    main() 