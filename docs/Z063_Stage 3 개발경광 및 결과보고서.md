### 개요

- 식별자: Z063
- 범위: Stage 3 파이프라인(map → branch) 개발경과 및 결과보고
- 상태: 작성중

### 1) 진행 경과 요약

- 전용 테스트 페이지 생성 및 DB 소속 확인 완료
- map 단계: 속성 ID 원문 사용·UTF-8 전송으로 성공 전환
- branch 단계: 상태(status) 속성 매핑에서 실패 재현 및 원인 후보 확정

### 2) 핵심 조치 사항

- 키 소스 단일화: property_map(스키마 원문)만 사용
- 스키마 해시 검증: 캐시-실스키마 일치성 확인
- 전송 대상 검증: parent.database_id 강제, page 업데이트 시 대상 DB 소속 확인
- 요청 직전 불변 검증 미들웨어: props 키 집합·타입 스키마·금지문자 점검

### 2-1) 직면했던 문제와 해결

### 2-2) 서대리 문제해결 기록(교훈 아카이브)

- 문제 → 원인 → 해결 → 기술적 성과 → 교훈 → 재발 방지 체크리스트 순으로 축약 기록합니다.
- 사례 #1 — 한글 인코딩 깨짐으로 JSON 파싱 오류
    - 문제: "종료되지 않은 문자열" 등 JSON 파싱 오류 다발
    - 원인: PowerShell 기본 코드페이지 및 I/O 인코딩 불일치
    - 해결: PowerShell 7+ 권장, chcp 65001 고정, Input/OutputEncoding UTF-8, 해시테이블 → ConvertTo-Json → UTF-8 바이트 전송
    - 기술적 성과: map 단계 200 OK 전환, 멀티바이트 문자 손상 0건
    - 교훈: CLI·런타임 인코딩을 애플리케이션 레벨에서 강제해야 재현 안정 확보
    - 재발 방지: 시작 시점 인코딩 셀프체크 로그 출력 및 실패 시 fail-fast
- 사례 #2 — 속성명 기반 접근으로 매핑 불일치
    - 문제: 사람친화 키 사용으로 '문서 ?목' 등 손상, 매핑 실패
    - 원인: property_id 대신 name 기반 키 병용
    - 해결: Databases GET 응답의 property_id 원문만 사용, property_map.json 단일화
    - 기술적 성과: 키 불변성 확보, 매핑 성공률 향상
    - 교훈: 스키마 참조는 id 원문만 신뢰
    - 재발 방지: 빌드 단계 키 불변성 검증 미들웨어 유지
- 사례 #3 — parent 누락으로 DB 외부 페이지 생성
    - 문제: PATCH/CREATE 경로 이탈로 ID 불일치
    - 원인: parent.database_id 미설정
    - 해결: parent.database_id 강제, 대상 page_id의 소속 DB 사전 검증
    - 기술적 성과: 생성/업데이트 경로 일원화
    - 교훈: 요청 전 대상·부모 불변 검증은 필수
    - 재발 방지: 사전 검증 미들웨어 + 회귀 테스트 케이스 추가
- 사례 #4 — status/date/url 페이로드 스키마 불일치
    - 문제: 타입별 포맷 상이로 API 400 발생
    - 해결: status {"status":{"name":"작성중"}}, date {"date":{"start":"YYYY-MM-DD"}}, url {"url":"https://…"} 표준화
    - 기술적 성과: branch 단계 4xx 제거, 회귀 안정
    - 교훈: 타입별 표준 페이로드 스펙을 코드에 상수화
    - 재발 방지: 전송 직전 스키마 밸리데이션 및 샘플 페이로드 스냅샷 로그

> 신규 이슈 발생 시 위 포맷으로 항목 추가합니다. G1 통과 후 G2(10건) 확장 시 실패 케이스는 이 섹션에 요약 기록합니다.
> 
- 문제: 한글 인코딩 깨짐으로 JSON 파싱 오류 발생(예: "종료되지 않은 문자열")
    - 해결: PowerShell 7+ 권장, chcp 65001 + Input/OutputEncoding UTF-8 고정, 해시테이블 → ConvertTo-Json → UTF-8 바이트 전송 고정
- 문제: 속성명 기반 접근으로 '문서 ?목' 등 이름 손상 및 매핑 불일치
    - 해결: Databases GET 응답의 property_id 원문만 사용. URL 파생·정규화 금지. property_map.json로 단일화
- 문제: URL 인코딩된 ID(%7B… 등) 사용으로 "Invalid property identifier {MdI" 발생
    - 해결: API 원문 id만 채택. %, {, }, 공백 포함 시 fail-fast. 요청 직전 props.keys() 위생 검사
- 문제: Stage 3에서 parent 누락으로 DB 외부에 페이지 생성되어 ID 불일치 오류 유발
    - 해결: parent.database_id 강제. PATCH 대상 page_id의 소속 DB 검증 가드
- 문제: Stage 3 내부 병합 단계에서 props 키가 사람친화 키로 되돌아가는 변조
    - 해결: build_props 단일 진입점에서만 property_id로 구성. 이후 단계는 값만 추가, 키 불변. 요청 직전 불변 검증 미들웨어 추가
- 문제: status/date/url 페이로드 스키마 불일치
    - 해결: 타입별 표준 형태 강제
        - status: {"status":{"name":"작성중"}}
        - date: {"date":{"start":"YYYY-MM-DD"}}
        - url: {"url":"https://…"}
- 문제: 테스트 페이지가 DB 소속이 아니어서 업데이트 실패
    - 해결: ZOBIS 개발문서 DB 소속 전용 테스트 페이지(Z062_API 테스트 페이지) 생성 후 회귀 검증

### 3) 남은 이슈와 해결 계획

- branch 단계 상태 매핑
    - 조치: property_id 기반으로 [status.name](http://status.name) 정확 매칭, PATCH /pages/<page_id> 확인
    - 회귀: "작성중" → "검토중" 2-step 갱신 테스트

### 4) 로그 및 근거(요약)

- 독립 테스트: title+URL 최소 본문 200 OK
- Stage 3 A/B 본문 비교: parent 누락 → 생성 경로로 이탈 발견, 수정 적용
- 최신 재검증: map OK, branch에서 상태 키 탐색 불일치 → 패치 진행 중

### 5) 합격 기준(AC)

- G1 단건: extract/prompt/map/branch 전 단계 200 OK
- 상태 속성 2회 연속 갱신 성공("작성중"↔"검토중")
- props 키 집합 검증 100% 통과, 금지문자 0건

### 6) 다음 단계

### 7) 서대리 후속 지시(확정)

- 코드 패치: branch 단계 status 업데이트 로직을 property_id 기반으로 수정. DB 옵션명과 동일한 [status.name](http://status.name) 매칭. 전송 전 밸리데이션(props 키 집합, 타입 스키마 status/date/url, 금지문자[% {} 공백] fail-fast), parent.database_id 강제 및 page_id 소속 DB 사전 검증 유지
- 환경·연동 증빙: G2N 웹훅 /health 200 캡처(외부 접근 URL 포함), 키·환경값 재확인, 테스트 대상(Z062_API) 지정
- G1 회귀: “작성중 → 검토중 → 작성중” 2-step. 전 단계 2xx, 2회 연속 정확 갱신, 금지문자 0건. trace_id·page_id·database_id·property_id·요청/응답 요약 로그 제출
- G2 배치: G1 합격 후 10건 동시성 3~5로 실행. 재시도(1s,2s,4s). 결과표(성공/실패, 평균 처리시간, 실패 Top3, 재현 로그 링크) 제출
- 문서화: 본 문서의 “서대리 문제해결 기록(교훈 아카이브)”에 이번 패치 내용을 문제→원인→해결→성과→교훈→재발 방지 순으로 즉시 기록. 증빙 캡처 첨부
- 타임라인: D0 T+2h G1 회귀 결과 보고. D0 T+6h G2 10건 결과 리포트
- branch_[z042.py](http://z042.py) 상태 매핑 구간 property_id 기반 패치 적용
- G1 재시도 → 통과 즉시 G2 10건 동시성 3~5 확장
- 실행 로그 표준화 및 실패 케이스 자동 수집