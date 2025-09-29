# LLM 활용 방안 구체화 - Gemini 프롬프트 전략

**작성일**: 2025년 8월 22일 15:48 KST  
**작성자**: 노팀장 (Technical Advisor)  
**대상**: 조대표님 (Project Owner), 나실장 (Project Manager), 서대리 (Lead Developer)  
**목적**: Gemini Pro를 활용한 최적화된 의미 추출 시스템 구축

---

## I. 전략 개요

### 1.1 기본 방향
**조대표님 특화 LLM 활용**:
- 보험중개업 + 에너지 + 방산 도메인 전문성 반영
- GitMind 기반 구조화 사고방식 지원
- 30년 경험 지식과 신규 정보의 창의적 연결

**서대리 구축 시스템 활용**:
- 기존 `llm_extractor_test.py` 기반 확장
- Gemini Pro API 2개 키 최적 활용
- 문서 파싱 → LLM 분석 → 노션 업로드 파이프라인 완성

### 1.2 핵심 추출 목표
1. **핵심 키워드**: 비즈니스 기회 식별을 위한 전문 용어
2. **문서 요약**: 조대표님 의사결정을 위한 핵심 정보
3. **관련 인물**: 인적 네트워크 확장 기회 발굴
4. **창의적 연결**: 기존 지식과의 혁신적 조합 제안

---

## II. 도메인별 특화 프롬프트 전략

### 2.1 보험중개업 특화 키워드 추출

#### 기본 프롬프트 템플릿:
```
당신은 20년 경험의 글로벌 보험중개 전문가입니다. 
다음 문서에서 보험중개업과 관련된 핵심 키워드를 추출하세요.

[문서 내용]
{document_text}

다음 관점에서 키워드를 추출하세요:
1. 보험상품 관련: (예: 건설공사보험, 배상책임보험, 사이버보험)
2. 리스크 요소: (예: 정치적위험, 환율위험, 기술적위험)
3. 산업 분야: (예: 신재생에너지, 방위산업, 해상풍력)
4. 규제/정책: (예: RPS, K-방산, IFRS17)
5. 지역/국가: (예: 미국, 유럽, 동남아)
6. 기업/기관: (예: 효성중공업, 한화시스템, K-SURE)

결과를 JSON 형식으로 출력하세요:
{
  "insurance_products": ["키워드1", "키워드2"],
  "risk_factors": ["키워드1", "키워드2"],
  "industries": ["키워드1", "키워드2"],
  "regulations": ["키워드1", "키워드2"],
  "regions": ["키워드1", "키워드2"],
  "organizations": ["키워드1", "키워드2"]
}
```

#### 에너지 분야 특화 버전:
```
당신은 신재생에너지 분야 보험 전문가입니다.
다음 문서에서 에너지 산업 보험중개와 관련된 키워드를 추출하세요.

[문서 내용]
{document_text}

특별히 다음 영역에 주목하세요:
- 태양광/풍력 프로젝트 리스크: (예: 출력보증, 날씨위험, 설비고장)
- ESS 관련 위험: (예: 화재위험, 배터리성능, 열폭주)
- PF 대출 조건: (예: 건설공사보험, 재물보험, 기계보험)
- 정부 정책: (예: RPS, REC, 탄소중립, RE100)
- 프로젝트 단계: (예: 개발, 건설, 운영, 금융조달)

결과를 JSON으로 출력하되, 각 키워드에 보험중개 기회도 점수(1-10)를 포함하세요.
```

#### 방산 분야 특화 버전:
```
당신은 방위산업 보험 전문가입니다.
다음 문서에서 방산 분야 보험중개 기회를 분석하세요.

[문서 내용]
{document_text}

다음 관점에서 분석하세요:
- 방산수출 관련: (예: 정치적위험보험, 신용보험, 수출보증)
- 기술보안: (예: 사이버보안, 기술유출, 산업스파이)
- 국제협력: (예: 오프셋, 기술이전, 공동개발)
- 규제환경: (예: 무기수출통제, 국제제재, 수출허가)

각 키워드마다 록톤코리아의 차별화 가능 영역을 함께 제시하세요.
```

### 2.2 지능형 문서 요약 전략

#### 의사결정 지원형 요약:
```
당신은 조대표(록톤코리아 영업대표)의 개인 비서입니다.
다음 문서를 조대표의 의사결정에 도움이 되도록 요약하세요.

[문서 내용]
{document_text}

요약 기준:
1. 비즈니스 기회: 새로운 영업 기회나 시장 기회
2. 리스크 경고: 주의해야 할 위험 요소나 변화
3. 액션 아이템: 조대표가 취해야 할 구체적 행동
4. 인적 네트워크: 연결 가능한 키 인물이나 기관

결과를 다음 형식으로 출력하세요:

📊 **핵심 요약** (2문장)
[문서의 가장 중요한 내용을 2문장으로 요약]

🎯 **비즈니스 기회**
- [구체적 기회 1]
- [구체적 기회 2]

⚠️ **주의사항**
- [위험요소나 고려사항]

✅ **권장 액션**
- [즉시 실행 가능한 행동]
- [중기적 준비사항]

👥 **키 인물**
- [연결 고려 대상 인물 및 이유]
```

#### GitMind 구조 반영 요약:
```
이 문서를 GitMind 마인드맵 구조로 정리하여 요약하세요.

[문서 내용]
{document_text}

마인드맵 구조:
중심 주제 → 주요 가지(3-5개) → 세부 항목

결과를 다음과 같이 구조화하세요:

🎯 **중심 주제**: [문서의 핵심 주제]

📋 **주요 가지**:
1. **[가지1 제목]**
   - 세부 항목 1
   - 세부 항목 2
   
2. **[가지2 제목]**
   - 세부 항목 1
   - 세부 항목 2

3. **[가지3 제목]**
   - 세부 항목 1
   - 세부 항목 2

🔗 **연결 고리**: [다른 프로젝트나 지식과의 연결점]
```

### 2.3 관련 인물 추출 및 네트워크 분석

#### 인물 정보 추출 프롬프트:
```
당신은 비즈니스 네트워킹 전문가입니다.
다음 문서에서 조대표(보험중개업)에게 가치 있는 인물들을 추출하세요.

[문서 내용]
{document_text}

다음 정보를 JSON 형식으로 추출하세요:

{
  "key_persons": [
    {
      "name": "인물명",
      "title": "직책",
      "organization": "소속 기관",
      "expertise": ["전문분야1", "전문분야2"],
      "relevance_to_insurance": "보험중개업과의 연관성 설명",
      "networking_priority": "높음/보통/낮음",
      "potential_opportunity": "구체적 협력 기회"
    }
  ],
  "organizations": [
    {
      "name": "기관명",
      "type": "정부기관/민간기업/협회",
      "role": "역할이나 영향력",
      "insurance_relevance": "보험중개와의 관련성"
    }
  ]
}

특별히 다음 유형의 인물에 주목하세요:
- 정책 결정권자 (정부 고위직, 공기업 임원)
- 기술 전문가 (R&D 센터장, CTO)
- 사업 의사결정자 (CEO, 사업부장)
- 금융 관계자 (은행, 투자사, 보험사)
```

#### 인적 네트워크 확장 분석:
```
다음 인물 정보를 바탕으로 조대표의 인적 네트워크 확장 전략을 제안하세요.

[기존 네트워크]
{existing_network}

[새로 발견된 인물]
{new_persons}

분석 결과:

🌐 **네트워크 갭 분석**
- 부족한 영역: [현재 네트워크에서 부족한 분야]
- 중복 영역: [과도하게 집중된 분야]

🎯 **우선 접촉 대상** (상위 3명)
1. [인물명] - [접촉 이유 및 기대 효과]
2. [인물명] - [접촉 이유 및 기대 효과]
3. [인물명] - [접촉 이유 및 기대 효과]

🤝 **접근 전략**
- [구체적 접촉 방법 및 시나리오]

🔄 **네트워크 연결 기회**
- [기존 인물을 통한 새 인물 소개 가능성]
```

---

## III. 창의적 연결 시스템

### 3.1 기존 지식과의 연결 발굴

#### 지식 연결 프롬프트:
```
당신은 창의적 사고 전문가입니다.
다음 새로운 정보와 기존 지식을 연결하여 혁신적 아이디어를 제안하세요.

[새로운 정보]
{new_document}

[기존 지식 베이스]
{existing_knowledge}

다음 관점에서 창의적 연결을 찾으세요:

🧩 **직접적 연결**
- [명확한 관련성이 있는 연결점]

🌟 **간접적 연결**
- [일견 관련 없어 보이지만 창의적으로 연결 가능한 영역]

💡 **혁신적 아이디어**
- [기존 지식과 새 정보의 조합으로 만들 수 있는 새로운 비즈니스 아이디어]

⚡ **실행 가능한 아이디어** (상위 3개)
1. [아이디어명]: [구체적 실행 방안]
2. [아이디어명]: [구체적 실행 방안]
3. [아이디어명]: [구체적 실행 방안]

🎯 **즉시 검증 가능한 아이디어**
- [조대표가 당장 테스트해볼 수 있는 소규모 아이디어]
```

### 3.2 30년 아카이브 활용 프롬프트

#### 레거시 지식 재발견:
```
당신은 디지털 아카이브 전문가입니다.
조대표의 30년 경험과 축적된 정보를 바탕으로 다음 새 정보의 가치를 재평가하세요.

[새로운 문서]
{new_document}

[30년 아카이브 샘플]
{archive_sample}

분석 관점:

📚 **과거 경험과의 연결**
- [유사한 과거 프로젝트나 경험]
- [과거 실패/성공 사례에서 얻을 교훈]

🔄 **반복 패턴 인식**
- [30년간 반복되는 비즈니스 패턴]
- [변화하는 트렌드와 불변하는 원칙]

💎 **숨겨진 가치 발굴**
- [과거에는 중요하지 않았지만 지금은 가치 있는 정보]
- [재조명할 만한 아이디어나 인사이트]

🚀 **미래 예측**
- [과거 패턴을 바탕으로 한 미래 전망]
- [다가올 기회에 대한 준비 방안]
```

---

## IV. 단계별 프롬프트 실행 전략

### 4.1 1차 분석 (기본 정보 추출)

**실행 순서**:
1. **문서 유형 판별** → 도메인별 특화 프롬프트 선택
2. **기본 키워드 추출** → 보험/에너지/방산 분야별 키워드
3. **핵심 요약 생성** → 의사결정 지원형 2문장 요약
4. **인물 정보 추출** → 네트워킹 기회 분석

### 4.2 2차 분석 (심화 연결)

**실행 순서**:
1. **기존 지식과 연결** → Knowledge_Graph DB 참조
2. **인적 네트워크 분석** → People_Network DB 연결
3. **창의적 아이디어 생성** → Ideas_Incubator DB 입력
4. **실행 계획 제안** → Projects_Master DB 연결

### 4.3 3차 분석 (전략적 활용)

**실행 순서**:
1. **비즈니스 기회 평가** → 수익성 및 실현 가능성 점수화
2. **리스크 분석** → 잠재적 위험 요소 식별
3. **우선순위 제안** → 조대표 일정 및 자원 고려
4. **장기 전략 연결** → 30년 비전과의 정합성 검토

---

## V. API 최적화 전략

### 5.1 Gemini Pro 2개 키 활용 방안

**Key 1 (Primary)**: 
- 대량 문서 일괄 처리
- 기본 키워드 추출
- 표준 요약 생성

**Key 2 (Secondary)**:
- 창의적 연결 분석
- 복잡한 전략 분석
- 인적 네트워크 분석

**로드 밸런싱**:
```python
def select_api_key(task_type, complexity_level):
    if task_type == "basic_extraction" and complexity_level <= 5:
        return API_KEY_1
    elif task_type == "creative_analysis" or complexity_level > 7:
        return API_KEY_2
    else:
        return random.choice([API_KEY_1, API_KEY_2])
```

### 5.2 토큰 효율성 최적화

**문서 분할 전략**:
- 5000토큰 단위로 분할
- 중요 섹션 우선 처리
- 요약 → 상세 분석 순차 진행

**프롬프트 재사용**:
- 도메인별 템플릿 캐싱
- 공통 지시사항 모듈화
- 동적 프롬프트 조합

---

## VI. 품질 보증 및 검증

### 6.1 추출 품질 검증 기준

**키워드 추출 품질**:
- 도메인 관련성: 80% 이상
- 중복률: 20% 이하
- 신규 키워드 발굴률: 30% 이상

**요약 품질**:
- 핵심 정보 포함도: 90% 이상
- 조대표 의사결정 도움도: 주관적 평가 4점/5점 이상
- 실행 가능한 액션 아이템 포함: 필수

**인물 추출 정확도**:
- 인물명 정확도: 95% 이상
- 직책/소속 정확도: 85% 이상
- 비즈니스 연관성 적절성: 80% 이상

### 6.2 지속적 개선 시스템

**피드백 루프**:
1. **조대표 평가** → 월 1회 추출 결과 평가
2. **프롬프트 개선** → 평가 결과 기반 프롬프트 튜닝
3. **성능 모니터링** → API 호출 시간, 토큰 사용량 최적화
4. **도메인 확장** → 새로운 사업 영역 대응 프롬프트 개발

**A/B 테스트**:
- 프롬프트 버전별 성능 비교
- 키워드 추출 방식 최적화
- 요약 스타일 개인화

---

## VII. 실제 구현 가이드

### 7.1 서대리 기존 시스템 확장

**현재 `llm_extractor_test.py` 기반 확장**:
```python
# 도메인별 프롬프트 관리자
class DomainPromptManager:
    def __init__(self):
        self.insurance_prompts = self.load_insurance_prompts()
        self.energy_prompts = self.load_energy_prompts()
        self.defense_prompts = self.load_defense_prompts()
    
    def select_prompt(self, document_type, analysis_depth):
        # 문서 유형과 분석 깊이에 따른 최적 프롬프트 선택
        pass

# 다단계 분석 엔진
class MultiStageAnalyzer:
    def __init__(self, api_keys):
        self.primary_key = api_keys[0]
        self.secondary_key = api_keys[1]
        self.prompt_manager = DomainPromptManager()
    
    def analyze_document(self, document_text):
        # 1차: 기본 정보 추출
        basic_info = self.extract_basic_info(document_text)
        
        # 2차: 심화 연결 분석
        connections = self.analyze_connections(basic_info)
        
        # 3차: 전략적 인사이트
        insights = self.generate_insights(connections)
        
        return self.combine_results(basic_info, connections, insights)
```

### 7.2 노션 DB 연동 최적화

**자동 분류 및 태깅**:
```python
def auto_categorize_document(extracted_info):
    # LLM 추출 결과 → 노션 DB 속성 자동 매핑
    categories = {
        'insurance_products': '보험상품',
        'risk_factors': '리스크요소',
        'key_persons': '핵심인물',
        'business_opportunities': '사업기회'
    }
    
    notion_properties = {}
    for key, category in categories.items():
        if key in extracted_info:
            notion_properties[category] = extracted_info[key]
    
    return notion_properties
```

---

## VIII. 기대 효과 및 성공 지표

### 8.1 정량적 효과

**처리 효율성**:
- 문서 분석 시간: 수동 30분 → 자동 3분 (90% 단축)
- 키워드 추출 정확도: 95% 이상
- 인물 네트워크 확장: 월 평균 20명 → 50명 (150% 증가)

**비즈니스 임팩트**:
- 신규 비즈니스 기회 발굴: 월 평균 5건 → 15건 (200% 증가)
- 인적 네트워크 활용도: 30% → 70% (133% 증가)
- 아이디어 실행률: 10% → 40% (300% 증가)

### 8.2 정성적 효과

**조대표 업무 혁신**:
- "찾은 정보를 지식으로 연결 못함" → 자동 연결 시스템
- "구슬만 모으고 꿰지 못함" → AI 기반 아이디어 조합
- "30년 정보 아카이브" → 의미론적 지식 체계 완성

**의사결정 품질 향상**:
- 정보 기반 의사결정 비율 증가
- 위험 예측 정확도 향상
- 기회 포착 속도 개선

---

**전략 수립 완료**: 2025년 8월 22일 15:48 KST  
**다음 단계**: 서대리와 협업하여 프롬프트 시스템 실제 구현 착수

---

## VI. 하이브리드 시스템 구현 방안

### 6.1 노트북LM 워크스페이스 구축

#### 프로젝트별 소스 관리:
```
노트북LM 프로젝트 구성 전략:

📚 프로젝트 1: "조대표_30년_지식베이스"
├── 사업경험_연대기.pdf (주요 프로젝트 히스토리)
├── 성공실패_사례집.docx (교훈 모음)
├── 핵심인사이트_모음.pdf (깨달음과 원칙)
└── 인적네트워크_데이터베이스.xlsx

📚 프로젝트 2: "현재진행_프로젝트"
├── 록톤영업전략_v2.docx
├── GIA개발계획_전체.pdf  
├── 개인발전계획_2025.docx
└── 월간리뷰_모음.pdf

📚 프로젝트 3: "아이디어_인큐베이터"
├── GitMind_마인드맵_백업/
├── 창업아이디어_리스트.docx
├── 기술트렌드_분석노트.pdf
└── 미래예측_메모.txt

📚 프로젝트 4: "업계_전문정보"
├── 보험중개_전문자료/
├── 에너지산업_분석자료/
├── 방산업계_동향자료/
└── 정책변화_추적자료/
```

#### 노트북LM 활용 워크플로우:
```python
class NotebookLMManager:
    def __init__(self):
        self.projects = {
            'personal_knowledge': 'knowledge_base_project_id',
            'current_projects': 'current_work_project_id', 
            'idea_incubator': 'ideas_project_id',
            'industry_intel': 'industry_project_id'
        }
    
    def route_document_to_notebook(self, document_info):
        """문서 성격에 따라 적절한 노트북LM 프로젝트로 라우팅"""
        if self.is_personal_sensitive(document_info):
            return self.upload_to_project('personal_knowledge', document_info)
        elif self.is_current_work(document_info):
            return self.upload_to_project('current_projects', document_info)
        # ... 기타 분류 로직
    
    def analyze_with_context(self, query, project_context):
        """특정 프로젝트 컨텍스트로 노트북LM 분석 실행"""
        return self.notebook_api.chat(project_context, query)
```

### 6.2 Gemini Pro 연동 시스템

#### API 키 관리 및 로드 밸런싱:
```python
class HybridLLMController:
    def __init__(self):
        self.gemini_primary = GeminiClient(api_key_1)
        self.gemini_secondary = GeminiClient(api_key_2)
        self.notebook_manager = NotebookLMManager()
        
    def analyze_document(self, document_info):
        # 1단계: 민감도 평가
        sensitivity = self.assess_sensitivity(document_info)
        
        if sensitivity >= 8:  # 매우 민감
            return self.notebook_only_analysis(document_info)
        elif sensitivity <= 3:  # 공개 정보
            return self.gemini_only_analysis(document_info)
        else:  # 하이브리드 분석
            return self.hybrid_analysis(document_info)
    
    def hybrid_analysis(self, document_info):
        # 노트북LM: 개인 관점 분석
        personal_view = self.notebook_manager.analyze_with_personal_context(document_info)
        
        # Gemini Pro: 외부 시장 관점 분석
        market_view = self.gemini_# LLM 활용 방안 구체화 - Gemini 프롬프트 전략

**작성일**: 2025년 8월 22일 15:48 KST  
**작성자**: 노팀장 (Technical Advisor)  
**대상**: 조대표님 (Project Owner), 나실장 (Project Manager), 서대리 (Lead Developer)  
**목적**: Gemini Pro를 활용한 최적화된 의미 추출 시스템 구축

---

## I. 전략 개요

### 1.1 기본 방향
**조대표님 특화 하이브리드 LLM 활용**:
- 보험중개업 + 에너지 + 방산 도메인 전문성 반영
- GitMind 기반 구조화 사고방식 지원
- 30년 경험 지식과 신규 정보의 창의적 연결
- **로컬 자료 보안성 + 클라우드 확장성 동시 확보**

**이중 LLM 시스템 구축**:
- **Gemini Pro API**: 외부 정보 처리, 실시간 분석, 확장 가능성
- **구글 노트북LM**: 로컬 민감 자료, 심층 분석, 프라이버시 보장
- 기존 `llm_extractor_test.py` 기반 통합 확장

### 1.2 핵심 추출 목표
1. **핵심 키워드**: 비즈니스 기회 식별을 위한 전문 용어
2. **문서 요약**: 조대표님 의사결정을 위한 핵심 정보
3. **관련 인물**: 인적 네트워크 확장 기회 발굴
4. **창의적 연결**: 기존 지식과의 혁신적 조합 제안

---

## II. 하이브리드 LLM 전략 - Gemini Pro + 노트북LM

### 2.1 역할 분담 및 활용 영역

#### 구글 노트북LM 전담 영역:
**로컬 민감 자료 분석**:
- 조대표님의 30년 개인 아카이브 (15GB × 10계정)
- 사업 기밀 문서 (건설자재 유통업, 내부 전략 문서)
- 개인 메모 및 아이디어 노트 (GitMind, OneNote, 아이폰 메모)
- 고객 정보 및 계약 관련 문서

**심층 분석 특화**:
- 장기간 패턴 분석 (30년 아카이브 트렌드)
- 개인화된 지식 체계 구축
- 프라이빗 아이디어 인큐베이션
- 보안이 중요한 전략 수립

#### Gemini Pro API 전담 영역:
**외부 정보 실시간 처리**:
- 공개 뉴스, 보고서, 정책 문서
- 경쟁사 분석, 시장 동향
- 인물 정보 (공개된 프로필)
- 일반적인 업무 문서

**확장성 요구 작업**:
- 대량 문서 일괄 처리
- 실시간 정보 수집 연동
- 노션 DB 자동 업로드
- API 기반 자동화 시스템

### 2.2 노트북LM 특화 활용 방안

#### 로컬 지식 베이스 구축:
```
노트북LM 프로젝트 구조:

📁 GIA_조대표_개인지식베이스/
├── 📂 30년_아카이브/
│   ├── 사업경험_요약집.pdf
│   ├── 핵심인사이트_모음.docx
│   └── 실패성공_사례집.pdf
├── 📂 현재진행_프로젝트/
│   ├── 록톤영업전략.docx
│   ├── GIA개발계획.pdf
│   └── 개인발전계획.pdf
├── 📂 아이디어_노트/
│   ├── GitMind_마인드맵_모음/
│   ├── 개인메모_컬렉션.txt
│   └── 창업아이디어_리스트.docx
└── 📂 네트워크_정보/
    ├── 핵심인물_데이터베이스.xlsx
    ├── 업계관계도.pdf
    └── 미팅노트_모음.docx
```

#### 노트북LM 전용 프롬프트 전략:

**개인 경험 기반 분석**:
```
당신은 조대표의 30년 사업 경험을 모두 알고 있는 개인 컨설턴트입니다.
업로드된 개인 아카이브를 바탕으로 다음 새로운 상황을 분석하세요.

[새로운 상황/문제]
{current_situation}

[조대표의 과거 경험에서]
1. 🎯 유사한 과거 경험:
   - 성공 사례: [구체적 사례와 성공 요인]
   - 실패 사례: [실패 원인과 교훈]

2. 🧠 축적된 인사이트:
   - [과거 경험에서 도출된 핵심 원칙]
   - [반복되는 성공 패턴]

3. 💡 개인화된 해결 방안:
   - [조대표의 강점을 활용한 접근법]
   - [과거 실패를 피하는 전략]

4. 🚀 실행 계획:
   - [조대표 스타일에 맞는 구체적 단계]
   - [활용 가능한 기존 네트워크/자원]
```

**아이디어 진화 추적**:
```
조대표의 아이디어 노트와 과거 프로젝트를 바탕으로 
다음 새로운 아이디어의 발전 가능성을 분석하세요.

[새로운 아이디어]
{new_idea}

[개인 아카이브 분석 결과]
📈 **아이디어 진화도**:
- 초기 아이디어 (20XX년): [과거 유사 아이디어]
- 중간 발전 (20XX년): [발전된 형태]
- 현재 완성도: [현재 아이디어 수준]

🎯 **실현 가능성**:
- 조대표의 현재 역량: [보유 스킬/네트워크 매칭도]
- 필요한 추가 자원: [부족한 부분]
- 예상 실행 기간: [현실적 타임라인]

⚡ **즉시 실행 가능한 첫 단계**:
- [오늘 당장 할 수 있는 작업]
- [1주일 내 검증 방법]
```

### 2.3 하이브리드 연동 시스템

#### 정보 분류 및 라우팅:
```python
class HybridLLMRouter:
    def __init__(self):
        self.gemini_client = GeminiProClient()
        self.notebookLM_processor = NotebookLMProcessor()
        
    def route_document(self, document_info):
        sensitivity_score = self.assess_sensitivity(document_info)
        
        if sensitivity_score > 7:  # 민감 정보
            return self.notebookLM_processor.analyze(document_info)
        elif sensitivity_score < 3:  # 공개 정보
            return self.gemini_client.analyze(document_info)
        else:  # 혼합 처리
            return self.hybrid_analysis(document_info)
    
    def assess_sensitivity(self, document_info):
        # 문서 내용, 출처, 유형 기반 민감도 평가
        sensitive_keywords = ['계약', '재무', '전략', '개인']
        public_sources = ['뉴스', '정책', '공개보고서']
        # 점수 계산 로직
        pass
```

#### 크로스 검증 시스템:
```python
def cross_validate_insights(gemini_result, notebookLM_result):
    """
    Gemini Pro 외부 분석과 노트북LM 내부 분석 결과 교차 검증
    """
    validation = {
        'external_perspective': gemini_result,
        'internal_perspective': notebookLM_result,
        'consensus_insights': find_common_insights(gemini_result, notebookLM_result),
        'conflicting_views': identify_conflicts(gemini_result, notebookLM_result),
        'synthesis_recommendation': synthesize_recommendations(gemini_result, notebookLM_result)
    }
    return validation
```

---

## III. 도메인별 특화 프롬프트 전략

### 3.1 보험중개업 특화 키워드 추출 (Gemini Pro 담당)

#### 기본 프롬프트 템플릿:
```
당신은 20년 경험의 글로벌 보험중개 전문가입니다. 
다음 문서에서 보험중개업과 관련된 핵심 키워드를 추출하세요.

[문서 내용]
{document_text}

다음 관점에서 키워드를 추출하세요:
1. 보험상품 관련: (예: 건설공사보험, 배상책임보험, 사이버보험)
2. 리스크 요소: (예: 정치적위험, 환율위험, 기술적위험)
3. 산업 분야: (예: 신재생에너지, 방위산업, 해상풍력)
4. 규제/정책: (예: RPS, K-방산, IFRS17)
5. 지역/국가: (예: 미국, 유럽, 동남아)
6. 기업/기관: (예: 효성중공업, 한화시스템, K-SURE)

결과를 JSON 형식으로 출력하세요:
{
  "insurance_products": ["키워드1", "키워드2"],
  "risk_factors": ["키워드1", "키워드2"],
  "industries": ["키워드1", "키워드2"],
  "regulations": ["키워드1", "키워드2"],
  "regions": ["키워드1", "키워드2"],
  "organizations": ["키워드1", "키워드2"]
}
```

#### 에너지 분야 특화 버전:
```
당신은 신재생에너지 분야 보험 전문가입니다.
다음 문서에서 에너지 산업 보험중개와 관련된 키워드를 추출하세요.

[문서 내용]
{document_text}

특별히 다음 영역에 주목하세요:
- 태양광/풍력 프로젝트 리스크: (예: 출력보증, 날씨위험, 설비고장)
- ESS 관련 위험: (예: 화재위험, 배터리성능, 열폭주)
- PF 대출 조건: (예: 건설공사보험, 재물보험, 기계보험)
- 정부 정책: (예: RPS, REC, 탄소중립, RE100)
- 프로젝트 단계: (예: 개발, 건설, 운영, 금융조달)

결과를 JSON으로 출력하되, 각 키워드에 보험중개 기회도 점수(1-10)를 포함하세요.
```

#### 방산 분야 특화 버전:
```
당신은 방위산업 보험 전문가입니다.
다음 문서에서 방산 분야 보험중개 기회를 분석하세요.

[문서 내용]
{document_text}

다음 관점에서 분석하세요:
- 방산수출 관련: (예: 정치적위험보험, 신용보험, 수출보증)
- 기술보안: (예: 사이버보안, 기술유출, 산업스파이)
- 국제협력: (예: 오프셋, 기술이전, 공동개발)
- 규제환경: (예: 무기수출통제, 국제제재, 수출허가)

각 키워드마다 록톤코리아의 차별화 가능 영역을 함께 제시하세요.
```

### 3.2 지능형 문서 요약 전략 (하이브리드 접근)

#### 노트북LM 전용 개인화 요약:
```
[조대표의 개인 아카이브 기반]
이 문서를 조대표의 과거 경험과 현재 상황을 고려하여 개인화된 요약을 제공하세요.

[문서 내용]
{document_text}

[개인화 요약 기준]
1. **과거 경험 연결**: 유사한 과거 프로젝트나 경험과의 연결점
2. **개인 강점 활용**: 조대표의 특별한 강점을 활용할 수 있는 부분
3. **네트워크 활용**: 기존 인적 네트워크를 통해 실행 가능한 부분
4. **개인 목표 연결**: 장기적 개인 발전 목표와의 연결성

📝 **개인화 요약** (조대표님만을 위한 특별 버전)
[과거 경험과 연결된 핵심 내용]

🎯 **조대표님 전용 액션 플랜**
- [개인 강점 기반 접근법]
- [기존 네트워크 활용 방안]
- [장기 목표와의 연결점]

⚠️ **개인적 주의사항**
- [과거 실패 경험을 바탕으로 한 주의점]
- [개인 약점 보완 방안]
```

#### Gemini Pro 전용 외부 관점 요약:
```
[외부 정보 객관적 분석]
이 문서를 보험중개업계 전문가 관점에서 객관적으로 요약하세요.

[문서 내용]
{document_text}

[객관적 분석 기준]
1. **시장 동향**: 업계 전반적 트렌드와의 관련성
2. **경쟁사 동향**: 다른 브로커들의 대응 방향
3. **규제 환경**: 정책 변화가 미치는 영향
4. **기술 혁신**: 인슈어테크 등 신기술 영향

🌐 **시장 관점 요약**
[업계 전반적 시각에서의 핵심 내용]

📊 **경쟁 분석**
- [경쟁사들의 예상 반응]
- [시장 내 포지셔닝 기회]

🚀 **업계 트렌드 연결**
- [관련 산업 동향]
- [신기술 활용 기회]
```
```
당신은 조대표(록톤코리아 영업대표)의 개인 비서입니다.
다음 문서를 조대표의 의사결정에 도움이 되도록 요약하세요.

[문서 내용]
{document_text}

요약 기준:
1. 비즈니스 기회: 새로운 영업 기회나 시장 기회
2. 리스크 경고: 주의해야 할 위험 요소나 변화
3. 액션 아이템: 조대표가 취해야 할 구체적 행동
4. 인적 네트워크: 연결 가능한 키 인물이나 기관

결과를 다음 형식으로 출력하세요:

📊 **핵심 요약** (2문장)
[문서의 가장 중요한 내용을 2문장으로 요약]

🎯 **비즈니스 기회**
- [구체적 기회 1]
- [구체적 기회 2]

⚠️ **주의사항**
- [위험요소나 고려사항]

✅ **권장 액션**
- [즉시 실행 가능한 행동]
- [중기적 준비사항]

👥 **키 인물**
- [연결 고려 대상 인물 및 이유]
```

#### GitMind 구조 반영 요약:
```
이 문서를 GitMind 마인드맵 구조로 정리하여 요약하세요.

[문서 내용]
{document_text}

마인드맵 구조:
중심 주제 → 주요 가지(3-5개) → 세부 항목

결과를 다음과 같이 구조화하세요:

🎯 **중심 주제**: [문서의 핵심 주제]

📋 **주요 가지**:
1. **[가지1 제목]**
   - 세부 항목 1
   - 세부 항목 2
   
2. **[가지2 제목]**
   - 세부 항목 1
   - 세부 항목 2

3. **[가지3 제목]**
   - 세부 항목 1
   - 세부 항목 2

🔗 **연결 고리**: [다른 프로젝트나 지식과의 연결점]
```

### 3.3 관련 인물 추출 및 네트워크 분석 (하이브리드 접근)

#### 노트북LM - 기존 네트워크 연결 분석:
```
조대표의 기존 인적 네트워크 데이터베이스를 바탕으로 
새로 발견된 인물들과의 연결 가능성을 분석하세요.

[새로 발견된 인물]
{new_persons}

[기존 네트워크 분석 결과]
🔗 **직접 연결 가능성**
- [조대표가 직접 아는 사람을 통한 소개 경로]
- 경로: 조대표 → [중간인물] → [목표인물]

🌐 **간접 연결 네트워크**
- [2-3단계 인맥을 통한 접근 경로]
- 신뢰도별 연결 경로 평가

💼 **비즈니스 관계 기반 접근**
- [공통 업무 영역이나 프로젝트를 통한 자연스러운 접촉]
- [업계 모임이나 행사를 통한 만남 기회]

📝 **개인화된 접근 전략**
- [조대표의 성격과 스타일에 맞는 네트워킹 방법]
- [과거 성공한 인맥 형성 패턴 활용]
```

#### Gemini Pro - 공개 정보 기반 인물 분석:
```
공개 정보를 바탕으로 다음 인물들의 비즈니스 프로필을 분석하세요.

[인물 정보]
{person_info}

[공개 정보 분석]
👤 **공개 프로필 분석**
- 경력, 학력, 공개 활동 내역
- SNS 활동 패턴 및 관심사
- 언론 인터뷰 및 발언 분석

🎯 **비즈니스 관심사**
- 주요 관심 분야 및 투자 영역
- 현재 진행 중인 프로젝트
- 업계 내 영향력 및 포지션

🤝 **접촉 가능한 공개 채널**
- 참여하는 업계 행사
- 소속 기관의 공식 채널
- 전문 분야 컨퍼런스나 세미나
```
```
당신은 비즈니스 네트워킹 전문가입니다.
다음 문서에서 조대표(보험중개업)에게 가치 있는 인물들을 추출하세요.

[문서 내용]
{document_text}

다음 정보를 JSON 형식으로 추출하세요:

{
  "key_persons": [
    {
      "name": "인물명",
      "title": "직책",
      "organization": "소속 기관",
      "expertise": ["전문분야1", "전문분야2"],
      "relevance_to_insurance": "보험중개업과의 연관성 설명",
      "networking_priority": "높음/보통/낮음",
      "potential_opportunity": "구체적 협력 기회"
    }
  ],
  "organizations": [
    {
      "name": "기관명",
      "type": "정부기관/민간기업/협회",
      "role": "역할이나 영향력",
      "insurance_relevance": "보험중개와의 관련성"
    }
  ]
}

특별히 다음 유형의 인물에 주목하세요:
- 정책 결정권자 (정부 고위직, 공기업 임원)
- 기술 전문가 (R&D 센터장, CTO)
- 사업 의사결정자 (CEO, 사업부장)
- 금융 관계자 (은행, 투자사, 보험사)
```

#### 인적 네트워크 확장 분석:
```
다음 인물 정보를 바탕으로 조대표의 인적 네트워크 확장 전략을 제안하세요.

[기존 네트워크]
{existing_network}

[새로 발견된 인물]
{new_persons}

분석 결과:

🌐 **네트워크 갭 분석**
- 부족한 영역: [현재 네트워크에서 부족한 분야]
- 중복 영역: [과도하게 집중된 분야]

🎯 **우선 접촉 대상** (상위 3명)
1. [인물명] - [접촉 이유 및 기대 효과]
2. [인물명] - [접촉 이유 및 기대 효과]
3. [인물명] - [접촉 이유 및 기대 효과]

🤝 **접근 전략**
- [구체적 접촉 방법 및 시나리오]

🔄 **네트워크 연결 기회**
- [기존 인물을 통한 새 인물 소개 가능성]
```

---

## IV. 30년 아카이브 활용 전략 (노트북LM 특화)

### 4.1 개인 지식 진화 추적

#### 장기 패턴 분석:
```
조대표의 30년 아카이브를 바탕으로 개인 지식과 사고의 진화 과정을 분석하세요.

[분석 관점]
📈 **사고 진화 패턴**
- 20대: [초기 사업 아이디어와 접근 방식]
- 30대: [경험을 통한 사고 변화]
- 40대: [성숙한 판단력과 전략적 사고]
- 50대: [현재의 통합적 관점]

🎯 **반복되는 성공 공식**
- [30년간 일관되게 성공으로 이어진 패턴]
- [시대가 변해도 유효한 개인 원칙]

⚠️ **과거 실수에서 얻은 교훈**
- [반복되지 않도록 주의해야 할 패턴]
- [실패에서 도출한 핵심 인사이트]

🚀 **미래 예측 및 준비**
- [과거 패턴을 바탕으로 한 다음 10년 전망]
- [준비해야 할 역량이나 네트워크]
```

### 4.2 개인 아이디어 인큐베이션

#### 아이디어 성숙도 추적:
```
조대표의 과거 아이디어 노트들을 분석하여 현재 아이디어의 성숙도를 평가하세요.

[현재 아이디어]
{current_idea}

[아이디어 진화 분석]
🌱 **아이디어 기원**
- 최초 등장: [언제, 어떤 계기로 떠올랐는지]
- 초기 형태: [처음에는 어떤 모습이었는지]

🌿 **중간 발전 과정**
- 발전 단계: [시간에 따른 아이디어 변화]
- 영향 요소: [아이디어 발전에 영향을 준 경험이나 정보]

🌳 **현재 성숙도**
- 완성도 평가: [현재 얼마나 구체화되었는지]
- 실행 준비도: [실제 실행을 위해 부족한 부분]

🚀 **다음 단계 제안**
- [아이디어를 한 단계 더 발전시키기 위한 구체적 방법]
- [조대표의 과거 패턴을 바탕으로 한 실행 전략]
```

### 4.3 개인 브랜드 및 전문성 개발

#### 전문성 진화 맵핑:
```
30년 아카이브를 바탕으로 조대표의 전문성 발전 과정을 분석하고 
미래 전문성 개발 방향을 제안하세요.

[전문성 진화 분석]
🎓 **전문성 발전 여정**
- 초기 전문 분야: [시작했던 영역]
- 확장 과정: [어떻게 전문성이 넓어졌는지]
- 현재 고유 영역: [조대표만의 독특한 전문성]

💎 **차별화 요소**
- [다른 사람이 갖지 못한 조대표만의 강점]
- [복합적 경험에서 나오는 고유한 관점]

🎯 **미래 전문성 개발 방향**
- [기존 강점을 더욱 깊게 발전시킬 영역]
- [새롭게 개발할 가치가 있는 전문 분야]
- [시대 변화에 맞춘 역량 업그레이드]

📚 **개인 브랜드 전략**
- [조대표의 독특한 포지셔닝]
- [전문가로서의 차별화된 가치 제안]
```

---

## V. 창의적 연결 시스템 (하이브리드 접근)

### 5.1 내부-외부 지식 융합 (노트북LM + Gemini Pro)

#### 하이브리드 창의적 연결:
```
[노트북LM 분석 결과: 개인 경험 기반]
{personal_insights}

[Gemini Pro 분석 결과: 외부 시장 정보 기반]
{market_insights}

두 분석 결과를 융합하여 혁신적 아이디어를 도출하세요.

🧩 **내부-외부 연결점**
- [개인 경험과 시장 동향의 교집합]
- [조대표의 강점이 시장 기회와 만나는 지점]

💡 **융합 아이디어** (TOP 3)
1. [개인 경험 + 시장 기회] = [혁신적 사업 아이디어]
2. [보유 네트워크 + 외부 트렌드] = [새로운 협력 모델]
3. [축적된 지식 + 신기술] = [차별화된 서비스]

⚡ **즉시 검증 가능한 아이디어**
- [조대표가 기존 자원으로 당장 테스트할 수 있는 아이디어]
- [낮은 비용으로 시장 반응을 확인할 수 있는 방법]

🎯 **실행 우선순위**
- [개인 역량과 시장 기회를 종합한 우선순위]
- [단기-중기-장기 실행 로드맵]
```

#### 지식 연결 프롬프트:
```
당신은 창의적 사고 전문가입니다.
다음 새로운 정보와 기존 지식을 연결하여 혁신적 아이디어를 제안하세요.

[새로운 정보]
{new_document}

[기존 지식 베이스]
{existing_knowledge}

다음 관점에서 창의적 연결을 찾으세요:

🧩 **직접적 연결**
- [명확한 관련성이 있는 연결점]

🌟 **간접적 연결**
- [일견 관련 없어 보이지만 창의적으로 연결 가능한 영역]

💡 **혁신적 아이디어**
- [기존 지식과 새 정보의 조합으로 만들 수 있는 새로운 비즈니스 아이디어]

⚡ **실행 가능한 아이디어** (상위 3개)
1. [아이디어명]: [구체적 실행 방안]
2. [아이디어명]: [구체적 실행 방안]
3. [아이디어명]: [구체적 실행 방안]

🎯 **즉시 검증 가능한 아이디어**
- [조대표가 당장 테스트해볼 수 있는 소규모 아이디어]
```

    def hybrid_analysis(self, document_info):
        # 노트북LM: 개인 관점 분석
        personal_view = self.notebook_manager.analyze_with_personal_context(document_info)
        
        # Gemini Pro: 외부 시장 관점 분석
        market_view = self.gemini_primary.analyze_market_perspective(document_info)
        
        # 두 관점 융합
        return self.synthesize_insights(personal_view, market_view)
    
    def synthesize_insights(self, personal_view, market_view):
        """개인 관점과 시장 관점을 융합한 최종 인사이트 도출"""
        synthesis_prompt = f"""
        개인 경험 기반 분석: {personal_view}
        시장 동향 기반 분석: {market_view}
        
        두 관점을 융합하여 조대표에게 최적화된 종합 인사이트를 제공하세요.
        """
        return self.gemini_secondary.generate_synthesis(synthesis_prompt)
```

### 6.3 데이터 보안 및 프라이버시 관리

#### 민감도 기반 라우팅:
```python
def assess_document_sensitivity(document_info):
    """문서 민감도 평가 (1-10 점수)"""
    sensitivity_factors = {
        'personal_finance': 10,      # 개인 재무 정보
        'business_strategy': 9,      # 사업 전략
        'customer_data': 9,          # 고객 정보  
        'internal_memo': 8,          # 내부 메모
        'meeting_notes': 7,          # 미팅 노트
        'idea_notes': 6,             # 아이디어 노트
        'market_research': 4,        # 시장 조사
        'public_news': 2,            # 공개 뉴스
        'general_info': 1            # 일반 정보
    }
    
    content_keywords = extract_keywords(document_info['content'])
    source_type = document_info.get('source_type', 'unknown')
    
    base_score = sensitivity_factors.get(source_type, 5)
    
    # 키워드 기반 조정
    sensitive_keywords = ['계약', '재무', '전략', '비밀', '개인', '고객정보']
    for keyword in sensitive_keywords:
        if keyword in content_keywords:
            base_score += 1
    
    return min(base_score, 10)  # 최대 10점

class SecurityManager:
    def __init__(self):
        self.encryption_key = self.load_encryption_key()
    
    def secure_upload_to_notebook(self, sensitive_document):
        """민감 문서의 안전한 노트북LM 업로드"""
        # 1. 로컬 암호화
        encrypted_content = self.encrypt_content(sensitive_document)
        
        # 2. 노트북LM에 업로드 (로컬 처리 보장)
        return self.notebook_manager.upload_secure(encrypted_content)
    
    def sanitize_for_gemini(self, document_info):
        """Gemini Pro 전송 전 민감 정보 제거/마스킹"""
        content = document_info['content']
        
        # 개인정보 마스킹
        content = self.mask_personal_info(content)
        content = self.mask_financial_data(content)
        content = self.mask_customer_data(content)
        
        return {**document_info, 'content': content}
```

---

## VII. 통합 워크플로우 및 사용자 경험

### 7.1 조대표님 맞춤 인터페이스

#### 단일 진입점 시스템:
```
🎯 GIA 통합 분석 시스템

📄 문서 업로드
├── 📂 드래그 앤 드롭 (자동 민감도 판별)
├── 🔗 URL 입력 (웹 문서 분석)
├── 📧 이메일 연동 (Gmail, Outlook)
└── ☁️ 클라우드 동기화 (Google Drive, OneDrive)

🤖 분석 옵션 선택
├── 🏠 개인 관점 (노트북LM - 과거 경험 기반)
├── 🌐 시장 관점 (Gemini Pro - 외부 정보 기반)  
├── 🔄 융합 분석 (하이브리드 - 양쪽 관점 종합)
└── ⚡ 빠른 요약 (핵심 정보만 즉시 추출)

📊 결과 확인
├── 📝 요약 보고서 (조대표 의사결정용)
├── 🎯 액션 아이템 (즉시 실행 가능한 과제)
├── 👥 인물 네트워크 (연결 기회)
└── 💡 창의적 아이디어 (신규 비즈니스 기회)

🔄 노션 자동 연동
├── 📚 적절한 DB에 자동 분류 저장
├── 🏷️ 태그 및 관계 자동 설정
├── 📈 대시보드 업데이트
└── 🔔 중요 인사이트 알림
```

#### 조대표님 일일 워크플로우 최적화:
```
🌅 아침 루틴 (9:00 AM)
├── 📱 중요 알림 확인 (GIA가 밤새 분석한 중요 정보)
├── 📧 우선순위 이메일 요약 (AI가 선별한 핵심 메일)
├── 📊 오늘의 액션 아이템 (어제 분석에서 도출된 할 일)
└── 🎯 오늘의 네트워킹 기회 (만날 만한 사람 제안)

🏢 업무 중 (실시간)
├── 📄 받은 문서 즉시 분석 (드래그 앤 드롭만으로)
├── 💡 회의 중 아이디어 즉시 기록 (음성 인식 → 노트북LM)
├── 👥 만난 사람 정보 즉시 업데이트 (People_Network)
└── 🔄 새 정보와 기존 지식 자동 연결

🌆 저녁 정리 (6:00 PM)  
├── 📋 오늘의 인사이트 리뷰 (하루 분석 결과 요약)
├── 🎯 내일의 우선순위 제안 (AI 기반 일정 최적화)
├── 💭 떠오른 아이디어 정리 (Ideas_Incubator 업데이트)
└── 📚 30년 아카이브 연결 (오늘 경험을 과거와 연결)
```

### 7.2 GitMind 연동 강화

#### 마인드맵 ↔ 노트북LM 양방향 연동:
```python
class GitMindNotebookBridge:
    def __init__(self):
        self.gitmind_api = GitMindAPI()
        self.notebook_manager = NotebookLMManager()
    
    def mindmap_to_notebook_analysis(self, mindmap_url):
        """GitMind 마인드맵을 노트북LM으로 분석"""
        # 1. 마인드맵 구조 추출
        mindmap_structure = self.gitmind_api.export_structure(mindmap_url)
        
        # 2. 노트북LM으로 심층 분석
        analysis_prompt = f"""
        조대표의 마인드맵 구조를 분석하고 개선 방안을 제안하세요.
        
        [마인드맵 구조]
        {mindmap_structure}
        
        [분석 요청]
        1. 구조적 완성도 평가
        2. 누락된 중요 요소 식별  
        3. 논리적 연결성 개선 방안
        4. 실행 가능성 강화 방안
        """
        
        return self.notebook_manager.analyze_with_context(
            analysis_prompt, 'personal_knowledge'
        )
    
    def notebook_insights_to_mindmap(self, insights):
        """노트북LM 분석 결과를 GitMind 구조로 변환"""
        mindmap_structure = self.convert_to_mindmap_format(insights)
        return self.gitmind_api.create_or_update_mindmap(mindmap_structure)
```

---

## VIII. 성능 최적화 및 비용 관리

### 8.1 하이브리드 시스템 비용 효율성

#### 비용 최적화 전략:
```python
class CostOptimizer:
    def __init__(self):
        self.gemini_cost_per_token = 0.00015  # 예시 비용
        self.notebook_lm_cost = 0  # 로컬 처리
        
    def optimize_processing_route(self, document_info):
        """비용과 품질을 고려한 최적 처리 경로 선택"""
        
        # 복잡도 평가
        complexity = self.assess_complexity(document_info)
        sensitivity = self.assess_sensitivity(document_info)
        urgency = document_info.get('urgency', 'normal')
        
        if sensitivity >= 8:  # 민감 정보
            return 'notebook_only'  # 비용 0, 보안 최우선
        elif complexity <= 3 and urgency == 'low':
            return 'notebook_primary'  # 저비용 처리
        elif urgency == 'high':
            return 'gemini_primary'  # 빠른 처리
        else:
            return 'hybrid'  # 품질 최우선
    
    def batch_process_optimization(self, documents):
        """문서 일괄 처리 최적화"""
        # 유사한 문서들을 그룹화하여 효율적 처리
        grouped_docs = self.group_similar_documents(documents)
        
        for group in grouped_docs:
            optimal_route = self.optimize_processing_route(group[0])
            yield self.process_group(group, optimal_route)
```

### 8.2 API 호출 최적화

#### 스마트 캐싱 시스템:
```python
class SmartCache:
    def __init__(self):
        self.cache = {}
        self.similarity_threshold = 0.85
    
    def check_similar_analysis(self, document_hash):
        """유사한 문서의 기존 분석 결과 재활용"""
        for cached_hash, result in self.cache.items():
            similarity = self.calculate_similarity(document_hash, cached_hash)
            if similarity > self.similarity_threshold:
                return self.adapt_cached_result(result, document_hash)
        return None
    
    def cache_result(self, document_hash, analysis_result):
        """분석 결과 캐싱 (중요 결과만)"""
        if self.is_worth_caching(analysis_result):
            self.cache[document_hash] = analysis_result
            self.cleanup_old_cache()  # 용량 관리
```

---

## IX. 실제 구현 로드맵

### 9.1 Phase 1: 기본 하이브리드 시스템 (1-2주)

**우선 구현 사항**:
1. **노트북LM 프로젝트 세팅**
   - 4개 핵심 프로젝트 생성
   - 조대표님 기존 중요 문서 업로드
   - 기본 분석 프롬프트 테스트

2. **하이브리드 라우터 개발**  
   - 민감도 평가 시스템
   - Gemini Pro ↔ 노트북LM 분기 로직
   - 서대리 기존 시스템 확장

3. **기본 워크플로우 구축**
   - 문서 업로드 → 자동 분석 → 노션 저장
   - 조대표님 테스트 및 피드백

### 9.2 Phase 2: 고도화 및 통합 (3-4주)

**고도화 사항**:
1. **창의적 연결 시스템**
   - 노트북LM ↔ Gemini Pro 융합 분석
   - 30년 아카이브 심층 활용
   - 자동 아이디어 생성 엔진

2. **GitMind 완전 연동**
   - 마인드맵 ↔ 노트북LM 양방향 연동
   - 실시간 구조 분석 및 개선 제안

3. **성능 최적화**
   - 스마트 캐싱 시스템
   - 비용 최적화 알고리즘

### 9.3 Phase 3: 완전 자동화 (1-2개월)

**자동화 확장**:
1. **멀티 계정 통합**
   - 10개 구글 계정 자동 모니터링
   - MS Office 365 연동
   - 이메일 자동 분석 및 분류

2. **실시간 지능형 알림**
   - 중요 정보 자동 감지
   - 네트워킹 기회 실시간 제안
   - 아이디어 성숙도 추적

3. **개인 AI 어시스턴트 완성**
   - 조대표님 전용 "자비스" 수준 달성
   - 능동적 정보 제안 시스템
   - 장기 목표 달성 지원 시스템

---

## X. 기대 효과 및 혁신성

### 10.1 하이브리드 시스템의 혁신적 가치

**보안성 + 확장성 동시 확보**:
- 민감 정보: 노트북LM 로컬 처리 (100% 보안)
- 일반 정보: Gemini Pro 클라우드 처리 (무한 확장)
- 융합 분석: 두 시스템의 장점 결합

**개인화 + 객관성 균형**:
- 노트북LM: 조대표님 30년 경험 기반 개인화 분석
- Gemini Pro: 외부 시장 정보 기반 객관적 분석
- 융합 결과: 개인 강점과 시장 기회의 최적 매칭

### 10.2 정량적 효과 예측

**처리 효율성**:
- 문서 분석 시간: 30분 → 2분 (93% 단축)
- 노트북LM 활용 시 민감 정보 처리 비용 0원
- 하이브리드 분석으로 Gemini Pro 토큰 사용량 40% 절약

**비즈니스 임팩트**:
- 30년 아카이브 활용도: 10% → 80% (700% 증가)
- 개인 경험 기반 아이디어 정확도: 90% 이상
- 신규 사업 기회 발굴: 월 5건 → 20건 (300% 증가)

### 10.3 조대표님 업무 혁신

**"구슬을 꿰는" 시스템 완성**:
- 30년 경험 → 의미론적 지식 체계 구축
- 새 정보 → 기존 경험과 자동 연결
- 아이디어 → 실행 가능한 계획으로 진화

**진정한 개인 AI 어시스턴트**:
- 조대표님만을 위한 맞춤형 분석
- 개인 패턴 학습을 통한 예측적 제안  
- 평생 학습 및 성장 동반자 역할

---

**하이브리드 전략 수립 완료**: 2025년 8월 22일 15:50 KST  
**다음 단계**: 조대표님 승인 후 노트북LM 프로젝트 세팅 및 하이브리드 시스템 구현 착수

#### 레거시 지식 재발견:
```
당신은 디지털 아카이브 전문가입니다.
조대표의 30년 경험과 축적된 정보를 바탕으로 다음 새 정보의 가치를 재평가하세요.

[새로운 문서]
{new_document}

[30년 아카이브 샘플]
{archive_sample}

분석 관점:

📚 **과거 경험과의 연결**
- [유사한 과거 프로젝트나 경험]
- [과거 실패/성공 사례에서 얻을 교훈]

🔄 **반복 패턴 인식**
- [30년간 반복되는 비즈니스 패턴]
- [변화하는 트렌드와 불변하는 원칙]

💎 **숨겨진 가치 발굴**
- [과거에는 중요하지 않았지만 지금은 가치 있는 정보]
- [재조명할 만한 아이디어나 인사이트]

🚀 **미래 예측**
- [과거 패턴을 바탕으로 한 미래 전망]
- [다가올 기회에 대한 준비 방안]
```

---

## IV. 단계별 프롬프트 실행 전략

### 4.1 1차 분석 (기본 정보 추출)

**실행 순서**:
1. **문서 유형 판별** → 도메인별 특화 프롬프트 선택
2. **기본 키워드 추출** → 보험/에너지/방산 분야별 키워드
3. **핵심 요약 생성** → 의사결정 지원형 2문장 요약
4. **인물 정보 추출** → 네트워킹 기회 분석

### 4.2 2차 분석 (심화 연결)

**실행 순서**:
1. **기존 지식과 연결** → Knowledge_Graph DB 참조
2. **인적 네트워크 분석** → People_Network DB 연결
3. **창의적 아이디어 생성** → Ideas_Incubator DB 입력
4. **실행 계획 제안** → Projects_Master DB 연결

### 4.3 3차 분석 (전략적 활용)

**실행 순서**:
1. **비즈니스 기회 평가** → 수익성 및 실현 가능성 점수화
2. **리스크 분석** → 잠재적 위험 요소 식별
3. **우선순위 제안** → 조대표 일정 및 자원 고려
4. **장기 전략 연결** → 30년 비전과의 정합성 검토

---

## V. API 최적화 전략

### 5.1 Gemini Pro 2개 키 활용 방안

**Key 1 (Primary)**: 
- 대량 문서 일괄 처리
- 기본 키워드 추출
- 표준 요약 생성

**Key 2 (Secondary)**:
- 창의적 연결 분석
- 복잡한 전략 분석
- 인적 네트워크 분석

**로드 밸런싱**:
```python
def select_api_key(task_type, complexity_level):
    if task_type == "basic_extraction" and complexity_level <= 5:
        return API_KEY_1
    elif task_type == "creative_analysis" or complexity_level > 7:
        return API_KEY_2
    else:
        return random.choice([API_KEY_1, API_KEY_2])
```

### 5.2 토큰 효율성 최적화

**문서 분할 전략**:
- 5000토큰 단위로 분할
- 중요 섹션 우선 처리
- 요약 → 상세 분석 순차 진행

**프롬프트 재사용**:
- 도메인별 템플릿 캐싱
- 공통 지시사항 모듈화
- 동적 프롬프트 조합

---

## VI. 품질 보증 및 검증

### 6.1 추출 품질 검증 기준

**키워드 추출 품질**:
- 도메인 관련성: 80% 이상
- 중복률: 20% 이하
- 신규 키워드 발굴률: 30% 이상

**요약 품질**:
- 핵심 정보 포함도: 90% 이상
- 조대표 의사결정 도움도: 주관적 평가 4점/5점 이상
- 실행 가능한 액션 아이템 포함: 필수

**인물 추출 정확도**:
- 인물명 정확도: 95% 이상
- 직책/소속 정확도: 85% 이상
- 비즈니스 연관성 적절성: 80% 이상

### 6.2 지속적 개선 시스템

**피드백 루프**:
1. **조대표 평가** → 월 1회 추출 결과 평가
2. **프롬프트 개선** → 평가 결과 기반 프롬프트 튜닝
3. **성능 모니터링** → API 호출 시간, 토큰 사용량 최적화
4. **도메인 확장** → 새로운 사업 영역 대응 프롬프트 개발

**A/B 테스트**:
- 프롬프트 버전별 성능 비교
- 키워드 추출 방식 최적화
- 요약 스타일 개인화

---

## VII. 실제 구현 가이드

### 7.1 서대리 기존 시스템 확장

**현재 `llm_extractor_test.py` 기반 확장**:
```python
# 도메인별 프롬프트 관리자
class DomainPromptManager:
    def __init__(self):
        self.insurance_prompts = self.load_insurance_prompts()
        self.energy_prompts = self.load_energy_prompts()
        self.defense_prompts = self.load_defense_prompts()
    
    def select_prompt(self, document_type, analysis_depth):
        # 문서 유형과 분석 깊이에 따른 최적 프롬프트 선택
        pass

# 다단계 분석 엔진
class MultiStageAnalyzer:
    def __init__(self, api_keys):
        self.primary_key = api_keys[0]
        self.secondary_key = api_keys[1]
        self.prompt_manager = DomainPromptManager()
    
    def analyze_document(self, document_text):
        # 1차: 기본 정보 추출
        basic_info = self.extract_basic_info(document_text)
        
        # 2차: 심화 연결 분석
        connections = self.analyze_connections(basic_info)
        
        # 3차: 전략적 인사이트
        insights = self.generate_insights(connections)
        
        return self.combine_results(basic_info, connections, insights)
```

### 7.2 노션 DB 연동 최적화

**자동 분류 및 태깅**:
```python
def auto_categorize_document(extracted_info):
    # LLM 추출 결과 → 노션 DB 속성 자동 매핑
    categories = {
        'insurance_products': '보험상품',
        'risk_factors': '리스크요소',
        'key_persons': '핵심인물',
        'business_opportunities': '사업기회'
    }
    
    notion_properties = {}
    for key, category in categories.items():
        if key in extracted_info:
            notion_properties[category] = extracted_info[key]
    
    return notion_properties
```

---

## VIII. 기대 효과 및 성공 지표

### 8.1 정량적 효과

**처리 효율성**:
- 문서 분석 시간: 수동 30분 → 자동 3분 (90% 단축)
- 키워드 추출 정확도: 95% 이상
- 인물 네트워크 확장: 월 평균 20명 → 50명 (150% 증가)

**비즈니스 임팩트**:
- 신규 비즈니스 기회 발굴: 월 평균 5건 → 15건 (200% 증가)
- 인적 네트워크 활용도: 30% → 70% (133% 증가)
- 아이디어 실행률: 10% → 40% (300% 증가)

### 8.2 정성적 효과

**조대표 업무 혁신**:
- "찾은 정보를 지식으로 연결 못함" → 자동 연결 시스템
- "구슬만 모으고 꿰지 못함" → AI 기반 아이디어 조합
- "30년 정보 아카이브" → 의미론적 지식 체계 완성

**의사결정 품질 향상**:
- 정보 기반 의사결정 비율 증가
- 위험 예측 정확도 향상
- 기회 포착 속도 개선

---

**전략 수립 완료**: 2025년 8월 22일 15:48 KST  
**다음 단계**: 서대리와 협업하여 프롬프트 시스템 실제 구현 착수