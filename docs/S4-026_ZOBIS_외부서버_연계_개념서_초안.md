# S4-026 ZOBIS 외부서버 연계 전체 개념서 (초안)

## 문서 정보
- 문서 번호: S4-026
- 제목: ZOBIS 외부서버 연계 전체 개념서 (노션우선 + 서버보강 투트랙)
- 작성일: 2025-10-03 01:40 KST
- 작성자: 서대리
- 검토: 조대표님, 나실장님, 선과장님

## 1) 배경과 목표
- ZOBIS는 기본적으로 노션 기반(C2N 버튼, 대시보드, DB)으로 동작하며, 필요 시 외부 자원(웹훅, 크론, G-Drive, LLM API)을 안전하게 활용하는 투트랙 운영이 목표
- 리스크: 서버 연결 장애 시 성능 저하·불능화 가능성, 비용 증가
- 해결: 핵심 기능은 노션 내 지속 가능하게 설계하고, 부가/고가용성 요구 기능만 서버에 위임. 서버 다운 시에도 필수업무는 노션으로 지속 가능하게 함

## 2) 투트랙 운영 모델 (Notion-First + Server-Augmented)
- 트랙 A: Notion-First(오프라인 내성)
  - C2N 버튼, 문서 읽기/기록, 간단 집계는 노션 API 직접 호출/지연 실행으로 대체 가능
  - 서버 불가 시: 수동 실행 스크립트(로컬) 또는 지연 큐(노션 태그)로 대체 수행
- 트랙 B: Server-Augmented(지능/자동화 강화)
  - 웹훅 수신, KPI 배치 수집, 링크 유효성 배치 검증, G2N 감시, LLM 파이프라인, 알림 훅 등 상시 자동화
  - 서버 다운 시: 비차단. “지연 처리”로 라벨링하고 복귀 시 재처리

## 3) 전체 개념도(텍스트)
- 사용자(조대표) → Notion(버튼/DB/대문)
- Notion Automation → Webhook(서버) → C2N 실행키 검증(HMAC, ts, nonce)
- 서버 워커 → Notion API/Google Drive/LLM API 연동 → 결과 로그/요약 자동 첨부(Z072/Z062)
- 배치(크론) → KPI 스냅샷, 링크 검증 → 알림 훅(Slack/이메일/Notion 경보)
- 저장소 → GitHub(코드/CI), Artifact/Container Registry(이미지), Secret Manager(키)

## 4) 구성요소
- 노션측: 실행 버튼(C2N), 대시보드(Z073), 결과 허브(Z072), 개발문서(Z062), 정책(Z075)
- 서버측: Webhook 서버(`/webhook/*`), Health(`/healthz`), 배치(KPI/링크), 알림 훅, G-Drive 감시, LLM 파이프라인
- 공통: 보안(HMAC-SHA256, ts±5~10m, nonce 1회성), 스키마 해시, 옵션 화이트리스트, 로그 표준화

## 5) 호스팅 옵션 비교(요지)
- GitHub Pages/Actions
  - Pages: 정적만. 웹훅/배치 불가 → 운영 서버로 부적합
  - Actions: 스케줄/워크플로 가능하나 수신형 웹훅에 취약, 장기 실행/비용 비효율
- Heroku(파이썬)
  - 장점: 간단 배포, 무료 티어 축소. Web + Scheduler 애드온 용이
  - 단점: 리전/가격 대비 성능 한계, 장기적으로 비용/유연성 열세
- Cloud Run(권장)
  - 장점: 완전 관리형, 자동 스케일, HTTPS, Secret Manager/Cloud Scheduler/Logs 연계, 비용 효율(초단위 과금)
  - 단점: GCP 의존, 초콜드스타트(대부분 수 초, Health로 완화)
- 대안: Fly.io/Railway(간단), AWS Fargate/Lambda(유연·복잡)

결론: 24/7 웹훅 + 배치 + 보안/비용 고려 시 Cloud Run + Cloud Scheduler + Secret Manager 권장

## 6) 서버 연계 서비스 vs 독립 서비스
- 서버 연계 서비스(강화)
  - 웹훅 기반 C2N 실행, KPI/링크 배치, 알림 훅, G2N 감시·이관, LLM 확장
- 독립 서비스(서버 없이도 가동)
  - 노션 문서 읽기/기록(지연 허용), 소규모 수동 실행 스크립트, ZNNN_ 번호 부여(수동/반자동), 간단 집계/리포트

## 7) 장애·비용 리스크 완화
- 장애 대응
  - 버튼 실패 시: “지연 처리” 라벨 + 재시도 큐(노션 태그) + 수동 트리거 스크립트
  - 배치 실패 시: 1회 재시도, 알림 전송, 다음 주기 자동 복구
  - NTP/서명 실패 시: body_raw/canonical/sig 3쌍 로그로 즉시 진단
- 비용 관리(대략)
  - Cloud Run 초단위 과금: 저빈도 트래픽 시 월 수~수십 USD 수준
  - Scheduler/Secrets/Logs 소액. LLM 사용량은 사용량 연동
  - 저부하 아키텍처 유지(무상시 정지, 콜드스타트 허용)

## 8) 보안·운영 표준(요약)
- HMAC-SHA256 + base64url, canonical JSON(NFC), 헤더: X-Timestamp/X-Nonce/X-Signature
- 스키마 해시 캐시(불일치: apply 차단), 옵션 동기화, parent.database_id 검사
- KPI(P95 경고>6s/위험>8s), 링크 실패 24h 3건↑ 알림, 10분 캐시 카드 반영
- 롤백: cron 비활성, 알림 비활성, 설정 복원

## 9) 권장 기준 아키텍처
- 런타임: Cloud Run(Container) + Secret Manager(키) + Cloud Scheduler(배치) + Cloud Logging
- 엔드포인트: `/webhook/*`, `/healthz`, 배치 엔트리포인트 2종(KPI/링크)
- 배포: GitHub Actions → Cloud Run, IaC(Optional) → 재현성 확보

## 10) 단계별 롤아웃
1) 파일럿: 단일 리전, 최소 인스턴스 0, 로그 수집·알림 연동
2) 본선: 최소 인스턴스 1(콜드스타트 완화), 커스텀 도메인/HTTPS, SLA 99.9% 목표
3) 확장: 멀티 리전, 큐/워크플로(Cloud Tasks/Workflows), 성능 튜닝

## 11) 의사결정 요약
- 기본 원칙: Notion-First. 서버는 가치를 추가하는 부분에만 사용
- 선택: Cloud Run 권장(보안/비용/운영 자동화 우수). Heroku는 간이 PoC, GitHub Pages/Actions는 보조용
- 다운타임 내성: 모든 버튼/배치를 “지연 처리” 가능 상태로 설계

## 12) 부록(참조)
- Z073 대문, Z075 운영 기준, Z077 사용자 시나리오, S4-018 서버 필요성
- 운영 문서: `README/OPERATIONS.md`, 배치/알림 설정 JSON, PR/릴노 템플릿
