## Z064: A2G2N Stage 3 개발경과·결과·문제해결·재발방지

### 1) 개요
- 목적: 웹 검색 수집(AI2G) → 임시 저장 → G2N → Notion 등록까지 Prio1 블로커 해제 및 10건 E2E 가동
- 기간: D~D+1
- 최종 상태: 스모크 200 OK, 10건 Notion 페이지 생성 200(제목 정상)

### 2) 성공 기준(AC)
- 403 블로커 해제: Google CSE로 200/링크 반환
- 데이터 10건 수집 및 Notion DB 자동 등록
- 보고: Page ID 10건, 로그 스니펫, 지연(P50/P95)

### 3) 실제 수행 내역
- 검색 어댑터 구현: Google CSE 어댑터(재시도 1,2,4s, 타임아웃 8s, 키 마스킹)
- 스모크 테스트 추가: `scripts/smoke_cse_test.py` (쿼리: 서남해해상풍력발전사업)
- 수집기: `scripts/a2g2n_collect_only.py` → `temp_drive/*.md` 10건 생성
- 등록기(개선): `scripts/a2g2n_register_from_temp.py`
  - .env BOM 허용 로더 추가, 스키마 조회, property_id 기반 title 전송
- 프로브: `scripts/notion_probe_and_register.py`, `scripts/print_db_schema.py`

### 4) 문제점과 원인
- 403 오류: 키 제한/환경 공백 등으로 발생 가능 → 키 trim 및 제약 조정으로 해소
- .env 인코딩 오류: UTF-16/BOM 파일로 로드 실패 → BOM 관용 로더 도입
- 401 Unauthorized: 잘못된/미주입 토큰 → 올바른 토큰 주입·검증으로 해소
- 400 Validation Error: DB 스키마 불일치(표시명/타입 mismatch) → property_id(title) 기반 최소 페이로드 전환

### 5) 해결 방안(적용 완료)
- 키/환경: 어댑터에서 env `strip()` 처리, 로그 마스킹 적용
- .env 로딩: `.env/.env.local/config.env` BOM 허용 파서 추가
- Notion 인증·권한: `users/me`·`databases/:id` 사전 프로브로 401/403 즉시 판별
- 등록 페이로드: property_id=`title`에 title만 필수 전송(이번 러닝은 URL 생략)

### 6) 재발 방지 체크리스트
- 실행 전 헬스체크 자동화: `users/me`=200, `databases/:id`=200 확인 후 등록
- 환경 일관성: `.env.example`는 UTF-8(no BOM) 고정, 실운영 `.env`는 복사 생성
- 비밀관리: 토큰·키 원문은 외부 시크릿 금고, 금고 문서에는 메모만 유지
- 스키마 변화 감지: 등록 전 DB 스키마 캐시·비교, 불일치 시 fail-fast
- 페이로드 전략: 표시명 대신 property_id 우선, 최소 필수 → 점진적 추가

### 7) 산출물(발췌)
- 수집: `temp_drive/*.md` 10건
- Notion 페이지(10/10 생성 200):
  - 27da613d-25ff-8149-ae6e-c2ca6d037402
  - 27da613d-25ff-8141-a2ac-d030383a020a
  - 27da613d-25ff-815c-bb65-c2695a1f7c44
  - 27da613d-25ff-81b0-9a3f-f16d5500f84f
  - 27da613d-25ff-8132-9ea3-dd93f6197479
  - 27da613d-25ff-81b7-943b-fea3ca647af7
  - 27da613d-25ff-8171-b898-f2ea7476f197
  - 27da613d-25ff-813a-8739-f525ad7c6144
  - 27da613d-25ff-81af-a1e5-fa783715dee1
  - 27da613d-25ff-813a-8f1f-c5327385ee8f
- 성능(로컬 기준): P50≈0.6s, P95≈1.4s

### 8) 교훈(Lessons Learned)
- 환경이 품질의 절반: 키 제한·BOM·세션 주입 같은 비코드 이슈가 가장 큰 리스크
- 최소 구현·최대 안전: property_id 기반 최소 페이로드가 초기 성공 확률을 높임
- 실행 전 정답 검증: 프로브(users/me, databases)로 인증/권한을 선판별하면 MTTR 단축

### 9) 후속 과제(권장)
- URL(`{MdI`)·상태·태그 등 선택 필드 단계적 추가 및 배치 성능 튜닝
- SERPAPI/Bing 백업 어댑터 연결 및 벤치마크 리포트
- CI에 .env/BOM 및 스키마 검증 스텝 추가


