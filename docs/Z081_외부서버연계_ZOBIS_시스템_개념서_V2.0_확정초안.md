### Z081 외부서버 연계 ZOBIS 시스템 개념서 V2.0 — 확정 초안 (Notion-First · Server-Assisted)

### 문서 메타

- 문서 번호: Z081
- 근거·통합: Z030 초안 요소 채택 + Z080(선과장안) 통합 반영
- 참조: [Z080_외부서버 연동 아키텍처 초안(Notion-first · Server-assisted)](https://www.notion.so/Z080_-Notion-first-Server-assisted-df146d8c7a474f57aeb924b1ccbf4d31?pvs=21) · [Z073_케이스 1·2·3 통합 테스트 결과 보고](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66?pvs=21) · [Z075_노션DB커서접근실행키 작성방안(C2N프로세스)](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21) · [Z077_협업프로세스 사용자 시나리오 최종본(C2N·G2N·A1G2N)](https://www.notion.so/Z077_-C2N-G2N-A1G2N-578e2e421ba94161b1e87757515c821d?pvs=21) · [Z079_STAGE4_종료보고서(운영 고정화·문서화 마감)](https://www.notion.so/Z079_STAGE4_-063bcca7ebcf461fb7b7bc3c794d9fd4?pvs=21)

---

### 1) 전략 목표 — 오너십·운영 지속성·비용 효율

- 자동화 극대화와 함께 조대표님의 시스템 오너십을 보장
- 서버 장애 시에도 Track 2(Notion-First)로 수동/반자동 명맥 유지
- 비용은 서버리스 우선으로 최소화, 필요 시만 서버 호출

---

### 2) 투트랙 운영 원칙(Notion-First)

- Track 1 (Server-Augmented, 강화)
    - Cloud Run 기반 "서대리 시스템"이 고부가가치 지능형 자동화·배치 실행(C2N/G2N/A1G2N, KPI/링크 검증, ZNNN_ 번호체계)
- Track 2 (Notion-First, 지속성)
    - Notion 자체 기능 + 수동 프로세스로 필수 업무 연속성 확보(지시서 기록·링크 첨부·간단 집계 등)

---

### 3) 아키텍처 및 호스팅 결정

- 개념 흐름
    
    사용자(Notion 대문·DB·버튼)
    
    →(C2N 웹훅)→ 서버(서대리 시스템)
    
    →(Notion API/Google Drive/LLM API)→ 결과를 Notion DB로 회수
    
- 호스팅 최종 결정: Google Cloud Run(Serverless)
    - 이유: 미사용시 0원 수준, 자동 확장, Secret Manager·Scheduler·Logging 연계, HTTPS 관리형
    - 보조: Heroku로 초기 PoC 가능, 본선은 Cloud Run 권장
- 운영 표준: 코드/CI는 GitHub. 실행은 Cloud Run(중장기 표준)

---

### 4) 서비스 구분 — 서버 연계 vs 노션 독립

- 서버 연계(최대 시너지)
    - A1G2N 선제 조사+LLM 분석, G2N 이관, C2N 통제, KPI/링크 배치, ZNNN_ 원자적 예약(충돌 스킵·이력)
- 노션 독립(오너십·지속성)
    - 단건 문서 등록/경과 기록, 예외적 수동 링크 첨부, 번호 부여 수동/반자동, 간단 집계·레포트
- 판단 기준: 건수·동시성·외부 API·보안 검증·SLA·비용 대비 효과

---

### 5) 보안·리스크·운영 표준

- 보안
    - HMAC-SHA256 + base64url, canonical JSON(NFC), X-Timestamp·X-Nonce(1회성)
    - SSL 유효성, (가능 시) IP 제한, 시크릿 매니저 관리
- 가드
    - schema_hash(dryrun=경고, apply=차단), 옵션 화이트리스트, JSON Schema 입력 검증, parent.database_id 검사
- 운영
    - KPI 카드: 48h + 7d 동시 표출, 10분 캐시 갱신, P95 경고>6.0s·위험>8.0s
    - 링크 검증: 최종 HTTP 200, 응답 ≤1.5s, SSL 유효, Notion URL, 3xx 1회 자동 추적
    - 장애 대응: 버튼 실패 시 "지연 처리" 라벨 + 복구 후 자동 재처리
    - 비용 제어: 서버리스·캐시·중복 방지, LLM/Drive 쿼터 상한 관리

---

### 6) Track 2(서버 다운 시) 운용 시나리오

- A1G2N 대체: 외부 AI(Perplexity/ChatGPT 등) 조사 → Notion에 수동 기록
- G2N 대체: G-Drive 링크를 Notion DB에 수동 등록, 상태=수동 처리
- C2N 대체: 지시서 페이지에 수동 요약 작성 및 상태=검토대기로 전환

---

### 7) 단계별 로드맵(확정)

- Stage 5(운영 상시화·배포)
    - 컨테이너화 → Cloud Run 배포 → G1 재검증(/healthz ≤500ms, C2N2 ≤6s, C2N3 ≤8s, 2회 성공)
- Stage 6(품질·확장)
    - A1G2N 스케줄러 상시화, G2N 무인 루프, 소스 화이트리스트·중복 융합·자동 태깅, 감사로그·승인흐름 옵션
- Stage 7(비용·신뢰성)
    - 호출 캐싱·증분 처리·큐 재시도(백오프), LLM 비용 최적화·선택 처리

---

### 8) 의사결정 매트릭스(요약)

- 실시간 웹훅·상시가동·보안키 필요 → Cloud Run(권고)/Heroku(초기)
- 배치 전용·실시간 불필요 → GitHub Actions(+서버리스 함수) 병행 가능
- 비용 최저화 우선 → Heroku 저가 플랜 시작, 성장 시 Cloud Run로 이관
- 장애 내성 최우선 → Cloud Run + 멀티 리전 + 헬스 체크

---

### 9) 운영 지침 연계

- 통합 테스트·진척 허브: [Z073_케이스 1·2·3 통합 테스트 결과 보고](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66?pvs=21)
- 운영 지침(보안·가드·정책): [Z075_노션DB커서접근실행키 작성방안(C2N프로세스)](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21)
- 사용자 시나리오(버튼 동선): [Z077_협업프로세스 사용자 시나리오 최종본(C2N·G2N·A1G2N)](https://www.notion.so/Z077_-C2N-G2N-A1G2N-578e2e421ba94161b1e87757515c821d?pvs=21)
- Stage 4 종료 보고: [Z079_STAGE4_종료보고서(운영 고정화·문서화 마감)](https://www.notion.so/Z079_STAGE4_-063bcca7ebcf461fb7b7bc3c794d9fd4?pvs=21)
- 전 버전(선과장 초안): [Z080_외부서버 연동 아키텍처 초안(Notion-first · Server-assisted)](https://www.notion.so/Z080_-Notion-first-Server-assisted-df146d8c7a474f57aeb924b1ccbf4d31?pvs=21)

---

### 부록 — 선택지별 포인트(요지)

- GitHub Pages/Actions: 정적/배치 보조, 운영 서버로는 부적합(수신형 웹훅 X)
- Heroku: 빠른 PoC·저비용 시작, 장기 유연성/성능은 한계
- Cloud Run: 초단위 과금·자동 확장·보안/운영 통합 — 중장기 표준


