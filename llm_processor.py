#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 기반 뉴스 분류 및 요약 처리 모듈
작성일: 2025년 1월 12일
작성자: 서대리 (Lead Developer)
목적: Gemini-2.0-flash를 활용한 뉴스 자동 분류, 요약, 중요도 판단

주요 기능:
- 뉴스 카테고리 자동 분류 (방위산업/신재생에너지/보험중개)
- 조대표님 맞춤 요약 생성 (1-2문장)
- 비즈니스 중요도 판단 (낮음/보통/높음/매우중요)
"""

import json
import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from mvp_config import APIConfig, BusinessKeywords, ProcessingConfig

# Google Generative AI 라이브러리 (설치 필요: pip install google-generativeai)
try:
    import google.generativeai as genai
except ImportError:
    logging.error("google-generativeai 라이브러리가 설치되지 않았습니다. pip install google-generativeai 실행해주세요.")
    exit(1)

class LLMProcessor:
    """LLM 기반 뉴스 처리기"""
    
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
    
    def create_classification_prompt(self, title: str, description: str) -> str:
        """뉴스 분류를 위한 프롬프트 생성"""
        categories = list(BusinessKeywords.get_all_categories().keys())
        
        prompt = f"""
다음 뉴스를 분석하여 가장 적합한 카테고리로 분류해주세요.

카테고리 옵션:
- 방위산업: 국방, 방산, 군수산업, K-방산, 무기 수출 관련
- 신재생에너지: 태양광, 풍력, ESS, 배터리, 에너지저장장치 관련  
- 보험중개: 보험업계, 보험상품, 보험영업, 보험정책 관련

뉴스 제목: {title}
뉴스 내용: {description}

응답 형식: 카테고리명만 정확히 입력 (방위산업 또는 신재생에너지 또는 보험중개)
"""
        return prompt
    
    def create_importance_prompt(self, title: str, description: str, category: str) -> str:
        """중요도 판단을 위한 프롬프트 생성"""
        
        prompt = f"""
다음 {category} 관련 뉴스의 비즈니스 중요도를 판단해주세요.

판단 기준:
- 매우중요: 대규모 계약, 정책 변화, 시장 혁신, 규제 변경
- 높음: 신규 사업기회, 기술 혁신, 주요 투자 발표
- 보통: 일반적인 시장 동향, 기업 소식
- 낮음: 단순 소식, 예상 가능한 내용

뉴스 제목: {title}
뉴스 내용: {description}

응답 형식: 중요도만 정확히 입력 (매우중요 또는 높음 또는 보통 또는 낮음)
"""
        return prompt
    
    def create_summary_prompt(self, title: str, description: str, category: str) -> str:
        """요약 생성을 위한 프롬프트 생성"""
        
        prompt = f"""
다음 {category} 뉴스를 조대표님(CEO)에게 보고할 1-2문장의 핵심 요약을 작성해주세요.

요약 가이드라인:
- 비즈니스 관점에서 핵심 포인트 중심
- 구체적인 수치나 금액이 있다면 포함
- 우리 사업에 미칠 영향 고려
- 명확하고 간결한 문체

뉴스 제목: {title}
뉴스 내용: {description}

응답 형식: 1-2문장의 요약문만 작성
"""
        return prompt
    
    def call_llm(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """LLM API 호출 (재시도 로직 포함)"""
        if not self.model:
            return self.simulate_llm_response(prompt)
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                result = response.text.strip()
                
                if result:
                    return result
                else:
                    logging.warning(f"[LLM] 빈 응답 (시도 {attempt + 1}/{max_retries})")
                    
            except Exception as e:
                logging.error(f"[LLM] API 호출 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 지수적 백오프
        
        logging.error(f"[LLM] 최종 실패 - 기본값 반환")
        return None
    
    def simulate_llm_response(self, prompt: str) -> str:
        """LLM API 키가 없을 때 시뮬레이션 응답"""
        if "카테고리" in prompt:
            # 카테고리 분류 시뮬레이션
            if any(word in prompt for word in ["방산", "국방", "군수"]):
                return "방위산업"
            elif any(word in prompt for word in ["에너지", "태양광", "풍력", "ESS"]):
                return "신재생에너지"
            elif any(word in prompt for word in ["보험", "보험업"]):
                return "보험중개"
            else:
                return "신재생에너지"  # 기본값
        
        elif "중요도" in prompt:
            # 중요도 판단 시뮬레이션
            if any(word in prompt for word in ["대규모", "정책", "혁신", "계약"]):
                return "높음"
            else:
                return "보통"
        
        elif "요약" in prompt:
            # 요약 시뮬레이션
            return "LLM API 키 미설정으로 인한 시뮬레이션 요약입니다."
        
        return "시뮬레이션 응답"
    
    def extract_category(self, response: str) -> str:
        """LLM 응답에서 카테고리 추출"""
        valid_categories = ["방위산업", "신재생에너지", "보험중개"]
        
        for category in valid_categories:
            if category in response:
                return category
        
        # 기본값
        return "신재생에너지"
    
    def extract_importance(self, response: str) -> str:
        """LLM 응답에서 중요도 추출"""
        valid_importance = ["매우중요", "높음", "보통", "낮음"]
        
        for importance in valid_importance:
            if importance in response:
                return importance
        
        # 기본값
        return "보통"
    
    def process_single_article(self, article: Dict) -> Dict:
        """단일 뉴스 기사 LLM 처리"""
        title = article.get('제목', '')
        description = article.get('요약', '')
        
        logging.info(f"[LLM] 처리 중: {title[:30]}...")
        
        try:
            # 1. 카테고리 분류
            category_prompt = self.create_classification_prompt(title, description)
            category_response = self.call_llm(category_prompt)
            category = self.extract_category(category_response) if category_response else "신재생에너지"
            
            # 2. 중요도 판단
            importance_prompt = self.create_importance_prompt(title, description, category)
            importance_response = self.call_llm(importance_prompt)
            importance = self.extract_importance(importance_response) if importance_response else "보통"
            
            # 3. 요약 생성
            summary_prompt = self.create_summary_prompt(title, description, category)
            summary_response = self.call_llm(summary_prompt)
            summary = summary_response if summary_response else description[:200]
            
            # 기사 정보 업데이트
            article['태그'] = [category]
            article['중요도'] = importance
            article['요약'] = summary
            article['요약 품질 평가'] = "높음" if summary_response else "낮음"
            
            logging.info(f"[LLM] 완료: {category} | {importance} | {len(summary)}자")
            
            # API 호출 간격 (Rate limit 방지)
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"[LLM] 처리 실패: {str(e)}")
            # 실패 시 기본값 유지
        
        return article
    
    def process_articles_batch(self, articles: List[Dict], batch_size: int = 5) -> List[Dict]:
        """뉴스 기사들 배치 처리"""
        total = len(articles)
        processed = []
        
        logging.info(f"[LLM] {total}건 기사 처리 시작 (배치 크기: {batch_size})")
        
        for i in range(0, total, batch_size):
            batch = articles[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            logging.info(f"[LLM] 배치 {batch_num}/{total_batches} 처리 중...")
            
            for article in batch:
                processed_article = self.process_single_article(article)
                processed.append(processed_article)
            
            # 배치 간 휴식 (API Rate limit 방지)
            if i + batch_size < total:
                time.sleep(3)
        
        logging.info(f"[LLM] 전체 처리 완료: {len(processed)}건")
        return processed
    
    def generate_processing_report(self, articles: List[Dict]) -> str:
        """처리 결과 리포트 생성"""
        if not articles:
            return "처리된 기사가 없습니다."
        
        # 통계 계산
        categories = {}
        importance_levels = {}
        quality_levels = {}
        
        for article in articles:
            # 카테고리별
            category = article.get('태그', ['기타'])[0]
            categories[category] = categories.get(category, 0) + 1
            
            # 중요도별
            importance = article.get('중요도', '보통')
            importance_levels[importance] = importance_levels.get(importance, 0) + 1
            
            # 요약 품질별
            quality = article.get('요약 품질 평가', '보통')
            quality_levels[quality] = quality_levels.get(quality, 0) + 1
        
        report = f"""
📊 LLM 처리 결과 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 전체 처리: {len(articles)}건

🏷️ 카테고리별 분류:
"""
        for category, count in categories.items():
            emoji = "🛡️" if "방위" in category else "🔋" if "에너지" in category else "🏢"
            report += f"  {emoji} {category}: {count}건\n"
        
        report += f"\n⭐ 중요도별 분포:\n"
        for importance, count in importance_levels.items():
            emoji = "🔴" if importance == "매우중요" else "🟠" if importance == "높음" else "🟢"
            report += f"  {emoji} {importance}: {count}건\n"
        
        report += f"\n✨ 요약 품질:\n"
        for quality, count in quality_levels.items():
            emoji = "🔥" if quality == "높음" else "⚡" if quality == "보통" else "❄️"
            report += f"  {emoji} {quality}: {count}건\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        return report

def main():
    """메인 실행 함수 (테스트용)"""
    print("🤖 LLM 처리기 테스트 시작")
    print("=" * 50)
    
    # 샘플 데이터로 테스트
    sample_articles = [
        {
            "제목": "한국형 차세대 전투기 KF-21, 첫 해외 수출 계약 체결",
            "요약": "한국항공우주산업(KAI)이 개발한 KF-21 보라매 전투기가 첫 해외 수출 계약을 체결했다고 발표했습니다.",
            "URL": "https://example.com/news1",
            "발행일": "2025-01-12"
        },
        {
            "제목": "정부, 해상풍력 발전단지 확대 정책 발표",
            "요약": "정부가 2030년까지 해상풍력 발전용량을 현재의 3배로 확대하는 정책을 발표했습니다.",
            "URL": "https://example.com/news2", 
            "발행일": "2025-01-12"
        }
    ]
    
    processor = LLMProcessor()
    processed_articles = processor.process_articles_batch(sample_articles)
    
    print("\n" + processor.generate_processing_report(processed_articles))
    
    # 결과 출력
    for i, article in enumerate(processed_articles, 1):
        print(f"\n📰 기사 {i}:")
        print(f"  제목: {article['제목']}")
        print(f"  카테고리: {article['태그'][0]}")
        print(f"  중요도: {article['중요도']}")
        print(f"  요약: {article['요약'][:100]}...")

if __name__ == "__main__":
    main() 