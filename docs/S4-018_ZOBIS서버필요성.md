세 가지 핵심 프로세스 **(G2N, A2G2N, C2N)**의 원활하고 지능적인 작동을 위해서는 ZOBIS 시스템의 핵심 엔진인 '서대리 시스템'이 서버 환경에서 상시 배포 및 가동하고 있어야 합니다.

단순히 Notion이나 Google Drive의 자체 자동화 기능만으로는 이 모든 시나리오를 완성할 수 없습니다. 서대리 시스템이 바로 이 모든 복잡한 로직과 AI 분석을 실행하는 '뇌' 역할을 하기 때문입니다.

⚙️ 서버 환경이 필수인 이유 (아키텍처 관점)
서대리 시스템(서버)은 조대표님의 워크플로우를 완성하기 위한 세 가지 결정적인 역할을 수행합니다.

1. C2N (Notion 통제) 프로세스의 핵심: 웹훅 리스너
C2N 프로세스는 **'버튼 원클릭'**으로 시스템을 제어하는 핵심 기능입니다. 이는 서버가 상시 가동하고 있어야만 가능합니다.

역할	설명	서버 의존성
명령 수신 (웹훅)	조대표님이 Notion에서 [C2N-Health] 같은 버튼을 클릭하면, Notion Automation이 미리 정의된 **웹훅 주소(URL)**로 신호를 보냅니다.	필수: 이 주소는 인터넷상에서 항상 접근 가능한 공개 엔드포인트여야 합니다. 즉, 상시 가동하는 서버가 요청을 기다리고 있어야 합니다.
보안 검증	웹훅을 받은 서버는 즉시 HMAC 서명, Nonce, Timestamp를 검증해야 합니다. (선과장님 지침 4번)	필수: 보안 가드 체인 로직은 서버(서대리 시스템)에서만 실행 가능하며, 이는 0.1초 이내에 이루어져야 합니다.

Sheets로 내보내기
2. G2N / A2G2N 프로세스의 핵심: AI 분석 엔진
G2N과 A2G2N은 단순한 파일 복사가 아니라, AI를 활용한 **'지능형 처리'**가 핵심입니다.

역할	설명	서버 의존성
G드라이브 모니터링	G2N 프로세스는 G드라이브 INBOX 폴더를 주기적으로 혹은 실시간으로 감지해야 합니다.	필수: 서버가 상시 모니터링해야 하며, Notion Automation으로는 G-Drive를 직접 모니터링할 수 없습니다.
LLM API 호출	파일을 Notion에 등록한 후, AI가 문서를 분류하고 요약하는 (선과장님 지침의 Level 2: 분류/정제 자동화) 단계가 필요합니다.	필수: Claude나 Gemini 같은 외부 LLM API를 호출하여 문서를 분석하고, 그 결과를 Notion DB에 업데이트하는 복잡한 로직은 서대리 시스템(서버)에서만 실행할 수 있습니다.

Sheets로 내보내기
🚀 결론: 상시 가동 환경 구축 (D1의 목표)
현재 개발이 완료된 로직들을 최종적으로 활용하기 위해서는 **서대리 시스템이 안정적인 서버 환경(클라우드 또는 엔터프라이즈 환경)**에 배포되어야 합니다.

배포 환경: AWS, Google Cloud, Azure 등의 클라우드 서버 또는 사내 엔터프라이즈 서버

운영 상태: 24시간 365일 상시 가동

선과장님께서 현재 Notion 대문과 DB에 [C2N] 버튼을 배치하는 작업을 준비 중이신데, 이 버튼이 실제 작동하기 위해서는 서대리 시스템이 상시 대기 중인 상태에서 웹훅 주소를 받을 준비가 되어 있어야 합니다. 이 배포 작업이 완료되면 조대표님의 모든 시나리오가 실시간으로 작동하게 됩니다.

#서버가동에 대한 선과장의 의견
조대표님, 나실장 의견에 동의합니다. 선과장 관점에서 “상시 가동 서버 운영”은 C2N·G2N·A2G2N을 실제 현업에서 끊김 없이 돌리기 위한 필수 전제입니다.[[1]](https://www.notion.so/Z071_STAGE-4-ZOBIS-cf2474a5c8ee463ca2c0166d86ef68b8?pvs=21)[[2]](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21)

### 결론

- 서버 상시 배포 없이 버튼과 자동화만으로는 한계가 분명합니다. C2N의 웹훅 수신·보안 검증, G2N·A2G2N의 모니터링·AI 분석은 모두 서버(서대리 시스템)에서 상시 처리되어야 합니다.[[3]](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21)
- Stage 4 계획의 “운영 고정화 → 상시 배치화 → 품질 보증” 로드맵을 서버 배포로 완성해야 합니다.[[4]](https://www.notion.so/Z071_STAGE-4-ZOBIS-cf2474a5c8ee463ca2c0166d86ef68b8?pvs=21)[[5]](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66?pvs=21)

### 권장 아키텍처(요약)

- 인바운드
    - Notion 버튼 → Notion Automation → 서버 웹훅(HTTPS, 공개 엔드포인트)
    - Drive 이벤트/폴링 → 서버 수신
- 코어
    - 실행키 검증(HMAC+nonce+ts), JSON Schema 검증, schema_hash 가드
    - 워크플로우 엔진: C2N1/2/3, G2N, A2G2N
    - LLM 호출(분류·요약), 업서트 키 처리, 옵션 화이트리스트
- 아웃바운드
    - Notion DB 쓰기, Z072 결과 링크 자동 첨부, KPI 로그 적재
- 관측성
    - 구조화 로그 + KPI 스냅샷(성공률, P95, 중복 스킵률, 최근 7일 실패 유형)
    - 대문 KPI 카드로 상시 노출[*설계 반영됨*][[6]](https://www.notion.so/ZOBIS-227a613d25ff803ea9d0e3ffe520610c?pvs=21)[[7]](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66?pvs=21)

### 배포·운영 계획(D1 목표)

- 환경: GCP Cloud Run(또는 AWS Fargate) + HTTPS(Managed TLS)
- 가용성: 24x365, 무중단 롤링 업데이트
- 보안
    - HMAC 서명, ts ≤ 10분, nonce 1회성(메모리+파일 TTL)
    - IP 제한(가능 시) + 최소 권한 토큰
- 성능
    - C2N2 P95 ≤ 6s, C2N3 P95 ≤ 8s, Health 응답 ≤ 500ms
- 비용·확장
    - 서버리스 우선(무부하 시 비용↓), 동시성 3~5로 G2 파일럿 10건 대응

### 즉시 액션(선과장 → 서대리)

- 배포
    - 현재 코드 컨테이너라이즈, Cloud Run 배포, 웹훅 엔드포인트 공개
    - 헬스체크(“/healthz”), 시크릿은 Secret Manager 관리
- 연결
    - 대문·DB 상단 C2N 버튼에 프로덕션 웹훅 URL 바인딩
    - 실행키 서명 규격(정규화 문자열·Base64 URL-safe·서명 필드 제외) 최종 고정[[8]](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21)
- 검증
    - G1 버튼 동작 프로덕션 검증 로그·스크린샷 Z073 첨부
    - Z072 자동 첨부(C2N2·C2N3) 재확인[[9]](https://www.notion.so/Z072_-e69469e716954b1ca7e3ded5736d1603?pvs=21)[[10]](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66?pvs=21)

### 단계별 로드맵(요약)

- D1: 서버 배포·웹훅 연결·G1 검증(버튼→서버→노션 라운드트립 증빙)[[11]](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66?pvs=21)
- D2: G2 파일럿(10건) + KPI 대문 고정(성공률·P95·중복·실패 유형)[[12]](https://www.notion.so/ZOBIS-227a613d25ff803ea9d0e3ffe520610c?pvs=21)
- D3: 번호체계(ZNNN_) 프로토타입 → 회귀 통과 후 운영 반영[[13]](https://www.notion.so/Z071_STAGE-4-ZOBIS-cf2474a5c8ee463ca2c0166d86ef68b8?pvs=21)
- 상시: Z075 지침과 Z077 시나리오를 서버 운영 기준에 맞춰 지속 동기화[[14]](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21)[[15]](https://www.notion.so/Z077_-C2N-G2N-A1G2N-578e2e421ba94161b1e87757515c821d?pvs=21)

### 마무리

버튼은 “UI의 트리거”일 뿐, 실제 두뇌는 서버(서대리 시스템)입니다. 상시 가동 배포가 완료되면, 조대표님은 Notion만으로 G2N·A2G2N·C2N 전 과정을 원클릭으로 통제할 수 있습니다.[[16]](https://www.notion.so/ZOBIS-227a613d25ff803ea9d0e3ffe520610c?pvs=21)[[17]](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17?pvs=21)[[18]](https://www.notion.so/Z077_-C2N-G2N-A1G2N-578e2e421ba94161b1e87757515c821d?pvs=21)

#서대리의 의견
I'll open the S4-018 document to extract key points and draft concise 서대리 의견.

[1 tool called]

서대리 의견(요지)

- 필수 결론 동의: C2N 웹훅 수신·보안 검증, G2N/A2G2N 모니터링·AI 분석은 상시 가동 서버 없이는 불가. 즉시 서버 배포로 전환해야 함. 참고: Z071, Z075, Z073, Z072, Z077.
- 배포 타겟 제안: GCP Cloud Run 우선. 이유: 무부하 시 비용 최소화, HTTPS/TLS 기본, 무중단 롤링, Secret Manager 연동 용이.
- 보안·가드 고정: HMAC(NFC+canonical JSON+base64url), ts≤10분, nonce 1회성, JSON Schema, schema_hash(apply=차단), 옵션 화이트리스트 동적 로딩. 이미 코드에 반영됐으며 프로덕션에서도 동일 적용 필요.
- 관측성 표준: logs/* 표준화 + metrics/* KPI 스냅샷(json+md). 대문 KPI 카드와 Z072 결과 링크 자동 첨부 연동 유지.
- 운영 절차: G1(버튼-서버 왕복 증빙) → G2(10건 파일럿, p95 SLA, 실패 택소노미) → ZNNN_ 회귀 후 운영 반영.

즉시 실행 제안(서버 배포 D1)

- 컨테이너라이즈: webhook_server.py, scripts/run_notion_workflow_enhanced.py 포함 이미지 빌드
- 배포: Cloud Run(지역: asia-northeast3), minInstances=0, maxInstances=3, concurrency=10
- 네트워크/보안: HTTPS only, X-Signature/ts/nonce 필수, Secret Manager로 키 주입, IP allowlist(가능 시)
- 헬스체크: /healthz 200, 로그에 request_id·verdict 최소화 기록
- 바인딩: Notion 버튼 웹훅 URL 교체(C2N-Health, C2N1, C2N2, C2N3)
- 검증: G1 프로덕션 로그 3건+스크린샷 2장 Z073 첨부

리스크·보완

- 스키마 변동 리스크: NEWS/DEV DB 변경 시 schema_hash mismatch로 apply 차단됨. 대응: 캐시 재생성 API(/admin/refresh-schema?db=…) 또는 버튼 “Refresh Schema” 제공.
- 시간 동기화: 서버 NTP 고정 필요. drift > ±5분 시 실시간 실패.
- 옵션 동기화: 태그/중요도 변경 시 주기적 동기화 또는 동적 조회 유지.

요청사항

- Cloud Run 배포 승인 및 프로젝트/권한 제공
- 프로덕션 웹훅 도메인 확정(예: c2n.zobis.app)
- 버튼 URL 교체 일정 확정(Z075 기준)

참조
- Z071 Stage4 계획, Z075 C2N 지침, Z073 증빙 허브, Z072 결과 추적, Z077 사용자 시나리오.