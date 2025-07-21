#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두산중공업 사용자 친화적 처리 시스템
작성일: 2025년 7월 19일
작성자: 서대리 (Lead Developer)
목적: 노팀장님 요청에 따른 단순 텍스트 입력, 명확한 오류 메시지, 실시간 진행 상황
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class DoosanUserFriendlyProcessor:
    """두산중공업 사용자 친화적 처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.progress_log = []
        self.error_log = []
        self.user_feedback = []
        
    def simple_text_input(self, text: str) -> Dict:
        """단순 텍스트 입력 지원"""
        print("📝 단순 텍스트 입력 처리 시작")
        print("=" * 40)
        
        # 텍스트 전처리
        cleaned_text = self._preprocess_text(text)
        
        # 자동 분류 및 구조화
        structured_data = self._auto_structure_text(cleaned_text)
        
        # 사용자 친화적 피드백 생성
        feedback = self._generate_user_feedback(structured_data)
        
        return {
            "success": True,
            "original_text": text,
            "cleaned_text": cleaned_text,
            "structured_data": structured_data,
            "feedback": feedback,
            "processing_time": time.time()
        }
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 특수문자 정리
        text = re.sub(r'[^\w\s가-힣\-\.\,\:\;\(\)\[\]\{\}]', '', text)
        
        return text
    
    def _auto_structure_text(self, text: str) -> Dict:
        """텍스트 자동 구조화"""
        structured_data = {
            "📊 기업 위험 프로파일 DB": [],
            "💰 기업 재무 및 프로젝트 DB": [],
            "🔋 신재생에너지 프로젝트 DB": [],
            "👥 기업 핵심 인물 DB": [],
            "🏛️ 정부 정책 영향 분석 DB": [],
            "🌍 글로벌 보험중개 시장 DB": []
        }
        
        # 키워드 기반 자동 분류
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 위험 관련 키워드
            if any(keyword in line for keyword in ['위험', '리스크', '위험도', '위험요소']):
                structured_data["📊 기업 위험 프로파일 DB"].append({
                    "원본텍스트": line,
                    "분류근거": "위험 관련 키워드 감지"
                })
            
            # 재무 관련 키워드
            elif any(keyword in line for keyword in ['매출', '수익', '프로젝트', '계약', '재무']):
                structured_data["💰 기업 재무 및 프로젝트 DB"].append({
                    "원본텍스트": line,
                    "분류근거": "재무 관련 키워드 감지"
                })
            
            # 신재생에너지 관련 키워드
            elif any(keyword in line for keyword in ['태양광', '풍력', 'ESS', '신재생', '에너지']):
                structured_data["🔋 신재생에너지 프로젝트 DB"].append({
                    "원본텍스트": line,
                    "분류근거": "신재생에너지 관련 키워드 감지"
                })
            
            # 인물 관련 키워드
            elif any(keyword in line for keyword in ['대표이사', '경영진', '이사', '부사장', '사장']):
                structured_data["👥 기업 핵심 인물 DB"].append({
                    "원본텍스트": line,
                    "분류근거": "인물 관련 키워드 감지"
                })
            
            # 정책 관련 키워드
            elif any(keyword in line for keyword in ['정책', '법규', '규제', '지원', '정부']):
                structured_data["🏛️ 정부 정책 영향 분석 DB"].append({
                    "원본텍스트": line,
                    "분류근거": "정책 관련 키워드 감지"
                })
            
            # 보험 관련 키워드
            elif any(keyword in line for keyword in ['보험', '중개', '시장', '글로벌']):
                structured_data["🌍 글로벌 보험중개 시장 DB"].append({
                    "원본텍스트": line,
                    "분류근거": "보험 관련 키워드 감지"
                })
        
        return structured_data
    
    def _generate_user_feedback(self, structured_data: Dict) -> Dict:
        """사용자 친화적 피드백 생성"""
        total_lines = sum(len(data) for data in structured_data.values())
        classified_lines = sum(len(data) for data in structured_data.values() if data)
        
        feedback = {
            "처리결과": "성공" if total_lines > 0 else "실패",
            "총텍스트라인": total_lines,
            "분류된라인": classified_lines,
            "분류율": f"{(classified_lines/total_lines)*100:.1f}%" if total_lines > 0 else "0%",
            "DB별분포": {},
            "추천사항": []
        }
        
        # DB별 분포 계산
        for db_name, data in structured_data.items():
            if data:
                feedback["DB별분포"][db_name] = len(data)
        
        # 추천사항 생성
        if classified_lines == 0:
            feedback["추천사항"].append("텍스트에 키워드가 부족합니다. 더 구체적인 정보를 추가해 주세요.")
        elif classified_lines < total_lines * 0.5:
            feedback["추천사항"].append("일부 텍스트가 분류되지 않았습니다. 키워드를 더 명확히 해 주세요.")
        else:
            feedback["추천사항"].append("텍스트 분류가 잘 되었습니다. 노션 DB 입력을 진행합니다.")
        
        return feedback
    
    def clear_error_messages(self, error: str) -> str:
        """명확한 오류 메시지 생성"""
        error_patterns = {
            "notion_api_error": "노션 API 연결 오류입니다. 인터넷 연결과 API 키를 확인해 주세요.",
            "rate_limit_error": "API 호출 제한에 도달했습니다. 잠시 후 다시 시도해 주세요.",
            "validation_error": "데이터 형식이 올바르지 않습니다. 필수 필드를 확인해 주세요.",
            "duplicate_error": "중복된 데이터가 발견되었습니다. 자동으로 처리됩니다.",
            "network_error": "네트워크 연결 오류입니다. 인터넷 연결을 확인해 주세요.",
            "unknown_error": "알 수 없는 오류가 발생했습니다. 시스템을 다시 시작해 주세요."
        }
        
        # 오류 패턴 매칭
        for pattern, message in error_patterns.items():
            if pattern in error.lower():
                return message
        
        # 기본 오류 메시지
        return f"오류가 발생했습니다: {error[:100]}..."
    
    def real_time_progress(self, current: int, total: int, stage: str = "처리중"):
        """실시간 진행 상황 표시"""
        progress_percent = (current / total) * 100 if total > 0 else 0
        
        # 진행률 바 생성
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 진행 상황 출력
        print(f"\r{stage}: [{bar}] {current}/{total} ({progress_percent:.1f}%)", end='', flush=True)
        
        if current >= total:
            print()  # 줄바꿈
        
        # 진행 로그 저장
        self.progress_log.append({
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "current": current,
            "total": total,
            "progress_percent": progress_percent
        })
    
    def auto_retry_logic(self, func, max_retries: int = 3, delay: float = 1.0):
        """자동 재시도 로직"""
        for attempt in range(max_retries):
            try:
                result = func()
                if attempt > 0:
                    print(f"✅ 재시도 성공 (시도 {attempt + 1}/{max_retries})")
                return result
            except Exception as e:
                error_msg = self.clear_error_messages(str(e))
                print(f"❌ 시도 {attempt + 1}/{max_retries} 실패: {error_msg}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ {delay}초 후 재시도...")
                    time.sleep(delay)
                    delay *= 2  # 지수 백오프
                else:
                    print(f"❌ 최대 재시도 횟수 초과: {error_msg}")
                    raise e
    
    def get_user_friendly_report(self) -> Dict:
        """사용자 친화적 보고서 생성"""
        report = {
            "처리요약": {
                "총진행단계": len(self.progress_log),
                "총오류수": len(self.error_log),
                "사용자피드백수": len(self.user_feedback)
            },
            "진행상황": self.progress_log[-10:] if self.progress_log else [],  # 최근 10개
            "오류내역": self.error_log[-5:] if self.error_log else [],  # 최근 5개
            "사용자피드백": self.user_feedback[-5:] if self.user_feedback else []  # 최근 5개
        }
        
        return report

def main():
    """메인 실행 함수 (테스트)"""
    print("👤 두산중공업 사용자 친화적 처리 시스템 테스트")
    print("=" * 50)
    
    processor = DoosanUserFriendlyProcessor()
    
    # 단순 텍스트 입력 테스트
    test_text = """
    두산중공업은 해외 프로젝트에서 환율 리스크에 노출되어 있습니다.
    정경훈 대표이사는 30년 경력의 전문가입니다.
    2024년 매출 15,000억원을 달성했습니다.
    태양광 발전소 200MW 프로젝트를 진행 중입니다.
    """
    
    result = processor.simple_text_input(test_text)
    print(f"처리 결과: {result['feedback']['처리결과']}")
    print(f"분류율: {result['feedback']['분류율']}")
    
    # 실시간 진행 상황 테스트
    print("\n실시간 진행 상황 테스트:")
    for i in range(11):
        processor.real_time_progress(i, 10, "데이터 처리")
        time.sleep(0.2)
    
    # 오류 메시지 테스트
    print("\n오류 메시지 테스트:")
    error_messages = [
        "notion_api_error: Connection failed",
        "rate_limit_error: Too many requests",
        "validation_error: Invalid data format",
        "unknown_error: Something went wrong"
    ]
    
    for error in error_messages:
        clear_message = processor.clear_error_messages(error)
        print(f"원본: {error}")
        print(f"정리: {clear_message}")
        print()
    
    # 사용자 친화적 보고서
    report = processor.get_user_friendly_report()
    print(f"처리 요약: {report['처리요약']}")

if __name__ == "__main__":
    main() 