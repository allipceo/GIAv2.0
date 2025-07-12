#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
입찰/낙찰 뉴스 전용 LLM 처리 모듈
작성일: 2025년 1월 13일
작성자: 서대리 (Lead Developer)
목적: Gemini-2.0-flash를 활용한 입찰/낙찰 뉴스 자동 분류, 요약, 중요도 판단

주요 기능:
- 입찰/낙찰 유형 자동 분류 (입찰공고/낙찰결과/계약소식/관련뉴스)
- 조대표님 맞춤 요약 생성 (비즈니스 관점)
- 중요도 판단 강화 (금액, 규모, 정책 등 고려)
"""

import json
import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from mvp_config import APIConfig, BusinessKeywords, ProcessingConfig, BidDatabaseFields

# Google Generative AI 라이브러리
try:
    import google.generativeai as genai
except ImportError:
    logging.error("google-generativeai 라이브러리가 설치되지 않았습니다.")
    exit(1)

class BidLLMProcessor:
    """입찰/낙찰 뉴스 전용 LLM 처리기"""
    
    def __init__(self):
        self.api_key = APIConfig.LLM_API_KEY
        self.model_name = APIConfig.LLM_MODEL_NAME
        
        # Gemini API 초기화
        if self.api_key != "YOUR_GEMINI_API_KEY":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
            logging.warning("Gemini API 키가 설정되지 않았습니다. 시뮬레이션 모드로 동작합니다.")
    
    def create_bid_type_prompt(self, title: str, description: str) -> str:
        """입찰/낙찰 유형 분류를 위한 프롬프트 생성"""
        
        prompt = f"""
다음 뉴스를 분석하여 가장 적합한 입찰/낙찰 유형으로 분류해주세요.

유형 옵션:
- 입찰공고: 입찰 공고, 사업자 모집, 제안서 요청, 경쟁입찰 공고 등
- 낙찰결과: 낙찰자 선정, 업체 선정, 계약자 발표, 수주 확정 등
- 계약소식: 계약 체결, 계약 서명, MOU, 협약, 파트너십 등
- 관련뉴스: 입찰/낙찰 관련 정책, 동향, 분석, 일반 소식 등

뉴스 제목: {title}
뉴스 내용: {description}

응답 형식: 유형명만 정확히 입력 (입찰공고 또는 낙찰결과 또는 계약소식 또는 관련뉴스)
"""
        return prompt
    
    def create_bid_importance_prompt(self, title: str, description: str, category: str, bid_type: str) -> str:
        """입찰/낙찰 뉴스의 중요도 판단을 위한 프롬프트 생성"""
        
        prompt = f"""
다음 {category} 분야의 {bid_type} 뉴스의 비즈니스 중요도를 판단해주세요.

판단 기준:
- 매우중요: 수천억원 이상 대규모 계약, 국가 정책 변화, 신규 시장 창출
- 중요: 수백억원 규모 계약, 주요 기업 간 경쟁, 기술 혁신 관련
- 높음: 수십억원 규모 계약, 신규 사업기회, 규제 변화
- 보통: 일반적인 입찰/낙찰 소식, 중소 규모 계약
- 낮음: 단순 정보성 소식, 소규모 계약

특별 고려사항:
- 계약 금액이 명시된 경우 우선 고려
- 정부 정책이나 법률 변화 관련 시 중요도 상향
- 신기술이나 혁신적 사업 모델인 경우 중요도 상향

뉴스 제목: {title}
뉴스 내용: {description}

응답 형식: 중요도만 정확히 입력 (매우중요 또는 중요 또는 높음 또는 보통 또는 낮음)
"""
        return prompt
    
    def create_bid_summary_prompt(self, title: str, description: str, category: str, bid_type: str) -> str:
        """입찰/낙찰 뉴스 요약 생성을 위한 프롬프트 생성"""
        
        prompt = f"""
다음 {category} 분야의 {bid_type} 뉴스를 조대표님(CEO)에게 보고할 1-2문장의 핵심 요약을 작성해주세요.

요약 가이드라인:
- 비즈니스 기회 관점에서 핵심 포인트 중심
- 계약 금액, 사업 규모, 참여 기업 등 구체적 정보 포함
- 우리 사업에 미칠 영향이나 시사점 고려
- 입찰 일정, 조건, 주요 요구사항 등 실무적 정보 포함 (해당 시)
- 명확하고 간결한 문체로 작성

뉴스 제목: {title}
뉴스 내용: {description}

응답 형식: 1-2문장의 요약문만 작성
"""
        return prompt
    
    def call_llm(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """LLM API 호출 (재시도 로직 포함)"""
        if not self.model:
            return self.simulate_bid_llm_response(prompt)
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                result = response.text.strip()
                
                if result:
                    return result
                else:
                    logging.warning(f"[BID_LLM] 빈 응답 (시도 {attempt + 1}/{max_retries})")
                    
            except Exception as e:
                logging.error(f"[BID_LLM] API 호출 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 지수적 백오프
        
        logging.error(f"[BID_LLM] 최종 실패 - 기본값 반환")
        return None
    
    def simulate_bid_llm_response(self, prompt: str) -> str:
        """LLM API 키가 없을 때 시뮬레이션 응답"""
        if "유형" in prompt and "입찰" in prompt:
            # 유형 분류 시뮬레이션
            if any(word in prompt for word in ["공고", "모집", "제안서"]):
                return "입찰공고"
            elif any(word in prompt for word in ["낙찰", "선정", "수주"]):
                return "낙찰결과"
            elif any(word in prompt for word in ["계약", "체결", "협약"]):
                return "계약소식"
            else:
                return "관련뉴스"
        
        elif "중요도" in prompt:
            # 중요도 판단 시뮬레이션
            if any(word in prompt for word in ["대규모", "수천억", "정책", "국가"]):
                return "매우중요"
            elif any(word in prompt for word in ["수백억", "주요", "기술"]):
                return "중요"
            else:
                return "보통"
        
        elif "요약" in prompt:
            # 요약 시뮬레이션
            return "LLM API 키 미설정으로 인한 시뮬레이션 요약입니다."
        
        return "시뮬레이션 응답"
    
    def extract_bid_type(self, response: str) -> str:
        """LLM 응답에서 입찰/낙찰 유형 추출"""
        valid_types = BidDatabaseFields.TYPE_OPTIONS
        
        for bid_type in valid_types:
            if bid_type in response:
                return bid_type
        
        # 기본값
        return "관련뉴스"
    
    def extract_importance(self, response: str) -> str:
        """LLM 응답에서 중요도 추출"""
        valid_importance = ["매우중요", "중요", "높음", "보통", "낮음"]
        
        for importance in valid_importance:
            if importance in response:
                return importance
        
        # 기본값
        return "보통"
    
    def detect_amount_in_text(self, text: str) -> Optional[str]:
        """텍스트에서 금액 정보 추출"""
        # 금액 관련 패턴 매칭
        amount_patterns = [
            r'(\d+)조\s*원',
            r'(\d+)천억\s*원',
            r'(\d+)백억\s*원',
            r'(\d+)억\s*원',
            r'(\d+)\s*million',
            r'(\d+)\s*billion',
            r'\$\s*(\d+)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def process_single_bid_article(self, article: Dict) -> Dict:
        """단일 입찰/낙찰 뉴스 기사 LLM 처리"""
        title = article.get('제목', '')
        description = article.get('주요내용', '')
        category = article.get('분야', [''])[0] if article.get('분야') else ''
        
        logging.info(f"[BID_LLM] 처리 중: {title[:30]}...")
        
        try:
            # 1. 입찰/낙찰 유형 분류
            type_prompt = self.create_bid_type_prompt(title, description)
            type_response = self.call_llm(type_prompt)
            bid_type = self.extract_bid_type(type_response) if type_response else "관련뉴스"
            
            # 2. 중요도 판단
            importance_prompt = self.create_bid_importance_prompt(title, description, category, bid_type)
            importance_response = self.call_llm(importance_prompt)
            importance = self.extract_importance(importance_response) if importance_response else "보통"
            
            # 3. 요약 생성
            summary_prompt = self.create_bid_summary_prompt(title, description, category, bid_type)
            summary_response = self.call_llm(summary_prompt)
            summary = summary_response if summary_response else description[:200]
            
            # 4. 금액 정보 추출
            amount_info = self.detect_amount_in_text(f"{title} {description}")
            
            # 기사 정보 업데이트
            article['유형'] = bid_type
            article['중요도'] = importance
            article['주요내용'] = summary
            article['금액정보'] = amount_info  # 추가 정보
            article['LLM처리완료'] = True
            article['처리시간'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            logging.info(f"[BID_LLM] 완료: {category} | {bid_type} | {importance}")
            
            # API 호출 간격 (Rate limit 방지)
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"[BID_LLM] 처리 실패: {str(e)}")
            # 실패 시 기본값 유지
            article['LLM처리완료'] = False
        
        return article
    
    def process_bid_articles_batch(self, articles: List[Dict], batch_size: int = 3) -> List[Dict]:
        """입찰/낙찰 뉴스 기사들 배치 처리"""
        total = len(articles)
        processed = []
        
        logging.info(f"[BID_LLM] {total}건 입찰/낙찰 기사 처리 시작 (배치 크기: {batch_size})")
        
        for i in range(0, total, batch_size):
            batch = articles[i:i + batch_size]
            logging.info(f"[BID_LLM] 배치 {i//batch_size + 1}/{(total-1)//batch_size + 1} 처리 중...")
            
            for article in batch:
                processed_article = self.process_single_bid_article(article)
                processed.append(processed_article)
            
            # 배치 간 대기 시간
            if i + batch_size < total:
                time.sleep(3)
        
        logging.info(f"[BID_LLM] 전체 처리 완료: {len(processed)}건")
        return processed
    
    def generate_bid_processing_report(self, articles: List[Dict]) -> str:
        """입찰/낙찰 뉴스 처리 결과 리포트 생성"""
        total = len(articles)
        
        # 유형별 분포
        type_counts = {}
        for bid_type in BidDatabaseFields.TYPE_OPTIONS:
            count = len([a for a in articles if a.get('유형') == bid_type])
            type_counts[bid_type] = count
        
        # 중요도별 분포
        importance_counts = {}
        for importance in ["매우중요", "중요", "높음", "보통", "낮음"]:
            count = len([a for a in articles if a.get('중요도') == importance])
            importance_counts[importance] = count
        
        # 분야별 분포
        category_counts = {}
        for category in BidDatabaseFields.CATEGORY_OPTIONS:
            count = len([a for a in articles if category in a.get('분야', [])])
            category_counts[category] = count
        
        # LLM 처리 성공률
        success_count = len([a for a in articles if a.get('LLM처리완료', False)])
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        report = f"""
📊 입찰/낙찰 뉴스 LLM 처리 결과 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 전체 처리: {total}건

🏷️ 유형별 분류:
  📋 입찰공고: {type_counts.get('입찰공고', 0)}건
  🎯 낙찰결과: {type_counts.get('낙찰결과', 0)}건
  📝 계약소식: {type_counts.get('계약소식', 0)}건
  📰 관련뉴스: {type_counts.get('관련뉴스', 0)}건

⭐ 중요도별 분포:
  🔴 매우중요: {importance_counts.get('매우중요', 0)}건
  🟠 중요: {importance_counts.get('중요', 0)}건
  🟡 높음: {importance_counts.get('높음', 0)}건
  🟢 보통: {importance_counts.get('보통', 0)}건
  ⚪ 낮음: {importance_counts.get('낮음', 0)}건

🏢 분야별 분포:
  🔋 신재생에너지: {category_counts.get('신재생에너지', 0)}건
  🛡️ 방위산업: {category_counts.get('방위산업', 0)}건

✨ LLM 처리 성공률: {success_rate:.1f}% ({success_count}/{total}건)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
    
    def save_processed_bid_data(self, articles: List[Dict], filename: str) -> bool:
        """처리된 입찰/낙찰 데이터 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            logging.info(f"[BID_LLM] {filename}에 {len(articles)}건 저장 완료")
            return True
        except Exception as e:
            logging.error(f"[BID_LLM] 파일 저장 실패: {str(e)}")
            return False

def main():
    """메인 실행 함수"""
    logging.info("[BID_LLM] 입찰/낙찰 뉴스 LLM 처리 시작")
    
    try:
        # 최근 수집된 입찰/낙찰 데이터 로드
        import os
        import glob
        
        # data 폴더에서 가장 최근 bid_news 파일 찾기
        bid_files = glob.glob("data/bid_news_*.json")
        if not bid_files:
            logging.error("[BID_LLM] 처리할 입찰/낙찰 데이터 파일이 없습니다.")
            return
        
        latest_file = max(bid_files, key=os.path.getctime)
        logging.info(f"[BID_LLM] 파일 로드: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        # LLM 프로세서 초기화
        processor = BidLLMProcessor()
        
        # 배치 처리
        processed_articles = processor.process_bid_articles_batch(articles)
        
        # 처리 결과 리포트
        report = processor.generate_bid_processing_report(processed_articles)
        logging.info(report)
        
        # 처리된 데이터 저장
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_file = f"data/processed_bid_news_{timestamp}.json"
        
        if processor.save_processed_bid_data(processed_articles, output_file):
            logging.info(f"[BID_LLM] 처리 완료: {len(processed_articles)}건")
        else:
            logging.error("[BID_LLM] 저장 실패")
            
    except Exception as e:
        logging.error(f"[BID_LLM] 실행 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main() 