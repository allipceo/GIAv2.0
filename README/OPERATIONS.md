# ZOBIS 운영 가이드

## 개요

ZOBIS 시스템의 운영 및 모니터링을 위한 종합 가이드입니다.

## 핵심 문서 링크

- **[Z073 - 통합 테스트·진척 관리](https://www.notion.so/Z073_-1-2-3-1935f44dcfc44e8bae11cca4c9acdf66)**
- **[Z075 - C2N 지침](https://www.notion.so/Z075_-DB-C2N-1ab15d1a018b4ffaa5da0d0c9ddc1d17)**
- **[Z077 - 사용자 시나리오](https://www.notion.so/Z077_-C2N-G2N-A1G2N-578e2e421ba94161b1e87757515c821d)**
- **[Z072 - 결과 허브](https://www.notion.so/Z072_-e69469e716954b1ca7e3ded5736d1603)**
- **[Z062 - 대상 문서](https://www.notion.so/Z062_-62d899af747846aa91630239e9120a22)**

## 시스템 구성

### 1. KPI 모니터링

#### 자동 수집
- **수집 주기**: 일 1회 (매일 02:00)
- **수집 스크립트**: `scripts/kpi_batch_collector.py`
- **로그 파일**: `/var/log/kpi_batch.log`

#### 지표 항목
- **성공률**: 현재 세션, 7일 rolling
- **P95 지연시간**: C2N2 ≤ 6s, C2N3 ≤ 8s
- **중복 스킵률**: 업서트 중복 방지율
- **실패 원인 분포**: 네트워크, 옵션, 스키마, 권한, 기타

#### 임계값
- **P95 경고**: > 6.0s
- **P95 위험**: > 8.0s
- **성공률 최소**: > 90%

### 2. 링크 검증

#### 검증 대상
- **C2N2**: Z062 "개발결과" 섹션 최근 24시간 링크
- **C2N3**: Z072 "케이스 3 결과 링크" 섹션 최근 24시간 링크

#### 검증 기준
- **HTTP 상태**: 200 필수, 3xx 리다이렉션 1회 허용
- **응답 시간**: 경고 > 1.5s, 위험 > 3.0s
- **SSL 인증서**: 유효성 필수, 자체서명/만료 불허
- **URL 형식**: Notion 도메인 우선, 외부 절대경로만 허용

#### 배치 실행
- **실행 주기**: 일 1회
- **실행 스크립트**: `scripts/link_validation_batch.py`
- **로그 파일**: `/var/log/link_validation.log`

### 3. 알림 시스템

#### 알림 채널 (우선순위)
1. **Slack Webhook** (1차) - 즉시 알림
2. **이메일** (2차) - 중요 수준 이상
3. **Notion 페이지** (3차) - 상단 "운영 경보" 섹션

#### 알림 조건
- **P95 위험**: 8.0s 초과 상태가 30분 이상 지속
- **링크 실패 누적**: 24시간 내 3건 이상
- **성공률 저하**: 7일 rolling 성공률 < 90%

### 4. ZNNN_ 번호체계

#### 패턴 규칙
- **정규식**: `^Z\d{3}_`
- **범위**: Z001_ ~ Z999_
- **총 용량**: 999개 문서

#### 동작 규칙
1. **원자적 예약**: 최대값+1 방식
2. **충돌 처리**: 해당 번호 스킵, 다음 번호 예약
3. **이력 기록**: 예약·충돌·스킵 모두 기록

#### 회귀 테스트
- **테스트 주기**: 필요 시
- **테스트 스크립트**: `test_znnn_regression.py`
- **성공 기준**: 90% 이상 성공률

## 설정 파일

### KPI 임계값
- **파일**: `config/kpi_thresholds.json`
- **내용**: P95 임계값, 성공률 최소값, rolling 윈도우

### 링크 검증 정책
- **파일**: `config/link_validation.json`
- **내용**: HTTP/SSL 정책, URL 형식 요구사항

### 알림 훅 설정
- **파일**: `config/alert_hooks.json`
- **내용**: Slack/이메일/Notion 알림 설정

## 배치 작업

### Linux cron 설정
```bash
# KPI 수집 (매일 02:00)
0 2 * * * /path/to/scripts/kpi_batch_collector.py >> /var/log/kpi_batch.log 2>&1

# 링크 검증 (매일 03:00)
0 3 * * * /path/to/scripts/link_validation_batch.py >> /var/log/link_validation.log 2>&1
```

### Windows Task Scheduler
- **KPI 수집**: 매일 02:00 실행
- **링크 검증**: 매일 03:00 실행
- **로그 파일**: `C:\logs\kpi_batch.log`, `C:\logs\link_validation.log`

## 모니터링 대시보드

### 대문 KPI 카드
- **48시간 지표**: 현재 세션 성공률, P95 지연시간
- **7일 Rolling**: 7일 평균 성공률, P95 지연시간
- **캐시 갱신**: 10분 간격
- **경고 배지**: P95 > 6.0s (노란색), P95 > 8.0s (빨간색)

### 운영 경보
- **위치**: Z073 상단 "운영 경보" 섹션
- **갱신**: 알림 발생 시 자동 업데이트
- **해제**: 조건 해제 시 자동 해제 알림

## 문제 해결

### 일반적인 문제
1. **P95 위험 초과**: 시스템 부하 확인, 리소스 모니터링
2. **링크 검증 실패**: SSL 인증서 갱신, URL 형식 확인
3. **알림 미발송**: 웹훅 URL 확인, 네트워크 연결 상태 점검

### 로그 확인
```bash
# KPI 배치 로그
tail -f /var/log/kpi_batch.log

# 링크 검증 로그
tail -f /var/log/link_validation.log

# 알림 훅 로그
tail -f /var/log/alert_hooks.log
```

### 성능 모니터링
```bash
# 시스템 리소스 확인
htop
df -h
free -m

# 네트워크 연결 확인
netstat -tulpn
ss -tulpn
```

## 롤백 절차

### 긴급 롤백
1. **cron 비활성화**: `crontab -e`에서 해당 라인 주석 처리
2. **알림 훅 비활성화**: `config/alert_hooks.json`에서 `enabled: false`
3. **설정 파일 복원**: 이전 버전으로 복원

### 점진적 롤백
1. **배치 작업 중단**: cron 작업 일시 중단
2. **설정 검토**: 문제 원인 파악
3. **단계적 복구**: 설정 수정 후 점진적 재활성화

## 연락처

- **시스템 관리자**: admin@zobis.com
- **개발팀**: dev@zobis.com
- **긴급 연락**: +82-10-0000-0000

---

**최종 업데이트**: 2025-10-03 01:25 KST
**문서 버전**: v1.0
**작성자**: 서대리
