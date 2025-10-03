# ZNNN_ 번호체계 프로토타입 명세서

## 개요

ZOBIS 시스템의 문서 번호 자동 할당을 위한 원자적 예약 시스템입니다.

## 패턴 정의

- **정규식**: `^Z\d{3}_`
- **범위**: Z001_ ~ Z999_
- **총 용량**: 999개 문서

## 동작 규칙

### 1. 원자적 예약
- 최대값+1 방식으로 다음 번호를 원자적으로 예약
- 데이터베이스 트랜잭션을 통한 동시성 제어
- 예약 실패 시 즉시 다음 번호로 스킵

### 2. 충돌 처리
- 동시 예약 시도 시 첫 번째 요청만 성공
- 나머지 요청은 자동으로 다음 번호로 스킵
- 모든 충돌과 스킵을 이력에 기록

### 3. 이력 관리
- 예약 시도: timestamp, thread_id, requested_number
- 충돌 감지: timestamp, thread_id, conflicted_number, final_number
- 스킵 이력: timestamp, thread_id, skipped_from, skipped_to

## 구현 세부사항

### 멀티스레드 경합 테스트
- **방식**: 실제 멀티스레드/비동기 병렬 실행
- **지연**: 각 요청에 5~10ms 난수 지연 삽입
- **동시성**: 최대 10개 스레드 동시 실행

### 데이터베이스 스키마
```sql
CREATE TABLE znnn_reservations (
    id INTEGER PRIMARY KEY,
    number VARCHAR(6) UNIQUE NOT NULL,
    thread_id VARCHAR(50),
    timestamp DATETIME,
    status ENUM('reserved', 'conflicted', 'skipped')
);

CREATE TABLE znnn_history (
    id INTEGER PRIMARY KEY,
    action VARCHAR(20),
    thread_id VARCHAR(50),
    from_number VARCHAR(6),
    to_number VARCHAR(6),
    timestamp DATETIME
);
```

### API 인터페이스
```python
def reserve_next_number() -> str:
    """다음 사용 가능한 ZNNN_ 번호를 원자적으로 예약"""
    pass

def get_current_max() -> str:
    """현재 최대 번호 조회"""
    pass

def get_reservation_history(limit: int = 100) -> List[Dict]:
    """예약 이력 조회"""
    pass
```

## 예외 처리

### 1. 범위 초과
- Z999_ 도달 시 예외 발생
- 관리자 알림 및 수동 처리 필요

### 2. 데이터베이스 오류
- 연결 실패 시 재시도 (최대 3회)
- 트랜잭션 롤백 시 이력 기록

### 3. 동시성 오류
- 데드락 감지 시 랜덤 지연 후 재시도
- 최대 재시도 횟수 초과 시 예외 발생

## 성능 요구사항

- **응답 시간**: P95 < 100ms
- **동시 처리**: 최대 100 TPS
- **가용성**: 99.9% uptime
- **데이터 일관성**: ACID 보장

## 모니터링

### 지표
- 예약 성공률
- 충돌 발생률
- 평균 응답 시간
- 데이터베이스 연결 상태

### 알림
- 범위 초과 경고 (Z950_ 도달 시)
- 성능 임계값 초과
- 데이터베이스 오류 발생

## 테스트 시나리오

### 1. 기본 기능 테스트
- 단일 요청으로 Z001_ 예약
- 순차 요청으로 Z002_, Z003_ 예약
- 최대값 조회 정확성 확인

### 2. 동시성 테스트
- 10개 스레드 동시 실행
- 충돌 감지 및 스킵 확인
- 이력 기록 정확성 검증

### 3. 예외 상황 테스트
- 데이터베이스 연결 실패
- 범위 초과 시뮬레이션
- 트랜잭션 롤백 처리

## 배포 계획

### Phase 1: 개발 환경
- 단위 테스트 통과
- 기본 기능 검증

### Phase 2: 스테이징 환경
- 동시성 테스트
- 성능 테스트
- 예외 처리 검증

### Phase 3: 프로덕션 배포
- 점진적 롤아웃
- 모니터링 활성화
- 성능 지표 수집
